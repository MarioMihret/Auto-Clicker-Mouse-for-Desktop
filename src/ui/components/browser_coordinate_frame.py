"""
Browser Coordinate Frame - UI component for displaying and controlling browser coordinates
"""

import customtkinter as ctk
from typing import Callable

class BrowserCoordinateFrame(ctk.CTkFrame):
    """Frame for displaying and controlling a single browser's coordinates"""
    
    def __init__(self, master, browser_index, **kwargs):
        super().__init__(master, **kwargs)
        self.browser_index = browser_index
        
        # Coordinate variables
        self.coordinate_var = ctk.StringVar(value="No position selected")
        self.is_active = ctk.BooleanVar(value=True)
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the browser coordinate frame UI"""
        # Use a grid layout with 2 rows to fit everything
        self.grid_columnconfigure(1, weight=1)
        
        # Row 1: Browser label and coordinate
        browser_label = ctk.CTkLabel(
            self,
            text=f"Browser {self.browser_index+1}:",
            width=100
        )
        browser_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        
        coord_label = ctk.CTkLabel(
            self,
            textvariable=self.coordinate_var,
            width=250
        )
        coord_label.grid(row=0, column=1, padx=5, pady=(10, 0), sticky="w", columnspan=3)
        
        # Row 2: Checkbox and buttons
        active_checkbox = ctk.CTkCheckBox(
            self,
            text="Active",
            variable=self.is_active,
            onvalue=True,
            offvalue=False
        )
        active_checkbox.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="w")
        
        # Select position button
        self.select_btn = ctk.CTkButton(
            self,
            text="Select Position",
            width=120,
            state="disabled"
        )
        self.select_btn.grid(row=1, column=1, padx=10, pady=(5, 10), sticky="e")
        
    def set_position(self, x, y):
        """Set the position for this browser"""
        self.coordinate_var.set(f"Position: ({x}, {y})")
        
    def set_browser_object(self, browser, on_select_callback):
        """Set the browser object for this frame"""
        if browser:
            self.select_btn.configure(
                state="normal",
                command=lambda: on_select_callback(self.browser_index)
            )
        else:
            self.select_btn.configure(state="disabled") 