@echo off
REM Check if virtual environment folder exists
IF NOT EXIST "venv" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
)

REM Activate the virtual environment
call venv\Scripts\activate.bat

REM Install required Python packages
echo Installing dependencies...
pip install tabulate tk

REM Run the script
echo Running the script...
python DVR_view.py

REM Deactivate the virtual environment after running
deactivate

pause