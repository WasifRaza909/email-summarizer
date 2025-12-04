@echo off
REM Email Summarizer Pro - Setup Assistant
REM This script checks if all required files are in place

echo.
echo ========================================
echo   Email Summarizer Pro - Setup Check
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+
    echo    Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python is installed

REM Check if requirements are installed
python -c "import customtkinter, google_auth_oauthlib, requests" 2>nul
if errorlevel 1 (
    echo ❌ Dependencies not installed
    echo.
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed
) else (
    echo ✅ All dependencies are installed
)

REM Check for .env file
if not exist ".env" (
    echo.
    echo ⚠️  .env file not found
    echo Copying from .env.example...
    copy .env.example .env >nul
    if errorlevel 1 (
        echo ❌ Failed to create .env file
        pause
        exit /b 1
    )
    echo ✅ Created .env file (Edit it with your API key)
) else (
    echo ✅ .env file exists
)

REM Check for credentials.json
if not exist "credentials.json" (
    echo.
    echo ❌ credentials.json not found - THIS IS REQUIRED!
    echo.
    echo 📋 Steps to get credentials.json:
    echo.
    echo 1. Go to: https://console.cloud.google.com/
    echo 2. Create a new project
    echo 3. Enable "Gmail API" for your project
    echo 4. Go to "Credentials" menu
    echo 5. Click "Create Credentials" ^> "OAuth 2.0 Desktop Application"
    echo 6. Download the JSON file and rename it to "credentials.json"
    echo 7. Place it in this directory (same folder as this script^)
    echo 8. Run this setup script again
    echo.
    echo Then run: python email_customtkinter_gui.py
    echo.
    pause
    exit /b 1
) else (
    echo ✅ credentials.json exists
)

REM Check .env has API key
python -c "from dotenv import load_dotenv; import os; load_dotenv(); key = os.getenv('GEMINI_API_KEY'); exit(0 if key else 1)" 2>nul
if errorlevel 1 (
    echo.
    echo ❌ GEMINI_API_KEY not set in .env file
    echo.
    echo 📋 Steps to get your Gemini API key:
    echo 1. Go to: https://aistudio.google.com/app/apikey
    echo 2. Click "Create API Key"
    echo 3. Copy the key
    echo 4. Edit .env file and add: GEMINI_API_KEY=your_key_here
    echo.
    pause
    exit /b 1
) else (
    echo ✅ GEMINI_API_KEY is configured
)

echo.
echo ========================================
echo   ✅ All checks passed!
echo ========================================
echo.
echo You can now run the app with:
echo    python email_customtkinter_gui.py
echo.
pause
