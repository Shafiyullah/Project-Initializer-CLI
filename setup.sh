#!/bin/bash

echo "Running initial setup for the Automated Configuration Tool..."

# Check for Python 3
if ! command -v python3 &> /dev/null
then
    echo "Python 3 not found. Please install Python 3 and try again."
    exit 1
fi

# Run the main Python script with superuser privileges
python3 main.py