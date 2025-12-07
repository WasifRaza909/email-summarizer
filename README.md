# Email Summarizer Pro
### AI-Powered Gmail Email Summary & Reply Generator

A lightweight, professional desktop application that connects to your Gmail inbox and uses Google's advanced Gemini AI to automatically generate intelligent email summaries and draft professional replies.

---

## 📋 Table of Contents

1. [Features](#features)
2. [Quick Start](#quick-start)
3. [System Requirements](#system-requirements)
4. [Installation](#installation)
5. [Getting API Keys & Credentials](#getting-api-keys--credentials)
   - [Step 1: Create a Google Cloud Project](#step-1-create-a-google-cloud-project)
   - [Step 2: Enable Required APIs](#step-2-enable-required-apis)
   - [Step 3: Create OAuth 2.0 Credentials](#step-3-create-oauth-20-credentials)
   - [Step 4: Get Gemini API Key](#step-4-get-gemini-api-key)
6. [Configuration](#configuration)
7. [Usage Guide](#usage-guide)
8. [Troubleshooting](#troubleshooting)
9. [Security & Privacy](#security--privacy)
10. [File Structure](#file-structure)
11. [Support](#support)

---

## ✨ Features

- **✅ Gmail OAuth 2.0 Integration** - Secure, seamless login without storing passwords
- **✅ Smart Email Loading** - Fetch 1-10 unread emails with one click
- **✅ AI-Powered Summaries** - Instant email summarization using Gemini 2.5 Flash
- **✅ Draft Reply Generation** - Get AI-written professional draft responses
- **✅ Lazy Summarization** - Only summarize the emails you open (saves API credits)
- **✅ Credential Caching** - One-click re-login with cached credentials
- **✅ Modern Material Design UI** - Professional dark theme with smooth animations
- **✅ Cross-Platform** - Works on Windows, macOS, and Linux
- **✅ Cost-Optimized** - Minimal API usage for maximum efficiency
- **✅ 100% Privacy** - No server-side storage, all data stays on your computer

---

## 🚀 Quick Start

### Windows (Fastest Way)
```bash
# Simply double-click this file:
run_gui.bat
```

### Python/Command Line
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python email_customtkinter_gui.py
```

### First Run Workflow
1. Launch the application
2. **Setup Screen** appears automatically:
   - Paste your **Gemini API Key**
   - Upload your **credentials.json** file
   - Click "✓ Save & Continue"
3. Click **"🔓 Login"** to authenticate with Gmail
4. Select number of emails (1-10) and click **"📧 Load Emails"**
5. Click any email to see AI-generated summary and draft reply

---

## 💻 System Requirements

- **OS**: Windows 7+, macOS 10.12+, or Linux
- **Python**: 3.8 or higher (if running from source)
- **RAM**: 2GB minimum
- **Internet**: Required for Gmail & Gemini API access
- **Active Gmail Account**: For email access
- **Google Gemini API Key**: Free tier available at https://aistudio.google.com/app/apikey

---

## 📦 Installation

### Option 1: Windows Batch File (Recommended)
```bash
# Run the setup batch file to install dependencies and set up config
setup.bat

# Then run the app
run_gui.bat
```

### Option 2: Manual Installation
```bash
# Clone or download the repository
cd email-summarizer

# Install Python dependencies
pip install -r requirements.txt

# Run the application
python email_customtkinter_gui.py
```

### Option 3: Docker (Optional)
```bash
docker build -t email-summarizer .
docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix email-summarizer
```

---

## 🔑 Getting API Keys & Credentials

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the **Project Selector** (top-left dropdown)
3. Click **"NEW PROJECT"**
4. Enter a project name: `Email Summarizer` (or any name)
5. Click **"CREATE"**
6. Wait for the project to be created (this may take a few moments)

### Step 2: Enable Required APIs

#### Enable Gmail API:
1. In the Cloud Console, search for **"Gmail API"**
2. Click on **"Gmail API"** from the results
3. Click **"ENABLE"**
4. Wait for it to be enabled

#### Enable Google Gemini/Generative AI API:
1. Search for **"Generative Language API"** (or "Gemini API")
2. Click on it from the results
3. Click **"ENABLE"**

### Step 3: Create OAuth 2.0 Credentials

1. In the Cloud Console sidebar, go to **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** (top button)
3. Select **"OAuth client ID"**
4. If prompted, configure the consent screen first:
   - Click **"CONFIGURE CONSENT SCREEN"**
   - Select **"External"** (for personal use)
   - Click **"CREATE"**
   - Fill in the details:
     - **App name**: `Email Summarizer`
     - **User support email**: (your email)
     - **Developer contact**: (your email)
   - Click **"SAVE AND CONTINUE"**
   - You can skip the scopes (just click "SAVE AND CONTINUE")
   - Click **"SAVE AND CONTINUE"** on test users
   - Click **"BACK TO DASHBOARD"**

5. Now create OAuth credentials:
   - Go to **"Credentials"** again
   - Click **"+ CREATE CREDENTIALS"**
   - Select **"OAuth client ID"**
   - Choose **"Desktop application"**
   - Click **"CREATE"**
   - You'll see a popup with your credentials - click **"DOWNLOAD JSON"**
   - Save this file as **`credentials.json`** in the app folder

### Step 4: Get Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click **"Get API Key"** (or **"Create API Key"**)
3. Select **"Create API key in new project"**
4. Copy the API key (looks like: `AIzaSy...`)
5. Keep it safe - you'll enter it in the app's setup screen

---

## ⚙️ Configuration

### First Run Setup (AUTOMATIC)
When you launch the app for the first time, the **Setup Screen** appears automatically:

1. **Enter Gemini API Key**
   - Go to https://aistudio.google.com/app/apikey
   - Copy your API key (starts with `AIzaSy...`)
   - Paste it in the setup window
   - Click "Validate" - the app will check it automatically

2. **Select credentials.json**
   - Click "📁 Select credentials.json"
   - Navigate to your downloaded OAuth JSON file
   - Select it - the path will be saved

3. **Click "✓ Save & Continue"**
   - The app is now configured and ready to use!
   - Your settings are saved automatically

### Important: Do NOT Edit config.py
- ❌ DO NOT manually edit `config.py`
- ✅ Use the app's Setup Screen instead (Settings → Change Credentials)
- The app handles all configuration automatically

---

## 📖 Usage Guide

### Load Emails
1. Click **"🔓 Login"** to authenticate with Gmail (first time only)
2. Select the number of emails to load: **2, 3, 5, 10, or 20**
3. Click **"📧 Load Emails"**
4. Wait for emails to appear in the list

### View Summary & Draft Reply
1. **Click any email** in the list
2. The app automatically generates:
   - **Summary**: Key points and main ideas
   - **Draft Reply**: A professional response ready to send
3. Read at your own pace - no rush!

### Logout
1. Click **"🔓 Login"** button while logged in
2. Confirm logout
3. Your cached credentials are deleted for security

### Change Credentials
1. Click **"⚙️ Settings"** (gear icon in top-right)
2. Click **"Change Credentials"**
3. Follow the setup wizard again
4. New credentials will be saved automatically

---

## 🔧 Troubleshooting

### "Error: credentials.json not found"
- **Solution**: Upload your credentials.json file in the Setup Screen
- Get it from: Google Cloud Console → Credentials → Download JSON

### "Invalid API Key"
- **Solution**: Check your Gemini API key at https://aistudio.google.com/app/apikey
- Make sure you copied the entire key (starts with `AIzaSy...`)
- Ensure the key is enabled for the Generative Language API

### "No emails appear after clicking Load"
- **Solution**: 
  - Check if you have unread emails in Gmail
  - Try changing the email count (2, 3, 5, etc.)
  - Make sure Gmail API is enabled in Cloud Console

### "Gmail login keeps failing"
- **Solution**:
  - Delete `gmail_token.pkl` file from the app directory
  - Restart the app
  - Try logging in again
  - Make sure "Less secure app access" is enabled (if using older Google accounts)

### "Summarization is very slow"
- **Solution**:
  - Gemini API has rate limits on free tier
  - Wait a few minutes between summaries
  - Consider upgrading your API plan

### "App crashes on startup"
- **Solution**:
  - Reinstall Python dependencies: `pip install --upgrade -r requirements.txt`
  - Make sure Python 3.8+ is installed
  - Check that `config.py` exists in the app folder

---

## 🔒 Security & Privacy

### We Protect Your Data
✅ **NO Server Storage** - Nothing is sent to our servers
✅ **Local Processing** - All credentials and data stay on your computer
✅ **Secure OAuth** - We use industry-standard OAuth 2.0 (not passwords)
✅ **Encrypted Cache** - Credentials are cached locally in Python pickle format
✅ **No Tracking** - We don't track your usage or emails
✅ **No Data Collection** - We don't collect any personal information

### What Gets Sent?
- **Only to Gmail**: Your Gmail credentials (via secure OAuth)
- **Only to Gemini API**: Email body text (for summarization)
- **Nothing Else**: No server uploads, no analytics, no ads

### Data You Control
- Delete credentials anytime by clicking **Logout**
- Delete `gmail_token.pkl` and `config.py` to completely reset
- All data deletion is permanent and immediate

### Security Best Practices
1. ✅ Never share your credentials.json file
2. ✅ Never share your API keys with anyone
3. ✅ Keep your Python dependencies updated: `pip install --upgrade -r requirements.txt`
4. ✅ Logout when done using the app
5. ✅ Delete the app folder completely if you no longer need it

---

## 📁 File Structure

```
email-summarizer/
├── email_customtkinter_gui.py    # Main application
├── config.py                      # Configuration (auto-generated)
├── requirements.txt               # Python dependencies
├── README.md                      # This file
├── LICENSE.txt                    # License information
├── run_gui.bat                    # Windows launcher
├── setup.bat                      # Windows setup
├── credentials.example.json       # Example OAuth structure
├── .env.example                   # Example environment variables
└── gmail_token.pkl                # Cached Gmail credentials (created on first login)
```

### Generated Files (Created on First Run)
- `config.py` - Your API keys and settings
- `gmail_token.pkl` - Cached Gmail token (delete to logout)

---

### Common Issues

**Q: Do I need to pay for the APIs?**
A: No! Both Gmail API and Gemini API have free tiers with generous limits.

**Q: Can I use this with multiple email accounts?**
A: Currently, one account at a time. Logout and login with a different account to switch.

**Q: Is my email data safe?**
A: Yes! We never store emails on servers. Only the text needed for summarization is sent to Gemini API.

**Q: Can I use this offline?**
A: No, you need internet for Gmail and Gemini API access.

**Q: Will this work on Mac/Linux?**
A: Yes! It's cross-platform. Just install Python and run `python email_customtkinter_gui.py`

---

## 📄 License

This project is provided as-is. See LICENSE.txt for full details.

---

## 🙏 Credits

Built with:
- **CustomTkinter** - Modern GUI framework
- **Google APIs** - Gmail and Gemini integration
- **Material Design** - Professional UI/UX

---

**Made with ❤️ for busy professionals. Process emails smarter, not harder.**

Last Updated: December 2025
