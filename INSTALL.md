# Email Summarizer Pro - Installation & Setup Guide

## Quick Start (Windows)

### Option 1: Using the Installer (Recommended)
1. Download and run `email-summarizer-setup.exe`
2. Follow the on-screen installer
3. At the end, the setup wizard will help you configure credentials
4. Launch from Start Menu

### Option 2: Portable Version
1. Extract `email-summarizer-portable.zip`
2. Run `email-summarizer.exe`
3. Follow "First Time Setup" below

### Option 3: From Source (Python)
1. Ensure Python 3.8+ is installed
2. Extract the source files
3. Open Command Prompt in the folder
4. Run: `pip install -r requirements.txt`
5. Follow "First Time Setup" below

---

## First Time Setup

### Step 1: Get Google Gmail API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (name: "Email Summarizer" or similar)
3. Enable the Gmail API:
   - Go to "APIs & Services" → "Library"
   - Search for "Gmail API"
   - Click "Enable"
4. Create OAuth 2.0 Desktop credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Desktop application"
   - Click "Create"
5. Download the JSON file as `credentials.json`
6. **Place it in the same folder as the application** (or at `C:\Users\YourUsername\AppData\Roaming\email-summarizer\credentials.json`)

### Step 2: Get Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the API key
4. Create a `.env` file in the same folder as the application, add:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
   Replace `your_api_key_here` with the key you copied.

### Step 3: First Launch

1. Run the application
2. Click "🔓 Login"
3. Authorize with your Gmail account in the browser popup
4. You're ready to go!

---

## Troubleshooting

### "Login failed" / "Credentials not found"
- **Solution**: Ensure `credentials.json` is in the correct folder:
  - **Windows Portable/Installer**: Same folder as the `.exe` file
  - **Python Version**: Same folder as `email_customtkinter_gui.py`
  - **Alternative Path**: `C:\Users\YourUsername\AppData\Roaming\email-summarizer\credentials.json`

### "API Error 403" or "Permission Denied"
- **Solution**: 
  - Verify Gmail API is **enabled** in Google Cloud Console
  - Check that your OAuth credentials are for "Desktop application"
  - Regenerate credentials if needed

### ".env file not found" or "Gemini API Key missing"
- **Solution**:
  - Create a `.env` file in the application folder
  - Add the line: `GEMINI_API_KEY=your_key`
  - Save and restart the application

### "No emails loading"
- **Solution**:
  - Ensure your Gmail account has unread emails
  - Try logging out and back in
  - Check Gmail API quota in Google Cloud Console

### "Summary not generating"
- **Solution**:
  - Verify Gemini API key is correct in `.env`
  - Check your API usage quota at [Google AI Studio](https://aistudio.google.com/app/apikey)
  - Ensure internet connection is stable

---

## File Locations

| File | Location |
|------|----------|
| `credentials.json` | Application folder or `%APPDATA%\email-summarizer\` |
| `.env` | Application folder |
| Tokens (cached) | `%APPDATA%\email-summarizer\token.pkl` |

---

## Security Notes

- **Credentials are stored locally** on your machine and not sent anywhere except to Google
- **Tokens are cached** in `%APPDATA%\email-summarizer\` for convenience
- **To logout**, click "🔐 Logout" to clear cached credentials
- **To revoke access**, visit [Google Account Permissions](https://myaccount.google.com/permissions) and remove access

---

## Support

For issues:
1. Check the troubleshooting section above
2. Verify credentials are correctly configured
3. Ensure Python 3.8+ is installed (if running from source)
4. Check internet connection

---

## Uninstalling

**Windows Installer**: Go to Settings → Apps → Email Summarizer Pro → Uninstall

**Portable**: Delete the extracted folder

**Python**: Delete the project folder

To fully remove:
- Delete `C:\Users\YourUsername\AppData\Roaming\email-summarizer\` (removes tokens & cached data)

---

**Version**: 1.0.0  
**Last Updated**: December 2025
