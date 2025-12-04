"""
Configuration file for Email Summarizer Pro
Edit this file to add your API keys and settings
"""

import os
import sys
from dotenv import load_dotenv
try:
    import keyring
except Exception:
    keyring = None

# Fix Unicode encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables from .env file
load_dotenv()

# ========== GMAIL API CONFIGURATION ==========
GMAIL_CREDENTIALS_FILE = 'credentials.json'  # OAuth 2.0 credentials file
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
GMAIL_TOKEN_CACHE = 'token.pkl'  # Local cache for credentials

# ========== GEMINI API CONFIGURATION ==========
# First try environment, then fallback to keyring (if available)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
if not GEMINI_API_KEY and keyring:
    try:
        # Use application/service name 'email-summarizer'
        GEMINI_API_KEY = keyring.get_password('email-summarizer', 'gemini_api_key') or ''
    except Exception:
        GEMINI_API_KEY = ''

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

# Gemini settings
GEMINI_TEMPERATURE = 0.2
GEMINI_MAX_TOKENS = 2048

# ========== APP SETTINGS ==========
# Default number of emails to load
DEFAULT_EMAIL_COUNT = 5
DEFAULT_SUMMARIZE_ON_LOAD = False  # Lazy loading by default

# Thread pool workers for parallel summarization
PARALLEL_WORKERS = 4

# UI Settings
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 850
MIN_WINDOW_WIDTH = 1100
MIN_WINDOW_HEIGHT = 650

# ========== VALIDATION ==========
def validate_config():
    """Check if required configuration is set"""
    errors = []
    warnings = []
    
    if not GEMINI_API_KEY:
        errors.append("❌ GEMINI_API_KEY not found in .env file")
    
    # Check credentials in priority order: AppData first, then project folder
    appdata = os.getenv('APPDATA') or os.path.expanduser('~')
    app_cred = os.path.join(appdata, 'email-summarizer', 'credentials.json')
    
    if os.path.exists(app_cred):
        # AppData location takes priority (set by setup screen)
        GMAIL_CREDENTIALS_FILE = app_cred
    elif os.path.exists(GMAIL_CREDENTIALS_FILE):
        # Fall back to project folder
        pass
    else:
        # Not found anywhere
        errors.append(f"❌ {GMAIL_CREDENTIALS_FILE} not found - You cannot login to Gmail!")
    
    if errors or warnings:
        print("\n" + "="*50)
        print("⚠️  Email Summarizer Pro - Configuration Check")
        print("="*50)
        
        if errors:
            print("\n❌ CRITICAL ERRORS (Fix these first):")
            for error in errors:
                print(f"   {error}")
        
        if warnings:
            print("\n⚠️  WARNINGS:")
            for warning in warnings:
                print(f"   {warning}")
        
        print("\n📋 SETUP INSTRUCTIONS:")
        print("\n   1️⃣  Get credentials.json from Google Cloud:")
        print("      • Go to: https://console.cloud.google.com/")
        print("      • Create a new project")
        print("      • Enable Gmail API")
        print("      • Create OAuth 2.0 Desktop credentials")
        print("      • Download as JSON → Rename to 'credentials.json'")
        print("      • Place in this directory")
        
        print("\n   2️⃣  Get Gemini API Key:")
        print("      • Go to: https://aistudio.google.com/app/apikey")
        print("      • Create API Key")
        print("      • Edit .env file → Add: GEMINI_API_KEY=your_key")
        
        print("\n   3️⃣  Run setup assistant:")
        print("      • Double-click: setup.bat (Windows)")
        print("      • Or run: python email_customtkinter_gui.py")
        
        print("\n📚 For detailed help, see SETUP_GUIDE.md")
        print("="*50 + "\n")
        
        return False
    
    return True

if __name__ == "__main__":
    print("📝 Email Summarizer Pro - Configuration Check")
    print("=" * 50)
    if validate_config():
        print("✅ All configuration is valid!")
        print(f"   Gemini API Key: {'Set ✓' if GEMINI_API_KEY else 'Missing ✗'}")
        print(f"   Gmail Credentials: {'Found ✓' if os.path.exists(GMAIL_CREDENTIALS_FILE) else 'Missing ✗'}")
    else:
        print("\n❌ Please fix the configuration issues above")
