import subprocess
import os
import sys
import logging
import shutil
import platform
from typing import List, Dict, Optional
from pathlib import Path

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
            
    for package in packages:
        logging.info(f"Processing package: {package}...")
        try:
            # For package managers that check by name (apt, dnf, yum, pacman), use the package string
            if package_manager in ["apt-get", "yum", "dnf", "pacman"]:
                 check_cmd = [*cmd_map["check"], package.split(" ")[0]]
            elif package_manager == "winget":
                 check_cmd = [*cmd_map["check"], package]
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


def initialize_git_repo(repo_path: str, initial_files: List[str]):
    """
    Creates the project directory, initializes Git, and creates initial files.
    """
    logging.info("\n--- Automated Version Control Setup ---")

    if not shutil.which("git"):
        logging.error("Git is not installed or not in PATH. Skipping version control setup.")
        return

    # This is the one place we need the original path
    original_path = os.getcwd()
    
    if not os.path.exists(repo_path):
        os.makedirs(repo_path)
        logging.info(f"Created directory: {repo_path}")
    else:
        logging.warning(f"Directory '{repo_path}' already exists. Using it.")

    # Temporarily change to repo path to initialize
    try:
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
    
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to perform Git operation. Error: {e.stderr.decode().strip()}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        os.chdir(original_path)


