#!/bin/bash

# Ensure that Python 3.9 and the venv package are installed on the system
echo -e "\e[32mVerifing that Python 3.9 and the venv package are installed...\e[0m"
sudo apt update
sudo apt install python3.9 python3.9-venv -y

# Check if the virtual environment directory already exists
if [ ! -d "venv" ]; then
    echo -e "\e[32mVirtual environment not found. Creating one...\e[0m"
    # If the virtual environment doesn't exist, create a new one using Python 3.9
    python3.9 -m venv venv
fi

# Activate the virtual environment
echo -e "\e[32mActivating the virtual environment...\e[0m"
source venv/bin/activate

# Upgrade pip inside the virtual environment to the latest version
echo -e "\e[32mUpgrading pip...\e[0m"
pip install --upgrade pip

# Install the required Python packages (tabulate and tk) within the virtual environment
echo -e "\e[32mInstalling dependencies in the virtual environment...\e[0m"
pip install tabulate tk

# Run the Python script within the virtual environment
echo -e "\e[32mRunning the script...\e[0m"
python3.9 DVR_view.py
