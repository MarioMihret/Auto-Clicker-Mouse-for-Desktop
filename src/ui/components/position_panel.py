"""
Position Panel component - Manages position selection for the autoclicker
"""

import tkinter as tk
import customtkinter as ctk
import logging
from typing import List, Tuple, Callable

logger = logging.getLogger(__name__)

class PositionPanel(ctk.CTkFrame):
    """
    Panel that displays and manages the position selection for clicking
    """
    def __init__(self, parent, on_select_positions, on_clear_positions, on_multi_click_change=None):
        """
        Initialize the position panel
        
        Args:
            parent: Parent frame to place this panel in
            on_select_positions: Callback when select positions button is clicked
            on_clear_positions: Callback when clear positions button is clicked
            on_multi_click_change: Callback when multi-click toggle is changed
        """
        super().__init__(parent, corner_radius=10)
        
        self.on_select_positions = on_select_positions
        self.on_clear_positions = on_clear_positions
        self.on_multi_click_change = on_multi_click_change
        self.positions: List[Tuple[int, int]] = []
        
        # Use the enhanced UI setup
        self._setup_ui()
        
    def _on_select(self):
        """Handle select positions button click"""
        if self.on_select_positions:
            self.on_select_positions()
            
    def _on_clear(self):
        """Handle clear positions button click"""
        if self.on_clear_positions:
            self.on_clear_positions()
    
    def _on_multi_click_toggled(self):
        """Handle multi-click toggle change"""
        is_enabled = self.multi_click_var.get()
        if self.on_multi_click_change:
            self.on_multi_click_change(is_enabled)
            
    def set_multi_click(self, enabled):
        """Set the multi-click toggle state"""
        self.multi_click_var.set(enabled)
        
    def get_multi_click(self):
        """Get the multi-click toggle state"""
        return self.multi_click_var.get()
    
    def grid(self, **kwargs):
        """Grid the panel with the given arguments"""
        super().grid(**kwargs)
        
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
            
        super().grid(**kwargs)
        
    def set_positions(self, positions: List[Tuple[int, int]]):
        """
        Update the positions and display
        
        Args:
            positions: List of (x, y) coordinates
        """
        self.positions = positions
        
        if not positions:
            self.positions_text.configure(text="Using cursor position")
        elif len(positions) == 1:
            self.positions_text.configure(text=f"Position: ({positions[0][0]}, {positions[0][1]})")
        else:
            # Format multiple positions (limit display to first 5 for mobile)
            if len(positions) > 5:
                pos_text = f"{len(positions)} positions selected\nShowing first 5:"
                for i, (x, y) in enumerate(positions[:5]):
                    pos_text += f"\n{i+1}. ({x}, {y})"
                pos_text += f"\n... and {len(positions)-5} more"
            else:
                pos_text = f"{len(positions)} positions selected:"
                for i, (x, y) in enumerate(positions):
                    pos_text += f"\n{i+1}. ({x}, {y})"
            
            self.positions_text.configure(text=pos_text)
            
    def get_positions(self) -> List[Tuple[int, int]]:
        """
        Get the current positions
        
        Returns:
            List[Tuple[int, int]]: List of (x, y) coordinates
        """
        return self.positions

    def _setup_ui(self):
        """Set up the UI components"""
        # Main label with icon
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        
        label = ctk.CTkLabel(
            header_frame, 
            text="Click Positions", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        label.pack(side="left", padx=(0, 5))
        
        # Positions display
        self.positions_text = ctk.CTkLabel(
            self, 
            text="Using cursor position",
            font=ctk.CTkFont(size=12),
            text_color="#6c757d"
        )
        self.positions_text.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w")
        
        # Button frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        # Select positions button
        self.select_button = ctk.CTkButton(
            button_frame,
            text="Select Positions",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#17a2b8",  # Cyan color
            hover_color="#138496",  # Darker cyan
            command=self._on_select
        )
        self.select_button.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="ew")
        
        # Clear positions button
        clear_button = ctk.CTkButton(
            button_frame,
            text="Clear Positions",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#6c757d",  # Gray color
            hover_color="#5a6268",  # Darker gray
            command=self._on_clear
        )
        clear_button.grid(row=0, column=1, padx=(5, 0), pady=5, sticky="ew")
        
        # Multi-click toggle section
        toggle_frame = ctk.CTkFrame(self, fg_color="transparent")
        toggle_frame.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="ew")
        
        # Toggle switch label
        toggle_label = ctk.CTkLabel(
            toggle_frame,
            text="Multi-click Mode",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        toggle_label.pack(side="left", padx=(0, 10))
        
        # Toggle help text
        toggle_help = ctk.CTkLabel(
            toggle_frame,
            text="Click all positions at once",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        toggle_help.pack(side="left", padx=(0, 10))
        
        # Toggle switch
        self.multi_click_var = ctk.BooleanVar(value=False)
        switch = ctk.CTkSwitch(
            toggle_frame,
            text="",
            variable=self.multi_click_var,
            command=self._on_multi_click_toggled,
            progress_color="#007bff"  # Blue for active state
        )
        switch.pack(side="right", padx=5) 