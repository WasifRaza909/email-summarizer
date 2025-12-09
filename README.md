# AI Email Summarizer

**AI-Powered Gmail Summarization Tool**

Streamline your email workflow with intelligent summarization powered by Google's Gemini AI. Read less, understand more.

---

## 🔒 Security First

This application is **100% secure** for your credentials:
- ✅ **No server-side storage** - Your data never leaves your machine
- ✅ **No passwords stored** - Uses secure OAuth 2.0 authentication
- ✅ **Credentials cached locally** - All data stays on your computer
- ✅ **Transparent code** - Review the source code anytime for peace of mind

---

## ✨ Features

- **🔐 Secure Gmail Integration** - OAuth 2.0 authentication with no password storage
- **📧 Batch Email Loading** - Load up to 20 unread emails at once
- **✨ Smart AI Summaries** - Instant email summarization using Google Gemini
- **📝 Draft Replies** - Auto-generate professional email responses
- **⚡ View All Summaries** - See all email summaries at once for quick overview
- **💾 Credential Caching** - Seamless re-authentication with cached credentials
- **🔄 Change Credentials** - Switch API keys or Gmail accounts anytime
- **🖥️ Clean Interface** - Modern, intuitive desktop application
- **💯 100% Local & Private** - All processing happens on your machine

---

## 📦 Installation

### Windows (Easiest)
1. Download and extract the application
2. Double-click `Launch Ai Email Summarizer.bat`
3. The app will launch automatically

### Manual Installation (Windows/Mac/Linux)
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

---

## 🔑 Getting API Keys & Credentials

You'll need two free credentials from Google. Both are quick to set up!

### Step 1: Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown at the top-left
3. Click **"NEW PROJECT"**
4. Name it: `AI Email Summarizer`
5. Click **"CREATE"** and wait for completion

### Step 2: Enable Gmail API
1. Search for **"Gmail API"** in the Cloud Console
2. Click on it and press **"ENABLE"**
3. Wait for activation

### Step 3: Create OAuth 2.0 Credentials
1. Go to **"Credentials"** in the left sidebar
2. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
3. If prompted, configure the OAuth consent screen:
   - Select **"External"**
   - App name: `AI Email Summarizer`
   - Add your email
   - Click **"SAVE AND CONTINUE"** through all steps
4. Go back to **Credentials** and create a new **OAuth client ID**
5. Choose **"Desktop application"** and click **"CREATE"**
6. Click **"DOWNLOAD JSON"**
7. Save the file as `credentials.json` in your app folder

### Step 4: Get Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click **"Get API Key"**
3. Copy the API key (starts with `AIzaSy...`)
4. Keep it safe - you'll paste it in the app

---

## 🚀 How to Use

### First Launch
1. Open the application
2. A setup screen appears
3. Paste your **Gemini API Key**
4. Click to select your **credentials.json** file
5. Click **"Save & Continue"**

### Login to Gmail
1. Click the **"Login"** button
2. Your browser opens - sign in with your Google account
3. Grant the app permission to access your Gmail
4. You're authenticated! (Your credentials are cached for future use)

### Load Emails
1. Select how many emails to load (**2 to 20**)
2. Click **"Load Emails"**
3. Your emails appear in the list

### View Email Summary & Draft Reply
1. Click on any email in the list
2. The app instantly shows:
   - **Summary** - Key points of the email
   - **Draft Reply** - A professional response ready to send
3. Read and review at your pace

### View All Summaries at Once
1. Click the **"View All Summaries"** button
2. See all loaded email summaries on one page
3. Quickly understand your entire inbox at a glance

### Change Your Credentials
2. Click **"Change Credentials"**
3. Update your API key or Gmail account
4. Your new credentials are saved automatically

---

## 📋 Features in Detail

### Security & Privacy
- **Zero server storage** - Nothing uploaded to any server
- **Local credentials** - API keys and credentials stored only on your machine
- **Standard OAuth 2.0** - No passwords transmitted or stored
- **Private processing** - All data stays on your computer

### Email Processing
- **Load up to 20 emails** - Process a full batch at once
- **AI summarization** - Google Gemini generates intelligent summaries
- **Draft replies** - Professional responses ready to send
- **View all at once** - See all summaries on a single page

### Credential Management
- **Cached authentication** - Quick re-login without re-entering credentials
- **Change anytime** - Switch API keys or Gmail accounts with one click
- **Secure deletion** - Delete cached credentials anytime from the app

---

## ❓ FAQ

**Q: Is this app safe for my Gmail credentials?**
- A: Yes! We use industry-standard OAuth 2.0. Your password is never stored or transmitted. Check the code yourself!

**Q: Will this cost money?**
- A: No! Both Gmail API and Gemini API offer free tiers with generous limits.

**Q: Where are my credentials stored?**
- A: Only on your local machine. Check `config.py` and `gmail_token.pkl` in the app folder.

**Q: Can I use this with multiple Gmail accounts?**
- A: Yes! Click Settings → Change Credentials to switch accounts.

**Q: What if I want to remove all my data?**
- A: Simply delete the app folder. All your cached credentials are removed instantly.

**Q: How much email can I process at once?**
- A: Load and summarize up to 20 emails in a single batch.

**Q: Is my email data saved anywhere?**
- A: No! Email text is sent only to Gemini API for summarization. We never store it on any server.

**Q: Can I review the code?**
- A: Absolutely! The source code is available for your inspection and transparency.

---

**Process emails smarter, not harder. 🚀**
