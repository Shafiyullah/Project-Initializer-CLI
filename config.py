# This file contains all the user-configurable settings for the automation script.

# --- Software Configuration ---
# Define packages for each specific package manager. The script will detect the
# manager and use the corresponding list.

# - "apt-get": For Debian, Ubuntu, etc.
# - "dnf": For Fedora, CentOS 8+, etc.
# - "yum": For older CentOS/RHEL/Amazon Linux
# - "pacman": For Arch Linux, Manjaro, etc.
# - "brew": For macOS (Homebrew)
# - "winget": For Windows Package Manager (use the package's "Id")

PACKAGES_TO_INSTALL = {
    "apt-get": [
        "git",
        "vim",
        "curl",
        "htop",
        "python3-pip"
    ],
    "dnf": [
        "git",
        "vim",
        "curl",
        "htop",
        "python3-pip"
    ],
    "yum": [ # Added yum support based on main.py logic
        "git",
        "vim",
        "curl",
        "htop",
        "python3-pip"
    ],
    "pacman": [
        "git",
        "vim",
        "curl",
        "htop",
        "python-pip"
    ],
    "brew": [
        "git",
        "vim",
        "curl",
        "htop"
    ],
    "winget": [
        "Git.Git",
        "vim.vim",
        "Python.Python3",
        "Microsoft.VisualStudioCode"
        # To find a package ID, run: winget search <appName>
    ]
}


# --- Version Control Setup ---
# The path for the new project directory and Git repository.
REPO_PATH = "my-cross-platform-project"

# A list of files to create and add to the initial commit.
# User can modify as they want to initial the any type of files in the list. 
INITIAL_FILES = [
    "README.md",
    "main.py",
    ".gitignore",
]

# The message for the first git commit.
COMMIT_MESSAGE = "Initial project setup via automation script"

# --- Feature: Virtual Environment Setup ---
# Enable (True/False) the creation of a Python virtual environment.
CREATE_VENV = True

# Name of the virtual environment directory.
VENV_NAME = ".venv"

# List of Python packages to install into the new environment.
PIP_PACKAGES = [
    "requests",
    "numpy"
    # Add more python packages which user wants specified packages to install.
]