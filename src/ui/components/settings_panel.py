"""
Settings Panel component - Manages interval and click type settings
"""

import customtkinter as ctk
from typing import Callable, Optional
import logging

logger = logging.getLogger(__name__)

class IntervalPanel(ctk.CTkFrame):
    """Panel for adjusting click interval"""
    
    def __init__(
        self, 
        master, 
        initial_value: int = 1000, 
        on_change: Optional[Callable[[int], None]] = None
    ):
        super().__init__(master, corner_radius=10)
        self.on_change = on_change
        # Store internal value in milliseconds but display in seconds
        self.interval_ms = initial_value
        # Convert to seconds for display (with one decimal place)
        self.interval_sec = initial_value / 1000
        self.interval_var = ctk.DoubleVar(value=self.interval_sec)
        
        # Set up UI components
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the UI components"""
        # Main label
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        
        label = ctk.CTkLabel(
            header_frame, 
            text="Click Interval", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        label.pack(side="left")
        
        # Help text for interval
        help_label = ctk.CTkLabel(
            self,
            text="Time between clicks (in seconds)",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        help_label.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w")
        
        # Frame for the slider and value
        slider_frame = ctk.CTkFrame(self, fg_color="transparent")
        slider_frame.grid(row=2, column=0, padx=10, pady=(0, 5), sticky="ew")
        slider_frame.grid_columnconfigure(0, weight=1)
        
        # Slider (0.05 to 5 seconds)
        self.slider = ctk.CTkSlider(
            slider_frame, 
            from_=0.05, 
            to=5.0,
            number_of_steps=99,
            variable=self.interval_var,
            command=self._on_slider_change,
            progress_color="#007bff",  # Blue progress
            button_color="#0056b3"     # Darker blue button
        )
        self.slider.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")
        
        # Value label with sec
        self.value_label = ctk.CTkLabel(
            slider_frame, 
            text=f"{self.interval_var.get():.1f} sec", 
            width=80,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.value_label.grid(row=0, column=1, padx=5, pady=5)
        
        # Preset buttons
        presets_frame = ctk.CTkFrame(self, fg_color="transparent")
        presets_frame.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        # Add preset buttons (0.1, 0.5, 1.0 seconds)
        presets = [0.1, 0.5, 1.0]
        for i, preset in enumerate(presets):
            btn = ctk.CTkButton(
                presets_frame, 
                text=f"{preset:.1f} sec",
                width=70,
                height=28,
                font=ctk.CTkFont(size=12),
                fg_color="#6c757d",    # Gray
                hover_color="#5a6268", # Darker gray
                command=lambda p=preset: self._set_preset(p)
            )
            btn.grid(row=0, column=i, padx=5, pady=5)
    
    def _on_slider_change(self, value):
        """Handle slider value changes"""
        # Update the value label (in seconds)
        sec_value = float(value)
        self.value_label.configure(text=f"{sec_value:.1f} sec")
        
        # Convert to milliseconds for the autoclicker
        ms_value = int(sec_value * 1000)
        self.interval_ms = ms_value
        
        # Call the callback if provided
        if self.on_change:
            self.on_change(ms_value)
    
    def _set_preset(self, value_sec):
        """Set a preset interval value"""
        # Update the slider and variable (seconds)
        self.interval_var.set(value_sec)
        self.value_label.configure(text=f"{value_sec:.1f} sec")
        
        # Convert to milliseconds for the autoclicker
        ms_value = int(value_sec * 1000)
        self.interval_ms = ms_value
        
        # Call the callback if provided
        if self.on_change:
            self.on_change(ms_value)
    
    def get_interval(self):
        """Get the current interval in milliseconds"""
        return self.interval_ms
    
    def set_interval(self, ms_value):
        """Set the interval from milliseconds"""
        self.interval_ms = ms_value
        sec_value = ms_value / 1000
        self.interval_var.set(sec_value)
        self.value_label.configure(text=f"{sec_value:.1f} sec")

class DurationPanel(ctk.CTkFrame):
    """Panel for setting click duration"""
    
    def __init__(
        self, 
        master, 
        initial_value: int = 0, 
        on_change: Optional[Callable[[int], None]] = None
    ):
        super().__init__(master, corner_radius=10)
        self.on_change = on_change
        self.minutes_var = ctk.IntVar(value=initial_value)
        
        # Set up UI components
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI components"""
        # Main label
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        
        label = ctk.CTkLabel(
            header_frame, 
            text="Duration", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        label.pack(side="left")
        
        # Help text
        help_label = ctk.CTkLabel(
            self, 
            text="Time to run in minutes (0 = indefinite clicking)", 
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        help_label.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w")
        
        # Duration input frame
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.grid(row=2, column=0, padx=10, pady=(0, 5), sticky="ew")
        
        # Entry for duration
        self.entry = ctk.CTkEntry(
            input_frame,
            width=120,
            height=32,
            textvariable=self.minutes_var,
            font=ctk.CTkFont(size=13)
        )
        self.entry.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")
        
        # Apply button
        self.apply_btn = ctk.CTkButton(
            input_frame,
            text="Apply",
            width=90,
            height=32,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#007bff",  # Blue
            hover_color="#0056b3",  # Darker blue
            command=self._on_apply
        )
        self.apply_btn.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Preset buttons
        presets_frame = ctk.CTkFrame(self, fg_color="transparent")
        presets_frame.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        # Add preset buttons (1, 5, 15 minutes)
        presets = [1, 5, 15]
        for i, preset in enumerate(presets):
            btn = ctk.CTkButton(
                presets_frame, 
                text=f"{preset} min",
                width=70,
                height=28,
                font=ctk.CTkFont(size=12),
                fg_color="#6c757d",  # Gray
                hover_color="#5a6268",  # Darker gray
                command=lambda p=preset: self._set_preset(p)
            )
            btn.grid(row=0, column=i, padx=5, pady=5)
    
    def _on_apply(self):
        """Handle apply button click"""
        try:
            minutes = int(self.minutes_var.get())
            if minutes < 0:
                minutes = 0
                self.minutes_var.set(0)
            
            if self.on_change:
                self.on_change(minutes)
        except ValueError:
            # Reset to 0 if invalid input
            self.minutes_var.set(0)
            if self.on_change:
                self.on_change(0)
    
    def _set_preset(self, value):
        """Set a preset duration value"""
        self.minutes_var.set(value)
        
        if self.on_change:
            self.on_change(value)
    
    def get_duration(self):
        """Get the current duration in minutes"""
        return self.minutes_var.get()
    
    def set_duration(self, value):
        """Set the duration in minutes"""
        self.minutes_var.set(value) 