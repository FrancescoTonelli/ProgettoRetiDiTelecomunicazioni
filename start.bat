@echo off
REM Install required Python packages
echo Installing dependencies...
python -m pip install --upgrade pip
pip install tabulate tk

REM Run the script
echo Running the script...
python .\DVR_view.py