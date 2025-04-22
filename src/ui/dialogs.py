"""
Dialogs - UI dialog windows for the application
"""

import tkinter as tk
import customtkinter as ctk
import logging

# Configure logging
logger = logging.getLogger(__name__)

class AboutDialog:
    """
    About dialog window showing application information
    """
    def __init__(self, parent):
        """
        Initialize the about dialog
        
        Args:
            parent: Parent window
        """
        self.parent = parent
        
        # Create dialog window
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("About AutoClicker")
        self.dialog.geometry("400x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Make dialog modal
        self.dialog.focus_set()
        
        # App title
        title_label = ctk.CTkLabel(
            self.dialog,
            text="AutoClicker",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Version
        version_label = ctk.CTkLabel(
            self.dialog,
            text="Version 1.0.0",
            font=ctk.CTkFont(size=12)
        )
        version_label.pack(pady=5)
        
        # Description
        desc_label = ctk.CTkLabel(
            self.dialog,
            text="An easy-to-use utility for automating mouse clicks\nat configurable intervals.",
            font=ctk.CTkFont(size=12),
            justify=tk.CENTER
        )
        desc_label.pack(pady=10)
        
        # Copyright
        copyright_label = ctk.CTkLabel(
            self.dialog,
            text="© 2023 Your Name",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        copyright_label.pack(pady=5)
        
        # Features
        features_frame = ctk.CTkFrame(self.dialog)
        features_frame.pack(pady=10, padx=20, fill=tk.X)
        
        features_label = ctk.CTkLabel(
            features_frame,
            text="Features:",
            font=ctk.CTkFont(weight="bold"),
            anchor=tk.W
        )
        features_label.pack(anchor=tk.W, pady=5)
        
        features_text = """• Configurable click intervals
• Single and double-click support
• Keyboard shortcuts"""
        
        features_desc = ctk.CTkLabel(
            features_frame,
            text=features_text,
            justify=tk.LEFT,
            anchor=tk.W
        )
        features_desc.pack(anchor=tk.W, padx=10)
        
        # Close button
        close_button = ctk.CTkButton(
            self.dialog,
            text="Close",
            command=self.close
        )
        close_button.pack(pady=20)
        
        # Wait for dialog to close
        parent.wait_window(self.dialog)
        
    def close(self) -> None:
        """
        Close the dialog
        """
        self.dialog.destroy() 