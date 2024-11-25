#!/bin/bash

# Check if virtual environment folder exists
sudo apt install python3.9-venv

if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3.9 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install required Python packages
echo "Installing dependencies..."
    sudo apt install python3-tabulate -y
    sudo apt install python3-tk -y
    clear

# Run the script
echo "Running the script..."
python3.9 DVR_view.py