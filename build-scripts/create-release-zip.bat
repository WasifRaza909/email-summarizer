@echo off
REM Email Summarizer Pro - Release Package Creator
REM Creates the ZIP package for CodeCanyon upload

setlocal enabledelayedexpansion

set "PROJECT_DIR=%~dp0"
set "PACKAGING_DIR=%PROJECT_DIR%packaging"
set "OUTPUT_NAME=email-summarizer-release.zip"
set "OUTPUT_PATH=%PACKAGING_DIR%\%OUTPUT_NAME%"

echo.
echo ========================================
echo Email Summarizer Pro - Package Creator
echo ========================================
echo.

REM Check if PowerShell is available
where powershell >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: PowerShell not found. Please install PowerShell 5.1+
    pause
    exit /b 1
)

REM Create packaging directory
if not exist "%PACKAGING_DIR%" mkdir "%PACKAGING_DIR%"

echo [1/4] Cleaning up sensitive files...
cd /d "%PROJECT_DIR%"
if exist credentials.json del /q credentials.json
if exist .env del /q .env
if exist token.pkl del /q token.pkl
if exist __pycache__ rmdir /s /q __pycache__ 2>nul
echo ✓ Cleaned

echo.
echo [2/4] Creating ZIP package...
echo       This may take a moment...

REM Use PowerShell to create the ZIP (handles Unicode/long paths)
powershell -NoProfile -Command ^
  "$items = @('^
    'config.py', '^
    'email_customtkinter_gui.py', '^
    'requirements.txt', '^
    'credentials.example.json', '^
    '.env.example', '^
    '.gitignore', '^
    'README.md', '^
    'INSTALL.md', '^
    'CHANGELOG.md', '^
    'SUPPORT.md', '^
    'item_description.txt', '^
    'LICENSE.txt', '^
    'GET_CREDENTIALS.md', '^
    'SETUP_GUIDE.md', '^
    'run_gui.bat', '^
    'setup.bat' ^
  ); ^
  if (Test-Path '%OUTPUT_PATH%') { Remove-Item '%OUTPUT_PATH%' -Force }; ^
  Compress-Archive -Path $items -DestinationPath '%OUTPUT_PATH%' -CompressionLevel Optimal"

if %errorlevel% equ 0 (
    echo ✓ Created: %OUTPUT_NAME%
) else (
    echo ERROR: Failed to create ZIP
    pause
    exit /b 1
)

echo.
echo [3/4] Generating checksums...

REM Generate SHA256 checksum
for /f "tokens=*" %%A in ('powershell -NoProfile -Command "Get-FileHash '%OUTPUT_PATH%' -Algorithm SHA256 | Select-Object -ExpandProperty Hash"') do set "CHECKSUM=%%A"

echo %CHECKSUM%  %OUTPUT_NAME% > "%PACKAGING_DIR%\SHA256SUMS.txt"
echo ✓ SHA256: %CHECKSUM%

echo.
echo [4/4] Package ready for upload!
echo.
echo ========================================
echo Package Location:
echo %OUTPUT_PATH%
echo.
echo File Size: 
for %%A in ("%OUTPUT_PATH%") do (
    set size=%%~zA
    echo !size! bytes
)
echo.
echo SHA256 Checksum:
echo %CHECKSUM%
echo.
echo Next Steps:
echo 1. Upload %OUTPUT_NAME% to CodeCanyon
echo 2. Create VirusTotal scan report (optional but recommended)
echo 3. Prepare screenshots and preview image
echo 4. Fill in CodeCanyon item details
echo.
echo ========================================
echo.
pause
