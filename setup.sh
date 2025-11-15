#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Starting project setup..."

# Check for Python 3. If not found, exit with a helpful error message.
if ! command -v python3 &> /dev/null 
then
    echo "ERROR: python3 could not be found." >&2
    echo "Please install Python 3 and ensure it's in your PATH." >&2
    exit 1
fi

# Determine the directory of the script and change to it.
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR"

# Run the Python script WITHOUT sudo.
# The main.py script will now ask for a password only if
# it needs to install system packages.
echo "Running the main Python automation script..."
python3 main.py

echo "Setup complete. Check setup.log for details."