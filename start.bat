@echo off
REM Check if virtual environment folder exists
IF NOT EXIST "venv" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
)

REM Activate the virtual environment
call venv\Scripts\activate.bat

REM Install required Python packages from requirements.txt
IF EXIST requirements.txt (
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    cls
) ELSE (
    echo No requirements.txt found, skipping dependency installation.
)

REM Run the DVR_view.py script
echo Running DVR_view.py...
python DVR_view.py

REM Deactivate the virtual environment after running
deactivate

pause