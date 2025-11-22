#!/bin/bash
set -e

# Check for Python 3
if ! command -v python3 &> /dev/null 
then
    echo "ERROR: python3 could not be found." >&2
    echo "Please install Python 3 and ensure it's in your PATH." >&2
    exit 1
fi

# Determine the directory of the script and change to it.
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR"

# Pass all arguments ($@) to the python script
# This allows you to run: ./setup.sh --name "my-cool-app"
echo "Running automation..."
python3 main.py "$@"