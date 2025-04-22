"""
Status Panel component - Displays the current status of the autoclicker
"""

import tkinter as tk
import customtkinter as ctk
import logging

logger = logging.getLogger(__name__)

class StatusPanel:
    """
    Panel that displays the current status of the autoclicker (running/stopped)
    """
    def __init__(self, parent):
        """
        Initialize the status panel
        
        Args:
            parent: Parent frame to place this panel in
        """
        self.parent = parent
        
        # Create frame
        self.frame = ctk.CTkFrame(parent)
        
        # Configure grid layout
        self.frame.grid_columnconfigure(0, weight=0)  # Label has fixed width
        self.frame.grid_columnconfigure(1, weight=0)  # Status indicator has fixed width
        self.frame.grid_columnconfigure(2, weight=1)  # Empty expandable column
        
        # Create status label and indicator
        status_label = ctk.CTkLabel(self.frame, text="Status:")
        status_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.status_indicator = ctk.CTkLabel(
            self.frame,
            text="Stopped",
            text_color="red"
        )
        self.status_indicator.grid(row=0, column=1, pady=5, sticky="w")
        
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
        
    def set_status(self, is_running):
        """
        Update the status indicator
        
        Args:
            is_running: Whether the autoclicker is running
        """
        if is_running:
            self.status_indicator.configure(text="Running", text_color="green")
        else:
            self.status_indicator.configure(text="Stopped", text_color="red") 