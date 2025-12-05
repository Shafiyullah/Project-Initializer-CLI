import os
import subprocess
import logging
import shutil
from pathlib import Path
from typing import List, Dict, Any
from .utils import is_admin

def install_packages(package_manager: str, packages_config: Dict[str, List[str]]):
    """
    Automates package installation using the detected package manager.
    """
    logging.info("--- Automated Software Configuration ---")

    packages = packages_config.get(package_manager)
    if not packages:
        return

    use_sudo = not is_admin() and platform.system() != "Windows"

    # Package manager command templates
    commands = {
        "apt-get": {"update": ["apt-get", "update"], "install": ["apt-get", "install", "-y"], "check": ["dpkg", "-s"]},
        "yum":     {"update": [], "install": ["yum", "install", "-y"], "check": ["rpm", "-q"]},
        "dnf":     {"update": [], "install": ["dnf", "install", "-y"], "check": ["rpm", "-q"]},
        "pacman":  {"update": ["pacman", "-Syu", "--noconfirm"], "install": ["pacman", "-S", "--noconfirm"], "check": ["pacman", "-Q"]},
        "brew":    {"update": ["brew", "update"], "install": ["brew", "install"], "check": ["brew", "list", "--versions"]},
        "winget":  {"update": [], "install": ["winget", "install", "-e", "--accept-source-agreements", "--id"], "check": ["winget", "list", "--id"]}
    }

    cmd_map = commands.get(package_manager)
    if not cmd_map:
        logging.warning(f"Unsupported package manager: {package_manager}")
        return

    if use_sudo:
        for key in ["update", "install"]:
            if cmd_map[key]: cmd_map[key].insert(0, "sudo")

    # Update package lists
    if cmd_map["update"]:
        logging.info("Updating package lists...")
        try:
            subprocess.run(cmd_map["update"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to update package lists: {e}")

    for package in packages:
        logging.info(f"Processing package: {package}...")
        try:
            check_arg = package if package_manager in ["winget", "brew"] else package.split(" ")[0]
            check_cmd = [*cmd_map["check"], check_arg]
            
            result = subprocess.run(check_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if package_manager == "brew" and package not in result.stdout: raise subprocess.CalledProcessError(1, cmd_map["check"])
            logging.info(f"> '{package}' is already installed.")
        except subprocess.CalledProcessError:
            logging.info(f"> Installing '{package}'...")
            try:
                install_cmd = cmd_map["install"] + [package]
                subprocess.run(install_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                logging.info(f"> Success.")
            except subprocess.CalledProcessError as e:
                logging.error(f"Failed to install '{package}': {e.stderr.decode().strip()}")

def create_project_structure(repo_path: str, structure: Dict[str, Any]):
    """
    Creates folders and files based on config.
    """
    logging.info(f"\n--- Scaffolding Project in '{repo_path}' ---")
    
    # Change to repo path first
    if not os.path.exists(repo_path):
        os.makedirs(repo_path)
    
    original_path = os.getcwd()
    os.chdir(repo_path)

    try:
        # Initialize Git immediately
        if not os.path.exists(".git"):
            subprocess.run(['git', 'init'], check=True, stdout=subprocess.DEVNULL)
            logging.info("Git repository initialized.")

        # Build structure
        for name, content in structure.items():
            if content is None:
                # It's a directory
                os.makedirs(name, exist_ok=True)
                # Create a .keep file so git tracks the empty folder
                with open(os.path.join(name, ".keep"), "w") as f: pass
                logging.info(f"Created directory: {name}/")
            elif isinstance(content, str):
                # It's a file
                if name == ".gitignore" and os.path.exists(os.path.join(original_path, ".gitignore")):
                    shutil.copyfile(os.path.join(original_path, ".gitignore"), name)
                elif not os.path.exists(name):
                    with open(name, "w") as f: f.write(content)
                    logging.info(f"Created file: {name}")

    except Exception as e:
        logging.error(f"Error creating structure: {e}")
    finally:
        os.chdir(original_path)

def secure_project(repo_path: str):
    """
    Security check. Ensures sensitive files are gitignored.
    """
    logging.info("\n--- Security Check ---")
    gitignore_path = os.path.join(repo_path, ".gitignore")
    
    # Ensure .gitignore exists
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, "w") as f: f.write("")
    
    # Read existing rules
    with open(gitignore_path, "r") as f:
        rules = f.read()
    
    # Rules we MUST enforce
    security_rules = [".env", ".venv/", "*.log", "__pycache__/"]
    
    with open(gitignore_path, "a") as f:
        for rule in security_rules:
            if rule not in rules:
                f.write(f"\n{rule}")
                logging.info(f"SECURITY: Added '{rule}' to .gitignore")

def setup_env_vars(repo_path: str, env_config: dict):
    logging.info("\n--- Environment Setup ---")
    
    # Project .env
    project_vars = env_config.get("project_env", {})
    if project_vars:
        env_path = os.path.join(repo_path, ".env")
        with open(env_path, "a") as f:
            for k, v in project_vars.items():
                f.write(f"{k}=\"{v}\"\n")
    
    # Shell Profile (Linux/Mac only)
    if platform.system() != "Windows":
        profile_lines = env_config.get("shell_profile", [])
        if profile_lines:
            home = Path.home()
            shell = os.environ.get("SHELL", "")
            p_file = home / (".zshrc" if "zsh" in shell else ".bashrc")
            try:
                with open(p_file, "a") as f:
                    f.write("\n" + "\n".join(profile_lines) + "\n")
                logging.info(f"Updated {p_file}")
            except Exception as e:
                logging.warning(f"Could not update shell profile: {e}")

def setup_venv(repo_path: str, venv_name: str, packages: List[str], create: bool):
    if not create: return
    logging.info("\n--- Virtual Environment ---")
    
    venv_path = os.path.join(repo_path, venv_name)
    if not os.path.exists(venv_path):
        subprocess.run([sys.executable, '-m', 'venv', venv_path], check=True)
        logging.info("Venv created.")

    # Determine pip path
    pip_exec = os.path.join(venv_path, "Scripts" if platform.system() == "Windows" else "bin", "pip")
    
    if os.path.exists(pip_exec) and packages:
        subprocess.run([pip_exec, 'install', *packages], check=True)
        logging.info("Packages installed.")

def run_hooks(repo_path: str, venv_name: str, commands: List[str]):
    if not commands: return
    logging.info("\n--- Post-Setup Hooks ---")
    
    cwd = os.getcwd()
    os.chdir(repo_path)
    
    # Resolve paths
    if platform.system() == "Windows":
        py_path = os.path.join(venv_name, "Scripts", "python.exe")
        pip_path = os.path.join(venv_name, "Scripts", "pip.exe")
    else:
        py_path = os.path.join(venv_name, "bin", "python")
        pip_path = os.path.join(venv_name, "bin", "pip")

    # Fallbacks
    if not os.path.exists(py_path): py_path = "python3"
    if not os.path.exists(pip_path): pip_path = "pip3"

    try:
        for cmd in commands:
            full_cmd = cmd.replace("{{VENV_PYTHON}}", py_path).replace("{{VENV_PIP}}", pip_path)
            logging.info(f"Running: {full_cmd}")
            subprocess.run(full_cmd, shell=True, check=True)
    finally:
        os.chdir(cwd)

def final_commit(repo_path: str, message: str):
    logging.info("\n--- Final Commit ---")
    cwd = os.getcwd()
    os.chdir(repo_path)
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', message], check=True)
        logging.info("Commited.")
    except Exception:
        logging.info("Nothing to commit or Git error.")
    finally:
        os.chdir(cwd)
