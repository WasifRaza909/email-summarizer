@echo off
REM Email Summarizer Pro - GUI Launcher
REM This script runs the main application silently

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Silently install/update dependencies
REM Inform user and silently install/update dependencies
echo Checking ^& Installing dependencies...
python -m pip install -q -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies.
    echo You can try running: python -m pip install -r requirements.txt
    pause
    exit /b 1
)
echo Dependencies installed successfully.

REM Change to script directory and launch GUI without showing console
cd /d "%~dp0"
start "" pythonw app.py
exit
