#!/bin/bash

# Check if virtual environment folder exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install required Python packages
echo "Installing dependencies..."
    pip install tabulate
    sudo apt install python3-tk -y
    clear

# Run the script
echo "Running the script..."
python3 DVR_view.py