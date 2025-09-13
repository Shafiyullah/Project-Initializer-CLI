import subprocess
import os
import sys
import config

def install_packages():
    """
    Automates the installation of packages from the config.py file.
    This function assumes a Debian/Ubuntu-based system for 'apt-get'.
    """
    print("--- Part 1: Automated Software Configuration ---")
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

def setup_version_control():
    """
    Automates the initialization of a Git repository, adds files, and makes a commit.
    """
    print("\n--- Part 2: Automated Version Control System ---")
    print("-" * 50)

    repo_path = "my-new-project"

    try:
        # Check if a directory for the project already exists
        if not os.path.exists(repo_path):
            os.makedirs(repo_path)
            print(f"Created directory: {repo_path}")

        # Change into the new project directory
        os.chdir(repo_path)

        # Initialize a new Git repository
        print("Initializing Git repository...")
        subprocess.run(['git', 'init'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Create a sample file
        with open("first_file.txt", "w") as f:
            f.write("This is my first automated file.")
        print("Created 'first_file.txt'.")

        # Add the file to the staging area
        print("Adding file to staging area...")
        subprocess.run(['git', 'add', 'first_file.txt'], check=True, stdout=subprocess.DEVNULL)

        # Make the initial commit
        print("Committing changes...")
        subprocess.run(['git', 'commit', '-m', 'Initial automated commit'], check=True, stdout=subprocess.DEVNULL)
        print("Initial commit successful.")

    except FileNotFoundError:
        print("Error: 'git' command not found. Please ensure Git is installed on your system.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to perform Git operation. Error: {e}")
    finally:
        # Change back to the original directory to prevent issues
        os.chdir('..')

def main():
    """
    The main entry point for the Automated Software Configuration and Version Control System.
    """
    # Check if the platform is Linux-based
    if os.name != 'posix':
        print("This script is designed for Linux-based systems. Exiting.")
        sys.exit(1)

    install_packages()
    setup_version_control()

    print("\n--- Automation Complete ---")
    print("The system has successfully configured software and set up a Git repository.")

if __name__ == "__main__":
    main()