# AI Email Summarizer Pro

**Professional AI-Powered Gmail Summarization & Management Tool**

Transform your email workflow with intelligent AI summarization powered by Google's Gemini AI. Process emails faster, understand context instantly, and never miss important messages. Perfect for professionals, businesses, and anyone managing high email volumes.

---

## 🎯 Overview

AI Email Summarizer Pro is a fully optimized, production-ready desktop application that connects to your Gmail account and uses Google's advanced Gemini AI to generate concise summaries and draft intelligent replies. Built with modern technology and a beautiful dark-themed interface, it streamlines email management while keeping your data 100% secure and private.

**Compatible with:** Windows, macOS, Linux

---

## 🔒 Security & Privacy First

Your data security is our top priority:

- ✅ **100% Local Processing** - All data stays on your machine, never uploaded to any server
- ✅ **OAuth 2.0 Authentication** - Industry-standard secure authentication, no password storage
- ✅ **Zero Data Collection** - We don't collect, store, or transmit your personal information
- ✅ **Encrypted Token Caching** - Credentials cached securely on your local machine only
- ✅ **Open Source Transparency** - Full source code available for review and audit
- ✅ **No Third-Party Tracking** - No analytics, no telemetry, complete privacy

---

## ✨ Key Features

### 🚀 **Optimized Performance**
- **Professional Splash Screen** - Elegant loading experience with progress indicators
- **Fast Startup** - Optimized module loading for quick application launch
- **Smooth UI** - Modern CustomTkinter-based interface with responsive design
- **Efficient Threading** - Background processing prevents UI freezing

### 📧 **Email Management**
- **Batch Email Loading** - Load 2-20 unread emails at once
- **Smart Filtering** - Focus on unread messages that need attention
- **Email Preview** - See sender, subject, and metadata at a glance
- **Click to Expand** - Select any email to view full details

### 🤖 **AI-Powered Intelligence**
- **Instant Summaries** - Google Gemini AI generates concise email summaries
- **Draft Replies** - Auto-generate professional, context-aware responses
- **Markdown Rendering** - Beautiful formatted summaries with proper styling
- **Bulk Summary View** - View all email summaries on one page
- **Smart Formatting** - Bold highlights, bullet points, and structured output

### 🎨 **Modern User Interface**
- **Dark Theme** - Eye-friendly professional design
- **Intuitive Layout** - Clean, organized interface for maximum productivity
- **Interactive Elements** - Clickable email cards with hover effects
- **Responsive Design** - Adapts to different screen sizes
- **Custom Icons** - Professional application icon

### 🔐 **Authentication & Credentials**
- **OAuth 2.0 Flow** - Secure Google account authentication
- **Credential Manager** - Built-in setup wizard for API keys and OAuth
- **Token Caching** - Stay logged in across sessions
- **Easy Re-authentication** - Quick login with cached credentials
- **Change Credentials** - Switch API keys or Gmail accounts anytime
- **Credential Validation** - Real-time verification of API keys and OAuth files

### 🛠️ **Advanced Features**
- **Clickable Gmail Links** - Direct links to emails in Gmail web interface
- **HTML Email Support** - Properly parse and display HTML emails
- **Error Handling** - Graceful error messages and recovery
- **Retry Logic** - Automatic retry for temporary failures
- **Thread Safety** - Concurrent processing with thread pool executors

### 💼 **Professional Quality**
- **Production Ready** - Fully tested and optimized codebase
- **Executable Build** - Standalone .exe file (no Python required)
- **Portable** - Run from anywhere, no installation needed
- **Resource Efficient** - Minimal CPU and memory usage
- **Cross-Platform** - Works on Windows, macOS, and Linux

---

## 📦 Multiple Installation Options

We provide **three flexible ways** to run the application - choose what works best for you:

### **Option 1: Standalone Executable (Recommended for Windows)**
**Perfect for end users who want instant access without any setup.**

