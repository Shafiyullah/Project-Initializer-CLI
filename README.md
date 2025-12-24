# Project-Initializer-CLI

This project is a command-line tool that **streamlines the setup of new software projects** with automated configuration, directory scaffolding, and version control. It serves as a practical demonstration of fundamental skills in **configuration management**, **automation**, and **DevOps best practices**.

The tool has three primary functions:
1. **Automated Configuration**: It installs required software packages from `config.yaml` across a wide range of operating systems (`apt`, `dnf`, `brew`, `winget`).
2. **Project Scaffolding**: It creates a custom directory structure (`src/`, `tests/`, etc.) and initial files based on your configuration.
3. **Secure Version Control**: It initializes a Git repository, enforces security rules (ignoring secrets), and performs the first commit programmatically.

---

## Features

* **Cross-Platform Support**: Automatically detects the system's package manager and installs the correct packages.
* **Smart CLI**: Use command-line flags (e.g., `--name`) to customize the project setup.
* **Project Templates**: *New!* Choose from multiple project structures (e.g., `default`, `basic`, `web`) defined in `config.yaml` using `--template`.
- **Interactive Mode**: Guided setup for project name, venv, and templates.
- **Dynamic .gitignore**: Fetch official templates (e.g., `python`, `windows`) from gitignore.io.
- **Custom Dependencies**: Add extra pip packages on the fly during setup.
- **Dry Run Mode**: Simulate the entire setup process without creating files.
- **Force Mode**: *New!* Use `--force` to overwrite existing directories if needed.
* **Security First**: Automatically checks and enforces `.gitignore` rules to ensure sensitive files like `.env` and `.venv/` are never committed.
* **Automated Environment Variables**: Securely generates a `.env` file and updates system-wide shell profiles.
* **Automated Python Environment**: Optionally creates a Python virtual environment and installs dependencies.
* **Post-Setup Hooks**: Define custom shell commands that run *after* setup but *before* the final commit.

---

## Getting Started

Follow these steps to use the automation tool for your projects.

### Prerequisites
* **Python 3**: Ensure `python3` is installed and accessible in your system's PATH.

### Installation & Usage

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/Shafiyullah/Project_Initilizer_CLI.git
    ```
    
    ```bash
    cd Project_Initilizer_CLI
    ```

2. **Edit Configuration (Optional):**
    Open `config.yaml` to customize the `PACKAGES_TO_INSTALL`, `PROJECT_STRUCTURE`, or `ENVIRONMENT_VARIABLES`.

3. **Run the Setup Script:**
    You can run the script with default settings or use arguments to customize the execution.

    **Standard Run (uses defaults):**
    ```bash
    python main.py
    ```

    **Dry Run (Simulate):**
    ```bash
    python main.py --name my-test-project --dry-run
    ```

    **Use a Template:**
    ```bash
    python main.py --name my-web-app --template web
    ```

---

## How to Use This Tool: A Simple Guide

This tool is designed to save you time. Here is how and when to use its different features.

### 1. The Easy Way (Interactive Mode)
**Best for:** Beginners or when you want to customize everything step-by-step.
Run the command:
```bash
python main.py --interactive
```
**What will happen?**
1.  It asks **Where** to create the project.
2.  It asks for the **Project Name**.
3.  It asks if you want a **Virtual Environment** (recommended for Python).
4.  It asks for extra **packages** (like `pandas`, `flask`).
5.  It checks if you have **Git**.
6.  It asks what files to ignore (e.g., `python, windows`).

### 2. The Safe Way (Dry Run)
**Best for:** Testing before doing anything. Use this if you are unsure what the tool will do.
```bash
python main.py --name my-test --dry-run
```
**What will happen?**
-   The tool will **print** everything it *would* do (creating folders, installing packages).
-   **Nothing** is actually created or changed.
-   Great for verifying your settings!

### 3. The Power User Way (CLI Arguments)
**Best for:** Automation scripts or when you know exactly what you want.
```bash
python main.py --name my-web-app --template web --no-venv
```
-   `--template`: Use a specific structure (defined in config.yaml).
-   `--no-venv`: Skip creating a virtual environment (faster).
-   `--force`: Overwrite an existing folder if you messed up.

---
## Technology Stack
* **Python**: The core programming language used for the automation logic.
* **argparse**: A Python library for robust command-line argument parsing.
* **subprocess module**: Used to execute system commands and Git operations safely.
* **logging module**: Used for creating a detailed log of all setup operations.
* **Git**: The project itself is version-controlled, and the script automates Git initialization.