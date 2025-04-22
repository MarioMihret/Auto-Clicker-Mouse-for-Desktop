"""
Browser Panel - UI component for browser automation controls
"""

import os
import logging
import threading
import asyncio
import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Callable, Dict, Any

from ...browser.browser_controller import BrowserType
from ...core.utils import resource_path

logger = logging.getLogger(__name__)

class BrowserPanel(ctk.CTkFrame):
    """Panel for browser automation controls"""
    
    def __init__(self, master, on_run_example=None, on_replay=None, **kwargs):
        """
        Initialize the browser panel
        
        Args:
            master: Parent widget
            on_run_example: Callback when run example button is clicked
            on_replay: Callback when replay button is clicked
        """
        super().__init__(master, **kwargs)
        self.on_run_example = on_run_example
        self.on_replay = on_replay
        
        # Configuration variables
        self.browser_count = ctk.IntVar(value=3)
        self.headless_mode = ctk.BooleanVar(value=False)
        self.recording_enabled = ctk.BooleanVar(value=True)
        self.auto_replay = ctk.BooleanVar(value=False)
        self.selected_recording = ctk.StringVar(value="")
        self.status_text = ctk.StringVar(value="Ready")
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the browser panel UI"""
        # Title
        self.title_label = ctk.CTkLabel(
            self, 
            text="Browser Automation", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(10, 15), sticky="w")
        
        # Configuration frame
        self.config_frame = ctk.CTkFrame(self)
        self.config_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.config_frame.grid_columnconfigure(1, weight=1)
        
        # Number of browsers
        ctk.CTkLabel(self.config_frame, text="Browser Count:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        browser_count_slider = ctk.CTkSlider(
            self.config_frame,
            from_=1,
            to=5,
            number_of_steps=4,
            variable=self.browser_count,
            command=lambda v: self.browser_count.set(int(v))
        )
        browser_count_slider.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        browser_count_value = ctk.CTkLabel(
            self.config_frame, 
            textvariable=ctk.StringVar(value=self.browser_count.get()),
            width=30
        )
        browser_count_value.grid(row=0, column=2, padx=5, pady=5, sticky="e")
        
        # Update the browser count value label when slider changes
        self.browser_count.trace_add("write", lambda *args: 
            browser_count_value.configure(text=str(self.browser_count.get())))
        
        # Headless mode
        headless_checkbox = ctk.CTkCheckBox(
            self.config_frame,
            text="Headless Mode",
            variable=self.headless_mode,
            onvalue=True,
            offvalue=False
        )
        headless_checkbox.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        # Recording enabled
        recording_checkbox = ctk.CTkCheckBox(
            self.config_frame,
            text="Record Sessions",
            variable=self.recording_enabled,
            onvalue=True,
            offvalue=False
        )
        recording_checkbox.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Auto replay
        auto_replay_checkbox = ctk.CTkCheckBox(
            self.config_frame,
            text="Auto Replay",
            variable=self.auto_replay,
            onvalue=True,
            offvalue=False
        )
        auto_replay_checkbox.grid(row=1, column=2, padx=10, pady=5, sticky="w")
        
        # Action buttons
        self.action_frame = ctk.CTkFrame(self)
        self.action_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.action_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Run example button
        run_example_button = ctk.CTkButton(
            self.action_frame,
            text="Run Example",
            command=self.run_example
        )
        run_example_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Replay button
        replay_button = ctk.CTkButton(
            self.action_frame,
            text="Replay Session",
            command=self.select_and_replay
        )
        replay_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # List recordings button
        list_recordings_button = ctk.CTkButton(
            self.action_frame,
            text="List Recordings",
            command=self.list_recordings
        )
        list_recordings_button.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")
        
        # Status frame
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        
        # Status label
        status_label = ctk.CTkLabel(
            self.status_frame,
            text="Status:",
            width=60
        )
        status_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        status_value = ctk.CTkLabel(
            self.status_frame,
            textvariable=self.status_text
        )
        status_value.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Help text
        help_label = ctk.CTkLabel(
            self,
            text=(
                "Browser Automation allows you to control multiple Chrome instances "
                "simultaneously. The example will open websites and perform actions "
                "automatically. You can record sessions and replay them later."
            ),
            wraplength=380,
            justify="left"
        )
        help_label.grid(row=4, column=0, columnspan=2, padx=10, pady=(10, 15), sticky="ew")
        
    def run_example(self):
        """Run the browser automation example"""
        if self.on_run_example:
            # Get configuration
            config = {
                "browser_count": self.browser_count.get(),
                "headless": self.headless_mode.get(),
                "record": self.recording_enabled.get(),
                "auto_replay": self.auto_replay.get()
            }
            
            # Update status
            self.status_text.set("Running example...")
            
            # Run in separate thread to avoid blocking UI
            threading.Thread(
                target=self._run_example_thread,
                args=(config,),
                daemon=True
            ).start()
    
    def _run_example_thread(self, config):
        """Run example in a separate thread"""
        try:
            # Call the provided callback
            if self.on_run_example:
                result = self.on_run_example(config)
                
                # Update UI from main thread
                self.after(100, lambda: self.status_text.set(
                    f"Example completed. Session: {os.path.basename(result) if result else 'N/A'}"
                ))
        except Exception as e:
            logger.error(f"Error running example: {e}")
            self.after(100, lambda: self.status_text.set(f"Error: {str(e)}"))
    
    def select_and_replay(self):
        """Select and replay a recorded session"""
        # Ask user to select a recording file
        recording_dir = "browser_recordings"
        initial_dir = os.path.join(os.getcwd(), recording_dir) if os.path.exists(recording_dir) else os.getcwd()
        
        filepath = filedialog.askopenfilename(
            title="Select Recording File",
            initialdir=initial_dir,
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if filepath:
            self.selected_recording.set(filepath)
            self.replay_recording(filepath)
    
    def replay_recording(self, filepath):
        """Replay a recording file"""
        if not os.path.exists(filepath):
            messagebox.showerror("Error", f"Recording file not found: {filepath}")
            return
        
        # Update status
        self.status_text.set(f"Replaying: {os.path.basename(filepath)}...")
        
        # Configuration
        config = {
            "filepath": filepath,
            "headless": self.headless_mode.get()
        }
        
        # Run in separate thread
        threading.Thread(
            target=self._replay_thread,
            args=(config,),
            daemon=True
        ).start()
    
    def _replay_thread(self, config):
        """Replay in a separate thread"""
        try:
            # Call the provided callback
            if self.on_replay:
                self.on_replay(config)
                
                # Update UI from main thread
                self.after(100, lambda: self.status_text.set("Replay completed"))
        except Exception as e:
            logger.error(f"Error replaying session: {e}")
            self.after(100, lambda: self.status_text.set(f"Error: {str(e)}"))
    
    def list_recordings(self):
        """List available recordings"""
        recording_dir = "browser_recordings"
        if not os.path.exists(recording_dir):
            messagebox.showinfo("Info", f"Recording directory '{recording_dir}' does not exist.")
            return
        
        # Find recordings
        recordings = []
        for filename in os.listdir(recording_dir):
            if filename.endswith(".json") and filename.startswith("browser_session_"):
                file_path = os.path.join(recording_dir, filename)
                file_size = os.path.getsize(file_path) / 1024  # KB
                mod_time = os.path.getmtime(file_path)
                
                from datetime import datetime
                date_str = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
                
                recordings.append({
                    "filename": filename,
                    "path": file_path,
                    "size": file_size,
                    "date": date_str
                })
        
        # Sort by modification time (newest first)
        recordings.sort(key=lambda x: x["path"], reverse=True)
        
        if not recordings:
            messagebox.showinfo("Info", "No recordings found.")
            return
        
        # Show recordings in a dialog
        self._show_recordings_dialog(recordings)
        
    def _show_recordings_dialog(self, recordings):
        """Show a dialog with the list of recordings"""
        # Create a new dialog window
        dialog = ctk.CTkToplevel(self)
        dialog.title("Browser Recordings")
        dialog.geometry("600x400")
        dialog.resizable(True, True)
        dialog.grab_set()  # Make dialog modal
        
        # Configure the layout
        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure(1, weight=1)
        
        # Title
        title_frame = ctk.CTkFrame(dialog)
        title_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="Available Recording Sessions",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(padx=10, pady=10)
        
        # Create a frame for the list with scrollbar
        list_frame = ctk.CTkScrollableFrame(dialog)
        list_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Header row
        header_frame = ctk.CTkFrame(list_frame)
        header_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(header_frame, text="Filename", width=200, font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(header_frame, text="Size (KB)", width=80, font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(header_frame, text="Date Modified", width=150, font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(header_frame, text="Actions", width=80, font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        # Add recordings to the list
        for i, rec in enumerate(recordings):
            row_frame = ctk.CTkFrame(list_frame)
            row_frame.grid(row=i+1, column=0, padx=5, pady=2, sticky="ew")
            
            # Filename
            filename_label = ctk.CTkLabel(row_frame, text=rec["filename"], width=200)
            filename_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            
            # Size
            size_label = ctk.CTkLabel(row_frame, text=f"{rec['size']:.2f}", width=80)
            size_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
            
            # Date
            date_label = ctk.CTkLabel(row_frame, text=rec["date"], width=150)
            date_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")
            
            # Replay button
            replay_button = ctk.CTkButton(
                row_frame,
                text="Replay",
                width=80,
                command=lambda path=rec["path"]: self._on_replay_from_dialog(dialog, path)
            )
            replay_button.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        # Buttons at the bottom
        button_frame = ctk.CTkFrame(dialog)
        button_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        close_button = ctk.CTkButton(
            button_frame,
            text="Close",
            command=dialog.destroy
        )
        close_button.pack(side="right", padx=10, pady=10)
        
    def _on_replay_from_dialog(self, dialog, filepath):
        """Callback when a replay button is clicked in the dialog"""
        dialog.destroy()  # Close the dialog
        self.replay_recording(filepath)  # Start replay 