1. Navigate to the `dist` folder
2. Double-click **`AI Email Summarizer.exe`**
3. The app launches immediately - no Python or dependencies needed!

**Advantages:**
- ✅ No Python installation required
- ✅ No dependency management
- ✅ One-click launch
- ✅ Portable - run from USB drive or any folder
- ✅ Optimized and pre-compiled

---

### **Option 2: Batch File Launcher (Windows)**
**Convenient launcher that handles Python environment automatically.**

1. Double-click **`Launch Ai Email Summarizer.bat`**
2. The batch file activates the Python environment and runs the app
3. Ideal for development or if you prefer running the Python version

**Advantages:**
- ✅ Automatic environment activation
- ✅ Runs latest code changes during development
- ✅ Easy debugging
- ✅ One-click launch with Python source

---

### **Option 3: Direct Python Execution (All Platforms)**
**For developers or advanced users who want full control.**

#### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

#### Installation Steps

1. **Clone or Download**
   ```bash
   cd "AI Email Summarizer"
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   python app.py
   ```

**Advantages:**
- ✅ Cross-platform (Windows, macOS, Linux)
- ✅ Full source code access
- ✅ Customizable and extensible
- ✅ Developer-friendly

---

## 🔑 API Setup Guide

To use the application, you need two free Google credentials. Follow these steps:

### **Step 1: Create Google Cloud Project**

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Click the **project dropdown** at the top-left
3. Click **"NEW PROJECT"**
4. Enter project name: `AI Email Summarizer Pro`
5. Click **"CREATE"** and wait for project creation

### **Step 2: Enable Gmail API**

1. In your new project, search for **"Gmail API"** in the search bar
2. Click on **Gmail API** from results
3. Click **"ENABLE"** button
4. Wait for activation (takes a few seconds)

### **Step 3: Create OAuth 2.0 Credentials**

1. Go to **APIs & Services** → **Credentials** (left sidebar)
2. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
3. If prompted to configure OAuth consent screen:
   - Select **"External"** user type
   - Fill in required fields:
     - App name: `AI Email Summarizer Pro`
     - User support email: (your email)
     - Developer contact: (your email)
   - Click **"SAVE AND CONTINUE"** through all steps
   - Add yourself as a test user in "Test users" section
4. Return to **Credentials** tab
5. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
6. Select **"Desktop application"**
7. Name it: `AI Email Summarizer Desktop`
8. Click **"CREATE"**
9. Click **"DOWNLOAD JSON"** in the confirmation dialog
10. Save the downloaded file as **`credentials.json`** in the app folder

### **Step 4: Get Gemini API Key**

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Get API Key"** or **"Create API Key"**
4. Select your Cloud project (or create a new one)
5. Copy the generated API key (format: `AIzaSy...`)
6. Store it securely - you'll enter it in the app

---

## 🚀 Getting Started

### **First Launch Setup**

1. **Launch the Application** (using any of the three methods above)

2. **Initial Configuration Screen**
   - The app opens with a setup wizard
   - Enter your **Gemini API Key** in the text field
   - Click **"Browse"** to select your **credentials.json** file
   - Click **"Save & Continue"**

3. **API Validation**
   - The app automatically validates your Gemini API key
   - Shows progress with visual feedback
   - Confirms successful validation

4. **You're Ready!**
   - Configuration is saved to `config.py`
   - You'll see the main application screen

---

### **Gmail Authentication**

1. Click the **"Login"** button in the main window
2. Your default browser opens automatically
3. Sign in with your Google account
4. Review and accept the permission request:
   - Read Gmail messages
   - View email metadata
5. You'll see "Authentication successful" in the browser
6. Return to the application - you're now logged in!
7. Your authentication token is cached in `gmail_token.pkl`

---

### **Loading Emails**

