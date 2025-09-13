# Automated Software Configuration & Version Control System

This project is a command-line tool that **streamlines the setup of new software projects** with automated configuration and version control. It serves as a practical demonstration of fundamental skills in **configuration management**, **automation**, and **version control**.

The tool has two primary functions:
1.  **Automated Software Configuration**: It reads a list of required software packages from a configuration file (`config.py`) and installs them on a Linux-based system.
2.  **Automated Version Control**: It initializes a new Git repository, creates a sample file, and performs the first commit—all programmatically.

## Features

* **Idempotent Package Installation:** The tool intelligently checks for existing packages, **preventing redundant installations** and ensuring a clean setup.
* **Modular Design:** The separation of core logic from configuration settings ensures the code is **highly readable and easily maintained**.
* **Seamless Version Control:** It demonstrates how to **programmatically interact with Git** using Python's `subprocess` module to automate essential version control workflows.
* **High Portability:** Easily adapt the tool for any project by **simply modifying the `config.py` configuration file**.

## How to Use

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/Shafiyullah/Automate-Software-Configuration-And-Version-Control-System.git](https://github.com/Shafiyullah/Automate-Software-Configuration-And-Version-Control-System.git)
    cd your-repo-name
    ```
2.  **Edit Configuration:**
    Open `config.py` and modify the `PACKAGES_TO_INSTALL` list with the software you need for your new project.
3.  **Run the Script:**
    The script will provide real-time feedback in the terminal as it installs packages and performs Git operations.
    ```bash
    python3 main.py
    ```

## Technology Stack

* **Python**: The core programming language.
* **`subprocess` module**: Used to run shell commands (like `apt-get` and `git`) from within Python.
* **Git**: The project itself is version-controlled with Git, and the script automates basic Git commands.