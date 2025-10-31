import subprocess
import os
import sys
import logging
import shutil
import platform
from typing import List, Dict, Optional

# --- Configuration ---
try:
    import config
except ImportError:
    print("FATAL: config.py not found. Please create it from the template.")
    sys.exit(1)

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("setup.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ])

def is_admin() -> bool:
    """Check if the script is running with administrative privileges."""
    try:
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else: 
            # POSIX (Linux, macOS)
            return os.geteuid() == 0
    except Exception as e:
        logging.error(f"Could not determine admin status: {e}")
        return False
    
def get_package_manager() -> Optional[str]:
    """Detects the appropriate package manager for the system (DNF prioritized over YUM)."""
    system = platform.system()
    if system == "Linux":
        if shutil.which("apt-get"): return "apt-get"
        # Prioritize dnf over yum on modern systems
        if shutil.which("dnf"): return "dnf" 
        if shutil.which("yum"): return "yum"
        if shutil.which("pacman"): return "pacman"
    elif system == "Darwin": # macOS
        if shutil.which("brew"): return "brew"
    elif system == "Windows":
        if shutil.which("winget"): return "winget"
        if shutil.which("choco"): return "choco"
    return None

def install_packages(package_manager: str, packages_config: Dict[str, List[str]]):
    """
    Automates package installation using the detected package manager.
    """
    logging.info("--- Automated Software Configuration ---")

    packages = packages_config.get(package_manager)
    if not packages:
        logging.info(f"No packages listed in config.py for '{package_manager}'. Skipping installation.")
        return

    use_sudo = not is_admin() and platform.system() != "Windows"

    # Package manager command templates
    commands: Dict[str, Dict[str, List[str]]] = {
        "apt-get": {
            "update": ["apt-get", "update"],
            "install": ["apt-get", "install", "-y"],
            "check": ["dpkg", "-s"]
        },
        "yum": {
            "update": [],
            "install": ["yum", "install", "-y"],
            "check": ["rpm", "-q"]
        },
        "dnf": {
            "update": [],
            "install": ["dnf", "install", "-y"],
            "check": ["rpm", "-q"]
        },
        "pacman": {
            "update": ["pacman", "-Syu", "--noconfirm"],
            "install": ["pacman", "-S", "--noconfirm"],
            "check": ["pacman", "-Q"]
        },
        "brew": {
            "update": ["brew", "update"],
            "install": ["brew", "install"],
            "check": ["brew", "list", "--versions"]
        },
        "winget": {
            "update": [],
            "install": ["winget", "install", "-e", "--accept-source-agreements", "--id"],
            "check": ["winget", "list", "--id"]
        }
    }

    cmd_map = commands[package_manager]
    
    # Prepend sudo if needed for POSIX systems
    if use_sudo:
        for key in ["update", "install"]:
            if cmd_map[key]:
                cmd_map[key].insert(0, "sudo")

    # Update package lists
    if cmd_map["update"]:
        logging.info("Updating package lists...")
        try:
            subprocess.run(cmd_map["update"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to update package lists. Error: {e.stderr.decode().strip()}")
            # Continue to package installation even if update fails
            
    for package in packages:
        logging.info(f"Processing package: {package}...")
        try:
            # For package managers that check by name (apt, dnf, yum, pacman), use the package string
            if package_manager in ["apt-get", "yum", "dnf", "pacman"]:
                 check_cmd = [*cmd_map["check"], package.split(" ")[0]]
            # Winget/Brew check logic is unique
            elif package_manager == "winget":
                 check_cmd = [*cmd_map["check"], package] # Winget checks by ID
            elif package_manager == "brew":
                check_cmd = [*cmd_map["check"], package]
            
            result = subprocess.run(check_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Additional check for brew to verify the package is in the output
            if package_manager == "brew" and package not in result.stdout:
                raise subprocess.CalledProcessError(1, cmd_map["check"])
                
            logging.info(f"> '{package}' is already installed. Skipping.")
        except subprocess.CalledProcessError:
            logging.info(f"> '{package}' not found. Attempting to install...")
            try:
                # Winget needs the package ID passed with the install command, which is already set up in cmd_map
                if package_manager == "winget":
                    install_cmd = cmd_map["install"] + [package]
                else:
                    install_cmd = cmd_map["install"] + [package]
                    
                subprocess.run(install_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                logging.info(f"> Successfully installed '{package}'.")
            except subprocess.CalledProcessError as e:
                logging.error(f"> Failed to install '{package}'. Please check permissions or package name.")
                logging.error(f"  Error details: {e.stderr.decode().strip()}")

def setup_version_control(repo_path: str, initial_files: List[str], commit_message: str):
    """
    Automates the initialization of a Git repository, adds specified files, and makes a commit.
    """
    logging.info("\n--- Automated Version Control Setup ---")

    if not shutil.which("git"):
        logging.error("Git is not installed or not in PATH. Skipping version control setup.")
        return

    original_path = os.getcwd()
    try:
        if not os.path.exists(repo_path):
            os.makedirs(repo_path)
            logging.info(f"Created directory: {repo_path}")
        else:
            logging.warning(f"Directory '{repo_path}' already exists. Using it.")

        os.chdir(repo_path)

        if not os.path.exists(".git"):
            logging.info("Initializing Git repository...")
            subprocess.run(['git', 'init'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        else:
            logging.warning("A .git directory already exists. Skipping git init.")

        for file_name in initial_files:
            if not os.path.exists(file_name):
                # Special handling for .gitignore: copy from script root if available
                if file_name == ".gitignore" and os.path.exists(os.path.join(original_path, ".gitignore")):
                    shutil.copyfile(os.path.join(original_path, ".gitignore"), file_name)
                    logging.info(f"Copied file: '{file_name}' from script root.")
                else:
                    with open(file_name, "w") as f:
                        f.write(f"# This is an automatically generated {file_name} file.\n")
                    logging.info(f"Created file: '{file_name}'")

        if initial_files:
            logging.info("Adding files to staging area...")
            subprocess.run(['git', 'add', *initial_files], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Check for staged changes before committing
        status_result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if status_result.stdout:
            logging.info("Committing changes...")
            subprocess.run(['git', 'commit', '-m', commit_message], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            logging.info("Initial commit successful.")
        else:
            logging.info("No changes to commit.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to perform Git operation. Error: {e.stderr.decode().strip()}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        os.chdir(original_path)

def setup_virtual_environment(repo_path: str, venv_name: str, pip_packages: List[str]):
    """
    Feature: Creates and activates a Python virtual environment and installs specified packages.
    """
    if not config.CREATE_VENV:
        return

    logging.info("\nAutomated Python Environment Setup")
    
    original_path = os.getcwd()
    try:
        os.chdir(repo_path)
        
        # 1. Create venv
        if not os.path.exists(venv_name):
            logging.info(f"Creating virtual environment: '{venv_name}'...")
            subprocess.run([sys.executable, '-m', 'venv', venv_name], check=True, capture_output=True)
            logging.info("Virtual environment created successfully.")
        else:
            logging.warning(f"Virtual environment '{venv_name}' already exists. Skipping creation.")

        # Determine the path to the 'pip' executable inside the venv
        if platform.system() == "Windows":
            pip_path = os.path.join(venv_name, "Scripts", "pip")
        else:
            pip_path = os.path.join(venv_name, "bin", "pip")
            
        if not os.path.exists(pip_path):
             logging.error(f"Could not find pip executable at '{pip_path}'. Skipping package installation.")
             return

        # 2. Install packages
        if pip_packages:
            logging.info(f"Installing Python packages: {', '.join(pip_packages)}...")
            try:
                # Use the venv's pip executable
                install_cmd = [pip_path, 'install', *pip_packages]
                subprocess.run(install_cmd, check=True, capture_output=True)
                logging.info("Python packages installed successfully.")
            except subprocess.CalledProcessError as e:
                logging.error(f"Failed to install Python packages. Error: {e.stderr.decode().strip()}")
                
    except Exception as e:
        logging.error(f"An unexpected error occurred during venv setup: {e}")
    finally:
        os.chdir(original_path)

def main():
    """Main entry point for the automation script."""
    logging.info(f"Running on: {platform.system()} ({platform.release()})")

    # Install Packages
    pkg_manager = get_package_manager()
    if pkg_manager:
        logging.info(f"Detected package manager: '{pkg_manager}'")
        if not is_admin() and platform.system() != "Windows":
            logging.warning("Script not run as root. Sudo password may be required for installation.")
        elif platform.system() == "Windows" and not is_admin():
            logging.warning("Script not run as Administrator. Elevation may be required.")
        install_packages(pkg_manager, config.PACKAGES_TO_INSTALL)
    else:
        logging.error("Could not detect a supported package manager. Skipping package installation.")

    # Setup Version Control
    setup_version_control(
        repo_path=config.REPO_PATH,
        initial_files=config.INITIAL_FILES,
        commit_message=config.COMMIT_MESSAGE
    )
    
    # Feature: Setup Virtual Environment
    if config.CREATE_VENV:
        setup_virtual_environment(
            repo_path=config.REPO_PATH,
            venv_name=config.VENV_NAME,
            pip_packages=config.PIP_PACKAGES
        )

    logging.info("\n--- Automation Complete ---")
    logging.info("Review 'setup.log' for a detailed record of all operations.")

if __name__ == "__main__":
    main()