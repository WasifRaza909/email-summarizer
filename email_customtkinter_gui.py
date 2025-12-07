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
        
        # List items - default
        self._text_widget.tag_config("list_item", 
                                     foreground="#202124")
    
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

Use markdown formatting:
- Use **bold** for important points
- Use * for bullet lists
- Use ## for section headers (SUMMARY, DRAFT REPLY)
- Format your response for readability

Email:
{body}
"""
        
        # Include API key in the URL for Gemini API (read from config module)
        api_url = f"{GEMINI_ENDPOINT}?key={config.GEMINI_API_KEY}"
        
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
        subject_text = subject[:55] + "..." if len(subject) > 55 else subject
        subject_label = ctk.CTkLabel(
            content,
            text=subject_text,
            font=("Segoe UI", FONT_MD, "bold"),
            text_color=COLOR_PRIMARY,
            justify="left",
            cursor="hand2"
        )
        subject_label.pack(anchor="w", pady=(0, 6))
        subject_label.bind("<Button-1>", self._on_click)
        
        # Sender - Secondary text color with proper contrast
        sender_text = sender[:50] + "..." if len(sender) > 50 else sender
        sender_label = ctk.CTkLabel(
            content,
            text=sender_text,
            font=("Segoe UI", FONT_XS),
            text_color=COLOR_TEXT_SECONDARY,
            justify="left",
            cursor="hand2"
        )
        sender_label.pack(anchor="w")
        sender_label.bind("<Button-1>", self._on_click)
        
        self.subject_label_ref = subject_label
        self.sender_label_ref = sender_label
    
    def _on_click(self, event=None):
        self.is_selected = True
        # Material Design: Use primary color with subtle elevation
        self.main_frame.configure(fg_color=COLOR_PRIMARY_LIGHT, border_color=COLOR_PRIMARY)
        self.subject_label_ref.configure(text_color=COLOR_PRIMARY)
        self.sender_label_ref.configure(text_color=COLOR_TEXT)
        if self.command:
            self.command()

    def apply_selection_style(self):
        """Apply selection styling without triggering the command"""
        self.is_selected = True
        self.main_frame.configure(fg_color=COLOR_PRIMARY_LIGHT, border_color=COLOR_PRIMARY)
        self.subject_label_ref.configure(text_color=COLOR_PRIMARY)
        self.sender_label_ref.configure(text_color=COLOR_TEXT)

    def deselect(self):
        self.is_selected = False
        # Return to default styling
        self.main_frame.configure(fg_color=COLOR_SURFACE, border_color=COLOR_BORDER)
        self.subject_label_ref.configure(text_color=COLOR_PRIMARY)


# ========== SETUP SCREEN ==========
class SetupScreen(ctk.CTkToplevel):
    """First-time setup wizard for credentials and API keys"""
    
    def __init__(self, parent, is_change_mode=False):
        super().__init__(parent)
        self.is_change_mode = is_change_mode
        
        if is_change_mode:
            self.title("Email Summarizer Pro - Change Credentials")
        else:
            self.title("Email Summarizer Pro - Initial Setup")
        
        self.geometry("600x700")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)
        
        # Make it modal
        self.transient(parent)
        self.grab_set()
        
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
        
        self.credentials_file_path = None
        self.result = {"api_key": "", "credentials_file": None}
        
        # Handle close button (X) - prompt before closing
        self.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
        self.create_setup_ui()
    
    def on_window_close(self):
        """Handle window close button (X) - exit the program immediately"""
        self.master.quit()
        self.master.destroy()
    
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
            title_text = "🚀 Welcome to Email Summarizer Pro"
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
            text="Enter your Gemini/OpenAI API Key",
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
            text="📁 Select credentials.json",
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
        """Open file dialog to select credentials.json"""
        file_path = filedialog.askopenfilename(
            title="Select credentials.json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            initialdir=os.path.expanduser("~")
        )
        
        if file_path:
            try:
                # Validate it's a valid JSON and has expected Gmail structure
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if 'installed' in data or 'web' in data:
                        self.credentials_file_path = file_path
                        filename = os.path.basename(file_path)
                        self.file_status.configure(text=f"✓ {filename}", text_color="#4CAF50")
                        self.upload_btn.configure(text="📁 Change File")
                    else:
                        messagebox.showerror("Invalid File", "This doesn't appear to be a valid OAuth credentials file")
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
        
        # Validate API key by testing it
        self.api_entry.configure(state="disabled")
        messagebox.showinfo("Testing API Key", "Testing your API key... Please wait.")
        
        if not self.test_gemini_api_key(api_key):
            self.api_entry.configure(state="normal")
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
        
        # Everything is valid - save settings
        try:
            # Create AppData folder if it doesn't exist
            app_data_path = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "email-summarizer"
            app_data_path.mkdir(parents=True, exist_ok=True)
            
            # Save API key to .env
            env_file = app_data_path / ".env"
            with open(env_file, 'w') as f:
                f.write(f"GEMINI_API_KEY={api_key}\n")
            
            # Copy credentials file
            cred_dest = app_data_path / "credentials.json"
            with open(self.credentials_file_path, 'r') as src:
                with open(cred_dest, 'w') as dst:
                    dst.write(src.read())
            
            # Create a marker file to indicate setup is complete
            setup_marker = app_data_path / ".setup_complete"
            setup_marker.touch()
            
            # Update global config with new paths
            import config as config_module
            config_module.GMAIL_CREDENTIALS_FILE = str(cred_dest)
            config_module.GEMINI_API_KEY = api_key
            
            messagebox.showinfo(
                "✓ Setup Complete",
                "✓ Settings saved!\n\nYour credentials are stored securely on your computer.\nClick OK to continue."
            )
            self.result = {"api_key": api_key, "credentials_file": str(cred_dest)}
            self.destroy()
        
        except Exception as e:
            messagebox.showerror("❌ Save Error", f"Failed to save settings: {str(e)}")
    
    def test_gemini_api_key(self, api_key):
        """Test if the Gemini API key is valid"""
        try:
            import requests
            
            test_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            
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
                    return False
            
            # If we got here, key is likely valid
            return True
        
        except Exception as e:
            return False
    
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
        self.title("Email Summarizer Pro - Signing In")
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
        self.title("Email Summarizer Pro")
        self.geometry("1400x850")
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
        
        # Check if first-time setup is needed
        self.check_first_time_setup()
        
        self.create_widgets()
        self.check_login_status()
    
    def check_first_time_setup(self):
        """Check if credentials/API key are missing and show setup screen if needed"""
        try:
            app_data_path = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "email-summarizer"
            credentials_path = app_data_path / "credentials.json"
            env_file_path = app_data_path / ".env"
            
            # Check if credentials.json exists (prefer AppData, then project root)
            cred_exists = credentials_path.exists() or os.path.exists(config.GMAIL_CREDENTIALS_FILE)
            
            # Check if API key exists in environment (after loading .env)
            # Re-read from environment to get the most current value
            from dotenv import dotenv_values
            env_vars = dotenv_values(env_file_path) if env_file_path.exists() else {}
            api_key_from_env = env_vars.get('GEMINI_API_KEY', '').strip()
            
            # Use API key from env or from config
            api_key_exists = bool(api_key_from_env or (config.GEMINI_API_KEY and config.GEMINI_API_KEY.strip()))
            
            # Show setup only if credentials OR API key is missing
            if not cred_exists or not api_key_exists:
                setup_screen = SetupScreen(self)
                self.wait_window(setup_screen)
                
                # After setup closes, reload .env and config to pick up new values
                try:
                    from dotenv import load_dotenv
                    load_dotenv(env_file_path, override=True)
                    
                    # Reload config module to get updated values
                    import importlib
                    importlib.reload(config)
                    
                    # Update the global GEMINI_API_KEY from reloaded config
                    globals()['GEMINI_API_KEY'] = config.GEMINI_API_KEY
                except Exception:
                    pass
                
                # Refresh the login status to re-enable Load button if credentials are now valid
                self.after(100, self.check_login_status)
                
                # Schedule fullscreen state to apply after all widgets are rendered
                self.after(500, lambda: self.state("zoomed"))
        except Exception as e:
            # Silently skip if there's an error
            pass
    
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
            text="Email Summarizer Pro",
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
            wraplength=500,
            justify="left"
        )
        self.subject_label.pack(anchor="w", pady=(0, 2), padx=10)
        
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
            wraplength=500,
            justify="left"
        )
        self.from_label.pack(anchor="w", padx=10)
        
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
        # Get current API key from config (which may have been reloaded after setup)
        current_api_key = config.GEMINI_API_KEY
        
        if is_logged_in():
            self.status_label.configure(text="✓ Logged in - Ready to load emails")
            if getattr(self, 'status_icon', None):
                self.status_icon.configure(text="🟢")
            self.login_btn.configure(state="disabled", fg_color="#CCCCCC", hover_color="#CCCCCC")
            
            # Only enable load button if API key is also available
            if current_api_key and current_api_key.strip():
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
    
    def get_service(self):
        creds = load_credentials()
        if creds:
            return build('gmail', 'v1', credentials=creds)
        return None
    
    def open_change_credentials(self):
        """Open the setup screen to change credentials and API key"""
        setup_screen = SetupScreen(self, is_change_mode=True)
        self.wait_window(setup_screen)
        
        # Check if user actually saved changes (not just closed or skipped)
        if setup_screen.result.get("api_key") or setup_screen.result.get("credentials_file"):
            # User saved changes - reload config
            try:
                app_data_path = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "email-summarizer"
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
            # Resolve credentials path: prefer AppData, then config, then local
            app_data_path = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "email-summarizer"
            appdata_cred = app_data_path / "credentials.json"
            cred_path = None
            
            if appdata_cred.exists():
                cred_path = str(appdata_cred)
            elif os.path.exists(config.GMAIL_CREDENTIALS_FILE):
                cred_path = config.GMAIL_CREDENTIALS_FILE
            elif os.path.exists('credentials.json'):
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
                    self_inner.send_header('Content-type', 'text/html')
                    self_inner.end_headers()
                    self_inner.wfile.write(b"<html><body><h3>You can close this window and return to the app.</h3></body></html>")
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

        # Open browser
        try:
            webbrowser.open(auth_url)
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
        app_data_path = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "email-summarizer"
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
                "6. Place the file in %APPDATA%\\email-summarizer or this directory\n"
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
            # Check if API key is available BEFORE loading emails (read from config module, not global)
            current_api_key = config.GEMINI_API_KEY
            if not current_api_key or not current_api_key.strip():
                messagebox.showerror(
                    "❌ Missing API Key",
                    "Cannot load emails without a valid Gemini API key.\n\n"
                    "Please go to 'Change Credentials' to add your API key."
                )
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
                q="is:unread",
                maxResults=self.max_emails
            ).execute()
            
            self.emails = results.get('messages', [])
            
            if not self.emails:
                self.progress_label.configure(text="✓ No unread emails found")
                messagebox.showinfo("Info", "No unread emails found")
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