1. Use the **dropdown menu** to select how many emails to load (2-20)
2. Click **"Load Emails"** button
3. The app fetches your latest unread emails
4. Email cards appear in a scrollable list showing:
   - Sender name/email
   - Subject line
   - Preview snippet

---

### **Viewing Summaries & Replies**

**Individual Email View:**
1. Click on any email card in the list
2. The right panel displays:
   - **Email Summary** - AI-generated concise summary with key points
   - **Suggested Reply** - Professional draft response
3. Summaries include:
   - Bold highlights for important information
   - Bullet points for clarity
   - Formatted text for readability
   - Direct Gmail link to the original email

**Bulk Summary View:**
1. Click **"View All Summaries"** button at the bottom
2. A new window opens showing all email summaries at once
3. Scroll through to get a complete overview
4. Perfect for quickly understanding your entire inbox

---

### **Managing Credentials**

**Change API Key or Gmail Account:**
1. Click **"Change Credentials"** button (gear icon)
2. Enter new Gemini API key (or keep the current one)
3. Select a new credentials.json file (or keep current)
4. Click **"Save & Continue"**
5. The app validates and saves your new settings
6. You may need to re-authenticate with Gmail

---

## 📋 Complete Feature List

### **Core Functionality**
- ✅ OAuth 2.0 Gmail authentication
- ✅ Secure credential management
- ✅ Gemini AI integration for summarization
- ✅ Batch email processing (up to 20 emails)
- ✅ AI-generated email summaries
- ✅ AI-generated draft replies
- ✅ Bulk summary view
- ✅ HTML email parsing
- ✅ Clickable Gmail links
- ✅ Token caching for persistent login

### **User Interface**
- ✅ Professional splash screen with progress bar
- ✅ Modern dark theme
- ✅ CustomTkinter-based UI
- ✅ Responsive layout
- ✅ Interactive email cards
- ✅ Hover effects and animations
- ✅ Markdown-formatted text rendering
- ✅ Bold/italic/code styling in summaries
- ✅ Scrollable email list
- ✅ Dual-pane layout

### **Advanced Features**
- ✅ Real-time API key validation
- ✅ Credential file validation
- ✅ Multi-threaded processing
- ✅ Background task execution
- ✅ Error handling and recovery
- ✅ Graceful failure messages
- ✅ Retry mechanisms
- ✅ Custom application icon
- ✅ Window centering and sizing
- ✅ Clean exit handling

### **Security**
- ✅ Local-only data storage
- ✅ No server communication (except Google APIs)
- ✅ Encrypted OAuth tokens
- ✅ No password storage
- ✅ Secure credential deletion
- ✅ Privacy-first design

### **Developer Features**
- ✅ Clean, documented code
- ✅ Modular architecture
- ✅ Exception handling
- ✅ Thread-safe operations
- ✅ PyInstaller build configuration
- ✅ Portable executable generation
- ✅ Cross-platform compatibility

---

## 🛠️ Technical Specifications

**Built With:**
- **Python 3.8+** - Core language
- **CustomTkinter** - Modern UI framework
- **Google APIs** - Gmail & Gemini integration
- **google-auth-oauthlib** - OAuth authentication
- **googleapiclient** - Gmail API client
- **requests** - HTTP client for Gemini API
- **PyInstaller** - Executable compilation

**Requirements:**
- Python 3.8 or higher (for source execution)
- Internet connection (for Gmail/Gemini API)
- Google Cloud Project with Gmail API enabled
- Gemini API key
- Windows/macOS/Linux operating system

**File Structure:**
```
AI Email Summarizer/
├── app.py                          # Main application
├── config.py                       # Configuration storage
├── requirements.txt                # Python dependencies
├── credentials.json                # OAuth credentials (user-provided)
├── gmail_token.pkl                 # Cached authentication token
├── app_icon.ico                    # Application icon
├── AI Email Summarizer.spec        # PyInstaller build spec
├── Launch Ai Email Summarizer.bat  # Windows launcher
├── dist/
│   └── AI Email Summarizer.exe     # Standalone executable
└── README.md                       # This file
```

