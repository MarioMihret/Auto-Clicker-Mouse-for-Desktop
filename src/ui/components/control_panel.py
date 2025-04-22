"""
Control Panel component - Provides control buttons for the autoclicker
"""

import tkinter as tk
import customtkinter as ctk
import logging

logger = logging.getLogger(__name__)

class ControlPanel:
    """
    Panel that provides control buttons for the autoclicker
    """
    def __init__(self, parent, on_toggle, on_exit):
        """
        Initialize the control panel
        
        Args:
            parent: Parent frame to place this panel in
            on_toggle: Callback when toggle button is clicked
            on_exit: Callback when exit button is clicked
        """
        self.parent = parent
        self.on_toggle = on_toggle
        self.on_exit = on_exit
        
        # Create frame
        self.frame = ctk.CTkFrame(parent)
        
        # Configure grid layout
        self.frame.grid_columnconfigure(0, weight=1)  # Toggle button is expandable
        self.frame.grid_columnconfigure(1, weight=1)  # Exit button is expandable
        
        # Start/Stop button
        self.toggle_button = ctk.CTkButton(
            self.frame,
            text="Start (F6)",
            command=self.on_toggle,
            height=40,  # Taller button
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#28a745",  # Green color
            hover_color="#218838"  # Darker green for hover
        )
        self.toggle_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Exit button
        exit_button = ctk.CTkButton(
            self.frame,
            text="Exit (F8)",
            height=40,  # Taller button
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#dc3545",  # Red color
            hover_color="#c82333",  # Darker red for hover
            command=self.on_exit
        )
        exit_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
    def grid(self, **kwargs):
        """Grid the frame with the given arguments"""
        self.frame.grid(**kwargs)
        
    def pack(self, **kwargs):
        """Legacy pack method - converts to grid if possible"""
        # If fill is specified, convert to sticky
        sticky = ""
        if 'fill' in kwargs:
            fill = kwargs.pop('fill')
            if fill == tk.X or fill == 'x':
                sticky = "ew"
            elif fill == tk.Y or fill == 'y':
                sticky = "ns"
            elif fill == tk.BOTH or fill == 'both':
                sticky = "nsew"
        
        # Add sticky to kwargs if it was converted
        if sticky:
            kwargs['sticky'] = sticky
            
        self.frame.grid(**kwargs)
        
    def set_toggle_state(self, is_running):
        """
        Update the toggle button state
        
        Args:
            is_running: Whether the autoclicker is running
        """
        if is_running:
            self.toggle_button.configure(text="Stop (F6)")
        else:
            self.toggle_button.configure(text="Start (F6)") 