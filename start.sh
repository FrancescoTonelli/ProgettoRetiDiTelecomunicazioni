#!/bin/bash

# Upgrade pip to the latest version
echo -e "\e[32mUpgrading pip...\e[0m"
pip install --upgrade pip

# Install the required Python packages (tabulate and tk)
echo -e "\e[32mInstalling dependencies...\e[0m"
pip install tabulate tk

# Run the Python script
echo -e "\e[32mRunning the script...\e[0m"
python3.9 DVR_view.py
