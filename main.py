import subprocess
import os
import sys
import logging
import shutil
from typing import List 

# --- Configuration ---
try:
    import config
except ImportError:
    print("FATAL: config.py not found. Please create it from the template.")
    sys.exit(1)

def install_packages():
    """
    Automates the installation of packages from the config.py file.
    This function assumes a Debian/Ubuntu-based system for 'apt-get'.
    """
    print("--- Automated Software Configuration ---")
    print("-" * 50)

    packages = config.PACKAGES_TO_INSTALL

    for package in packages:
        print(f"Checking for package: {package}...")
        try:
            # Check if package is already installed
            subprocess.run(['dpkg', '-s', package], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"  > {package} is already installed. Skipping.")
        except subprocess.CalledProcessError:
            print(f"  > {package} not found. Attempting to install...")
            try:
                # Update package lists and install the package
                subprocess.run(['sudo', 'apt-get', 'update'], check=True, stdout=subprocess.DEVNULL)
                subprocess.run(['sudo', 'apt-get', 'install', '-y', package], check=True, stdout=subprocess.DEVNULL)
                print(f"  > Successfully installed {package}.")
            except subprocess.CalledProcessError as e:
                print(f"  > Failed to install {package}. Please check permissions or package name.")
                print(f"Error: {e}")

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
                with open(file_name, "w") as f:
                    f.write("This is an automatically generated file.\n")
                logging.info(f"Created file: '{file_name}'")

        if initial_files:
            logging.info("Adding files to staging area...")
            subprocess.run(['git', 'add', *initial_files], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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

def main():
    """
    The main entry point for the Automated Software Configuration and Version Control System.
    """
    # Check if the platform is Linux-based
    if os.name != 'posix':
        print("This script is designed for Linux-based systems. Exiting.")
        sys.exit(1)

    install_packages()

    # Setup Version Control
    setup_version_control(
        repo_path=config.REPO_PATH,
        initial_files=config.INITIAL_FILES,
        commit_message=config.COMMIT_MESSAGE
    )

    logging.info("\n--- Automation Complete ---")
    logging.info("Review 'setup.log' for a detailed record of all operations.")

if __name__ == "__main__":
    main()