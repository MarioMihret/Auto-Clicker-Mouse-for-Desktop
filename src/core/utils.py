"""
Utils - Helper functions for the AutoClicker application
"""

import os
import sys
import logging
import logging.handlers
from typing import Optional, Callable
import time
from pynput import keyboard

def setup_logger(log_file: str, log_level: str, max_size: int, backup_count: int) -> None:
    """
    Setup logging configuration for the application

    Args:
        log_file: Path to the log file
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_size: Maximum size of the log file in bytes
        backup_count: Number of backup log files to keep
    """
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Setup file handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, 
        maxBytes=max_size, 
        backupCount=backup_count
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    logging.info(f"Logging initialized. Level: {log_level}, File: {log_file}")

def format_time_ms(milliseconds: int) -> str:
    """
    Format time in milliseconds to a readable string
    
    Args:
        milliseconds: Time in milliseconds
        
    Returns:
        Formatted time string
    """
    if milliseconds < 1000:
        return f"{milliseconds} ms"
    else:
        seconds = milliseconds / 1000
        return f"{seconds:.1f} sec"

def resource_path(relative_path: str) -> str:
    """
    Get the absolute path to a resource, works for development and PyInstaller
    
    Args:
        relative_path: Relative path to the resource
        
    Returns:
        Absolute path to the resource
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def calculate_clicks_per_time(interval_ms: int, time_unit: str = "hour") -> float:
    """
    Calculate how many clicks will be performed in a given time unit
    
    Args:
        interval_ms: Click interval in milliseconds
        time_unit: Time unit for calculation ("minute", "hour", or "day")
        
    Returns:
        float: Number of clicks in the specified time unit
    """
    clicks_per_second = 1000 / interval_ms
    
    if time_unit == "minute":
        return clicks_per_second * 60
    elif time_unit == "hour":
        return clicks_per_second * 3600
    elif time_unit == "day":
        return clicks_per_second * 86400
    else:
        return clicks_per_second

def throttle(func, delay: float):
    """
    Create a throttled version of a function that only executes once per delay period
    
    Args:
        func: The function to throttle
        delay: Minimum seconds between function executions
        
    Returns:
        function: Throttled function
    """
    last_call = 0
    
    def throttled(*args, **kwargs):
        nonlocal last_call
        current_time = time.time()
        
        if current_time - last_call >= delay:
            result = func(*args, **kwargs)
            last_call = current_time
            return result
            
    return throttled

class KeyboardListener:
    """Class to listen for keyboard events globally"""
    
    def __init__(self, on_key_press=None, on_key_release=None):
        """
        Initialize the keyboard listener
        
        Args:
            on_key_press: Callback for key press events
            on_key_release: Callback for key release events
        """
        self.on_key_press = on_key_press
        self.on_key_release = on_key_release
        self.listener = None
        
    def start(self):
        """Start listening for keyboard events"""
        if self.listener is None or not self.listener.is_alive():
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self.listener.daemon = True
            self.listener.start()
            logging.debug("Keyboard listener started")
            
    def stop(self):
        """Stop listening for keyboard events"""
        if self.listener and self.listener.is_alive():
            self.listener.stop()
            self.listener = None
            logging.debug("Keyboard listener stopped")
            
    def _on_press(self, key):
        """Handle key press events"""
        if self.on_key_press:
            return self.on_key_press(key)
            
    def _on_release(self, key):
        """Handle key release events"""
        if self.on_key_release:
            return self.on_key_release(key) 