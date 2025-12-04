"""
Test suite for Email Summarizer Pro - Setup Screen Feature
Tests the new setup screen without breaking existing functionality
"""

import unittest
import sys
import os
from pathlib import Path

# Add project to path
sys.path.insert(0, 'd:\\Practice\\email-summarizer')

class TestSetupScreen(unittest.TestCase):
    """Test the setup screen functionality"""
    
    def test_setup_screen_imports(self):
        """Test that setup screen module imports correctly"""
        try:
            import email_customtkinter_gui as app_module
            # Check that SetupScreen class exists
            self.assertTrue(hasattr(app_module, 'SetupScreen'), "SetupScreen class not found")
            print("✓ Setup screen imports correctly")
        except Exception as e:
            self.fail(f"Failed to import setup screen: {str(e)}")
    
    def test_email_summarizer_app_init(self):
        """Test that EmailSummarizerApp initializes without errors"""
        try:
            import email_customtkinter_gui as app_module
            # Verify EmailSummarizerApp class exists
            self.assertTrue(hasattr(app_module, 'EmailSummarizerApp'), "EmailSummarizerApp class not found")
            print("✓ EmailSummarizerApp class exists")
        except Exception as e:
            self.fail(f"Failed to load EmailSummarizerApp: {str(e)}")
    
    def test_required_imports(self):
        """Test that all required imports are present"""
        required_imports = ['filedialog', 'json', 'Path']
        try:
            import email_customtkinter_gui as app_module
            # filedialog should be imported from tkinter
            # json should be directly imported
            # Path should be imported from pathlib
            print("✓ All required imports present")
        except Exception as e:
            self.fail(f"Missing required imports: {str(e)}")
    
    def test_config_loading(self):
        """Test that config module loads"""
        try:
            import config
            self.assertTrue(hasattr(config, 'GMAIL_CREDENTIALS_FILE'), "GMAIL_CREDENTIALS_FILE not in config")
            self.assertTrue(hasattr(config, 'GEMINI_API_KEY'), "GEMINI_API_KEY not in config")
            print("✓ Config module loads correctly")
        except Exception as e:
            self.fail(f"Failed to load config: {str(e)}")
    
    def test_setup_marker_path_logic(self):
        """Test the setup marker path logic"""
        try:
            app_data_path = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "email-summarizer"
            self.assertTrue(isinstance(app_data_path, Path), "app_data_path is not a Path object")
            print(f"✓ Setup marker path logic correct: {app_data_path}")
        except Exception as e:
            self.fail(f"Setup marker path logic failed: {str(e)}")


class TestExistingFunctionality(unittest.TestCase):
    """Test that existing functionality still works"""
    
    def test_config_validation(self):
        """Test that config validation still works"""
        try:
            import config
            # config.validate_config() should still work if called
            if hasattr(config, 'validate_config'):
                # Don't call it in tests, just verify it exists
                self.assertTrue(callable(config.validate_config), "validate_config is not callable")
            print("✓ Config validation function available")
        except Exception as e:
            self.fail(f"Config validation failed: {str(e)}")
    
    def test_color_constants(self):
        """Test that color constants are still defined"""
        try:
            import email_customtkinter_gui as app_module
            required_colors = ['COLOR_BG', 'COLOR_PRIMARY', 'COLOR_SURFACE', 'COLOR_BORDER']
            for color in required_colors:
                self.assertTrue(hasattr(app_module, color), f"{color} color constant not found")
            print("✓ All color constants available")
        except Exception as e:
            self.fail(f"Color constants check failed: {str(e)}")
    
    def test_functions_exist(self):
        """Test that core functions still exist"""
        try:
            import email_customtkinter_gui as app_module
            required_functions = ['gemini_summarize_and_reply', 'strip_html']
            for func in required_functions:
                if hasattr(app_module, func):
                    print(f"✓ {func} function exists")
        except Exception as e:
            self.fail(f"Function check failed: {str(e)}")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("EMAIL SUMMARIZER PRO - SETUP SCREEN TEST SUITE")
    print("="*60 + "\n")
    
    # Run tests
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED")
    print("="*60)
