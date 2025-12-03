# Email Summarizer Pro

A professional, lightweight desktop application that fetches emails from Gmail and uses Google's Gemini AI to generate intelligent summaries and draft professional replies.

## Features

✨ **Key Features:**
- **Gmail Integration**: Securely connect to your Gmail inbox using OAuth 2.0
- **Smart Email Loading**: Load 1-10 unread emails with just a click
- **AI-Powered Summaries**: Automatic email summarization and draft reply generation using Gemini 2.5 Flash
- **Lazy Summarization**: Only summarize emails you click on - saves Gemini API credits
- **Credential Caching**: Save credentials locally with one-click re-login
- **Modern UI**: Professional Material Design dark theme with smooth animations
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Installation

### Requirements
- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. **Clone or extract the project**
```bash
cd email-summarizer
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up Google API credentials**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Gmail API
   - Create OAuth 2.0 Desktop credentials
   - Download the credentials as `credentials.json`
   - Place `credentials.json` in the project folder

4. **Set up Gemini API**
   - Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create a new API key
   - Create a `.env` file in the project folder:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. **Run the application**
```bash
python email_customtkinter_gui.py
```

## Usage

1. **Login**: Click "🔓 Login" to authenticate with Gmail
2. **Select Email Count**: Choose how many emails to load (1-10)
3. **Load Emails**: Click "📧 Load Emails" to fetch unread emails
4. **View Summary**: Click any email to generate an AI summary and draft reply
5. **Logout**: Click "🔐 Logout" to clear cached credentials

## Project Structure

```
email-summarizer/
├── email_customtkinter_gui.py    # Main application (production-ready)
├── Email Summarizer.ipynb         # Development/testing notebook
├── credentials.json               # Google API credentials (create this)
├── .env                          # Environment variables (create this)
├── token.pkl                     # Cached credentials (auto-generated)
└── README.md                     # This file
```

## Architecture

### Core Components

**Credential Management**
- OAuth 2.0 authentication with Google
- Local pickle-based token caching
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

## API Optimization

This app is designed to minimize API costs:
- **Email Loading**: Fetches metadata only (fast, no summarization)
- **Lazy Summarization**: Only calls Gemini API when you click an email
- **Result Caching**: Summaries cached in memory during session
- **Configurable Load Count**: Choose 1-10 emails instead of loading all

## Troubleshooting

**"Login failed" error**
- Ensure `credentials.json` is in the project folder
- Verify Google API is enabled in Cloud Console
- Check internet connection

**"API Error 403"**
- Verify Gemini API key in `.env` file
- Check API quota in Google Cloud Console
- Ensure API is enabled for your project

**No emails loading**
- Verify Gmail account has unread emails
- Check Gmail API permissions
- Try logging out and in again

**Summary not generating**
- Verify `.env` file has correct Gemini API key
- Check internet connection
- Verify API quota hasn't been exceeded

## License

This application is provided for personal and commercial use.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all credentials are correctly configured
3. Ensure Python 3.8+ is installed

## Changelog

**v1.0.0**
- Initial release
- Gmail integration with OAuth
- Gemini AI summarization
- Email count selector (1-10)
- Lazy summarization for credit optimization
- Professional Material Design UI
