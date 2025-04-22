"""
Main Window - Primary application window that integrates all UI components
"""

import os
import logging
import tkinter as tk
import customtkinter as ctk
from typing import Dict, Any
from tkinter import messagebox
import sys
import threading
import asyncio

# Core modules
from ..core.autoclicker import AutoClicker
from ..core.utils import resource_path, format_time_ms, setup_logger, KeyboardListener

# UI components
from .components.status_panel import StatusPanel
from .components.position_panel import PositionPanel
from .components.settings_panel import IntervalPanel, DurationPanel
from .components.control_panel import ControlPanel
from .components.position_picker import PositionPicker
from .components.browser_panel import BrowserPanel
from .components.interactive_browser_panel import InteractiveBrowserPanel

# Browser automation
from ..browser.example import run_browser_example, replay_recorded_session

logger = logging.getLogger(__name__)

class MainWindow:
    """
    Main application window that integrates all UI components
    """
    def __init__(self, autoclicker: AutoClicker, ui_settings: Dict[str, Any]):
        """
        Initialize the main window
        
        Args:
            autoclicker: AutoClicker instance
            ui_settings: UI settings dictionary
        """
        self.autoclicker = autoclicker
        self.ui_settings = ui_settings
        
        # State variables
        self.position_picking_mode = False
        self.cursor_position = (0, 0)
        
        # Register callback for stopping via Escape key
        self.autoclicker.set_on_stop_callback(self._on_autoclicker_stopped)
        
        # Setup window
        self.setup_window()
        
        # Setup UI components
        self.setup_ui()
        
        logger.info("Main window initialized")
        
    def setup_window(self):
        """Configure the main application window"""
        # Set up customtkinter
        ctk.set_appearance_mode("system")  # Use system theme
        ctk.set_default_color_theme("blue")  # Use default blue theme
        
        # Create the main window
        self.root = ctk.CTk()
        self.root.title(self.ui_settings["title"])
        
        # Increase default window size to ensure all elements are visible
        default_width = max(800, self.ui_settings.get('width', 800))
        default_height = max(700, self.ui_settings.get('height', 700))
        self.root.geometry(f"{default_width}x{default_height}")
        
        # Make sure the window scales with different screen densities
        # Increase scaling for larger text and UI elements
        self.root.tk.call('tk', 'scaling', 2.5)
        
        # Set minimum window size for responsive layout
        self.root.minsize(600, 650)
        
        # Configure row and column weights for responsive resizing
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Try to load the icon
        try:
            icon_path = resource_path(self.ui_settings["icon_path"])
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            logger.warning(f"Failed to load icon: {e}")
            
        # Set up window exit handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        
        # Set up keyboard bindings
        self.root.bind("<F6>", lambda e: self.toggle_clicking())
        self.root.bind("<F8>", lambda e: self.on_exit())
        self.root.bind("<Escape>", lambda e: self.stop_clicking())
        
        # Add window resize event handler
        self.root.bind("<Configure>", self.on_resize)
        
    def on_resize(self, event):
        """Handle window resize events"""
        # Only process if this is the root window being resized
        if event.widget == self.root:
            # Update wraplength for help text based on window width
            if hasattr(self, 'help_label'):
                new_width = max(250, event.width - 50)
                self.help_label.configure(wraplength=new_width)
                
            # Adjust scrollable frame width
            if hasattr(self, 'scrollable_frame'):
                new_width = max(280, event.width - 40)
                self.scrollable_frame.configure(width=new_width)
        
    def setup_ui(self):
        """Set up the user interface components"""
        # Configure root window grid
        self.root.grid_rowconfigure(0, weight=1)  # Main frame takes all available space
        self.root.grid_rowconfigure(1, weight=0)  # Status bar is fixed height
        
        # Main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Add scrollable content frame
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Create scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Title and branding section
        branding_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        branding_frame.grid(row=0, column=0, pady=(10, 5), sticky="ew")
        branding_frame.grid_columnconfigure(0, weight=1)
        
        # Title label with larger font and brand name
        title_label = ctk.CTkLabel(
            branding_frame, 
            text="GETU CLICKER", 
            font=ctk.CTkFont(size=34, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(5, 0), sticky="ew")
        
        # Tagline
        tagline_label = ctk.CTkLabel(
            branding_frame,
            text="Professional Auto-Clicking Tool",
            font=ctk.CTkFont(size=16, slant="italic"),
            text_color="gray70"
        )
        tagline_label.grid(row=1, column=0, pady=(0, 2), sticky="ew")
        
        # Developer attribution
        dev_attribution = ctk.CTkLabel(
            branding_frame,
            text="by Mario M",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#3a7ebf"  # Brand blue color
        )
        dev_attribution.grid(row=2, column=0, pady=(0, 5), sticky="ew")
        
        # Create tabview for different functionality
        self.tabview = ctk.CTkTabview(self.scrollable_frame)
        self.tabview.grid(row=1, column=0, padx=0, pady=10, sticky="ew")
        
        # Add tabs
        self.tabview.add("Auto Clicker")
        self.tabview.add("Browser Automation")
        self.tabview.add("Interactive Browser")
        
        # Set default tab
        self.tabview.set("Auto Clicker")
        
        # Auto Clicker tab
        self.setup_autoclicker_tab(self.tabview.tab("Auto Clicker"))
        
        # Browser Automation tab
        self.setup_browser_tab(self.tabview.tab("Browser Automation"))
        
        # Interactive Browser tab
        self.setup_interactive_browser_tab(self.tabview.tab("Interactive Browser"))
        
        # Help text
        self.help_label = ctk.CTkLabel(
            self.scrollable_frame,
            text=("Getu Clicker combines auto-clicking, browser automation, and interactive browser clicking. "
                 "Switch between tabs to access different features."),
            wraplength=400,
            justify="left",
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        )
        self.help_label.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="ew")
        
        # Status bar at bottom
        self.status_bar = ctk.CTkLabel(
            self.root,
            text="Ready",
            anchor=tk.W,
            font=ctk.CTkFont(size=10)
        )
        self.status_bar.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Create position picker
        self.position_picker = PositionPicker(
            on_complete=self._finish_position_picking,
            on_cancel=self._cancel_position_picking
        )
        
    def toggle_clicking(self):
        """Toggle the auto clicking on and off"""
        if self.autoclicker.is_running:
            self.stop_clicking()
        else:
            # Start clicking
            self.status_bar.configure(text="Auto-clicking in progress...")
            if self.autoclicker.positions:
                positions_text = "positions" if len(self.autoclicker.positions) > 1 else "position"
                if self.autoclicker.multi_click_enabled:
                    self.status_bar.configure(text=f"Clicking at {len(self.autoclicker.positions)} {positions_text} simultaneously...")
                else:
                    self.status_bar.configure(text=f"Clicking at {len(self.autoclicker.positions)} fixed {positions_text}...")
            else:
                self.status_bar.configure(text="Clicking at cursor position...")
            
            self.control_panel.set_toggle_state(True)
            self.autoclicker.start()
            
    def stop_clicking(self):
        """Stop the auto clicking"""
        if self.autoclicker.is_running:
            self.autoclicker.stop()
            self.control_panel.set_toggle_state(False)
            self.status_bar.configure(text="Ready")
        
    def on_interval_change(self, interval):
        """Handle interval changes"""
        self.autoclicker.interval = interval
        # Display interval in seconds
        seconds = interval / 1000
        self.status_bar.configure(text=f"Click interval set to {seconds:.1f} seconds")
    
    def on_duration_change(self, duration):
        """Handle duration changes"""
        self.autoclicker.set_duration(duration)
    
    def start_position_picking(self):
        """Start the position picking process"""
        if self.position_picking_mode:
            return
            
        self.position_picking_mode = True
        
        # Update UI
        self.status_bar.configure(text="Click to select positions. Press Enter when done or Esc to cancel...")
        
        # Minimize the window
        self.root.iconify()
        
        # Start position picking
        self.position_picker.start()
    
    def _finish_position_picking(self, positions):
    
        """
        Finish position picking and update UI
        
        Args:
            positions: List of (x, y) coordinates
        """
        # Update cursor position
        self.cursor_position = positions[-1] if positions else (0, 0)
        
        # Restore window
        self.root.after(0, lambda: self._apply_picked_positions(positions))
    
    def _apply_picked_positions(self, positions):
        """
        Apply the picked positions to the autoclicker
        
        Args:
            positions: List of (x, y) coordinates
        """
        # Restore window
        self.root.deiconify()
        self.root.focus_force()

        
        # Log all positions for debugging
        logger.info(f"Applying picked positions: {positions}")
        
        if not positions:
            self.status_bar.configure(text="No positions selected")
            return
            
        # Update autoclicker
        self.autoclicker.set_positions(positions)
        
        
        # Update UI
        self.position_panel.set_positions(positions)
        
        # Update status bar
        if len(positions) == 1:
            self.status_bar.configure(text=f"Position set to ({positions[0][0]}, {positions[0][1]})")
        else:
            self.status_bar.configure(text=f"Selected {len(positions)} positions")
        
        self.position_picking_mode = False
    
    def _cancel_position_picking(self):
        """Cancel position picking mode"""
        # Restore window
        self.root.deiconify()
        self.root.focus_force()
        
        self.status_bar.configure(text="Position picking canceled")
        self.position_picking_mode = False
    
    def clear_positions(self):
        """Clear the selected positions"""
        self.autoclicker.positions = []
        self.position_panel.set_positions([])
        self.status_bar.configure(text="Using cursor position for clicking")
    
    def on_multi_click_change(self, multi_click_enabled):
        """Handle changes to the multi-click toggle"""
        self.autoclicker.multi_click_enabled = multi_click_enabled
        if multi_click_enabled:
            self.status_bar.configure(text="Multi-click mode enabled - will click all positions simultaneously")
        else:
            self.status_bar.configure(text="Sequential click mode - will click positions one by one")
    
    def on_exit(self):
        """Handle application exit"""
        # Stop autoclicker if running
        if self.autoclicker.running:
            self.autoclicker.stop()
            
        # Stop and close interactive browsers if running
        if hasattr(self, 'interactive_browser_panel'):
            self.interactive_browser_panel.stop_and_close()
            
        logger.info("Application exiting")
        
        
        # Destroy main window
        self.root.destroy()
    
    def run(self):
        """Run the application main loop"""
        logger.info("Starting main loop")
        self.root.mainloop()

    def _on_autoclicker_stopped(self):
        """Callback when autoclicker is stopped"""
        # Use the main thread to update the UI
        self.root.after(0, lambda: self._update_ui_after_stop())
        
    def _update_ui_after_stop(self):
        """Update UI after autoclicker stops"""
        self.control_panel.set_toggle_state(False)
        self.status_bar.configure(text="Stopped clicking (Esc key pressed)")
        logger.info("UI updated after autoclicker stopped")

    def setup_autoclicker_tab(self, parent):
        """Set up the Auto Clicker tab"""
        # Status panel
        self.status_panel = StatusPanel(parent)
        self.status_panel.grid(row=0, column=0, pady=5, sticky="ew")
        
        # Position panel
        self.position_panel = PositionPanel(
            parent,
            on_select_positions=self.start_position_picking,
            on_clear_positions=self.clear_positions,
            on_multi_click_change=self.on_multi_click_change
        )
        self.position_panel.grid(row=1, column=0, pady=10, sticky="ew")
        
        # Interval panel
        self.interval_panel = IntervalPanel(
            parent,
            initial_value=self.autoclicker.interval,
            on_change=self.on_interval_change
        )
        self.interval_panel.grid(row=2, column=0, pady=10, sticky="ew")
        
        # Duration panel
        self.duration_panel = DurationPanel(
            parent,
            initial_value=0,  # Default to indefinite
            on_change=self.on_duration_change
        )
        self.duration_panel.grid(row=3, column=0, pady=10, sticky="ew")
        
        # Control panel
        self.control_panel = ControlPanel(
            parent,
            on_toggle=self.toggle_clicking,
            on_exit=self.on_exit
        )
        self.control_panel.grid(row=4, column=0, pady=10, sticky="ew")
        
    def setup_browser_tab(self, parent):
        """Set up the Browser Automation tab"""
        # Browser panel
        self.browser_panel = BrowserPanel(
            parent,
            on_run_example=self.on_run_browser_example,
            on_replay=self.on_replay_browser_session
        )
        self.browser_panel.grid(row=0, column=0, pady=10, sticky="ew")
        
    def setup_interactive_browser_tab(self, parent):
        """Set up the Interactive Browser Automation tab"""
        # Interactive browser panel
        self.interactive_browser_panel = InteractiveBrowserPanel(
            parent,
            on_start_browser=self.on_start_interactive_browser,
            on_stop_browser=self.on_stop_interactive_browser
        )
        self.interactive_browser_panel.grid(row=0, column=0, pady=10, sticky="ew")
        
    def on_run_browser_example(self, config):
        """Run the browser automation example"""
        try:
            # Run example in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                run_browser_example(
                    headless=config.get('headless', False),
                    record=config.get('record', True)
                )
            )
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Error running browser example: {e}")
            messagebox.showerror("Error", f"Failed to run browser example: {e}")
            return None
    
    def on_replay_browser_session(self, config):
        """Replay a browser session"""
        try:
            # Run replay in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                replay_recorded_session(
                    config.get('filepath', ''),
                    headless=config.get('headless', False)
                )
            )
            loop.close()
            return True
        except Exception as e:
            logger.error(f"Error replaying browser session: {e}")
            messagebox.showerror("Error", f"Failed to replay browser session: {e}")
            return False
    
    def on_start_interactive_browser(self, config):
        """Start the interactive browser automation"""
        # This is mostly handled within the InteractiveBrowserPanel itself
        self.status_bar.configure(text="Starting interactive browser automation...")
        return True
        
    def on_stop_interactive_browser(self):
        """Stop the interactive browser automation"""
        # This is mostly handled within the InteractiveBrowserPanel itself
        self.status_bar.configure(text="Interactive browser automation stopped")
        return True 