# Project-Initializer-CLI

This project is a command-line tool that **streamlines the setup of new software projects** with automated configuration and version control. It serves as a practical demonstration of fundamental skills in **configuration management**, **automation**, and **version control**.

The tool has two primary functions:
1. **Automated Software Configuration**: It reads a list of required software packages from a configuration file (`config.py`) and installs them on a wide range of operating systems.
2. **Automated Version Control**: It initializes a new Git repository, creates initial project files, and performs the first commit—all programmatically.

---

## Features

* **Cross-Platform Support**: The tool automatically detects the system's package manager (`apt`, `dnf`, `brew`, `winget`, etc.) and installs the correct packages.
* **Idempotent Package Installation**: The tool intelligently checks for existing packages, **preventing redundant installations** and ensuring a clean setup.
* **Automated Python Environment**: *New Feature!* It can **optionally create a Python virtual environment** and install necessary project dependencies (`requests`, `numpy`, etc.) via `pip`.
* **Modular Design**: The separation of core logic from user-configurable settings in `config.py` ensures the code is **highly readable and easily maintained**.
* **Seamless Version Control**: It demonstrates how to **programmatically interact with Git** using Python's `subprocess` module to automate essential version control workflows.
* **High Portability**: Easily adapt the tool for any project by **simply modifying the `config.py` configuration file**.

---

## Getting Started

Follow these steps to use the automation tool for your projects.

### Prerequisites
* **Python 3**: Ensure `python3` is installed and accessible in your system's PATH.

### Installation & Usage

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/Shafiyullah/Automate-Software-Configuration-And-Version-Control-System.git
    cd Automate-Software-Configuration-And-Version-Control-System
    ```

2. **Edit Configuration:**
    Open the `config.py` file and modify the `PACKAGES_TO_INSTALL` dictionary with the software packages you need. You can also change the `REPO_PATH`, `INITIAL_FILES`, and the new **virtual environment settings (`CREATE_VENV`, `VENV_NAME`, `PIP_PACKAGES`)** for your project.

3. **Run the Setup Script:**
    The `setup.sh` script will automatically check for prerequisites and run the main Python script with the necessary administrative permissions.
    ```bash
    ./setup.sh
    ```
    *Note: You may be prompted for your password to allow package installation.*

---

## Technology Stack

* **Python**: The core programming language used for the automation logic.
* **Bash**: The shell scripting language used for the user-friendly setup launcher.
* **`subprocess` module**: A built-in Python library used to execute system commands.
* **`logging` module**: A standard Python library for creating a detailed log of all setup operations.
* **Git**: The project itself is version-controlled with Git, and the script automates basic Git commands to initialize new projects.

---