def setup_environment_variables(env_vars_config: dict):
    """
    Feature: Configures environment variables from config.py.
    (Operates in the current working directory, expected to be REPO_PATH)
    """
    logging.info("\nAutomated Environment Variable Setup")
    
    # 1. Setup project-specific .env file (now uses relative path)
    project_vars = env_vars_config.get("project_env", {})
    if project_vars:
        env_file_path = ".env"
        logging.info(f"Writing project variables to: {env_file_path}")
        
        existing_keys = set()
        if os.path.exists(env_file_path):
            try:
                with open(env_file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line:
                            existing_keys.add(line.split('=', 1)[0].strip())
            except Exception as e:
                logging.error(f"Could not read existing .env file: {e}")

        try:
            with open(env_file_path, 'a', encoding='utf-8') as f:
                for key, value in project_vars.items():
                    if key not in existing_keys:
                        f.write(f"{key}=\"{value}\"\n")
                        logging.info(f"> Added '{key}' to .env")
                    else:
                        logging.info(f"> Skipping '{key}', already exists in .env")
        except Exception as e:
            logging.error(f"Failed to write to .env file: {e}")

    # 2. Setup system-wide shell profile variables
    profile_lines = env_vars_config.get("shell_profile", [])
    if not profile_lines:
        return

    if platform.system() == "Windows":
        logging.warning("Shell profile setup on Windows is not automated.")
        logging.warning("Please set these variables manually:")
        for line in profile_lines:
            logging.warning(f"  > {line}")
        return

    try:
        home_dir = Path.home()
        shell = os.environ.get("SHELL", "")
        profile_file = None

        if "bash" in shell:
            profile_file = home_dir / ".bashrc"
        elif "zsh" in shell:
            profile_file = home_dir / ".zshrc"
        else:
            profile_file = home_dir / ".profile" # Default fallback
        
        logging.info(f"Appending shell profile variables to: {profile_file}")
        
        existing_content = ""
        if os.path.exists(profile_file):
            with open(profile_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()

        with open(profile_file, 'a', encoding='utf-8') as f:
            f.write("\n")
            for line in profile_lines:
                if line in existing_content:
                    logging.info(f"> Skipping line, already in profile: '{line}'")
                else:
                    f.write(f"{line}\n")
                    logging.info(f"> Added to shell profile: '{line}'")
        
        logging.info(f"Shell profile updated. Please run 'source {profile_file}' or restart your terminal.")

    except Exception as e:
        logging.error(f"Failed to update shell profile: {e}")


def setup_virtual_environment(venv_name: str, pip_packages: List[str]):
    """
    Feature: Creates a Python venv and installs packages.
    (Operates in the current working directory, expected to be REPO_PATH)
    """
    if not config.CREATE_VENV:
        return

    logging.info("\nAutomated Python Environment Setup")
    
    try:
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


def execute_post_setup_hooks(venv_name: str, commands: List[str]):
    """
    Feature: Executes shell commands, using venv paths if they exist.
    (Operates in the current working directory, expected to be REPO_PATH)
    """
    if not commands:
        return

    logging.info("\n--- Executing Post-Setup Hooks ---")
    
    try:
        # Determine paths for venv executables
        if platform.system() == "Windows":
            python_exec = os.path.join(venv_name, "Scripts", "python.exe")
            pip_exec = os.path.join(venv_name, "Scripts", "pip.exe")
        else:
            python_exec = os.path.join(venv_name, "bin", "python")
            pip_exec = os.path.join(venv_name, "bin", "pip")

        # Fallback to system python/pip if venv doesn't exist
        if not os.path.exists(python_exec):
            logging.warning(f"Venv python '{python_exec}' not found. Falling back to system 'python3'.")
            python_exec = "python3"
            
        if not os.path.exists(pip_exec):
            logging.warning(f"Venv pip '{pip_exec}' not found. Falling back to system 'pip3'.")
            pip_exec = "pip3"

        for command in commands:
            # Replace placeholders
            cmd_to_run = command.replace("{{VENV_PYTHON}}", python_exec)
            cmd_to_run = cmd_to_run.replace("{{VENV_PIP}}", pip_exec)
            
            logging.info(f"Running hook: '{cmd_to_run}'...")
            try:
                # Use shell=True for convenience with commands like 'pip freeze > file'
                subprocess.run(cmd_to_run, shell=True, check=True, capture_output=True, text=True)
                logging.info(f"> Hook executed successfully.")
            except subprocess.CalledProcessError as e:
                logging.error(f"> Hook failed: {cmd_to_run}")
                logging.error(f"  Error: {e.stderr.strip()}")
                
    except Exception as e:
        logging.error(f"An unexpected error occurred during post-setup hooks: {e}")


def commit_final_changes(commit_message: str):
    """
    Adds all new files and creates the final initial commit.
    (Operates in the current working directory, expected to be REPO_PATH)
    """
    if not shutil.which("git"):
        logging.warning("Git not found, skipping final commit.")
        return
        
    logging.info("\n--- Finalizing Git Repository ---")
    try:
        logging.info("Adding all new files to staging...")
        subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
        
        status_result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if status_result.stdout:
            logging.info("Committing all changes...")
            subprocess.run(['git', 'commit', '-m', commit_message], check=True, capture_output=True)
            logging.info("Project files successfully committed.")
        else:
            logging.info("No changes detected. Skipping final commit.")
            
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to perform final Git commit. Error: {e.stderr.decode().strip()}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


def main():
    """Main entry point for the automation script."""
    logging.info(f"Running on: {platform.system()} ({platform.release()})")
    original_path = os.getcwd() # Store starting directory
    
    try:
        # 1. Install system-wide packages
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

        # 2. Initialize Git repo and create starter files
        initialize_git_repo(
            repo_path=config.REPO_PATH,
            initial_files=config.INITIAL_FILES
        )
        
        # Change into the project directory ONCE
        os.chdir(config.REPO_PATH)
        logging.info(f"Changed directory to '{os.getcwd()}'")
        
        # 3. Setup Environment Variables (.env and shell profile)
        setup_environment_variables(
            env_vars_config=config.ENVIRONMENT_VARIABLES
        )

        # 4. Setup Python Virtual Environment
        if config.CREATE_VENV:
            setup_virtual_environment(
                venv_name=config.VENV_NAME,
                pip_packages=config.PIP_PACKAGES
            )

        # 5. Run Post-Setup Hooks (e.g., pip freeze)
        execute_post_setup_hooks(
            venv_name=config.VENV_NAME,
            commands=config.POST_SETUP_COMMANDS
        )
        
        # 6. Create the final commit with all generated files
        commit_final_changes(
            commit_message=config.COMMIT_MESSAGE
        )
        
    except Exception as e:
        logging.error(f"A fatal error occurred: {e}", exc_info=True)
    finally:
        # Always return to the original directory
        os.chdir(original_path)
        logging.info(f"Changed directory back to '{original_path}'")
        
    logging.info("\n--- Automation Complete ---")
    logging.info("Review 'setup.log' for a detailed record of all operations.")

if __name__ == "__main__":
    main()