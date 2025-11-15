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
    "yum": [
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
    ]
}


# --- Version Control Setup ---
REPO_PATH = "my-cross-platform-project"
INITIAL_FILES = [
    "README.md",
    "main.py",
    ".gitignore",
]
# Modified commit message to reflect it happens at the end
COMMIT_MESSAGE = "feat: Initial project setup and configuration"

# Feature: Virtual Environment Setup
CREATE_VENV = True
VENV_NAME = ".venv"
PIP_PACKAGES = [
    "requests",
    "numpy",
    "python-dotenv"
]

# Feature: Environment Variable Setup 
ENVIRONMENT_VARIABLES = {
    "project_env": {
        "DEBUG": "True",
        "DATABASE_URL": "sqlite:///./test.db",
        "API_KEY": "YOUR_API_KEY_HERE"
    },
    "shell_profile": [
        "# Added by automation script",
        "export MY_GLOBAL_TOOL_PATH=\"/opt/my-tools\"",
    ]
}

# Feature: Post-Setup Hooks
# A list of shell commands to run *after* venv creation but *before* the final commit.
# Commands are run from within the REPO_PATH.
# Use '{{VENV_PYTHON}}' and '{{VENV_PIP}}' as placeholders.
POST_SETUP_COMMANDS = [
    # Generates a requirements.txt file from the installed venv packages
    "{{VENV_PIP}} freeze > requirements.txt",
    
    # Example: Initialize a dbt project (if dbt was in PIP_PACKAGES)
    # "dbt init my_dbt_project",
    
    # Example: Run a test script
    # "{{VENV_PYTHON}} main.py --test"
]