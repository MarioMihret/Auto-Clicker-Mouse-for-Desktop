"""
Browser Automation Module - Controls multiple browser instances independently
Provides both scripted automation and interactive position-based clicking
"""

# Import key components for easier access
from .browser_controller import BrowserController, BrowserType, TaskAction
from .interactive import setup_interactive_browser, perform_click_at_coordinates, cleanup_interactive_browser 