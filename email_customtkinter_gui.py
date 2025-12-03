import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
from concurrent.futures import ThreadPoolExecutor
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import requests
import base64
import re
from html.parser import HTMLParser

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
        
        # Use standard fonts for styling
        base_font = ("Segoe UI", 11)
        bold_font = ("Segoe UI", 11, "bold")
        italic_font = ("Segoe UI", 11, "italic")
        bold_italic_font = ("Segoe UI", 11, "bold", "italic")
        code_font = ("Courier New", 10)
        heading_font = ("Segoe UI", 12, "bold")
        
        # Configure tags for markdown rendering with ACTUAL STYLES
        self._text_widget.tag_config("bold", font=bold_font)
        self._text_widget.tag_config("italic", font=italic_font)
        self._text_widget.tag_config("bold_italic", font=bold_italic_font)
        
        # Code - monospace font with background
        self._text_widget.tag_config("code", 
                                     font=code_font,
                                     foreground="#C2185B",
                                     background="#F5F5F5")
        
        # Headings - bold + blue color
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
            # Insert text before match
            if match.start() > last_end:
                self._text_widget.insert(index, text[last_end:match.start()])
            
            if match.group(2):  # ***bold italic***
                self._text_widget.insert(index, match.group(2), 'bold_italic')
            elif match.group(4):  # **bold**
                self._text_widget.insert(index, match.group(4), 'bold')
            elif match.group(6):  # *italic*
                self._text_widget.insert(index, match.group(6), 'italic')
            elif match.group(8):  # `code`
                self._text_widget.insert(index, match.group(8), 'code')
            
            last_end = match.end()
        
        # Insert remaining text
        if last_end < len(text):
            self._text_widget.insert(index, text[last_end:])

# Colors - Modern Professional Palette
COLOR_PRIMARY = "#1A73E8"
COLOR_PRIMARY_DARK = "#1565C0"
COLOR_PRIMARY_LIGHT = "#E8F0FE"  # Light variant for selected state
COLOR_ACCENT = "#34A853"
COLOR_WARNING = "#FBBC04"
COLOR_ERROR = "#EA4335"
COLOR_BG = "#FFFFFF"
COLOR_SURFACE = "#F8F9FA"
COLOR_SURFACE_DARK = "#E8EAED"
COLOR_TEXT = "#202124"
COLOR_TEXT_SECONDARY = "#5F6368"
COLOR_BORDER = "#DADCE0"

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

def get_email_body_raw(service, message_id):
    try:
        message = service.users().messages().get(userId='me', id=message_id, format='full').execute()
        
        body = ""
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html':
                    data = part['body'].get('data', '')
                    if data:
                        html_body = base64.urlsafe_b64decode(data).decode('utf-8')
                        body = strip_html_tags(html_body)
        else:
            data = message['payload']['body'].get('data', '')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body[:2000] if body else ""
    except Exception as e:
        return f"Error reading email: {str(e)}"

def get_email_subject(service, message_id):
    try:
        message = service.users().messages().get(userId='me', id=message_id, format='metadata').execute()
        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
        sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown")
        return subject, sender
    except Exception as e:
        return "Error", str(e)

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
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY
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
        
        response = requests.post(GEMINI_ENDPOINT, headers=headers, json=payload)
        
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
        self.sender_label_ref.configure(text_color=COLOR_TEXT_SECONDARY)

