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
    "apt-get": ["git", "vim", "curl", "htop", "python3-pip"],
    "dnf":     ["git", "vim", "curl", "htop", "python3-pip"],
    "yum":     ["git", "vim", "curl", "htop", "python3-pip"],
    "pacman":  ["git", "vim", "curl", "htop", "python-pip"],
    "brew":    ["git", "vim", "curl", "htop"],
    "winget":  ["Git.Git", "vim.vim", "Python.Python3", "Microsoft.VisualStudioCode"]
}

# --- Default Project Settings ---
# These can be overridden by Command Line Arguments
DEFAULT_REPO_NAME = "my-automated-project"
COMMIT_MESSAGE = "feat: Initial project setup via automation"

# --- Feature: Project Scaffolding ---
# Define the folder structure and empty files to create.
# "None" means it's a folder. Strings are filenames.
PROJECT_STRUCTURE = {
    "src": None,              # Creates a src/ folder
    "tests": None,            # Creates a tests/ folder
    "docs": None,             # Creates a docs/ folder
    "README.md": "Initial documentation", # Creates file with content
    ".gitignore": None,       # Will be populated by the script
    "main.py": "# Entry point",
}

# --- Feature: Virtual Environment ---
CREATE_VENV = True
VENV_NAME = ".venv"
PIP_PACKAGES = [
    "requests",
    "numpy",
    "python-dotenv"
]

# --- Feature: Environment Variables ---
ENVIRONMENT_VARIABLES = {
    "project_env": {
        "DEBUG": "True",
        "API_KEY": "CHANGE_ME"
    },
    "shell_profile": [
        "# Added by automation script",
        "export MY_TOOL_PATH=\"/opt/my-tools\"",
    ]
}

# --- Feature: Post-Setup Hooks ---
POST_SETUP_COMMANDS = [
    "{{VENV_PIP}} freeze > requirements.txt"
]