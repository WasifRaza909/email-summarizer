@echo off
REM Email Summarizer Pro - GUI Launcher
REM This script runs the main application

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Checking ^& Installing dependencies... Don't worry, it's a one-time installation.
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Please run as Administrator and try again
    echo.
    pause
    exit /b 1
)

echo.
echo Checking configuration files...
if not exist credentials.json (
    echo WARNING: credentials.json not found. Setup will prompt you to authenticate.
)
if not exist .env (
    echo WARNING: .env file not found. Setup will prompt you for GEMINI_API_KEY.
)

echo.
echo Launching Email Summarizer Pro...
timeout /t 2 /nobreak

cls

REM Change to script directory and launch GUI
cd /d "%~dp0"
start "" pythonw app.py
exit
