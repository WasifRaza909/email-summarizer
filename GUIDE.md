# Email Summarizer Pro - Complete Guide

A professional, lightweight desktop application that fetches emails from Gmail and uses Google's Gemini AI to generate intelligent summaries and draft professional replies.

---

## Table of Contents

1. [Features](#features)
2. [Quick Start](#quick-start)
3. [Installation](#installation)
4. [Getting API Keys & Credentials](#getting-api-keys--credentials)
5. [Configuration](#configuration)
6. [Usage](#usage)
7. [Troubleshooting](#troubleshooting)
8. [File Guide](#file-guide)
9. [Security & Privacy](#security--privacy)
10. [Support](#support)

---

## Features

✨ **Key Features:**
- **Gmail Integration**: Securely connect to your Gmail inbox using OAuth 2.0
- **Smart Email Loading**: Load 1-10 unread emails with just a click
- **AI-Powered Summaries**: Automatic email summarization and draft reply generation using Gemini 2.5 Flash
- **Lazy Summarization**: Only summarize emails you click on - saves Gemini API credits
- **Credential Caching**: Save credentials locally with one-click re-login
- **Modern UI**: Professional Material Design dark theme with smooth animations
- **Cross-Platform**: Works on Windows, macOS, and Linux

---

## Quick Start

### Windows (Fastest Way)
1. Double-click `run_gui.bat` to launch the app
2. Click "🔓 Login" to authenticate with Gmail
3. Select number of emails (1-10) and click "📧 Load Emails"
4. Click any email to see AI-generated summary and draft reply

### Python/Command Line
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python email_customtkinter_gui.py
```

---

## Installation

### Requirements
- Python 3.8 or higher
- pip (Python package installer)
- Internet connection

### Step-by-Step Installation

1. **Extract or Clone the Project**
```bash
cd email-summarizer
```

2. **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

This installs:
- `customtkinter` - Modern UI framework
- `google-auth` - Gmail authentication
- `google-auth-oauthlib` - OAuth 2.0 support
- `google-auth-httplib2` - Google API support
- `google-api-client` - Gmail API client
- `google-generativeai` - Gemini AI integration
- `python-dotenv` - Environment variable management

---

## Getting API Keys & Credentials

### Part 1: Get Your credentials.json File (Gmail OAuth)

This file allows the app to access your Gmail inbox securely.

#### Step 1: Go to Google Cloud Console
- Visit: https://console.cloud.google.com/
- Sign in with your Google account

#### Step 2: Create/Select a Project
- Click the project dropdown at the top
- Click "NEW PROJECT"
- Enter name: `Email Summarizer`
- Click "CREATE"
- Wait for the project to be created, then select it

#### Step 3: Enable Gmail API
- Go to "APIs & Services" → "Library" (left menu)
- Search for `Gmail API`
- Click "Gmail API" from results
- Click the blue "ENABLE" button
- Wait for it to complete

#### Step 4: Create OAuth 2.0 Credentials
- Go to "APIs & Services" → "Credentials" (left menu)
- Click "Create Credentials" (blue button at top)
- Select "OAuth client ID"
- If prompted, configure OAuth consent screen first:
  - Click "CONFIGURE CONSENT SCREEN"
  - Select "External"
  - Click "CREATE"
  - Fill in required fields (App name, User support email)
  - Add your email under "Developer contact"
  - Click "SAVE AND CONTINUE" (skip optional fields)
  - Click "SAVE AND CONTINUE" again
  - Click "BACK TO DASHBOARD"
- Back to "Create Credentials":
  - Application type: Select "Desktop application"
  - Click "CREATE"

#### Step 5: Download credentials.json
- Look for your created credential in the "OAuth 2.0 Client IDs" section
- Click the download icon (⬇️) next to it
- A JSON file will download (usually named `client_secret_*.json`)
- **Rename it to `credentials.json`**
- **Place it in the Email Summarizer folder** (same folder as `email_customtkinter_gui.py`)

**Alternative**: You can also place it at:
- `C:\Users\YourUsername\AppData\Roaming\email-summarizer\credentials.json`

✅ **Done with Gmail setup!**

---

### Part 2: Get Your Gemini API Key

This key allows the app to use Google's Gemini AI for email summarization.

#### Step 1: Go to Google AI Studio
- Visit: https://aistudio.google.com/app/apikey

#### Step 2: Create API Key
- Click the blue "Create API Key" button
- Select "Create API key in new Google Cloud project"
- A new tab will open with your API key displayed
- Copy the entire API key (it looks like: `AIzaSy...`)

#### Step 3: Create `.env` File
- Open Notepad or any text editor
- Create a new file with this content:
```
GEMINI_API_KEY=paste_your_key_here
```
- Replace `paste_your_key_here` with your actual API key (no quotes needed)
- Save the file as `.env` (yes, just `.env` as the filename)
- **Place it in the Email Summarizer folder** (same folder as `email_customtkinter_gui.py`)

**Example `.env` file:**
```
GEMINI_API_KEY=AIzaSyDzJKi_M8nZ5e9fHK_QwXyZ123456789abc
```

✅ **Done with Gemini setup!**

---

## Configuration

All settings are centralized in `config.py`. The app reads credentials from:

### Files Created During Setup
- **`.env`** - Contains your Gemini API key (create manually)
- **`credentials.json`** - Gmail OAuth credentials (download from Google Cloud)
- **`token.pkl`** - Auto-generated auth token (created on first login - don't edit)
- **`.setup_complete`** - Marker file (created automatically)

### Environment Variables
The `.env` file supports these variables:
```
GEMINI_API_KEY=your_gemini_api_key_here
GMAIL_FOLDER=INBOX
MAX_EMAILS=10
ENABLE_CACHE=true
```

### AppData Storage Location
When running, the app also stores files at:
```
C:\Users\YourUsername\AppData\Roaming\email-summarizer\
├── .env
├── credentials.json
├── token.pkl
└── .setup_complete
```

---

## Usage

### First Time Usage

1. **Run the Application**
   - Windows: Double-click `run_gui.bat`
   - Python: Run `python email_customtkinter_gui.py`

2. **Setup Screen (First Launch)**
   - Select your `credentials.json` file (Gmail OAuth)
   - Enter your Gemini API key
   - Click "Save & Continue"
   - You're all set!

3. **Login**
   - Click "🔓 Login"
   - A browser window will open
   - Select your Google account
   - Click "Allow" when prompted for permissions
   - Return to the app (browser will close automatically)

### Daily Usage

1. **Load Emails**
   - Select number of emails (1-10) from dropdown
   - Click "📧 Load Emails"
   - Wait for emails to load (usually 1-2 seconds)

2. **View Email Summary**
   - Click on any email in the list
   - AI-generated summary appears instantly
   - Draft reply is also generated

3. **Logout**
   - Click "🔐 Logout"
   - Confirm when prompted
   - Session token is deleted, but credentials remain saved
   - Click "Login" again to use saved credentials

### Change Credentials Anytime
- Click "🔑 Change Credentials"
- Select new credentials.json file or enter new API key
- Click "Save & Continue"
- You'll be automatically logged out
- New credentials are now active

---

## Troubleshooting

### "Cannot find credentials.json"
**Solution**:
- Ensure `credentials.json` is in the same folder as `email_customtkinter_gui.py`
- Or place it at: `C:\Users\YourUsername\AppData\Roaming\email-summarizer\credentials.json`
- Make sure the filename is exactly `credentials.json` (case-sensitive on some systems)

### Login not working / "403 Permission Denied"
**Solution**:
- Verify Gmail API is **enabled** in Google Cloud Console
- Check that your OAuth credentials are for "Desktop application"
- Delete `token.pkl` from the app folder and try again
- Re-download `credentials.json` from Google Cloud Console

### ".env file not found" or "Gemini API Key missing"
**Solution**:
- Create a `.env` file in the Email Summarizer folder
- Add the line: `GEMINI_API_KEY=your_key_here`
- Save the file and restart the application
- Make sure there's no space around the `=` sign

### "GEMINI_API_KEY not found in environment"
**Solution**:
- Check that `.env` file exists in the app folder
- Open `.env` in notepad and verify the format is: `GEMINI_API_KEY=AIzaSy...`
- No quotes needed around the API key
- Restart the app after saving

### "No emails loading" or "No unread emails found"
**Solution**:
- Ensure your Gmail account has unread emails
- Try marking an email as unread in Gmail and try again
- Check Gmail API quota in [Google Cloud Console](https://console.cloud.google.com/apis/dashboard)
- Try logging out and back in

### "Summary not generating" or "API Error"
**Solution**:
- Verify Gemini API key is correct in `.env`
- Check your API usage quota at [Google AI Studio](https://aistudio.google.com/app/apikey)
- Ensure internet connection is stable
- Try generating summary again (sometimes API needs retry)

### Setup screen keeps appearing on startup
**Solution**:
- Delete the marker file: `C:\Users\{username}\AppData\Roaming\email-summarizer\.setup_complete`
- Restart the app
- The setup screen will appear again for you to confirm your credentials

### Can't log back in after logout
**Solution**:
- You don't need to! Logout only removes your session token
- Your `credentials.json` and API key remain saved
- Click "Login" → it will use saved credentials → browser will open
- Select your Google account in the browser

### "app froze" or "not responding"
**Solution**:
- Close the application completely
- Delete `token.pkl` file from the app folder
- Restart the app
- Try logging in again

---

## File Guide

| File | Purpose | Created By |
|------|---------|-----------|
| `email_customtkinter_gui.py` | Main application (run this!) | Included |
| `config.py` | Centralized configuration | Included |
| `requirements.txt` | Python dependencies | Included |
| `run_gui.bat` | Windows launcher shortcut | Included |
| `.env` | Your Gemini API key | You (create from template) |
| `credentials.json` | Gmail OAuth credentials | You (download from Google) |
| `token.pkl` | Cached session token | App (auto-created on login) |
| `.setup_complete` | Setup completion marker | App (auto-created) |

### Project Structure
```
email-summarizer/
├── email_customtkinter_gui.py    # Main application
├── config.py                     # Configuration
├── requirements.txt              # Dependencies
├── run_gui.bat                   # Windows launcher
├── credentials.json              # Create this (download from Google)
├── .env                          # Create this (add your API key)
├── token.pkl                     # Auto-created on first login
├── .setup_complete               # Auto-created after setup
└── GUIDE.md                      # This file
```

---

## Security & Privacy

### 🔐 What's Protected
- **Local storage only**: All credentials and tokens are stored only on your machine
- **No data collection**: The app doesn't collect or send your personal data anywhere
- **OAuth 2.0**: Uses industry-standard authentication (secure)
- **API keys**: Never exposed or shared with anyone

### 🛡️ Best Practices
1. **Keep `.env` file private**: Don't share your API key
2. **Keep `credentials.json` private**: Don't commit to version control
3. **Use `.gitignore`**: Prevents accidental upload of credentials
4. **Logout before sharing**: Use "🔐 Logout" before sharing your computer
5. **To revoke access**: Visit [Google Account Permissions](https://myaccount.google.com/permissions) and remove "Email Summarizer"

### ❌ What's Never Sent
- Your emails are not sent to any server (except Gmail API)
- Your API key is not shared with anyone
- Your credentials are not uploaded anywhere
- Summaries are sent only to Gemini API (for summarization)

### 🗑️ Uninstall & Cleanup
**Complete removal**:
1. Delete the Email Summarizer folder
2. Delete: `C:\Users\YourUsername\AppData\Roaming\email-summarizer\`

This removes all traces including tokens and cached credentials.

---

## Support

### Quick Troubleshooting Checklist
- [ ] `credentials.json` is in the app folder
- [ ] `.env` file has your Gemini API key
- [ ] Gmail API is enabled in Google Cloud Console
- [ ] You have unread emails in Gmail
- [ ] Internet connection is stable

### If Problem Persists
Provide the following information:
1. Your Windows/Python version
2. The exact error message (take a screenshot)
3. Steps you took to reproduce the issue
4. Whether you've tried the troubleshooting steps above

### Getting Help
1. Check the [Troubleshooting](#troubleshooting) section above first
2. Verify your `credentials.json` and `.env` files are correct
3. Ensure Python 3.8+ is installed (check: `python --version`)
4. Check your internet connection

### Security Notes
- Never share your `credentials.json` or `.env` file
- Never share your API keys
- If you accidentally share credentials, regenerate them immediately
- For Gmail: Visit [Google Account Permissions](https://myaccount.google.com/permissions)
- For Gemini: Visit [Google AI Studio](https://aistudio.google.com/app/apikey) and regenerate key

---

## Credentials Setup Behavior

### First App Launch
```
App Starts
  ↓
Check if credentials exist?
  → YES: Go to Login
  → NO: Show Setup Screen
  ↓
[Setup Screen]
  • Select credentials.json
  • Enter Gemini API key
  • Click Save & Continue
  ↓
Credentials saved → Go to Login
```

### Login Flow
```
Click "🔓 Login"
  ↓
Check for credentials.json
  ↓
Browser opens for Google login
  ↓
User completes login? → Save session token → Ready to load emails
User closes browser? → Show warning "Login Cancelled" → Try again
```

### Logout Flow
```
Click "🔐 Logout"
  ↓
Confirm: "Logout and delete cached session?"
  ↓
If YES:
  • Delete: token.pkl (session only)
  • Keep: credentials.json (stays safe)
  • Keep: .env file with API key
  ↓
Back to login screen
```

### Change Credentials Anytime
```
Click "🔑 Change Credentials"
  ↓
[Setup Screen Opens - "Update Your Credentials" mode]
  ↓
Enter new API key or select new credentials file
  ↓
Click Save & Continue
  ↓
Auto-logout (token.pkl deleted)
  ↓
Back to login screen with new credentials active
```

---

## Architecture Overview

### Core Components

**Credential Management**
- OAuth 2.0 authentication with Google
- Local pickle-based token caching (`token.pkl`)
- One-click logout and credential deletion

**Email Processing**
- Secure Gmail API integration
- HTML tag stripping and text extraction
- Multi-part email handling (plain text & HTML)

**AI Integration**
- Gemini 2.5 Flash API for summarization
- Lazy evaluation - summaries generated only on demand
- Configurable generation parameters

**UI Design**
- CustomTkinter framework for modern widgets
- Material Design 3 color palette
- Responsive dual-panel layout
- Real-time progress tracking

---

## API Optimization Tips

1. **Use lazy summarization**: Only summarize emails you need (saves API credits)
2. **Load fewer emails**: Start with 3-5, then load more if needed
3. **Batch processing**: Load multiple emails, then summarize together
4. **Monitor quota**: Check usage in [Google AI Studio](https://aistudio.google.com/app/apikey)
5. **Cache results**: Summaries are cached locally to avoid re-requesting

---

## Frequently Asked Questions (FAQ)

**Q: Is my password stored anywhere?**
A: No. The app uses OAuth 2.0, so you log in through Google's secure login page. Your password is never stored locally.

**Q: Can you access my emails?**
A: Only you can. The app stores authentication tokens locally, and only you have access to them. Emails are read through the Gmail API and never stored.

**Q: What if I want to stop using the app?**
A: Simply uninstall and delete the AppData folder at `C:\Users\YourUsername\AppData\Roaming\email-summarizer\`. To revoke access, visit [Google Account Permissions](https://myaccount.google.com/permissions).

**Q: Can I use this on multiple computers?**
A: Yes, but you'll need to set up credentials on each computer separately. Credentials are stored locally, not synced.

**Q: How much does this cost?**
A: The app is free. You'll need:
- Free Google Cloud account (Gmail API is free with usage limits)
- Free Gemini API (free tier with generous limits, paid tiers available)

**Q: What if I run out of API credits?**
A: For Gemini API, you can set a budget limit in [Google AI Studio](https://aistudio.google.com/app/apikey). Gmail API has rate limits but no cost.

**Q: Can I share my credentials with someone else?**
A: Not recommended. Each person should set up their own `credentials.json` and API key for security and privacy.

---

## Contact & Updates

**Last Updated**: December 2025  
**Version**: 1.0.0  
**License**: See LICENSE.txt

For bug reports or feature requests, please provide:
- Windows/Python version
- Error message (screenshot if possible)
- Steps to reproduce the issue

---

**Happy email summarizing! 🎉**
