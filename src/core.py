import os
import subprocess
import logging
import shutil
import platform
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import urllib.request
import urllib.error
from .utils import is_admin

def install_packages(package_manager: str, packages_config: Dict[str, List[str]], dry_run: bool = False):
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
            if package_manager == "brew" and package not in result.stdout: 
                raise subprocess.CalledProcessError(1, cmd_map["check"])
            
            logging.info(f"> '{package}' is already installed.")

        except subprocess.CalledProcessError:
            logging.info(f"> Installing '{package}'...")

            try:
                install_cmd = cmd_map["install"] + [package]
                if not dry_run:
                    subprocess.run(install_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                else:
                    logging.info(f"[DRY RUN] Would execute: {' '.join(install_cmd)}")

                logging.info(f"> Success.")

            except subprocess.CalledProcessError as e:
                logging.error(f"Failed to install '{package}': {e.stderr.decode().strip()}")

def create_project_structure(repo_path: str, structure: Dict[str, Any], dry_run: bool = False, force: bool = False):
    """
    Creates folders and files based on config.
    """
    logging.info(f"\n--- Scaffolding Project in '{repo_path}' ---")
    
    if os.path.exists(repo_path):
        if force:
            logging.warning(f"Project directory '{repo_path}' exists. Overwriting due to --force.")
            if not dry_run:
                pass 
        else:
            logging.error(f"Directory '{repo_path}' already exists. Use --force to overwrite.")
            if not dry_run:
                raise Exception(f"Directory '{repo_path}' already exists.")

    # Change to repo path first
    if not dry_run and not os.path.exists(repo_path):
        os.makedirs(repo_path)
    
    if dry_run:
        logging.info(f"[DRY RUN] Would create directory: {repo_path}")
        original_path = os.getcwd() # Don't change dir in dry run
    else:
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
                with open(os.path.join(name, ".keep"), "w") as f: 
                    pass

                logging.info(f"Created directory: {name}/")

            elif isinstance(content, str):
                # It's a file
                if name == ".gitignore" and os.path.exists(os.path.join(original_path, ".gitignore")):
                    shutil.copyfile(os.path.join(original_path, ".gitignore"), name)
                elif not os.path.exists(name):
                    with open(name, "w") as f:
                        f.write(content)
                    logging.info(f"Created file: {name}")

    except Exception as e:
        logging.error(f"Error creating structure: {e}")
    finally:
        os.chdir(original_path)

def secure_project(repo_path: str, gitignore_types: Optional[List[str]] = None, dry_run: bool = False):
    """
    Security check. Ensures sensitive files are gitignored.
    """
    logging.info("\n--- Security Check ---")
    gitignore_path = os.path.join(repo_path, ".gitignore")
    
    # Ensure .gitignore exists
    if not os.path.exists(gitignore_path):
        if not dry_run:
            with open(gitignore_path, "w") as f: 
                f.write("")
        else:
            logging.info("[DRY RUN] Would create empty .gitignore")
            return # Stop here for dry run to avoid file read error below if file doesn't exist
    
    if dry_run and not os.path.exists(gitignore_path): return
    
    # Read existing rules
    with open(gitignore_path, "r") as f:
        rules = f.read()
    
    # Rules we MUST enforce
    security_rules = [".env", ".venv/", "*.log", "__pycache__/"]
    
    with open(gitignore_path, "a") as f:
        for rule in security_rules:
            if rule not in rules:
                if not dry_run:
                    f.write(f"\n{rule}")
                    logging.info(f"SECURITY: Added '{rule}' to .gitignore")
                else:
                    logging.info(f"[DRY RUN] SECURITY: Would add '{rule}' to .gitignore")

    # Fetch dynamic gitignore
    if gitignore_types:
        logging.info(f"Fetching .gitignore templates for: {', '.join(gitignore_types)}")
        try:
            url = f"https://www.toptal.com/developers/gitignore/api/{','.join(gitignore_types)}"
            if not dry_run:
                with urllib.request.urlopen(url) as response:
                    content = response.read().decode('utf-8')
                    with open(gitignore_path, "a") as f:
                        f.write(f"\n\n# --- Fetched from gitignore.io ---\n{content}")
                    logging.info("Dynamic .gitignore content appended.")
            else:
                 logging.info(f"[DRY RUN] Would fetch and append .gitignore content from: {url}")
        except Exception as e:
            logging.error(f"Failed to fetch .gitignore content: {e}")

def setup_env_vars(repo_path: str, env_config: dict, dry_run: bool = False):
    logging.info("\n--- Environment Setup ---")
    
    # Project .env
    project_vars = env_config.get("project_env", {})
    if project_vars:
        if not dry_run:
            env_path = os.path.join(repo_path, ".env")
            with open(env_path, "a") as f:
                for k, v in project_vars.items():
                    f.write(f"{k}=\"{v}\"\n")
        else:
            logging.info(f"[DRY RUN] Would create .env with {len(project_vars)} variables")
    
    # Shell Profile (Linux/Mac only)
    if platform.system() != "Windows":
        profile_lines = env_config.get("shell_profile", [])
        if profile_lines:
            home = Path.home()
            shell = os.environ.get("SHELL", "")
            p_file = home / (".zshrc" if "zsh" in shell else ".bashrc")
            try:
                if not dry_run:
                    with open(p_file, "a") as f:
                        f.write("\n" + "\n".join(profile_lines) + "\n")
                    logging.info(f"Updated {p_file}")
                else:
                    logging.info(f"[DRY RUN] Would update shell profile {p_file}")
            except Exception as e:
                logging.warning(f"Could not update shell profile: {e}")

def setup_venv(repo_path: str, venv_name: str, packages: List[str], create: bool, dry_run: bool = False):
    if not create: return
    logging.info("\n--- Virtual Environment ---")
    
    venv_path = os.path.join(repo_path, venv_name)
    if not os.path.exists(venv_path):
        if not dry_run:
            subprocess.run([sys.executable, '-m', 'venv', venv_path], check=True)
            logging.info("Venv created.")
        else:
            logging.info(f"[DRY RUN] Would create venv at {venv_path}")

    # Determine pip path
    if platform.system() == "Windows":
        pip_exec = os.path.join(venv_path, "Scripts", "pip.exe")
        python_exec = os.path.join(venv_path, "Scripts", "python.exe")
    else:
        pip_exec = os.path.join(venv_path, "bin", "pip")
        python_exec = os.path.join(venv_path, "bin", "python")
    
    # Upgrade pip, setuptools, wheel to avoid issues with latest Python versions
    if os.path.exists(python_exec):
        logging.info("Upgrading pip, setuptools, and wheel...")
        if not dry_run:
            try:
                subprocess.run([python_exec, '-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools', 'wheel'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            except subprocess.CalledProcessError as e:
                logging.warning(f"Failed to upgrade pip: {e}")
        else:
            logging.info("[DRY RUN] Would upgrade pip, setuptools, wheel")
    
    if os.path.exists(pip_exec) and packages:
        if not dry_run:
            subprocess.run([pip_exec, 'install', *packages], check=True)
            logging.info("Packages installed.")
        else:
            logging.info(f"[DRY RUN] Would install packages: {packages}")
    elif dry_run and packages:
         logging.info(f"[DRY RUN] Would install packages: {packages} (pip not found yet)")

def run_hooks(repo_path: str, venv_name: str, commands: List[str], dry_run: bool = False):
    if not commands: return
    logging.info("\n--- Post-Setup Hooks ---")
    
    cwd = os.getcwd()
    if not dry_run:
        os.chdir(repo_path)
    # in dry run we stay in cwd or simulate paths
    
    # Resolve paths
    if platform.system() == "Windows":
        py_path = os.path.join(venv_name, "Scripts", "python.exe")
        pip_path = os.path.join(venv_name, "Scripts", "pip.exe")
    else:
        py_path = os.path.join(venv_name, "bin", "python")
        pip_path = os.path.join(venv_name, "bin", "pip")

    # Fallbacks
    if not os.path.exists(py_path): 
        py_path = "python3"

    if not os.path.exists(pip_path): 
        pip_path = "pip3"

    try:
        for cmd in commands:
            full_cmd = cmd.replace("{{VENV_PYTHON}}", py_path).replace("{{VENV_PIP}}", pip_path)
            logging.info(f"Running: {full_cmd}")
            if not dry_run:
                subprocess.run(full_cmd, shell=True, check=True)
            else:
                logging.info(f"[DRY RUN] Would execute hook: {full_cmd}")
    except Exception as e:
        logging.error(f"Error running hooks: {e}")
    finally:
        os.chdir(cwd)

def final_commit(repo_path: str, message: str, dry_run: bool = False):
    logging.info("\n--- Final Commit ---")
    cwd = os.getcwd()
    if not dry_run:
        os.chdir(repo_path)
    try:
        if not dry_run:
            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', message], check=True)
            logging.info("Commited.")
        else:
            logging.info(f"[DRY RUN] Would git add . and commit: '{message}' (in {repo_path})")
    except Exception:
        logging.info("Nothing to commit or Git error.")
    finally:
        os.chdir(cwd)
