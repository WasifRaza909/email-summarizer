@echo off
REM Email Summarizer Pro - Pre-Release Security Check
REM Verify no sensitive files are included before upload

setlocal enabledelayedexpansion

echo.
echo ========================================
echo Security Pre-Flight Check
echo ========================================
echo.

set "PROJECT_DIR=%~dp0.."
set "ERROR_COUNT=0"

echo Checking for exposed files...
echo.

REM Check for exposed credentials
if exist "%PROJECT_DIR%\credentials.json" (
    echo [ERROR] credentials.json found - contains OAuth secrets!
    set /a ERROR_COUNT+=1
)

REM Check for .env with API keys
if exist "%PROJECT_DIR%\.env" (
    for /f "usebackq tokens=*" %%A in ("%PROJECT_DIR%\.env") do (
        echo %%A | findstr /r /c:"AIzaSy" /c:"GOCSPX-" /c:"sk-" >nul
        if !errorlevel! equ 0 (
            echo [ERROR] .env contains exposed API keys!
            set /a ERROR_COUNT+=1
            goto :check_done
        )
    )
)

REM Check for token cache
if exist "%PROJECT_DIR%\token.pkl" (
    echo [WARNING] token.pkl found - consider adding to .gitignore
)

:check_done
if %ERROR_COUNT% gtr 0 (
    echo.
    echo ========================================
    echo SECURITY CHECK FAILED!
    echo Found %ERROR_COUNT% security issues
    echo ========================================
    echo.
    echo Please fix these before uploading:
    echo 1. Delete credentials.json (users will provide their own)
    echo 2. Replace .env with safe template (.env.example)
    echo 3. Delete token.pkl (auto-generated, not needed)
    echo.
    pause
    exit /b 1
) else (
    echo ✓ All checks passed
    echo.
    echo ========================================
    echo SECURITY CHECK PASSED
    echo Safe to create release package
    echo ========================================
    echo.
    pause
    exit /b 0
)
