#!/bin/bash

# Check if virtual environment folder exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install required Python packages from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
    clear
else
    echo "No requirements.txt found, skipping dependency installation."
fi

# Run the script
echo "Running the script..."
python3 DVR_view.py

# Deactivate the virtual environment after running
deactivate