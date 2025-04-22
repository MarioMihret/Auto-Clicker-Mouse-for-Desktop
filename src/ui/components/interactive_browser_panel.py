"""
Interactive Browser Panel - UI component for user-driven browser automation
"""

import os
import logging
import threading
import asyncio
import customtkinter as ctk
from tkinter import messagebox
from typing import Callable, Dict, Any, List, Tuple
import json
import time

from ...browser.browser_controller import BrowserController, BrowserType, BrowserTask, TaskAction
from ...browser.interactive import setup_interactive_browser, perform_click_at_coordinates, cleanup_interactive_browser
from ...core.utils import resource_path
from .browser_coordinate_frame import BrowserCoordinateFrame

logger = logging.getLogger(__name__)

class InteractiveBrowserPanel(ctk.CTkFrame):
    """Panel for interactive browser automation controls"""
    
    def __init__(self, master, on_start_browser=None, on_stop_browser=None, **kwargs):
        """
        Initialize the interactive browser panel
        
        Args:
            master: Parent widget
            on_start_browser: Callback when start browser button is clicked
            on_stop_browser: Callback when stop browser button is clicked
        """
        super().__init__(master, **kwargs)
        self.on_start_browser = on_start_browser
        self.on_stop_browser = on_stop_browser
        
        # Configuration variables
        self.browser_count = ctk.IntVar(value=1)
        self.headless_mode = ctk.BooleanVar(value=False)
        self.interval_ms = ctk.IntVar(value=1000)  # Default to 1 second
        self.click_coordinates = []  # List of (x, y) tuples for each browser
        self.is_running = ctk.BooleanVar(value=False)
        self.status_text = ctk.StringVar(value="Ready")
        self.coord_frames = []  # List of browser coordinate frames
        
        # Browser controller references
        self.controller = None
        self.browsers = []
        self.clicking_thread = None
        self.should_stop = False
        
        # Browser URL variable
        self.url_var = ctk.StringVar(value="https://www.example.com")
        
        # Window handles for browser identification
        self.window_handles = []
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the interactive browser panel UI"""
        # Make the whole panel use available width 
        self.grid_columnconfigure(0, weight=1)
        
        # Title section
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="ew")
        title_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="Interactive Browser Automation", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Configuration frame - use a grid with proper spacing
        config_frame = ctk.CTkFrame(self)
        config_frame.grid(row=1, column=0, padx=15, pady=10, sticky="ew")
        config_frame.grid_columnconfigure(1, weight=1)
        
        # ==== Browser Count ====
        count_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        count_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        count_frame.grid_columnconfigure(1, weight=1)
        
        count_label = ctk.CTkLabel(count_frame, text="Browser Count:", width=100)
        count_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        browser_count_slider = ctk.CTkSlider(
            count_frame,
            from_=1,
            to=5,
            number_of_steps=4,
            variable=self.browser_count,
            command=lambda v: self.browser_count.set(int(v))
        )
        browser_count_slider.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        browser_count_value = ctk.CTkLabel(
            count_frame, 
            textvariable=self.browser_count,
            width=30
        )
        browser_count_value.grid(row=0, column=2, padx=5, pady=5, sticky="e")
        
        # ==== URL input ====
        url_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        url_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        url_frame.grid_columnconfigure(1, weight=1)
        
        url_label = ctk.CTkLabel(url_frame, text="URL:", width=100)
        url_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        url_entry = ctk.CTkEntry(
            url_frame,
            textvariable=self.url_var,
            width=300
        )
        url_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        # ==== Click interval control ====
        interval_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        interval_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        interval_frame.grid_columnconfigure(1, weight=1)
        
        interval_label = ctk.CTkLabel(interval_frame, text="Click Interval (ms):", width=100)
        interval_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        interval_slider = ctk.CTkSlider(
            interval_frame,
            from_=100,
            to=10000,
            number_of_steps=99,
            variable=self.interval_ms,
            command=lambda v: self.interval_ms.set(int(v))
        )
        interval_slider.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        interval_value = ctk.CTkLabel(
            interval_frame, 
            textvariable=self.interval_ms,
            width=60
        )
        interval_value.grid(row=0, column=2, padx=5, pady=5, sticky="e")
        
        # ==== Options frame ====
        options_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        options_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        
        # Headless mode checkbox
        headless_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="Headless Mode",
            variable=self.headless_mode,
            onvalue=True,
            offvalue=False,
            width=120
        )
        headless_checkbox.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Add tooltip/help text for headless mode
        headless_help = ctk.CTkLabel(
            options_frame,
            text="(browsers run invisibly)",
            font=ctk.CTkFont(size=10, slant="italic"),
            text_color="gray60"
        )
        headless_help.grid(row=0, column=1, padx=0, pady=5, sticky="w")
        
        # Action buttons
        action_frame = ctk.CTkFrame(self)
        action_frame.grid(row=2, column=0, padx=15, pady=10, sticky="ew")
        action_frame.grid_columnconfigure(0, weight=1)
        action_frame.grid_columnconfigure(1, weight=1)
        
        # Launch browser button
        self.launch_button = ctk.CTkButton(
            action_frame,
            text="Launch Browsers",
            command=self.launch_browsers,
            height=36
        )
        self.launch_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Start/Stop clicking button
        self.start_button = ctk.CTkButton(
            action_frame,
            text="Start Clicking",
            command=self.toggle_clicking,
            state="disabled",
            height=36
        )
        self.start_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Status frame with coordinates
        status_frame = ctk.CTkFrame(self)
        status_frame.grid(row=3, column=0, padx=15, pady=5, sticky="ew")
        status_frame.grid_columnconfigure(1, weight=1)
        
        # Status label
        status_label = ctk.CTkLabel(
            status_frame,
            text="Status:",
            width=60,
            font=ctk.CTkFont(weight="bold")
        )
        status_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        status_value = ctk.CTkLabel(
            status_frame,
            textvariable=self.status_text
        )
        status_value.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Browser coordinates section
        coords_section = ctk.CTkFrame(self, fg_color="transparent")
        coords_section.grid(row=4, column=0, padx=15, pady=(10, 0), sticky="ew")
        coords_section.grid_columnconfigure(0, weight=1)
        
        # Browser coordinates title
        coords_title = ctk.CTkLabel(
            coords_section,
            text="Browser Windows & Coordinates:",
            font=ctk.CTkFont(weight="bold")
        )
        coords_title.grid(row=0, column=0, sticky="w")
        
        # Show column headers
        headers_frame = ctk.CTkFrame(coords_section, fg_color="transparent")
        headers_frame.grid(row=1, column=0, pady=(5, 0), sticky="ew")
        
        ctk.CTkLabel(headers_frame, text="Browser", width=80, font=ctk.CTkFont(size=12, slant="italic")).grid(row=0, column=0, padx=10, sticky="w")
        ctk.CTkLabel(headers_frame, text="Coordinates", width=150, font=ctk.CTkFont(size=12, slant="italic")).grid(row=0, column=1, padx=5, sticky="w")
        ctk.CTkLabel(headers_frame, text="Status", width=80, font=ctk.CTkFont(size=12, slant="italic")).grid(row=0, column=2, padx=5, sticky="w")
        ctk.CTkLabel(headers_frame, text="Action", width=120, font=ctk.CTkFont(size=12, slant="italic")).grid(row=0, column=3, padx=5, sticky="w")
        
        # Coordinates display area
        self.coordinates_frame = ctk.CTkScrollableFrame(self, height=150)
        self.coordinates_frame.grid(row=5, column=0, padx=15, pady=5, sticky="ew")
        
        # Help text
        help_frame = ctk.CTkFrame(self, fg_color="transparent")
        help_frame.grid(row=6, column=0, padx=15, pady=(10, 15), sticky="ew")
        help_frame.grid_columnconfigure(0, weight=1)
        
        help_label = ctk.CTkLabel(
            help_frame,
            text=(
                "Interactive Browser Automation allows you to visually select click positions "
                "in browser windows and automate clicking at those positions at specified intervals. "
                "Launch browsers, click 'Select Position' for each browser, then start the automation."
            ),
            wraplength=380,
            justify="left",
            font=ctk.CTkFont(size=11),
            text_color="gray70"
        )
        help_label.grid(row=0, column=0, sticky="ew")
    
    def launch_browsers(self):
        """Launch browser(s) and prepare for position selection"""
        # Get configuration
        browser_count = self.browser_count.get()
        headless = self.headless_mode.get()
        url = self.url_var.get()
        
        # Cannot use headless mode for position selection
        if headless:
            messagebox.showwarning("Warning", "Headless mode has been disabled for position selection.")
            self.headless_mode.set(False)
            headless = False
        
        # Update status
        self.status_text.set(f"Launching {browser_count} browser(s)...")
        
        # Clear previous coordinate displays
        for widget in self.coordinates_frame.winfo_children():
            widget.destroy()
        
        # Clear coordinate variables
        self.coord_frames = []
        self.click_coordinates = []
        
        # Create frames for each browser's coordinates
        for i in range(browser_count):
            coord_frame = BrowserCoordinateFrame(
                self.coordinates_frame, 
                i
            )
            coord_frame.grid(row=i, column=0, padx=5, pady=5, sticky="ew")
            self.coord_frames.append(coord_frame)
        
        # Run in a separate thread to avoid blocking UI
        threading.Thread(
            target=self._launch_browsers_thread,
            args=(browser_count, headless, url),
            daemon=True
        ).start()
    
    def _launch_browsers_thread(self, browser_count, headless, url):
        """Launch browsers in a separate thread"""
        try:
            # Create browser controller
            self.controller = BrowserController(recording_enabled=False)
            
            # Create browser instances
            self.browsers = self.controller.create_browsers(
                count=browser_count,
                browser_type=BrowserType.CHROME,
                headless=headless,
                urls=[url] * browser_count
            )
            
            # Give browsers time to open
            time.sleep(1)
            
            # Store window handles for identification
            self.window_handles = []
            for browser in self.browsers:
                self.window_handles.append(browser.current_window_handle)
            
            # Connect browser objects to coordinate frames
            for i, browser in enumerate(self.browsers):
                if i < len(self.coord_frames):
                    self.coord_frames[i].set_browser_object(
                        browser, 
                        self.activate_position_selection
                    )
            
            # Initialize click coordinates list
            self.click_coordinates = [None] * len(self.browsers)
            
            # Update UI from main thread
            self.after(100, lambda: self.status_text.set(
                f"{browser_count} browser(s) launched. Click 'Select Position' for each browser."
            ))
            
        except Exception as e:
            logger.error(f"Error launching browsers: {e}")
            self.after(100, lambda: self.status_text.set(f"Error: {str(e)}"))
            if self.controller:
                self.controller.close_all_browsers()
                self.controller = None
    
    def activate_position_selection(self, browser_index):
        """Activate position selection for a specific browser"""
        if browser_index >= len(self.browsers):
            logger.error(f"Browser index {browser_index} out of range")
            return
            
        try:
            browser = self.browsers[browser_index]
            
            # Check if browser window is still open
            try:
                # This will throw an exception if the window is closed
                browser.current_url
                
                # Ensure browser window is active/focused
                browser.switch_to.window(self.window_handles[browser_index])
                browser.maximize_window()  # Ensure window is visible
                
                # Update status
                self.status_text.set(f"Click anywhere in Browser {browser_index+1} to select click position")
                
                # Set up browser for coordinate selection
                setup_interactive_browser(browser, browser_index, self._on_coordinates_selected)
                
                # Update UI to show which browser is active for selection
                for i, frame in enumerate(self.coord_frames):
                    if i == browser_index:
                        frame.configure(border_width=2, border_color="blue", fg_color=("gray90", "gray25"))
                        frame.select_btn.configure(state="disabled", text="Selecting...")
                    else:
                        frame.configure(border_width=0, fg_color=("gray85", "gray30"))
                
            except Exception as e:
                # Browser window might be closed
                self.status_text.set(f"Browser {browser_index+1} is not accessible. Relaunching...")
                messagebox.showinfo("Browser Closed", f"Browser {browser_index+1} appears to be closed. Please relaunch browsers.")
                self.click_coordinates[browser_index] = None
                self._check_all_coordinates_selected()
                
        except Exception as e:
            logger.error(f"Error activating position selection for browser {browser_index}: {e}")
            messagebox.showerror("Error", f"Failed to activate position selection: {e}")
    
    def _on_coordinates_selected(self, browser_index, x, y):
        """Callback when coordinates are selected in a browser"""
        # Store coordinates
        if browser_index < len(self.click_coordinates):
            self.click_coordinates[browser_index] = (x, y)
            
        # Update UI from main thread
        self.after(100, lambda: self._update_coordinate_display(browser_index, x, y))
        
        # Reset the browser frame appearance
        self.after(100, lambda: self._reset_browser_frame_appearance(browser_index))
        
        # Enable start button if all active browsers have coordinates
        self.after(100, self._check_all_coordinates_selected)
    
    def _update_coordinate_display(self, browser_index, x, y):
        """Update the coordinate display for a browser"""
        if browser_index < len(self.coord_frames):
            self.coord_frames[browser_index].set_position(x, y)
    
    def _reset_browser_frame_appearance(self, browser_index):
        """Reset the appearance of a browser frame after selection"""
        if browser_index < len(self.coord_frames):
            frame = self.coord_frames[browser_index]
            frame.configure(border_width=0, fg_color=("gray85", "gray30"))
            frame.select_btn.configure(state="normal", text="Select Position")
            
            # Show success message
            self.status_text.set(f"Position selected for Browser {browser_index+1}")
    
    def _check_all_coordinates_selected(self):
        """Check if all active browsers have coordinates selected"""
        all_selected = True
        
        for i, frame in enumerate(self.coord_frames):
            if frame.is_active.get() and (i >= len(self.click_coordinates) or self.click_coordinates[i] is None):
                all_selected = False
                break
                
        if all_selected and any(frame.is_active.get() for frame in self.coord_frames):
            self.start_button.configure(state="normal")
        else:
            self.start_button.configure(state="disabled")
    
    def toggle_clicking(self):
        """Toggle automatic clicking on/off"""
        if self.is_running.get():
            # Stop clicking
            self.should_stop = True
            self.is_running.set(False)
            self.start_button.configure(text="Start Clicking")
            self.launch_button.configure(state="normal")
            self.status_text.set("Clicking stopped")
            
            # Enable select position buttons
            for frame in self.coord_frames:
                frame.select_btn.configure(state="normal")
        else:
            # Start clicking
            active_browsers = [i for i, frame in enumerate(self.coord_frames) if frame.is_active.get()]
            
            if not self.browsers or not active_browsers:
                messagebox.showwarning("Warning", "Please launch browsers and select positions first.")
                return
                
            # Check if all active browsers have coordinates
            missing_coords = False
            for i in active_browsers:
                if i >= len(self.click_coordinates) or self.click_coordinates[i] is None:
                    missing_coords = True
                    break
                    
            if missing_coords:
                messagebox.showwarning("Warning", "Please select positions for all active browsers.")
                return
                
            self.should_stop = False
            self.is_running.set(True)
            self.start_button.configure(text="Stop Clicking")
            self.launch_button.configure(state="disabled")
            
            # Disable select position buttons while clicking
            for frame in self.coord_frames:
                frame.select_btn.configure(state="disabled")
            
            # Get interval (convert from ms to seconds for the thread)
            interval_seconds = self.interval_ms.get() / 1000
            
            # Start clicking thread
            self.clicking_thread = threading.Thread(
                target=self._clicking_thread,
                args=(interval_seconds, active_browsers),
                daemon=True
            )
            self.clicking_thread.start()
            
            self.status_text.set(f"Clicking every {interval_seconds:.1f} seconds")
    
    def _clicking_thread(self, interval, active_browsers):
        """Thread that performs automatic clicking at the specified interval"""
        try:
            click_count = 0
            error_count = 0
            max_errors = 5
            
            while not self.should_stop and self.browsers and error_count < max_errors:
                try:
                    # Click at the selected position for active browsers
                    for i in active_browsers:
                        if i < len(self.browsers) and i < len(self.click_coordinates) and self.click_coordinates[i]:
                            try:
                                # Switch to correct window
                                browser = self.browsers[i]
                                if len(browser.window_handles) > 0:
                                    if browser.current_window_handle != self.window_handles[i]:
                                        browser.switch_to.window(self.window_handles[i])
                                    
                                    # Perform click
                                    x, y = self.click_coordinates[i]
                                    perform_click_at_coordinates(browser, x, y)
                            except Exception as e:
                                logger.error(f"Error clicking in browser {i}: {e}")
                                error_count += 1
                                # Show error in UI
                                self.after(100, lambda msg=f"Error clicking in Browser {i+1}: {str(e)[:50]}...": 
                                          self.status_text.set(msg))
                                
                                # If too many errors, break
                                if error_count >= max_errors:
                                    raise Exception(f"Too many errors ({error_count}). Stopping auto-clicking.")
                    
                    click_count += 1
                    # Update UI from main thread
                    self.after(100, lambda count=click_count: self.status_text.set(
                        f"Clicking (count: {count}) - every {interval:.1f} seconds"))
                    
                    # Wait for the next interval
                    time.sleep(interval)
                
                except Exception as e:
                    if "Connection refused" in str(e) or "has been closed" in str(e):
                        # Browser connection lost - try to recover
                        error_count += 1
                        self.after(100, lambda: self.status_text.set(f"Browser connection issue. Attempts: {error_count}/{max_errors}"))
                        time.sleep(1)  # Short pause before retrying
                    else:
                        # Other error - re-raise
                        raise
                    
        except Exception as e:
            logger.error(f"Error in clicking thread: {e}")
            self.after(100, lambda: self.status_text.set(f"Error: {str(e)}"))
        
        # Make sure to update the UI when the thread ends
        if not self.should_stop:  # Only if we didn't stop manually
            self.after(100, lambda: self.toggle_clicking())
    
    def stop_and_close(self):
        """Stop clicking and close all browsers"""
        # Stop clicking if running
        if self.is_running.get():
            self.should_stop = True
            self.is_running.set(False)
            self.start_button.configure(text="Start Clicking")
        
        # Close browsers
        if self.controller:
            try:
                self.controller.close_all_browsers()
                self.browsers = []
                self.window_handles = []
                self.controller = None
                self.status_text.set("Browsers closed")
                self.start_button.configure(state="disabled")
                
                # Clear coordinate frames
                for widget in self.coordinates_frame.winfo_children():
                    widget.destroy()
                self.coord_frames = []
                
            except Exception as e:
                logger.error(f"Error closing browsers: {e}")
                self.status_text.set(f"Error closing browsers: {str(e)}") 