# ========== MAIN APP ==========
ctk.set_appearance_mode("light")

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
        
        self.create_widgets()
        self.check_login_status()
    
    def create_widgets(self):
        # ===== HEADER =====
        header = ctk.CTkFrame(self, fg_color=COLOR_PRIMARY, height=85, corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header, fg_color=COLOR_PRIMARY)
        header_content.pack(fill="both", expand=True, padx=30, pady=15)
        
        left_header = ctk.CTkFrame(header_content, fg_color=COLOR_PRIMARY)
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
        
        right_header = ctk.CTkFrame(header_content, fg_color=COLOR_PRIMARY)
        right_header.pack(side="right", fill="y")
        
        self.status_icon = ctk.CTkLabel(
            right_header,
            text="🔴",
            font=("Segoe UI", FONT_ICON),
            text_color="#FFFFFF"
        )
        self.status_icon.pack(pady=(3, 0))
        
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
            font=("Segoe UI", FONT_XS, "bold"),
            text_color=COLOR_TEXT_SECONDARY
        )
        subj_title.pack(anchor="w", pady=(0, 2))
        
        self.subject_label = ctk.CTkLabel(
            info_frame,
            text="No email selected",
            font=("Segoe UI", FONT_MD),
            text_color=COLOR_TEXT,
            wraplength=500,
            justify="left"
        )
        self.subject_label.pack(anchor="w", pady=(0, 10))
        
        from_title = ctk.CTkLabel(
            info_frame,
            text="From:",
            font=("Segoe UI", FONT_LG, "bold"),
            text_color=COLOR_TEXT_SECONDARY
        )
        from_title.pack(anchor="w", pady=(0, 2))
        
        self.from_label = ctk.CTkLabel(
            info_frame,
            text="No email selected",
            font=("Segoe UI", FONT_LG),
            text_color=COLOR_PRIMARY,
            wraplength=500,
            justify="left"
        )
        self.from_label.pack(anchor="w")
        
        divider = ctk.CTkFrame(right_panel, fg_color=COLOR_BORDER, height=1)
        divider.pack(fill="x", padx=16, pady=10)
        
        # Summary text - now with markdown support
        self.summary_text = MarkdownTextWidget(
            right_panel,
            font=("Segoe UI", FONT_MD),
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
        if is_logged_in():
            self.status_label.configure(text="✓ Logged in - Ready to load emails")
            self.status_icon.configure(text="🟢")
            self.login_btn.configure(state="disabled", fg_color="#CCCCCC", hover_color="#CCCCCC")
            self.load_btn.configure(state="normal", fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_DARK)
            self.logout_btn.configure(state="normal", fg_color=COLOR_ERROR, hover_color="#C5221F")
            self.service = self.get_service()
        else:
            self.status_label.configure(text="✗ Not logged in")
            self.status_icon.configure(text="🔴")
            self.login_btn.configure(state="normal", fg_color=COLOR_ACCENT, hover_color="#2D8E47")
            self.load_btn.configure(state="disabled", fg_color="#CCCCCC", hover_color="#CCCCCC")
            self.logout_btn.configure(state="disabled", fg_color="#CCCCCC", hover_color="#CCCCCC")
    
    def get_service(self):
        creds = load_credentials()
        if creds:
            return build('gmail', 'v1', credentials=creds)
        return None
    
    def login(self):
        try:
            # Check if credentials.json exists
            if not os.path.exists('credentials.json'):
                messagebox.showerror(
                    "Missing credentials.json",
                    "❌ credentials.json not found!\n\n"
                    "📋 Setup Instructions:\n"
                    "1. Go to: https://console.cloud.google.com/\n"
                    "2. Create a new project\n"
                    "3. Enable Gmail API\n"
                    "4. Create OAuth 2.0 Desktop credentials\n"
                    "5. Download and save as 'credentials.json'\n"
                    "6. Place the file in this directory\n"
                    "7. Try login again\n\n"
                    "👉 See SETUP_GUIDE.md for detailed steps"
                )
                return
            
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            save_credentials(creds)
            self.check_login_status()
            messagebox.showinfo("Success", "✓ Login successful!")
        except FileNotFoundError:
            messagebox.showerror(
                "credentials.json Error",
                "❌ credentials.json file not found!\n\n"
                "Please follow the setup guide in SETUP_GUIDE.md"
            )
        except Exception as e:
            error_msg = str(e)
            if "credentials.json" in error_msg or "not found" in error_msg.lower():
                messagebox.showerror(
                    "Missing credentials.json",
                    "❌ credentials.json not found!\n\n"
                    "See SETUP_GUIDE.md for instructions."
                )
            else:
                messagebox.showerror("Login Error", f"Login failed: {error_msg}")
    
    def logout(self):
        if messagebox.askyesno("Confirm Logout", "Logout and delete cached credentials?"):
            delete_credentials()
            self.check_login_status()
            self.clear_emails()
            messagebox.showinfo("Success", "✓ Logged out")
    
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
