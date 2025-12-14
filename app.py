import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
from concurrent.futures import ThreadPoolExecutor
import os
import pickle
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import requests
import base64
import re
from html.parser import HTMLParser
from pathlib import Path
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# ========== IMPORT CENTRALIZED CONFIG ==========
try:
    import config
    GEMINI_API_KEY = config.GEMINI_API_KEY
    SCOPES = config.GMAIL_SCOPES
    TOKEN_CACHE_FILE = config.GMAIL_TOKEN_CACHE
    GEMINI_ENDPOINT = config.GEMINI_ENDPOINT
except ImportError:
    print("❌ Error: config.py not found. Please ensure config.py is in the same directory as this script.")
    exit(1)

# ========== MARKDOWN PARSER FOR TEXT DISPLAY ==========
class MarkdownTextWidget(ctk.CTkTextbox):
    """Enhanced text widget that renders markdown formatting with actual text styles"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get access to the underlying tkinter textbox
        self._text_widget = self._textbox
        
        # Use standard fonts for styling with increased font sizes
        base_font = ("Segoe UI", 12)
        bold_font = ("Segoe UI", 12, "bold")
        italic_font = ("Segoe UI", 12, "italic")
        bold_italic_font = ("Segoe UI", 12, "bold", "italic")
        code_font = ("Courier New", 11)
        heading_font = ("Segoe UI", 14, "bold")
        
        # Configure tags for markdown rendering with ACTUAL STYLES
        # Base text with larger font
        self._text_widget.tag_config("base", font=base_font)
        
        # Bold with color highlight (yellow/gold background)
        self._text_widget.tag_config("bold", 
                                     font=bold_font,
                                     foreground="#FFD700",
                                    )
        self._text_widget.tag_config("italic", font=italic_font)
        self._text_widget.tag_config("bold_italic", 
                                     font=bold_italic_font,
                                     foreground="#FFD700",
                                    )
        
        # Code - monospace font with background
        self._text_widget.tag_config("code", 
                                     font=code_font,
                                     foreground="#C2185B",
                                     background="#F5F5F5")
        
        # Headings - bold + blue color with increased size
        self._text_widget.tag_config("heading1", 
                                     font=heading_font,
                                     foreground="#1A73E8")
        
        self._text_widget.tag_config("heading2", 
                                     font=heading_font,
                                     foreground="#1A73E8")
        
        # List items - bright color for visibility on dark background
        self._text_widget.tag_config("list_item", 
                                     foreground="#FFD700")
    
    def insert_markdown(self, index, text):
        """Insert markdown text and parse formatting"""
        lines = text.split('\n')
        
        for line in lines:
            if not line.strip():
                # Empty line
                self._text_widget.insert("end", '\n')
                continue
            
            # Check for headings
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading_match:
                level = len(heading_match.group(1))
                content = heading_match.group(2)
                tag = f"heading{min(level, 2)}"
                self._text_widget.insert("end", content + '\n', tag)
                continue
            
            # Check for list items (- or * or •)
            list_match = re.match(r'^[\s]*([-*•])\s+(.+)$', line)
            if list_match:
                content = list_match.group(2)
                self._text_widget.insert("end", '  • ', 'list_item')
                self._insert_with_formatting("end", content)
                self._text_widget.insert("end", '\n')
                continue
            
            # Regular line with possible inline formatting
            self._insert_with_formatting("end", line)
            self._text_widget.insert("end", '\n')
    
    def _insert_with_formatting(self, index, text):
        """Insert text with inline markdown formatting (***bold italic***, **bold**, *italic*, `code`)"""
        # Pattern to match: ***bold italic***, **bold**, *italic*, `code`
        # Order matters: check longer patterns first
        pattern = r'(\*\*\*([^*]+)\*\*\*)|(\*\*([^*]+)\*\*)|(\*([^*]+)\*)|(`([^`]+)`)'
        
        last_end = 0
        for match in re.finditer(pattern, text):
            # Insert text before match with base font
            if match.start() > last_end:
                self._text_widget.insert(index, text[last_end:match.start()], 'base')
            
            if match.group(2):  # ***bold italic***
                self._text_widget.insert(index, match.group(2), 'bold_italic')
            elif match.group(4):  # **bold**
                self._text_widget.insert(index, match.group(4), 'bold')
            elif match.group(6):  # *italic*
                self._text_widget.insert(index, match.group(6), 'italic')
            elif match.group(8):  # `code`
                self._text_widget.insert(index, match.group(8), 'code')
            
            last_end = match.end()
        
        # Insert remaining text with base font
        if last_end < len(text):
            self._text_widget.insert(index, text[last_end:], 'base')

# Colors - Modern Professional Palette (Dark Theme Only)
COLOR_PRIMARY = "#8AB4F8"
COLOR_PRIMARY_DARK = "#5A96E8"
COLOR_PRIMARY_LIGHT = "#3D5A80"
COLOR_ACCENT = "#81C995"
COLOR_WARNING = "#FBC02D"
COLOR_ERROR = "#F28482"
COLOR_BG = "#121212"
COLOR_SURFACE = "#1E1E1E"
COLOR_SURFACE_DARK = "#2A2A2A"
COLOR_TEXT = "#E8EAED"
COLOR_TEXT_SECONDARY = "#9AA0A6"
COLOR_BORDER = "#3F3F3F"

# Current colors mapping (start with dark theme)
CURRENT_COLORS = {
    "bg": COLOR_BG,
    "surface": COLOR_SURFACE,
    "text": COLOR_TEXT,
    "surface_dark": COLOR_SURFACE_DARK,
    "primary": COLOR_PRIMARY,
}

# ========== FONT SIZES ==========
FONT_XS = 10      # Extra small - secondary text
FONT_SM = 10     # Small - labels, combobox
FONT_MD = 11     # Medium - body text, buttons
FONT_LG = 12     # Large - section titles
FONT_XL = 13     # Extra large - panel titles
FONT_XXL = 14    # 2X large - headers
FONT_TITLE = 26  # Title - main heading
FONT_ICON = 20   # Icon size

# ========== CREDENTIALS ==========
def save_credentials(creds):
    with open(TOKEN_CACHE_FILE, 'wb') as token:
        pickle.dump(creds, token)

def load_credentials():
    if os.path.exists(TOKEN_CACHE_FILE):
        with open(TOKEN_CACHE_FILE, 'rb') as token:
            return pickle.load(token)
    return None

def delete_credentials():
    if os.path.exists(TOKEN_CACHE_FILE):
        os.remove(TOKEN_CACHE_FILE)
        return True
    return False

def is_logged_in():
    return os.path.exists(TOKEN_CACHE_FILE)

# ========== EMAIL UTILS ==========
class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []

    def handle_data(self, d):
        self.text.append(d)

    def get_data(self):
        return ''.join(self.text)

def strip_html_tags(html):
    s = MLStripper()
    try:
        s.feed(html)
        return s.get_data()
    except:
        return html

def get_email_subject(service, message_id):
    """Get email subject and sender from message metadata"""
    try:
        message = service.users().messages().get(userId='me', id=message_id, format='metadata').execute()
        headers = message.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h.get('name') == 'Subject'), "No Subject")
        sender = next((h['value'] for h in headers if h.get('name') == 'From'), "Unknown")
        return subject, sender
    except Exception as e:
        return "Error", str(e)

def get_email_body_raw(service, message_id):
    """Get the full email body/content"""
    try:
        message = service.users().messages().get(userId='me', id=message_id, format='full').execute()
        
        # Try to get text part first, then html
        parts = message.get('payload', {}).get('parts', [])
        body = ""
        
        for part in parts:
            if part['mimeType'] == 'text/plain':
                data = part.get('body', {}).get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
            elif part['mimeType'] == 'text/html':
                data = part.get('body', {}).get('data', '')
                if data:
                    html_content = base64.urlsafe_b64decode(data).decode('utf-8')
                    body = strip_html_tags(html_content)
        
        # Fallback: try to get body from payload directly
        if not body:
            payload = message.get('payload', {})
            data = payload.get('body', {}).get('data', '')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body[:2000] if body else ""
    except Exception as e:
        return f"Error reading email: {str(e)}"

def gemini_summarize_and_reply(body):
    try:
        if not body.strip():
            return "No email content to summarize."
        
        prompt = f"""You are an AI assistant.
    Please:
    1. Summarize the following email in concise bullet points using markdown formatting.
    2. Draft a professional reply email based on the summary.

    Formatting requirements:
    - Use **bold** for important points and for section headings (e.g. **SUMMARY**, **DRAFT REPLY**).
    - Use * for bullet lists.
    - Use inline Markdown bold (`**...**`) for the section headers rather than markdown heading markers like `##`.
    - Format your response for readability and clarity.

    Email:
    {body}
    """
        
        # Get API key from AppData/.env (priority) or config module (fallback)
        api_key = ""
        try:
            app_data_path = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "ai-email-summarizer"
            env_file_path = app_data_path / ".env"
            if env_file_path.exists():
                from dotenv import dotenv_values
                env_vars = dotenv_values(env_file_path)
                api_key = env_vars.get('GEMINI_API_KEY', '').strip()
        except Exception:
            pass
        
        # Fallback to config if not found in AppData
        if not api_key:
            api_key = config.GEMINI_API_KEY.strip() if config.GEMINI_API_KEY else ""
        
        # Include API key in the URL for Gemini API
        api_url = f"{GEMINI_ENDPOINT}?key={api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 2048
            }
        }
        
        response = requests.post(api_url, headers=headers, json=payload)
        
        resp_json = response.json()
        
        if 'candidates' in resp_json and resp_json['candidates']:
            try:
                candidate = resp_json['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    return candidate['content']['parts'][0]['text']
                elif 'content' in candidate and 'text' in candidate['content']:
                    return candidate['content']['text']
                else:
                    return f"Unexpected response structure"
            except (KeyError, IndexError, TypeError) as e:
                return f"Error extracting text: {str(e)}"
        elif 'error' in resp_json:
            return f"Error from Gemini API: {resp_json['error'].get('message', 'Unknown Error')}"
        else:
            return "Gemini API response was empty or malformed"
    except Exception as e:
        return f"Error: {str(e)}"

# ========== CUSTOM COMPONENTS ==========
class EmailListItem(ctk.CTkFrame):
    def __init__(self, parent, subject, sender, command=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.command = command
        self.is_selected = False
        self.parent = parent
        
        # Main container with subtle shadow/border - Material Design
        main_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, corner_radius=8, border_width=1, border_color=COLOR_BORDER)
        main_frame.pack(fill="both", expand=True, padx=3, pady=3)
        main_frame.configure(cursor="hand2")
        
        self.main_frame = main_frame
        # Bind to all child elements
        self.bind("<Button-1>", self._on_click)
        main_frame.bind("<Button-1>", self._on_click)
        
        # Content frame with proper Material Design padding
        content = ctk.CTkFrame(main_frame, fg_color=COLOR_SURFACE, cursor="hand2")
        content.pack(fill="both", expand=True, padx=14, pady=11)
        content.bind("<Button-1>", self._on_click)
        
        # Subject - Material Design typography
        subject_text = subject[:50] + "..." if len(subject) > 50 else subject
        subject_label = ctk.CTkLabel(
            content,
            text=subject_text,
            font=("Segoe UI", FONT_MD, "bold"),
            text_color=COLOR_PRIMARY,
            anchor="w",
            cursor="hand2"
        )
        subject_label.pack(anchor="w", pady=(0, 6), fill="x")
        subject_label.bind("<Button-1>", self._on_click)
        
        # Sender - Secondary text color with proper contrast
        sender_text = sender[:50] + "..." if len(sender) > 50 else sender
        sender_label = ctk.CTkLabel(
            content,
            text=sender_text,
            font=("Segoe UI", FONT_XS),
            text_color=COLOR_TEXT_SECONDARY,
            anchor="w",
            cursor="hand2"
        )
        sender_label.pack(anchor="w", fill="x")
        sender_label.bind("<Button-1>", self._on_click)
        
        self.subject_label_ref = subject_label
        self.sender_label_ref = sender_label
    
    def _on_click(self, event=None):
        self.is_selected = True
        # Active tab: green border only, no background color change
        self.main_frame.configure(fg_color=COLOR_SURFACE, border_color=COLOR_ACCENT, border_width=2)
        self.subject_label_ref.configure(text_color=COLOR_PRIMARY)
        self.sender_label_ref.configure(text_color=COLOR_TEXT)
        if self.command:
            self.command()

    def apply_selection_style(self):
        """Apply selection styling without triggering the command"""
        self.is_selected = True
        self.main_frame.configure(fg_color=COLOR_SURFACE, border_color=COLOR_ACCENT, border_width=2)
        self.subject_label_ref.configure(text_color=COLOR_PRIMARY)
        self.sender_label_ref.configure(text_color=COLOR_TEXT)

    def deselect(self):
        self.is_selected = False
        # Return to default styling
        self.main_frame.configure(fg_color=COLOR_SURFACE, border_color=COLOR_BORDER, border_width=1)
        self.subject_label_ref.configure(text_color=COLOR_PRIMARY)


# ========== SETUP SCREEN ==========
class SetupScreen(ctk.CTkToplevel):
    """First-time setup wizard for credentials and API keys"""
    
    def __init__(self, parent, is_change_mode=False, previous_api_key=None, previous_creds_file=None):
        super().__init__(parent)
        self.parent_app = parent
        self.is_change_mode = is_change_mode
        
        if is_change_mode:
            self.title("AI Email Summarizer Pro - Change Credentials")
        else:
            self.title("AI Email Summarizer Pro - Initial Setup")
        
        self.geometry("600x700")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)
        
        # Make it modal
        self.transient(parent)
        # Don't use grab_set() - it prevents minimizing
        # Just use transient() to keep it on top of parent
        
        # Center on screen
        parent.update_idletasks()
        self.update_idletasks()
        
        # Get screen dimensions
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        
        # Calculate center position on screen (window is 600x700)
        window_w = 600
        window_h = 700
        x = (screen_w - window_w) // 2
        y = (screen_h - window_h) // 2
        
        # Ensure no negative coordinates
        x = max(0, x)
        y = max(0, y)
        
        self.geometry(f"+{int(x)}+{int(y)}")
        
        self.credentials_file_path = previous_creds_file  # Auto-fill if provided
        self.result = {"api_key": "", "credentials_file": None}
        self.changes_made = False  # Track if user actually made changes
        self.user_cancelled = False  # Track if user closed without saving
        self.previous_api_key = previous_api_key  # Store for comparison
        self.previous_creds_file = previous_creds_file  # Store for comparison
        
        # Handle close button (X) - behavior depends on mode
        self.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
        self.create_setup_ui()
        
        # Ensure the window is visible and on top
        self.lift()
        self.focus()
    
    def on_window_close(self):
        """Handle window close button (X) - notify parent to exit if during setup"""
        self.user_cancelled = True
        
        # If this is first-time setup (not change mode), tell parent to exit completely
        if not self.is_change_mode and hasattr(self.parent_app, 'close_requested'):
            self.parent_app.close_requested = True
            self.parent_app.setup_in_progress = False
        
        # Close this dialog
        self.destroy()
    
    def create_setup_ui(self):
        """Create the setup UI"""
        # Main container with padding
        container = ctk.CTkFrame(self, fg_color=COLOR_BG)
        container.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Title based on mode
        if self.is_change_mode:
            title_text = "🔄 Update Your Credentials"
            subtitle_text = "Change your API key or Gmail credentials"
        else:
            title_text = "🚀 Welcome to AI Email Summarizer Pro"
            subtitle_text = "Let's get you set up in 2 minutes"
        
        # Title
        title = ctk.CTkLabel(
            container,
            text=title_text,
            font=("Segoe UI", 18, "bold"),
            text_color=COLOR_PRIMARY
        )
        title.pack(pady=(0, 10))
        
        # Subtitle
        subtitle = ctk.CTkLabel(
            container,
            text=subtitle_text,
            font=("Segoe UI", 12),
            text_color="#A0A0A0"
        )
        subtitle.pack(pady=(0, 25))
        
        # ===== SECTION 1: API KEY =====
        api_section = ctk.CTkFrame(container, fg_color=COLOR_SURFACE, corner_radius=8)
        api_section.pack(fill="x", pady=(0, 20))
        
        api_title = ctk.CTkLabel(
            api_section,
            text="Enter your Gemini API Key",
            font=("Segoe UI", 13, "bold"),
            text_color=COLOR_PRIMARY
        )
        api_title.pack(anchor="w", padx=15, pady=(15, 5))
        
        api_desc = ctk.CTkLabel(
            api_section,
            text="Get it from: https://aistudio.google.com/app/apikey",
            font=("Segoe UI", 10),
            text_color="#808080"
        )
        api_desc.pack(anchor="w", padx=15, pady=(0, 10))
        
        self.api_entry = ctk.CTkEntry(
            api_section,
            placeholder_text="sk-... or AIzaSy...",
            height=45,
            font=("Segoe UI", 11),
            fg_color=COLOR_BG,
            border_color=COLOR_BORDER,
            border_width=1,
            show="•"  # Hide API key for security
        )
        self.api_entry.pack(fill="x", padx=15, pady=(0, 15))
        
        # Auto-fill with previous API key if in change mode
        if self.previous_api_key:
            self.api_entry.insert(0, self.previous_api_key)
        
        # ===== SECTION 2: CREDENTIALS FILE =====
        cred_section = ctk.CTkFrame(container, fg_color=COLOR_SURFACE, corner_radius=8)
        cred_section.pack(fill="x", pady=(0, 20))
        
        cred_title = ctk.CTkLabel(
            cred_section,
            text="Upload your Google credentials.json",
            font=("Segoe UI", 13, "bold"),
            text_color=COLOR_PRIMARY
        )
        cred_title.pack(anchor="w", padx=15, pady=(15, 5))
        
        cred_desc = ctk.CTkLabel(
            cred_section,
            text="Download from: Google Cloud Console → OAuth 2.0 Desktop",
            font=("Segoe UI", 10),
            text_color="#808080"
        )
        cred_desc.pack(anchor="w", padx=15, pady=(0, 10))
        
        # File selection button
        button_frame = ctk.CTkFrame(cred_section, fg_color=COLOR_SURFACE)
        button_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.upload_btn = ctk.CTkButton(
            button_frame,
            text="📁 Select credentials .json file",
            command=self.select_credentials_file,
            fg_color=COLOR_PRIMARY,
            hover_color="#1565C0",
            text_color="#FFFFFF",
            height=40,
            font=("Segoe UI", 11, "bold")
        )
        self.upload_btn.pack(side="left", fill="x", expand=True)
        
        self.file_status = ctk.CTkLabel(
            button_frame,
            text="❌ Not selected",
            font=("Segoe UI", 10),
            text_color="#FF6B6B"
        )
        self.file_status.pack(side="right", padx=(10, 0))
        
        # Auto-fill file status if credentials file was provided
        if self.credentials_file_path:
            filename = os.path.basename(self.credentials_file_path)
            self.file_status.configure(text=f"✓ {filename}", text_color="#4CAF50")
            self.upload_btn.configure(text="📁 Change File")
        
        # ===== SECURITY INFO =====
        security_section = ctk.CTkFrame(container, fg_color="#1B5E20", corner_radius=8)
        security_section.pack(fill="x", pady=(0, 20))
        
        security_title = ctk.CTkLabel(
            security_section,
            text="🔒 Your privacy is protected",
            font=("Segoe UI", 12, "bold"),
            text_color="#4CAF50"
        )
        security_title.pack(anchor="w", padx=15, pady=(12, 5))
        
        security_text = ctk.CTkLabel(
            security_section,
            text="✓ We do NOT store any credentials on servers.\n✓ All data remains on your computer only.\n✓ Direct connection to Gmail & Google APIs.",
            font=("Segoe UI", 10),
            text_color="#C8E6C9",
            justify="left"
        )
        security_text.pack(anchor="w", padx=15, pady=(0, 12))
        
        # ===== BUTTONS =====
        button_frame = ctk.CTkFrame(container, fg_color=COLOR_BG)
        button_frame.pack(fill="x", pady=(20, 0))
        
        self.save_btn = ctk.CTkButton(
            button_frame,
            text="✓ Save & Continue",
            command=self.save_settings,
            fg_color=COLOR_PRIMARY,
            hover_color="#1565C0",
            text_color="#FFFFFF",
            height=40,
            font=("Segoe UI", 12, "bold")
        )
        self.save_btn.pack(fill="x", pady=(0, 10))
        
        # Skip button removed to require completing setup before using the app
    
    def select_credentials_file(self):
        """Open file dialog to select credentials .json file"""
        file_path = filedialog.askopenfilename(
            title="Select credentials .json file",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            initialdir=os.path.expanduser("~")
        )
        
        if file_path:
            try:
                # Validate it's a valid JSON and has expected Gmail OAuth structure
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                    # Check if it has the OAuth structure
                    if not ('installed' in data or 'web' in data):
                        messagebox.showerror("Invalid File", "This doesn't appear to be a valid OAuth credentials file (missing 'installed' or 'web' key)")
                        return
                    
                    # Get the config section (either 'installed' or 'web')
                    oauth_config = data.get('installed', data.get('web', {}))
                    
                    # Validate required fields for OAuth credentials
                    required_fields = ['client_id', 'client_secret', 'redirect_uris']
                    missing_fields = [field for field in required_fields if field not in oauth_config]
                    
                    if missing_fields:
                        messagebox.showerror(
                            "Invalid Credentials File",
                            f"This credentials file is incomplete. Missing required fields:\n"
                            f"{', '.join(missing_fields)}\n\n"
                            f"Please download a valid OAuth credentials file from:\n"
                            f"Google Cloud Console → APIs & Services → Credentials"
                        )
                        return
                    
                    # Additional validation: check if redirect_uris is non-empty
                    if not oauth_config.get('redirect_uris') or not isinstance(oauth_config.get('redirect_uris'), list):
                        messagebox.showerror(
                            "Invalid Credentials File",
                            "This credentials file has no redirect URIs configured.\n\n"
                            "Please ensure your OAuth credentials are properly configured."
                        )
                        return
                    
                    # All validations passed
                    self.credentials_file_path = file_path
                    filename = os.path.basename(file_path)
                    self.file_status.configure(text=f"✓ {filename}", text_color="#4CAF50")
                    self.upload_btn.configure(text="📁 Change File")
            except json.JSONDecodeError:
                messagebox.showerror("Invalid JSON", "The selected file is not a valid JSON file")
            except Exception as e:
                messagebox.showerror("Error", f"Error reading file: {str(e)}")
    
    def save_settings(self):
        """Save settings and close - ONLY if both API key and credentials are provided"""
        api_key = self.api_entry.get().strip()
        
        # Validate API key
        if not api_key:
            messagebox.showwarning("Missing API Key", "❌ Please enter your Gemini API key")
            self.api_entry.focus()
            return
        
        # Validate credentials file
        if not self.credentials_file_path:
            messagebox.showwarning(
                "Missing Credentials File", 
                "❌ Please select your credentials.json file\n\n"
                "If you don't have it yet, you can:\n"
                "1. Get it from Google Cloud Console\n"
                "2. Skip Setup & Set it up later using 'Change Credentials'"
            )
            return
        
        # In change mode, check if anything actually changed
        if self.is_change_mode:
            # Check if API key changed
            api_key_changed = (api_key != self.previous_api_key) if self.previous_api_key else True
            
            # Check if credentials file changed (if user selected a new one)
            creds_changed = (self.credentials_file_path != self.previous_creds_file) if self.previous_creds_file else False
            
            # If nothing changed, just close without testing or validation
            if not api_key_changed and not creds_changed:
                self.result = {"api_key": api_key, "credentials_file": self.credentials_file_path}
                self.changes_made = False  # Mark that no changes were made
                self.update_idletasks()  # Ensure any pending updates are processed
                self.destroy()
                return
        
        # Re-validate credentials file before saving (in case it was modified or is invalid)
        # BUT: In change mode, if user didn't change the credentials file, skip validation
        # (they're only changing the API key)
        if self.credentials_file_path and os.path.exists(self.credentials_file_path):
            if not self._validate_credentials_file(self.credentials_file_path):
                messagebox.showerror(
                    "Invalid Credentials File",
                    "The selected credentials file is no longer valid.\n\n"
                    "Please select a valid OAuth credentials file from:\n"
                    "Google Cloud Console → APIs & Services → Credentials"
                )
                self.credentials_file_path = None
                self.file_status.configure(text="❌ Not selected", text_color="#FF6B6B")
                self.upload_btn.configure(text="📁 Select credentials .json file")
                return
        
        # Validate API key by testing it
        self.api_entry.configure(state="disabled")
        self.save_btn.configure(state="disabled")
        
        # Show custom auto-closing testing dialog
        self._show_testing_dialog()
        
        # Test in background
        self.after(100, lambda: self._test_and_continue(api_key))
    
    def _validate_credentials_file(self, file_path):
        """Validate that the credentials file is a valid OAuth credentials file"""
        try:
            if not os.path.exists(file_path):
                return False
            
            with open(file_path, 'r') as f:
                data = json.load(f)
                
                # Check if it has the OAuth structure
                if not ('installed' in data or 'web' in data):
                    return False
                
                # Get the config section (either 'installed' or 'web')
                oauth_config = data.get('installed', data.get('web', {}))
                
                # Validate required fields for OAuth credentials
                required_fields = ['client_id', 'client_secret', 'redirect_uris']
                if not all(field in oauth_config for field in required_fields):
                    return False
                
                # Check if redirect_uris is non-empty
                if not oauth_config.get('redirect_uris') or not isinstance(oauth_config.get('redirect_uris'), list):
                    return False
                
                return True
        except Exception:
            return False
    
    def test_gemini_api_key(self, api_key):
        """Test if the Gemini API key is valid"""
        try:
            import requests
            
            # First, validate API key format (basic sanity checks)
            api_key_stripped = api_key.strip()
            
            # Check minimum length (Google API keys are typically 40+ characters)
            if len(api_key_stripped) < 20:
                print(f"❌ API Key too short: {len(api_key_stripped)} characters (minimum 20 required)")
                return False
            
            # Check for invalid characters (API keys should be alphanumeric, dash, underscore)
            if not all(c.isalnum() or c in '-_' for c in api_key_stripped):
                print(f"❌ API Key contains invalid characters")
                return False
            
            # Check if it looks like a Gemini/Google API key (should start with specific patterns)
            # Gemini API keys usually start with "AIza" or similar
            if not (api_key_stripped.startswith('AIza') or api_key_stripped.startswith('sk-')):
                print(f"⚠️  Warning: API key doesn't match expected format (should start with 'AIza' or 'sk-')")
                # Still allow it to be tested against the API
            
            test_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key_stripped}"
            
            test_payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": "Hello"}
                        ]
                    }
                ]
            }
            
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(test_url, headers=headers, json=test_payload, timeout=5)
            resp_json = response.json()
            
            # Check if response indicates success or invalid key
            if 'error' in resp_json:
                error_msg = resp_json['error'].get('message', '').lower()
                if 'unauthenticated' in error_msg or 'invalid' in error_msg or 'unregistered' in error_msg:
                    print(f"❌ API Key validation failed: {resp_json['error'].get('message', 'Unknown error')}")
                    return False
            
            # If we got here, key is likely valid
            return True
        
        except requests.exceptions.Timeout:
            print(f"❌ API Key test timed out - check your internet connection")
            return False
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection error - check your internet connection")
            return False
        except Exception as e:
            print(f"❌ Error testing API key: {str(e)}")
            return False
    
    def _show_testing_dialog(self):
        """Show a clean testing dialog with loading animation"""
        self.test_dialog = ctk.CTkToplevel(self)
        self.test_dialog.title("Testing API Key")
        self.test_dialog.geometry("420x200")
        self.test_dialog.resizable(False, False)
        self.test_dialog.configure(fg_color="#1E1E1E")
        self.test_dialog.transient(self)
        
        # Make it stay on top
        self.test_dialog.lift()
        try:
            self.test_dialog.grab_set()
        except:
            pass
        
        # Center on screen
        self.test_dialog.update_idletasks()
        screen_w = self.test_dialog.winfo_screenwidth()
        screen_h = self.test_dialog.winfo_screenheight()
        x = (screen_w - 420) // 2
        y = (screen_h - 200) // 2
        self.test_dialog.geometry(f"+{x}+{y}")
        
        # Main container with padding
        container = ctk.CTkFrame(self.test_dialog, fg_color="#1E1E1E")
        container.pack(fill="both", expand=True, padx=20, pady=(25, 20))
        
        # Title
        title = ctk.CTkLabel(
            container,
            text="🔐 Testing API Key & Credentials",
            font=("Segoe UI", 14, "bold"),
            text_color="#4CAF50"
        )
        title.pack(pady=(0, 15))
        
        # Animated loading text
        self.loading_label = ctk.CTkLabel(
            container,
            text="Connecting to Google Gemini API",
            font=("Segoe UI", 11),
            text_color="#FFFFFF"
        )
        self.loading_label.pack(pady=(0, 12))
        
        # Status message
        self.status_label = ctk.CTkLabel(
            container,
            text="Validating your credentials, please wait...",
            font=("Segoe UI", 12),
            text_color="#CCCCCC"
        )
        self.status_label.pack(pady=(0, 0))
        
        # Ensure window is drawn before starting animations
        self.test_dialog.update()
    
    def _animate_progress_dots(self, label, step):
        """Animate progress dots"""
        if not hasattr(self, 'test_dialog') or not self.test_dialog.winfo_exists():
            return
        
        dots = ["●   ●   ●", "  ●   ●  ", "    ●    ", "  ●   ●  "]
        label.configure(text=dots[step % 4])
        
        # Continue animation every 200ms
        self.after(200, lambda: self._animate_progress_dots(label, step + 1))
    
    def _test_and_continue(self, api_key):
        """Test API key and continue with save if valid"""
        valid = self.test_gemini_api_key(api_key)
        
        # Close testing dialog
        if hasattr(self, 'test_dialog') and self.test_dialog.winfo_exists():
            self.test_dialog.destroy()
        
        if not valid:
            self.api_entry.configure(state="normal")
            self.save_btn.configure(state="normal")
            messagebox.showerror(
                "❌ Invalid API Key",
                "The API key you provided is invalid or not working.\n\n"
                "Please check:\n"
                "1. The key is correct and not expired\n"
                "2. The key is enabled on Google Cloud Console\n"
                "3. Gemini API is enabled for your project\n\n"
                "Get a key from: https://aistudio.google.com/app/apikey"
            )
            self.api_entry.focus()
            return
        
        self.api_entry.configure(state="normal")
        self.save_btn.configure(state="normal")
        
        # API key is valid - continue with saving settings
        self._finish_save(api_key)
    
    def _finish_save(self, api_key):
        """Complete the save process after API key is validated"""
        # Everything is valid - save settings
        try:
            # Create AppData folder if it doesn't exist
            app_data_path = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "ai-email-summarizer"
            app_data_path.mkdir(parents=True, exist_ok=True)
            
            # Save API key to .env
            env_file = app_data_path / ".env"
            with open(env_file, 'w') as f:
                f.write(f"GEMINI_API_KEY={api_key}\n")
            
            # Only copy/update credentials file if a new one was selected
            cred_dest = None
            if self.credentials_file_path and os.path.exists(self.credentials_file_path):
                # Remove old credential files (*.json files except the new one we're about to save)
                source_filename = os.path.basename(self.credentials_file_path)
                if app_data_path.exists():
                    for old_file in app_data_path.glob('*.json'):
                        if old_file.is_file() and old_file.name != source_filename:
                            try:
                                old_file.unlink()  # Delete the old file
                            except Exception:
                                pass  # Silently skip if we can't delete
                
                # Copy credentials file (preserve original filename)
                cred_dest = app_data_path / source_filename
                with open(self.credentials_file_path, 'r') as src:
                    with open(cred_dest, 'w') as dst:
                        dst.write(src.read())
            else:
                # No new credentials file selected - find existing one
                if app_data_path.exists():
                    for file in app_data_path.glob('*.json'):
                        if file.is_file():
                            cred_dest = file
                            break
            
            # Create a marker file to indicate setup is complete
            setup_marker = app_data_path / ".setup_complete"
            setup_marker.touch()
            
            # Update global config with new paths
            import config as config_module
            config_module.GEMINI_API_KEY = api_key
            if cred_dest:
                config_module.GMAIL_CREDENTIALS_FILE = str(cred_dest)
            
            messagebox.showinfo(
                "✓ Setup Complete",
                "✓ Settings saved!\n\nYour credentials are stored securely on your computer."
            )
            self.result = {"api_key": api_key, "credentials_file": str(cred_dest) if cred_dest else None}
            self.changes_made = True  # Mark that changes were actually saved
            # Auto-close setup dialog after showing success message
            self.after(100, self.destroy)
        
        except Exception as e:
            messagebox.showerror("❌ Save Error", f"Failed to save settings: {str(e)}")
    
    def skip_setup(self):
        """Skip setup - prompt varies based on what user entered"""
        api_key = self.api_entry.get().strip()
        has_creds_file = bool(self.credentials_file_path)
        
        # Case 1: User hasn't entered ANYTHING - offer to skip with warning
        if not api_key and not has_creds_file:
            response = messagebox.askyesno(
                "⚠️ Skip Setup",
                "Are you sure? Without credentials, you won't be able to:\n"
                "• Log in to Gmail\n"
                "• Summarize emails\n\n"
                "You can set them up anytime using 'Change Credentials'.\n\n"
                "Skip setup anyway?"
            )
            if response:
                self.destroy()
            return
        
        # Case 2: User entered API key but no credentials file
        if api_key and not has_creds_file:
            response = messagebox.askyesno(
                "⚠️ Skip Setup",
                "You've entered your API key but haven't selected credentials.json\n\n"
                "Without Gmail credentials, you won't be able to:\n"
                "• Log in to Gmail\n"
                "• Load or summarize emails\n\n"
                "Options:\n"
                "• Click 'No' to select credentials file\n"
                "• Click 'Yes' to skip and add credentials later\n\n"
                "Skip and add credentials later?"
            )
            if response:
                self.destroy()
            return
        
        # Case 3: User selected credentials but no API key
        if not api_key and has_creds_file:
            response = messagebox.askyesno(
                "⚠️ Skip Setup",
                "You've selected credentials.json but haven't entered your API key\n\n"
                "Without an API key, you won't be able to:\n"
                "• Summarize emails using AI\n"
                "• Use the smart summarization feature\n\n"
                "Options:\n"
                "• Click 'No' to enter your API key\n"
                "• Click 'Yes' to skip and add API key later\n\n"
                "Skip and add API key later?"
            )
            if response:
                self.destroy()
            return
        
        # Case 4: User entered BOTH - shouldn't reach here, but just in case
        # This would mean they should click Save instead of Skip
        messagebox.showinfo(
            "ℹ️ Ready to Save",
            "You've entered both your API key and selected credentials.json!\n\n"
            "Please click '✓ Save & Continue' to save your settings.\n\n"
            "If you want to skip setup anyway, clear one of the fields first."
        )

# ========== LOGIN MONITOR WINDOW ==========
class LoginMonitorWindow(ctk.CTkToplevel):
    """Modal window that monitors OAuth login progress and detects completion"""
    
    def __init__(self, parent, flow_callback):
        super().__init__(parent)
        self.title("AI Email Summarizer Pro - Signing In")
        self.geometry("450x250")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)
        
        # Make it modal
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 225
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 125
        self.geometry(f"+{x}+{y}")
        
        self.flow_callback = flow_callback
        self.login_complete = False
        self.need_retry = False
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        self.create_ui()
        self.start_monitoring()
    
    def create_ui(self):
        """Create the monitoring UI"""
        container = ctk.CTkFrame(self, fg_color=COLOR_BG)
        container.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Title
        title = ctk.CTkLabel(
            container,
            text="🔐 Signing In...",
            font=("Segoe UI", 18, "bold"),
            text_color=COLOR_PRIMARY
        )
        title.pack(pady=(0, 15))
        
        # Instructions
        instructions = ctk.CTkLabel(
            container,
            text="A browser window has opened.\n\n"
                 "Complete the Google sign-in process.\n"
                 "This window will close automatically when login is complete.",
            font=("Segoe UI", 11),
            text_color=COLOR_TEXT,
            justify="center",
            wraplength=400
        )
        instructions.pack(pady=(0, 25))
        
        # Progress animation
        progress_frame = ctk.CTkFrame(container, fg_color=COLOR_BG)
        progress_frame.pack(fill="x", pady=(0, 20))
        
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            fg_color=COLOR_SURFACE_DARK,
            progress_color=COLOR_PRIMARY,
            height=4,
            corner_radius=2
        )
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            container,
            text="⏳ Waiting for browser...",
            font=("Segoe UI", 10),
            text_color=COLOR_TEXT_SECONDARY
        )
        self.status_label.pack()
        
        # Cancel button
        button_container = ctk.CTkFrame(container, fg_color=COLOR_BG)
        button_container.pack(fill="x", pady=(20, 0))
        
        retry_btn = ctk.CTkButton(
            button_container,
            text="🔄 Retry",
            command=self.on_retry,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_DARK,
            text_color="#FFFFFF",
            font=("Segoe UI", 10),
            height=32,
            corner_radius=5
        )
        retry_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        cancel_btn = ctk.CTkButton(
            button_container,
            text="✕ Cancel",
            command=self.on_cancel,
            fg_color="#CCCCCC",
            hover_color="#B0B0B0",
            text_color=COLOR_TEXT,
            font=("Segoe UI", 10),
            height=32,
            corner_radius=5
        )
        cancel_btn.pack(side="left", fill="x", expand=True)
    
    def start_monitoring(self):
        """Start monitoring for login completion"""
        self.check_login_count = 0
        self.animate_progress()
    
    def animate_progress(self):
        """Animate progress bar and check for login completion"""
        if not self.login_complete and self.winfo_exists():
            # Animate progress bar
            current = self.progress_bar.get()
            self.progress_bar.set((current + 0.05) % 1.0)
            
            # Check if login completed
            if self.check_login_count % 4 == 0:  # Check every 2 seconds
                self.check_login_callback()
            
            self.check_login_count += 1
            self.after(500, self.animate_progress)
    
    def check_login_callback(self):
        """Call the flow callback to check for login completion"""
        try:
            result = self.flow_callback()
            if result:  # Login completed
                self.login_complete = True
                self.status_label.configure(text="✓ Login successful!")
                self.progress_bar.set(1.0)
                self.after(500, self.destroy)
        except Exception:
            pass
    
    def on_cancel(self):
        """User cancelled login - mark as cancelled and close"""
        self.login_complete = True  # Mark as complete so it stops checking
        self.status_label.configure(text="✓ Login cancelled")
        self.destroy()
    
    def on_retry(self):
        """User wants to retry - open browser again"""
        try:
            if hasattr(self, 'auth_url'):
                webbrowser.open(self.auth_url)
                self.status_label.configure(text="⏳ Waiting for browser...")
                self.need_retry = True
                # Reset counters to keep monitoring
                self.check_login_count = 0
        except Exception:
            pass

# ========== MAIN APP ==========
ctk.set_appearance_mode("dark")

class EmailSummarizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AI Email Summarizer Pro")
        self.minsize(1100, 650)
        self.resizable(True, True)
        self.configure(fg_color=COLOR_BG)
        
        self.service = None
        self.emails = []
        self.email_data = {}
        self.selected_email_id = None
        self.email_items = []
        self.max_emails = 5
        self.summarize_on_load = tk.BooleanVar(value=False)  # Toggle: lazy vs eager
        self.current_theme = "dark"  # Track current theme
        self.setup_in_progress = True  # Track if setup is happening
        self.close_requested = False  # Track if user clicked close button
        
        # Handle close button - always use this handler
        self.protocol("WM_DELETE_WINDOW", self.on_close_requested)
        
        # Withdraw window during setup to avoid showing background window
        self.withdraw()
        self.update_idletasks()  # Force window creation without showing it
        
        # Check for first-time setup BEFORE creating any widgets
        # This will block until setup is complete if needed
        self._do_first_time_setup()
        
        # If user closed the window, exit now
        if self.close_requested:
            self.destroy()
            return
        
        # Mark setup as complete
        self.setup_in_progress = False
        
        # Now create widgets only after setup is done
        self.create_widgets()
        self.check_login_status()
        
        # Show the window at full size
        self.after(0, self._show_fullscreen)
    
    def on_close_requested(self):
        """Handle window close button (X) - exit immediately"""
        self.close_requested = True
        self.setup_in_progress = False

        # Tear down any active setup dialog
        if hasattr(self, '_setup_screen') and self._setup_screen and self._setup_screen.winfo_exists():
            try:
                self._setup_screen.destroy()
            except:
                pass

        self.destroy()
        import sys
        sys.exit(0)
    
    def create_widgets(self):
        # ===== HEADER =====
        header = ctk.CTkFrame(self, fg_color=COLOR_SURFACE_DARK, height=85, corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header, fg_color=COLOR_SURFACE_DARK)
        header_content.pack(fill="both", expand=True, padx=30, pady=15)
        
        left_header = ctk.CTkFrame(header_content, fg_color=COLOR_SURFACE_DARK)
        left_header.pack(side="left", fill="both", expand=True)
        
        title = ctk.CTkLabel(
            left_header,
            text="AI Email Summarizer Pro",
            font=("Segoe UI", FONT_TITLE, "bold"),
            text_color="#FFFFFF"
        )
        title.pack(anchor="w", pady=(0, 0))
        
        self.status_label = ctk.CTkLabel(
            left_header,
            text="Status: Not logged in",
            font=("Segoe UI", FONT_SM),
            text_color="#E6E6E6"
        )
        self.status_label.pack(anchor="w", pady=(2, 0))
        
        # Right header intentionally omitted so no icon or box appears on the right
        # Keep a safe attribute so code that updates the icon won't raise AttributeError.
        self.status_icon = None
        
        # ===== TOOLBAR =====
        toolbar = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, height=65)
        toolbar.pack(fill="x", padx=0, pady=0)
        toolbar.pack_propagate(False)
        
        toolbar_content = ctk.CTkFrame(toolbar, fg_color=COLOR_SURFACE)
        toolbar_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left buttons
        left_buttons = ctk.CTkFrame(toolbar_content, fg_color=COLOR_SURFACE)
        left_buttons.pack(side="left", fill="y")
        
        self.login_btn = ctk.CTkButton(
            left_buttons,
            text="🔓 Login",
            command=self.login,
            fg_color=COLOR_ACCENT,
            hover_color="#2D8E47",
            text_color="#FFFFFF",
            font=("Segoe UI", FONT_MD, "bold"),
            width=110,
            height=40,
            corner_radius=5
        )
        self.login_btn.pack(side="left", padx=4)
        
        # Divider
        divider = ctk.CTkFrame(left_buttons, fg_color=COLOR_BORDER, width=1, height=35)
        divider.pack(side="left", padx=6)
        
        # Email count selector (visible in toolbar)
        count_label = ctk.CTkLabel(
            left_buttons,
            text="Load Mails:  ",
            font=("Segoe UI", FONT_XXL, "bold"),
            text_color=COLOR_TEXT
        )
        count_label.pack(side="left", padx=(4, 4))
        
        self.email_count_var = tk.StringVar(value="5")
        count_options = ["2", "3", "5", "10", "20"]
        self.count_combo = ctk.CTkComboBox(
            left_buttons,
            values=count_options,
            variable=self.email_count_var,
            state="readonly",
            fg_color=COLOR_SURFACE_DARK,
            border_color=COLOR_BORDER,
            button_color=COLOR_PRIMARY,
            dropdown_fg_color=COLOR_SURFACE,
            width=55,
            height=35,
            font=("Segoe UI", FONT_SM),
            corner_radius=4,
            button_hover_color=COLOR_PRIMARY_DARK
        )
        self.count_combo.pack(side="left", padx=(0, 8))
        
        # Divider
        divider2 = ctk.CTkFrame(left_buttons, fg_color=COLOR_BORDER, width=1, height=35)
        divider2.pack(side="left", padx=6)
        
        # Summarize on load toggle
        toggle_label = ctk.CTkLabel(
            left_buttons,
            text="Summarize all emails at once:",
            font=("Segoe UI", FONT_SM),
            text_color=COLOR_TEXT
        )
        toggle_label.pack(side="left", padx=(4, 6))
        
        self.summarize_toggle = ctk.CTkSwitch(
            left_buttons,
            text="",
            variable=self.summarize_on_load,
            onvalue=True,
            offvalue=False,
            fg_color=COLOR_ERROR,  # Red when OFF
            progress_color=COLOR_ACCENT,  # Green when ON
            button_color="#FFFFFF",
            button_hover_color="#F0F0F0",
            height=30,
            width=50
        )
        self.summarize_toggle.pack(side="left", padx=(0, 8))
        
        # Divider
        divider3 = ctk.CTkFrame(left_buttons, fg_color=COLOR_BORDER, width=1, height=35)
        divider3.pack(side="left", padx=6)
        
        self.load_btn = ctk.CTkButton(
            left_buttons,
            text="📧 Load Emails",
            command=self.load_emails_thread,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_DARK,
            text_color="#FFFFFF",
            font=("Segoe UI", FONT_MD, "bold"),
            width=130,
            height=40,
            corner_radius=5,
            state="disabled"
        )
        self.load_btn.pack(side="left", padx=4)
        
        self.logout_btn = ctk.CTkButton(
            left_buttons,
            text="🔐 Logout",
            command=self.logout,
            fg_color=COLOR_ERROR,
            hover_color="#C5221F",
            text_color="#FFFFFF",
            font=("Segoe UI", FONT_MD, "bold"),
            width=110,
            height=40,
            corner_radius=5,
            state="disabled"
        )
        self.logout_btn.pack(side="left", padx=4)
        
        # Divider
        divider4 = ctk.CTkFrame(left_buttons, fg_color=COLOR_BORDER, width=1, height=35)
        divider4.pack(side="left", padx=6)
        
        self.change_creds_btn = ctk.CTkButton(
            left_buttons,
            text="🔑 Change Credentials",
            command=self.open_change_credentials,
            fg_color="#6200EA",
            hover_color="#5E35B1",
            text_color="#FFFFFF",
            font=("Segoe UI", FONT_MD, "bold"),
            width=175,
            height=40,
            corner_radius=5
        )
        self.change_creds_btn.pack(side="left", padx=4)
        
        # Right side - Theme toggle button
        right_buttons = ctk.CTkFrame(toolbar_content, fg_color=COLOR_SURFACE)
        right_buttons.pack(side="right", fill="y")
        
        # ===== MAIN CONTENT =====
        content = ctk.CTkFrame(self, fg_color=COLOR_BG)
        content.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Left panel - Email list
        left_panel = ctk.CTkFrame(content, fg_color=COLOR_SURFACE, corner_radius=10)
        left_panel.pack(side="left", fill="both", expand=False, padx=(0, 10))
        
        email_title = ctk.CTkLabel(
            left_panel,
            text="📬 Inbox",
            font=("Segoe UI", FONT_XL, "bold"),
            text_color=COLOR_PRIMARY
        )
        email_title.pack(anchor="w", padx=14, pady=(12, 8))
        
        self.email_count_display = ctk.CTkLabel(
            left_panel,
            text="0 emails",
            font=("Segoe UI", FONT_XS),
            text_color=COLOR_TEXT_SECONDARY
        )
        self.email_count_display.pack(anchor="w", padx=14, pady=(0, 8))
        
        self.email_list_frame = ctk.CTkScrollableFrame(
            left_panel,
            fg_color=COLOR_SURFACE,
            width=350,
            height=650,
            corner_radius=8
        )
        self.email_list_frame.pack(fill="both", expand=True, padx=8, pady=(0, 10))
        
        # Right panel - Summary
        right_panel = ctk.CTkFrame(content, fg_color=COLOR_SURFACE, corner_radius=10)
        right_panel.pack(side="right", fill="both", expand=True)
        
        summary_title = ctk.CTkLabel(
            right_panel,
            text="📝 Summary & Draft Reply",
            font=("Segoe UI", FONT_XL, "bold"),
            text_color=COLOR_PRIMARY
        )
        summary_title.pack(anchor="w", padx=16, pady=(12, 10))
        
        # Email info section
        info_frame = ctk.CTkFrame(right_panel, fg_color=COLOR_BG)
        info_frame.pack(fill="x", padx=16, pady=(0, 12))
        
        subj_title = ctk.CTkLabel(
            info_frame,
            text="Subject:",
            font=("Segoe UI", FONT_LG, "bold"),
            text_color=COLOR_TEXT_SECONDARY
        )
        subj_title.pack(anchor="w", pady=(0, 2), padx=10)
        
        self.subject_label = ctk.CTkLabel(
            info_frame,
            text="No email selected",
            font=("Segoe UI", FONT_LG),
            text_color=COLOR_PRIMARY,
            justify="left",
            anchor="w"
        )
        self.subject_label.pack(anchor="w", pady=(0, 2), padx=10, fill="x")
        
        from_title = ctk.CTkLabel(
            info_frame,
            text="From:",
            font=("Segoe UI", FONT_LG, "bold"),
            text_color=COLOR_TEXT_SECONDARY
        )
        from_title.pack(anchor="w", pady=(0, 2), padx=10)
        
        self.from_label = ctk.CTkLabel(
            info_frame,
            text="No email selected",
            font=("Segoe UI", FONT_LG),
            text_color=COLOR_PRIMARY,
            justify="left",
            anchor="w"
        )
        self.from_label.pack(anchor="w", padx=10, fill="x")
        
        divider = ctk.CTkFrame(right_panel, fg_color=COLOR_BORDER, height=1)
        divider.pack(fill="x", padx=16, pady=10)
        
        # Summary text - now with markdown support
        self.summary_text = MarkdownTextWidget(
            right_panel,
            font=("Segoe UI", 13),
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=6,
            state="disabled",
            cursor=""
        )
        self.summary_text.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        
        # Status bar
        status_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, height=50)
        status_frame.pack(fill="x", padx=0, pady=0)
        status_frame.pack_propagate(False)
        
        status_content = ctk.CTkFrame(status_frame, fg_color=COLOR_SURFACE)
        status_content.pack(fill="both", expand=True, padx=20, pady=8)
        
        self.progress_label = ctk.CTkLabel(
            status_content,
            text="Ready to load emails",
            font=("Segoe UI", FONT_XS),
            text_color=COLOR_TEXT_SECONDARY
        )
        self.progress_label.pack(anchor="w", side="left", padx=(0, 15))
        
        self.progress_bar = ctk.CTkProgressBar(
            status_content,
            fg_color=COLOR_SURFACE_DARK,
            progress_color=COLOR_PRIMARY,
            height=3,
            corner_radius=2
        )
        self.progress_bar.pack(fill="x", expand=True, side="left")
        self.progress_bar.set(0)
    
    def check_login_status(self):
        # Get current API key from AppData .env (priority), then fall back to config
        current_api_key = ""
        try:
            app_data_path = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "ai-email-summarizer"
            env_file_path = app_data_path / ".env"
            if env_file_path.exists():
                from dotenv import dotenv_values
                env_vars = dotenv_values(env_file_path)
                current_api_key = env_vars.get('GEMINI_API_KEY', '').strip()
        except Exception:
            pass
        
        # Fallback to config if not found in AppData
        if not current_api_key:
            current_api_key = config.GEMINI_API_KEY.strip() if config.GEMINI_API_KEY else ""
        
        if is_logged_in():
            self.status_label.configure(text="✓ Logged in - Ready to load emails")
            if getattr(self, 'status_icon', None):
                self.status_icon.configure(text="🟢")
            self.login_btn.configure(state="disabled", fg_color="#CCCCCC", hover_color="#CCCCCC")
            
            # Only enable load button if API key is also available
            if current_api_key:
                self.load_btn.configure(state="normal", fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_DARK)
            else:
                self.load_btn.configure(state="disabled", fg_color="#CCCCCC", hover_color="#CCCCCC")
            
            self.logout_btn.configure(state="normal", fg_color=COLOR_ERROR, hover_color="#C5221F")
            self.change_creds_btn.configure(state="normal", fg_color="#6200EA", hover_color="#5E35B1")
            self.service = self.get_service()
        else:
            self.status_label.configure(text="✗ Not logged in")
            if getattr(self, 'status_icon', None):
                self.status_icon.configure(text="🔴")
            self.login_btn.configure(state="normal", fg_color=COLOR_ACCENT, hover_color="#2D8E47")
            self.load_btn.configure(state="disabled", fg_color="#CCCCCC", hover_color="#CCCCCC")
            self.logout_btn.configure(state="disabled", fg_color="#CCCCCC", hover_color="#CCCCCC")
            self.change_creds_btn.configure(state="normal", fg_color="#6200EA", hover_color="#5E35B1")
    
    def _show_fullscreen(self):
        """Show window at fullscreen state"""
        try:
            self.state("zoomed")
            self.deiconify()
        except Exception:
            self.deiconify()
    
    def _do_first_time_setup(self):
        """Check for first-time setup before creating any widgets"""
        try:
            import importlib
            import sys
            from dotenv import load_dotenv, dotenv_values
            
            # Keep looping until setup is complete (user cannot skip if no credentials exist)
            while self.setup_in_progress and not self.close_requested:
                # Allow window events to be processed
                self.update()
                
                # Check if window was closed
                if self.close_requested or not self.setup_in_progress:
                    return
                
                # Check for credentials in order of priority:
                # 1. Local credentials.json (most common for BAT file launch)
                # 2. AppData credentials
                # 3. Config path
                
                cred_exists = False
                
                # Priority 1: Check local credentials.json in current directory
                if os.path.exists('credentials.json'):
                    try:
                        with open('credentials.json', 'r') as f:
                            data = json.load(f)
                            if ('installed' in data or 'web' in data) and 'client_id' in data.get('installed', data.get('web', {})):
                                cred_exists = True
                    except Exception:
                        pass
                
                # Priority 2: Check AppData location
                if not cred_exists:
                    app_data_path = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "ai-email-summarizer"
                    if app_data_path.exists():
                        for file in app_data_path.glob('*.json'):
                            if file.is_file():
                                try:
                                    with open(file, 'r') as f:
                                        data = json.load(f)
                                        if 'installed' in data or 'web' in data:
                                            cred_exists = True
                                            break
                                except Exception:
                                    continue
                
                # Priority 3: Check config path
                if not cred_exists:
                    import config as config_module
                    cred_exists = os.path.exists(config_module.GMAIL_CREDENTIALS_FILE)
                
                # Check if API key exists
                app_data_path = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "ai-email-summarizer"
                env_file_path = app_data_path / ".env"
                
                env_vars = dotenv_values(env_file_path) if env_file_path.exists() else {}
                api_key_from_env = env_vars.get('GEMINI_API_KEY', '').strip()
                
                # Use API key from env or from config
                import config as config_module
                api_key_exists = bool(api_key_from_env or (config_module.GEMINI_API_KEY and config_module.GEMINI_API_KEY.strip()))
                
                # Check if setup is complete
                setup_complete = cred_exists and api_key_exists
                
                if setup_complete:
                    # All credentials and API key are available - exit setup loop
                    break
                
                # If user closed the window, exit immediately
                if self.close_requested or not self.setup_in_progress:
                    return
                
                # Setup is not complete - show setup screen (user cannot skip)
                self._setup_screen = SetupScreen(self, is_change_mode=False)
                self.wait_window(self._setup_screen)
                
                # Check again if user closed the window while setup was showing
                if self.close_requested or not self.setup_in_progress:
                    return
                
                # After setup closes, reload .env and config to pick up new values
                try:
                    # Reload dotenv to pick up new .env file
                    load_dotenv(env_file_path, override=True)
                    
                    # Reload config module to get updated values
                    if 'config' in sys.modules:
                        importlib.reload(sys.modules['config'])
                        config_module = sys.modules['config']
                    
                    # Update the global GEMINI_API_KEY from reloaded config
                    globals()['GEMINI_API_KEY'] = config_module.GEMINI_API_KEY
                except Exception as e:
                    pass
                
                # Loop back to check if setup was completed successfully
                # If user cancelled without saving, the loop will show the setup screen again
        except Exception as e:
            # Silently fail - setup may have been cancelled
            pass
    
    def get_service(self):
        creds = load_credentials()
        if creds:
            return build('gmail', 'v1', credentials=creds)
        return None
    
    def open_change_credentials(self):
        """Open the setup screen to change credentials and API key"""
        # Get current credentials to pre-fill the form
        app_data_path = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "ai-email-summarizer"
        env_file_path = app_data_path / ".env"
        
        # Get current API key
        from dotenv import dotenv_values
        env_vars = dotenv_values(env_file_path) if env_file_path.exists() else {}
        current_api_key = env_vars.get('GEMINI_API_KEY', '') or config.GEMINI_API_KEY
        
        # Get current credentials file
        current_creds_file = None
        if app_data_path.exists():
            for file in app_data_path.glob('*.json'):
                if file.is_file():
                    current_creds_file = str(file)
                    break
        
        # Open setup screen with previous credentials pre-filled
        setup_screen = SetupScreen(self, is_change_mode=True, previous_api_key=current_api_key, previous_creds_file=current_creds_file)
        self.wait_window(setup_screen)
        
        # Check if user actually made changes (flag is set to True only when changes are saved)
        if setup_screen.changes_made:
            # User saved changes - reload config
            try:
                app_data_path = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "ai-email-summarizer"
                env_file_path = app_data_path / ".env"
                
                from dotenv import load_dotenv
                load_dotenv(env_file_path, override=True)
                
                # Reload config module
                import importlib
                importlib.reload(config)
                
                # Ask if they want to logout to apply new credentials
                response = messagebox.askyesno(
                    "✓ Credentials Updated",
                    "✓ Credentials updated successfully!\n\n"
                    "Do you want to logout now to use the new credentials?\n"
                    "(You'll need to login again with the updated credentials)"
                )
                if response:
                    self.logout(skip_confirm=True)  # Skip double confirmation
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update credentials: {str(e)}")
        # If user skipped or closed without saving, do nothing
    
    def login(self):
        """Start login process in background thread to prevent UI freezing"""
        # Disable login button to prevent multiple clicks
        self.login_btn.configure(state="disabled", text="🔄 Logging in...")
        
        # Run login in background thread
        thread = threading.Thread(target=self._login_thread, daemon=True)
        thread.start()
        # Start a watchdog in case the OAuth browser is closed and the flow blocks
        try:
            # clear previous watchdog if exists
            if hasattr(self, "_login_watchdog_id") and self._login_watchdog_id:
                self.after_cancel(self._login_watchdog_id)
        except Exception:
            pass
        # Use short watchdogs to quickly detect if browser closes without successful login
        try:
            if hasattr(self, "_login_watchdog_id") and self._login_watchdog_id:
                self.after_cancel(self._login_watchdog_id)
        except Exception:
            pass
        # primary watchdog (30s) -- quick detection if browser closes
        self._login_watchdog_id = self.after(30000, self._login_watchdog)
        try:
            if hasattr(self, "_login_fallback_id") and self._login_fallback_id:
                self.after_cancel(self._login_fallback_id)
        except Exception:
            pass
        # fallback watchdog (60s) -- final safety net
        self._login_fallback_id = self.after(60000, self._login_watchdog)
    
    def _login_thread(self):
        """Background thread for OAuth login flow"""
        success = False
        try:
            # Resolve credentials path: prefer AppData (any valid OAuth JSON), then config, then local
            app_data_path = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "ai-email-summarizer"
            cred_path = None
            
            # Try to find any valid OAuth credentials file in AppData
            if app_data_path.exists():
                for file in app_data_path.glob('*.json'):
                    if file.is_file():
                        try:
                            with open(file, 'r') as f:
                                data = json.load(f)
                                if 'installed' in data or 'web' in data:
                                    cred_path = str(file)
                                    break
                        except Exception:
                            continue
            
            # Fallback: check config path
            if not cred_path and os.path.exists(config.GMAIL_CREDENTIALS_FILE):
                cred_path = config.GMAIL_CREDENTIALS_FILE
            
            # Fallback: check current directory
            if not cred_path and os.path.exists('credentials.json'):
                cred_path = 'credentials.json'
            
            if not cred_path:
                # Show setup screen on main thread
                self.after(0, self._show_setup_for_missing_credentials)
                return
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
                # Use custom, short-lived local server to capture auth code (non-blocking)
                # Loop with short 5s checks to detect callback quickly OR browser closure instantly
                creds = self._fetch_credentials_via_local_server(flow, timeout=5)

                if creds is None:
                    # Login did not complete within the wait window; likely the browser window
                    # was closed or the user cancelled. Prompt the user to retry or cancel.
                    self.after(0, self._prompt_login_not_completed)
                    return

                save_credentials(creds)
                self.after(0, self.check_login_status)
                self.after(0, lambda: messagebox.showinfo("Success", "✓ Login successful!"))
                success = True
            except (KeyboardInterrupt, SystemExit):
                # User cancelled via Ctrl+C or closed window
                self.after(0, lambda: messagebox.showwarning("Login Cancelled", "⚠️ Login was cancelled."))
                return
            except Exception as oauth_error:
                error_str = str(oauth_error).lower()
                # Handle user cancellation or browser close - catch common patterns
                if any(x in error_str for x in ["expecting value", "json", "eoferror", "invalid_request", "connection", "cancelled", "abort", "timeout"]):
                    self.after(0, lambda: messagebox.showwarning("Login Cancelled", "⚠️ Login was cancelled. Please try again and select your Google account."))
                    return
                else:
                    raise
                    
        except FileNotFoundError:
            self.after(0, lambda: messagebox.showerror(
                "credentials.json Error",
                "❌ credentials.json file not found!\n\n"
                "Please follow the setup guide in SETUP_GUIDE.md"
            ))
        except Exception as e:
            error_msg = str(e)
            if "credentials.json" in error_msg or "not found" in error_msg.lower():
                self.after(0, lambda: messagebox.showerror(
                    "Missing credentials.json",
                    "❌ credentials.json not found!\n\n"
                    "See SETUP_GUIDE.md for instructions."
                ))
            else:
                self.after(0, lambda msg=error_msg: messagebox.showerror("Login Error", f"Login failed: {msg}"))
        finally:
            # Always reset login button if login didn't succeed
            if not success:
                self.after(0, lambda: self.login_btn.configure(state="normal", text="🔓 Login"))
            else:
                # If login succeeded, cancel watchdog if present
                try:
                    if hasattr(self, "_login_watchdog_id") and self._login_watchdog_id:
                        self.after_cancel(self._login_watchdog_id)
                        self._login_watchdog_id = None
                except Exception:
                    pass

    def _login_watchdog(self):
        """Reset login UI if OAuth flow hasn't completed in time."""
        try:
            # If login button still shows logging-in state, reset it
            if getattr(self, 'login_btn', None):
                try:
                    # Force-reset regardless of current text/state
                    self.login_btn.configure(state="normal", text="🔓 Login", fg_color=COLOR_ACCENT, hover_color="#2D8E47")
                except Exception:
                    try:
                        self.login_btn.configure(state="normal", text="🔓 Login")
                    except Exception:
                        pass
                # Provide a non-modal status update so the user isn't interrupted
                try:
                    self.after(50, lambda: self.progress_label.configure(text="⚠️ Login in progress — waiting for browser to complete."))
                    self.after(50, lambda: self.status_label.configure(text="✗ Login pending in browser"))
                except Exception:
                    pass
        finally:
            try:
                # clear watchdog ids
                if hasattr(self, '_login_watchdog_id'):
                    self._login_watchdog_id = None
                if hasattr(self, '_login_fallback_id'):
                    self._login_fallback_id = None
            except Exception:
                pass

    def _fetch_credentials_via_local_server(self, flow, timeout=5):
        """OAuth flow with modal monitoring window.
        
        Opens browser for OAuth, shows modal that monitors for completion,
        detects when user successfully logs in or cancels.
        
        Returns credentials on success, or None on cancel/timeout.
        """
        # Define a simple handler to capture the GET with code
        class _OAuthHandler(BaseHTTPRequestHandler):
            def do_GET(self_inner):
                params = parse_qs(urlparse(self_inner.path).query)
                # store params on server
                self_inner.server.auth_params = params
                # respond with simple page
                try:
                    self_inner.send_response(200)
                    self_inner.send_header('Content-type', 'text/html; charset=utf-8')
                    self_inner.end_headers()
                    response_html = """
                    <html>
                    <head><title>AI Email Summarizer Pro - Login Complete</title></head>
                    <body style="font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                        <div style="text-align: center; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <h2 style="color: #333; margin-top: 0;">\u2713 Login Successful!</h2>
                            <p style="color: #666; font-size: 16px;">You can safely close this window and return to the app.</p>
                            <p style="color: #999; font-size: 14px;">The app will now load your emails.</p>
                        </div>
                    </body>
                    </html>
                    """
                    try:
                        self_inner.wfile.write(response_html.encode('utf-8'))
                    except Exception:
                        pass
                except Exception:
                    pass
            def log_message(self_inner, format, *args):
                return

        # Start server on an ephemeral port
        try:
            server = HTTPServer(('localhost', 0), _OAuthHandler)
        except Exception:
            return None

        port = server.server_port
        # Set redirect URI for the flow
        redirect_uri = f'http://localhost:{port}/'
        flow.redirect_uri = redirect_uri

        try:
            auth_url, _ = flow.authorization_url(prompt='consent')
        except Exception:
            return None

        # Open browser for initial auth URL
        browser_opened = False
        try:
            # Try to open in existing browser window/tab
            webbrowser.open(auth_url, new=0)
            browser_opened = True
        except Exception:
            try:
                # Fallback: open in new window if new=0 fails
                webbrowser.open(auth_url, new=1)
                browser_opened = True
            except Exception:
                pass

        # Callback function for monitor window to check login completion
        auth_params_holder = {'params': None}
        def check_login_completion():
            """Check if OAuth callback received"""
            try:
                server.timeout = 0.5  # Non-blocking check
                server.handle_request()
            except Exception:
                pass
            
            params = getattr(server, 'auth_params', None)
            if params:
                auth_params_holder['params'] = params
                return True
            return False

        # Show modal window while monitoring for login
        monitor_window = LoginMonitorWindow(self, check_login_completion)
        monitor_window.auth_url = auth_url  # Store for retry
        self.wait_window(monitor_window)

        # Check if user wants to retry
        if hasattr(monitor_window, 'need_retry') and monitor_window.need_retry:
            # Close server and restart the whole flow
            try:
                server.server_close()
            except Exception:
                pass
            # Recursively call to retry
            return self._fetch_credentials_via_local_server(flow, timeout)

        try:
            server.server_close()
        except Exception:
            pass

        params = auth_params_holder.get('params')
        if not params:
            # No callback received = login cancelled, browser closed, or failed
            return None

        code = None
        if 'code' in params:
            code = params['code'][0]
        elif 'error' in params:
            return None

        if not code:
            return None

        # Fetch token using the obtained code
        try:
            flow.fetch_token(code=code)
            return flow.credentials
        except Exception:
            return None
    
    def _show_setup_for_missing_credentials(self):
        """Show setup screen when credentials are missing (called from main thread)"""
        # Ensure UI is reset before showing setup
        try:
            self.login_btn.configure(state="normal", text="🔓 Login")
        except Exception:
            pass
        setup_screen = SetupScreen(self)
        self.wait_window(setup_screen)
        
        # After setup, try to resolve credentials again
        app_data_path = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "ai-email-summarizer"
        appdata_cred = app_data_path / "credentials.json"
        
        if appdata_cred.exists() or os.path.exists(config.GMAIL_CREDENTIALS_FILE) or os.path.exists('credentials.json'):
            # Credentials now exist, restart login
            self.login()
        else:
            messagebox.showerror(
                "Missing credentials.json",
                "❌ credentials.json not found!\n\n"
                "📋 Setup Instructions:\n"
                "1. Go to: https://console.cloud.google.com/\n"
                "2. Create a new project\n"
                "3. Enable Gmail API\n"
                "4. Create OAuth 2.0 Desktop credentials\n"
                "5. Download and save as 'credentials.json'\n"
                "6. Place the file in %APPDATA%\\ai-email-summarizer or this directory\n"
                "7. Try login again\n\n"
                "👉 See SETUP_GUIDE.md for detailed steps"
            )
            try:
                self.login_btn.configure(state="normal", text="🔓 Login")
            except Exception:
                pass

    def _prompt_login_not_completed(self):
        """Run on main thread: prompt the user when OAuth didn't complete.

        If the user chooses to retry, restart the login flow. Otherwise reset UI.
        """
        try:
            # Ask the user whether to retry login
            response = messagebox.askyesno(
                "Login Not Completed",
                "It looks like the browser window was closed or the login did not complete.\n\nDo you want to retry login now?"
            )
            if response:
                # Give a short delay to allow UI to reset, then restart login
                try:
                    self.login_btn.configure(state="normal", text="🔓 Login")
                except Exception:
                    pass
                # Start login again
                self.login()
            else:
                # Reset UI and status
                try:
                    self.login_btn.configure(state="normal", text="🔓 Login")
                except Exception:
                    pass
                self.status_label.configure(text="✗ Not logged in")
                if getattr(self, 'status_icon', None):
                    self.status_icon.configure(text="🔴")
        except Exception:
            # Fallback: reset UI
            try:
                self.login_btn.configure(state="normal", text="🔓 Login")
            except Exception:
                pass
            try:
                self.status_label.configure(text="✗ Not logged in")
                if getattr(self, 'status_icon', None):
                    self.status_icon.configure(text="🔴")
            except Exception:
                pass
    
    def logout(self, skip_confirm=False):
        """Logout and delete session token
        
        Args:
            skip_confirm: If True, logout without asking confirmation (used when changing credentials)
        """
        if skip_confirm or messagebox.askyesno("Confirm Logout", "Logout and delete cached session token?"):
            delete_credentials()
            self.check_login_status()
            self.clear_emails()
            if not skip_confirm:
                messagebox.showinfo("Success", "✓ Logged out")
    
    def toggle_theme(self):
        """Toggle between dark and light theme"""
        try:
            # Update all widgets with new colors
            self.update_widget_colors()
            self.update_idletasks()
        except Exception as e:
            messagebox.showerror("Error", f"Theme toggle failed: {e}")
    
    def update_widget_colors(self):
        """Update all widgets with current theme colors"""
        try:
            # Update main backgrounds
            self.configure(fg_color=CURRENT_COLORS["bg"])
            
            # Update all frames recursively
            def update_frames(widget):
                if hasattr(widget, 'configure'):
                    try:
                        if 'fg_color' in widget.configure():
                            widget.configure(fg_color=CURRENT_COLORS["surface"])
                    except:
                        pass
                    try:
                        if 'text_color' in widget.configure():
                            widget.configure(text_color=CURRENT_COLORS["text"])
                    except:
                        pass
                for child in widget.winfo_children():
                    update_frames(child)
            
            update_frames(self)
        except Exception as e:
            pass  # Silently fail if update doesn't work
    
    def _handle_missing_api_key_on_load(self):
        """Handle missing API key when user tries to load emails - open credentials setup"""
        response = messagebox.askyesno(
            "❌ Missing API Key",
            "Cannot load emails without a valid Gemini API key.\n\n"
            "Do you want to add your API key now?"
        )
        if response:
            self.open_change_credentials()
    
    def clear_emails(self):
        for widget in self.email_list_frame.winfo_children():
            widget.destroy()
        self.email_items = []
        self.email_data.clear()
        self.selected_email_id = None
        self.summary_text.configure(state="normal", cursor="")
        self.summary_text.delete("1.0", "end")
        self.summary_text.configure(state="disabled")
        self.subject_label.configure(text="No email selected")
        self.from_label.configure(text="No email selected")
        self.email_count_display.configure(text="0 emails")
    
    def load_emails_thread(self):
        thread = threading.Thread(target=self.load_emails, daemon=True)
        thread.start()
    
    def load_emails(self):
        try:
            # Check if API key is available BEFORE loading emails
            # Priority: AppData/.env (most recent), then config module (fallback)
            current_api_key = ""
            try:
                app_data_path = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "ai-email-summarizer"
                env_file_path = app_data_path / ".env"
                if env_file_path.exists():
                    from dotenv import dotenv_values
                    env_vars = dotenv_values(env_file_path)
                    current_api_key = env_vars.get('GEMINI_API_KEY', '').strip()
            except Exception:
                pass
            
            # Fallback to config if not found in AppData
            if not current_api_key:
                current_api_key = config.GEMINI_API_KEY.strip() if config.GEMINI_API_KEY else ""
            
            if not current_api_key:
                # API key is missing - show credentials setup screen instead of just an error
                self.after(0, lambda: self._handle_missing_api_key_on_load())
                self.load_btn.configure(state="normal", text="📧 Load Emails")
                return
            
            self.load_btn.configure(state="disabled", text="⏳ Loading emails...")
            self.max_emails = int(self.email_count_var.get())
            
            self.progress_label.configure(text="⏳ Fetching emails from Gmail...")
            self.progress_bar.set(0)
            self.update()
            
            self.clear_emails()
            
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['INBOX'],
                q="category:primary",
                maxResults=self.max_emails
            ).execute()
            
            self.emails = results.get('messages', [])
            
            if not self.emails:
                self.progress_label.configure(text="✓ No emails found in Primary")
                messagebox.showinfo("Info", "No emails found in Primary inbox")
                self.load_btn.configure(state="normal")
                return
            
            # Load email metadata without summarizing
            for idx, email in enumerate(self.emails):
                msg_id = email['id']
                subject, sender = get_email_subject(self.service, msg_id)
                body = get_email_body_raw(self.service, msg_id)
                
                self.email_data[msg_id] = {
                    'subject': subject,
                    'sender': sender,
                    'body': body,
                    'summary': None
                }
                
                # Add to UI
                item = EmailListItem(
                    self.email_list_frame,
                    subject=subject,
                    sender=sender,
                    command=lambda eid=msg_id: self.select_email(eid),
                    fg_color=COLOR_SURFACE,
                    height=65
                )
                item.pack(fill="x", padx=2, pady=2)
                self.email_items.append((msg_id, item))
                
                self.progress_bar.set((idx + 1) / len(self.emails))
                self.update()
            
            self.email_count_display.configure(text=f"{len(self.emails)} email{'s' if len(self.emails) != 1 else ''}")
            self.progress_bar.set(1.0)
            
            # If toggle is ON, summarize all emails FIRST before showing anything
            if self.summarize_on_load.get():
                self.progress_label.configure(text="⏳ Summarizing all emails...")
                self._summarize_all_emails()  # Run synchronously to wait for completion
            else:
                self.progress_label.configure(text="✓ Emails loaded. Click to summarize.")
            
            messagebox.showinfo("Success", f"✓ Loaded {len(self.emails)} emails")
            
            if self.emails:
                self.select_email(self.emails[0]['id'])
        
        except Exception as e:
            self.progress_label.configure(text=f"✗ Error: {str(e)[:40]}")
            messagebox.showerror("Error", f"Failed to load emails: {str(e)}")
        
        finally:
            self.load_btn.configure(state="normal", text="📧 Load Emails")
    
    def select_email(self, email_id):
        # Deselect previous
        if self.selected_email_id:
            for msg_id, item in self.email_items:
                if msg_id == self.selected_email_id:
                    item.deselect()
        
        self.selected_email_id = email_id
        
        # Apply selected styling to the clicked item
        for msg_id, item in self.email_items:
            if msg_id == email_id:
                item.apply_selection_style()
                break
        
        data = self.email_data.get(email_id)
        
        if data:
            self.subject_label.configure(text=data['subject'])
            self.from_label.configure(text=data['sender'])
            
            # If summary not yet generated, generate it
            if data['summary'] is None:
                self.summary_text.configure(state="normal", cursor="")
                self.summary_text.delete("1.0", "end")
                self.summary_text.insert("1.0", "⏳ Generating summary...\n\nPlease wait a few seconds for AI to process your email.")
                self.summary_text.configure(state="disabled")
                self.update()
                
                # Generate summary in background
                thread = threading.Thread(
                    target=self._generate_summary,
                    args=(email_id, data['body']),
                    daemon=True
                )
                thread.start()
            else:
                self.summary_text.configure(state="normal", cursor="xterm")
                self.summary_text.delete("1.0", "end")
                self.summary_text.insert_markdown("1.0", data['summary'])
                self.summary_text.configure(state="disabled")

    def _summarize_all_emails(self):
        """Summarize all loaded emails in PARALLEL when toggle is ON"""
        try:
            self.progress_label.configure(text="⏳ Summarizing all emails in parallel...")
            total = len(self.emails)
            completed = [0]  # Use list to allow modification in nested function
            
            def summarize_one(email_entry):
                """Summarize one email"""
                try:
                    msg_id = email_entry['id']
                    data = self.email_data.get(msg_id)
                    
                    if data and data['summary'] is None:
                        summary = gemini_summarize_and_reply(data['body'])
                        self.email_data[msg_id]['summary'] = summary
                    
                    # Update progress
                    completed[0] += 1
                    self.progress_bar.set(completed[0] / total)
                    self.progress_label.configure(text=f"⏳ Summarizing ({completed[0]}/{total})...")
                    self.update_idletasks()
                    
                except Exception as e:
                    msg_id = email_entry.get('id', 'unknown')
                    self.email_data[msg_id]['summary'] = f"Error: {str(e)}"
            
            # Use ThreadPoolExecutor to run 4 summaries in parallel
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(summarize_one, email) for email in self.emails]
                # Wait for all to complete
                for future in futures:
                    future.result()
            
            self.progress_label.configure(text="✓ All summaries ready!")
            # Refresh current selection to show cached summary
            if self.selected_email_id:
                data = self.email_data.get(self.selected_email_id)
                if data and data['summary']:
                    self.summary_text.configure(state="normal", cursor="xterm")
                    self.summary_text.delete("1.0", "end")
                    self.summary_text.insert_markdown("1.0", data['summary'])
                    self.summary_text.configure(state="disabled")
        except Exception as e:
            self.progress_label.configure(text=f"✗ Error summarizing: {str(e)[:40]}")

    def _generate_summary(self, email_id, body):
        try:
            summary = gemini_summarize_and_reply(body)
            self.email_data[email_id]['summary'] = summary
            
            # Update UI if still selected
            if self.selected_email_id == email_id:
                self.summary_text.configure(state="normal", cursor="xterm")
                self.summary_text.delete("1.0", "end")
                self.summary_text.insert_markdown("1.0", summary)
                self.summary_text.configure(state="disabled")
        except Exception as e:
            error_msg = f"Error generating summary: {str(e)}"
            if self.selected_email_id == email_id:
                self.summary_text.configure(state="normal", cursor="")
                self.summary_text.delete("1.0", "end")
                self.summary_text.insert("1.0", error_msg)
                self.summary_text.configure(state="disabled")

# ========== RUN APP ==========
if __name__ == "__main__":
    app = EmailSummarizerApp()
    app.mainloop()
