# Email Summarizer Pro - Setup Guide

## ⚡ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get Google API Credentials
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create a new project → Enable Gmail API → Create OAuth 2.0 Desktop credentials
- Download as `credentials.json` and place it here

### 3. Get Gemini API Key
- Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
- Create API key → Copy the key

### 4. Create Configuration
- Copy `.env.example` to `.env`
- Add your Gemini API key:
```
GEMINI_API_KEY=your_key_here
```

### 5. Run the App
```bash
python email_customtkinter_gui.py
```
Or on Windows, double-click: `run_gui.bat`

## 📁 Configuration

All settings are centralized in `config.py`. The app reads credentials from:
- **`.env`** - Your API keys and settings
- **`credentials.json`** - Google OAuth 2.0 credentials
- **`token.pkl`** - Auto-generated auth token (created on first login)

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| "credentials.json not found" | Download it from Google Cloud Console |
| "GEMINI_API_KEY not found" | Add it to `.env` file |
| "Login failed" | Delete `token.pkl` and try again |
| "No emails loading" | Ensure you have unread emails in Gmail |
| "Summary not generating" | Check your Gemini API quota |

## 📝 File Guide

- `email_customtkinter_gui.py` - Main application (run this!)
- `config.py` - Centralized configuration
- `.env` - Your API keys (create from `.env.example`)
- `credentials.json` - Gmail OAuth credentials (download from Google)
- `run_gui.bat` - Windows launcher shortcut

---
Need help? Read `README.md` for detailed documentation.