---

## ❓ Frequently Asked Questions

**Q: Is my Gmail data safe?**
> **A:** Absolutely! The app uses OAuth 2.0 (industry standard), and your password is never stored or transmitted. All processing happens locally on your machine. Email content is only sent to Google's Gemini API for summarization and never stored anywhere.

**Q: Does this cost money to use?**
> **A:** No! Both Gmail API and Gemini API have generous free tiers. For typical personal use, you won't hit the limits.

**Q: Where are my credentials stored?**
> **A:** All credentials are stored locally:
> - API key: `config.py` (plain text, keep secure)
> - OAuth credentials: `credentials.json` (JSON file)
> - Authentication token: `gmail_token.pkl` (encrypted cache)

**Q: Can I use multiple Gmail accounts?**
> **A:** Yes! Click "Change Credentials" to switch accounts. You'll need to re-authenticate with the new account.

**Q: What happens if I delete the app folder?**
> **A:** All your cached data is removed, including authentication tokens and API keys. Your Google Cloud project and API keys remain active in your Google account.

**Q: How many emails can I process?**
> **A:** You can load and summarize 2-20 emails per batch. The limit prevents API rate limiting and ensures smooth performance.

**Q: Can I customize the summaries?**
> **A:** The prompt is hardcoded, but you can modify `app.py` to adjust the Gemini AI prompt for different summary styles.

**Q: Does this work offline?**
> **A:** No, you need an internet connection to fetch emails from Gmail and generate summaries via Gemini API.

**Q: Can I see the source code?**
> **A:** Yes! All source code is included. Review `app.py` to see exactly how the app works.

**Q: What if I get an error during setup?**
> **A:** Common issues:
> - **Invalid API key:** Double-check your Gemini API key
> - **Invalid credentials.json:** Ensure you downloaded the OAuth Desktop client JSON
> - **Gmail API not enabled:** Enable Gmail API in your Google Cloud project
> - **Permission denied:** Add yourself as a test user in OAuth consent screen

**Q: How do I build the .exe myself?**
> **A:** Run: `pyinstaller "AI Email Summarizer.spec"` - the executable will be in the `dist` folder.

---

## 🎯 Use Cases

- **Busy Professionals** - Quickly understand dozens of emails without reading each one
- **Customer Support** - Get instant summaries of customer inquiries
- **Business Executives** - Stay on top of important communications
- **Freelancers** - Manage client emails efficiently
- **Students** - Process academic emails and notifications
- **Anyone with Email Overload** - Regain control of your inbox

---

## 🏆 Why Choose AI Email Summarizer Pro?

✅ **Fully Optimized** - Fast, efficient, production-ready  
✅ **Multiple Run Options** - .exe, .bat, or Python - your choice  
✅ **Professional Quality** - Clean code, modern UI, excellent UX  
✅ **100% Secure** - Privacy-first design, local processing only  
✅ **AI-Powered** - Google's advanced Gemini AI  
✅ **Open Source** - Full transparency and customization  
✅ **No Subscription** - One-time purchase, free Google APIs  
✅ **Regular Updates** - Continuous improvements and features  

---

## 📞 Support & Documentation

- **Source Code:** Fully documented in `app.py`
- **Configuration:** Check `config.py` for settings
- **Build Spec:** Review `AI Email Summarizer.spec` for executable build
- **Requirements:** All dependencies listed in `requirements.txt`

---

## 📄 License

This software is provided as-is for personal and commercial use. Review the license agreement included with your purchase.

---

## 🚀 Get Started Now!

1. Choose your preferred launch method (.exe, .bat, or Python)
2. Set up your Google Cloud credentials (5 minutes)
3. Launch the app and enjoy AI-powered email management!

**Transform your email workflow today. Work smarter, not harder.** 🎯
