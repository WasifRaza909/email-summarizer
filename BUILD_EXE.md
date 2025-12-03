# Creating Windows .EXE Files (PyInstaller Guide)

## Overview

To ship as a standalone `.exe` (no Python installation required), use PyInstaller.

This guide creates:
- **Setup installer** (`email-summarizer-setup.exe`)
- **Portable executable** (`email-summarizer-portable.exe`)

---

## Prerequisites

Install PyInstaller:
```bash
pip install pyinstaller
```

Verify installation:
```bash
pyinstaller --version
```

---

## Step 1: Prepare for Build

### Clean up development files
```bash
cd d:\Practice\email-summarizer
rmdir /s /q __pycache__
del /q *.pyc
del /q token.pkl
del /q credentials.json
```

### Verify all required files exist
- `email_customtkinter_gui.py` ✓
- `config.py` ✓
- `requirements.txt` ✓
- `credentials.example.json` ✓
- `.env.example` ✓
- All documentation files ✓

---

## Step 2: Build with PyInstaller

### Option A: Portable Executable (Recommended for Distribution)

```bash
cd d:\Practice\email-summarizer

pyinstaller ^
  --name "email-summarizer" ^
  --onefile ^
  --windowed ^
  --icon=icon.ico ^
  --add-data "credentials.example.json:." ^
  --add-data ".env.example:." ^
  --hidden-import=customtkinter ^
  --hidden-import=google.auth ^
  --hidden-import=google.auth.oauthlib ^
  --hidden-import=google.api_client ^
  --hidden-import=google_auth_httplib2 ^
  --collect-all customtkinter ^
  email_customtkinter_gui.py
```

Output: `dist/email-summarizer.exe`

### Option B: Directory Bundle (Faster Execution)

```bash
pyinstaller ^
  --name "email-summarizer" ^
  --onedir ^
  --windowed ^
  --icon=icon.ico ^
  --add-data "credentials.example.json:." ^
  --add-data ".env.example:." ^
  --hidden-import=customtkinter ^
  email_customtkinter_gui.py
```

Output: `dist/email-summarizer/email-summarizer.exe`

---

## Step 3: Create Windows Installer (NSIS)

### Install NSIS
Download & install: [NSIS](https://nsis.sourceforge.io/)

### Create installer script: `installer.nsi`

```nsis
; Email Summarizer Pro - Windows Installer
; Generated for NSIS

!include "MUI2.nsh"

; General Settings
Name "Email Summarizer Pro"
OutFile "email-summarizer-setup.exe"
InstallDir "$PROGRAMFILES\Email Summarizer Pro"

; UI Settings
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

; Installation
Section "Install"
  SetOutPath "$INSTDIR"
  
  ; Copy executable
  File "dist\email-summarizer\email-summarizer.exe"
  
  ; Copy data files
  File "credentials.example.json"
  File ".env.example"
  File "README.md"
  File "INSTALL.md"
  File "SUPPORT.md"
  
  ; Create Start Menu shortcuts
  CreateDirectory "$SMPROGRAMS\Email Summarizer Pro"
  CreateShortcut "$SMPROGRAMS\Email Summarizer Pro\Email Summarizer.lnk" "$INSTDIR\email-summarizer.exe"
  CreateShortcut "$SMPROGRAMS\Email Summarizer Pro\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

; Uninstallation
Section "Uninstall"
  RMDir /r "$INSTDIR"
  RMDir /r "$SMPROGRAMS\Email Summarizer Pro"
SectionEnd
```

### Build installer:
```bash
"C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi
```

Output: `email-summarizer-setup.exe`

---

## Step 4: Code Signing (Optional but Recommended)

### Generate self-signed certificate (for testing)
```powershell
$cert = New-SelfSignedCertificate -DnsName "email-summarizer.local" -Type CodeSigning -CertStoreLocation Cert:\CurrentUser\My
Export-Certificate -Cert $cert -FilePath cert.cer
```

### Sign the .exe files
```powershell
Set-AuthenticodeSignature -FilePath dist\email-summarizer.exe -Certificate $cert
Set-AuthenticodeSignature -FilePath email-summarizer-setup.exe -Certificate $cert
```

---

## Step 5: Generate Checksums

```powershell
$hash1 = (Get-FileHash dist\email-summarizer.exe -Algorithm SHA256).Hash
$hash2 = (Get-FileHash email-summarizer-setup.exe -Algorithm SHA256).Hash

"$hash1  email-summarizer.exe" | Out-File SHA256SUMS.txt
"$hash2  email-summarizer-setup.exe" | Out-File SHA256SUMS.txt -Append
```

---

## Step 6: VirusTotal Scan (Recommended)

1. Go to [VirusTotal](https://www.virustotal.com/)
2. Upload both `.exe` files
3. Wait for scan (~2 minutes)
4. Download the report
5. Include in CodeCanyon submission

> **Note**: First-time PyInstaller .exe files often get false positives. This is normal and expected.

---

## Step 7: Package for Distribution

```
email-summarizer-release.zip
├── email-summarizer.exe              (portable, no install needed)
├── email-summarizer-setup.exe        (installer version)
├── credentials.example.json
├── .env.example
├── README.md
├── INSTALL.md
├── SUPPORT.md
├── SHA256SUMS.txt
├── VIRUSTOTAL-REPORT.pdf
└── THIRD-PARTY-LICENSES.txt
```

---

## Troubleshooting

### "Module not found" errors
- Add `--hidden-import=module_name` for each missing module
- Common ones: customtkinter, google.auth, PIL, etc.

### Executable too large
- Use `--onedir` instead of `--onefile` (smaller, faster)
- Remove unused dependencies from `requirements.txt`

### "DLL not found" on user's machine
- Ensure all dependencies are included
- Test on clean Windows VM

### Antivirus false positives
- Sign the executable with a valid certificate
- Include VirusTotal scan report in documentation
- Note that PyInstaller exes may trigger false alarms

---

## Full Batch Script

Save as `build-exe.bat`:

```batch
@echo off
setlocal enabledelayedexpansion

echo Building Email Summarizer Pro Windows Executable...

set PROJECT_DIR=%~dp0

REM Clean
echo [1/4] Cleaning build artifacts...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build portable
echo [2/4] Building portable executable...
pyinstaller ^
  --name "email-summarizer" ^
  --onefile ^
  --windowed ^
  --add-data "credentials.example.json:." ^
  --add-data ".env.example:." ^
  --hidden-import=customtkinter ^
  --hidden-import=google.auth ^
  --hidden-import=google.auth.oauthlib ^
  email_customtkinter_gui.py

REM Generate checksums
echo [3/4] Generating checksums...
for /f "tokens=*" %%A in ('powershell -Command "(Get-FileHash dist\email-summarizer.exe -Algorithm SHA256).Hash"') do set "HASH=%%A"
echo !HASH!  email-summarizer.exe > SHA256SUMS.txt

REM Done
echo [4/4] Build complete!
echo ✓ Output: dist\email-summarizer.exe
echo ✓ Checksum: !HASH!
echo.
pause
```

---

## Next Steps

1. ✓ Create `.exe` files
2. ✓ Test on clean Windows VM
3. ✓ Generate SHA256 checksums
4. ✓ Scan with VirusTotal
5. ✓ Create Windows installer
6. ✓ Package for CodeCanyon upload

See: `RELEASE_GUIDE.md` for next steps.

---

**Last Updated**: December 2025
