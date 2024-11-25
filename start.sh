#!/bin/bash

# Ensure that Python 3.9 and the venv package are installed on the system
sudo apt update
sudo apt install python3.9 python3.9-venv -y

# Check if the virtual environment directory already exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    # If the virtual environment doesn't exist, create a new one using Python 3.9
    python3.9 -m venv venv
fi

# Activate the virtual environment
echo "Activating the virtual environment..."
source venv/bin/activate

# Upgrade pip inside the virtual environment to the latest version
echo "Upgrading pip..."
pip install --upgrade pip

# Install the required Python packages (tabulate and tk) within the virtual environment
echo "Installing dependencies in the virtual environment..."
pip install tabulate tk

# Clear the terminal screen
clear

# Run the Python script within the virtual environment
echo "Running the script..."
python3.9 DVR_view.py
