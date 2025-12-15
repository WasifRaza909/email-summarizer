"""
Configuration file for AI Email Summarizer Pro.
Stores Gmail and Gemini AI API configuration settings.
Use the app's setup screen to configure credentials instead of editing manually.
"""

import os
import sys
from dotenv import load_dotenv

if sys.platform == 'win32' and sys.stdout is not None:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

GMAIL_CREDENTIALS_FILE = 'credentials.json'
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
GMAIL_TOKEN_CACHE = 'token.pkl'

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"