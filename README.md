# Project-Initializer-CLI

This project is a command-line tool that **streamlines the setup of new software projects** with automated configuration, directory scaffolding, and version control. It serves as a practical demonstration of fundamental skills in **configuration management**, **automation**, and **DevOps best practices**.

The tool has three primary functions:
1. **Automated Configuration**: It installs required software packages from `config.py` across a wide range of operating systems (`apt`, `dnf`, `brew`, `winget`).
2. **Project Scaffolding**: It creates a custom directory structure (`src/`, `tests/`, etc.) and initial files based on your configuration.
3. **Secure Version Control**: It initializes a Git repository, enforces security rules (ignoring secrets), and performs the first commit programmatically.

---

## Features

* **Cross-Platform Support**: Automatically detects the system's package manager and installs the correct packages.
* **Smart CLI**: *New Feature!* Use command-line flags (e.g., `--name`) to customize the project setup on the fly without editing code.
* **Project Scaffolding**: *New Feature!* Define your project's folder structure and starter files in `config.py`, and the tool will build the directory tree for you.
* **Security First**: *New Feature!* Automatically checks and enforces `.gitignore` rules to ensure sensitive files like `.env` and `.venv/` are never committed.
* **Automated Environment Variables**: Securely generates a `.env` file for project secrets and updates system-wide shell profiles (like `.bashrc`) for global pathing.
* **Automated Python Environment**: Optionally creates a Python virtual environment and installs necessary project dependencies (`requests`, `numpy`, etc.) via `pip`.
* **Post-Setup Hooks**: Define custom shell commands (like `pip freeze > requirements.txt` or `npm install`) that run *after* setup but *before* the final commit.

---

## Getting Started

Follow these steps to use the automation tool for your projects.

### Prerequisites
* **Python 3**: Ensure `python3` is installed and accessible in your system's PATH.

### Installation & Usage

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/Shafiyullah/Automate-Software-Configuration-And-Version-Control-System.git
    ```
    
    ```bash
    cd Automate-Software-Configuration-And-Version-Control-System
    ```

2. **Edit Configuration (Optional):**
    Open `config.py` to customize the `PACKAGES_TO_INSTALL`, `PROJECT_STRUCTURE`, or `ENVIRONMENT_VARIABLES`.

3. **Run the Setup Script:**
    You can run the script with default settings or use arguments to customize the execution.

    **Standard Run (uses defaults):**
    ```bash
    ./setup.sh
    ```

---
## Technology Stack
* **Python**: The core programming language used for the automation logic.
* **Bash**: The shell scripting language used for the CLI entry point.
* **Argparse**: A Python library for robust command-line argument parsing.
* **`subprocess` module**: Used to execute system commands and Git operations safely.
* **`logging` module**: Used for creating a detailed log of all setup operations.
* **Git**: The project itself is version-controlled, and the script automates Git initialization.