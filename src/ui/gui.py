"""
GUI - Main Entry Point for the AutoClicker UI
"""

import logging
import os
from typing import Dict, Any
import threading

from ..core.autoclicker import AutoClicker
from ..core.utils import setup_logger, resource_path
from .main_window import MainWindow
from .splash_screen import SplashScreen

# Configure logging
logger = logging.getLogger(__name__)

class AutoClickerApp:
    """
    Main application class for the AutoClicker
    """
    def __init__(self):
        """
        Initialize the application
        """
        # Setup logging
        setup_logger(
            log_file="logs/app.log",
            log_level="INFO",
            max_size=1024 * 1024,  # 1MB
            backup_count=3
        )
        
        logger.info("Initializing AutoClicker application")
        
        # Initialize the core components
        self.autoclicker = AutoClicker(interval=1000)
        
        # Default UI settings
        self.ui_settings = {
            "title": "Getu Clicker",
            "width": 480,
            "height": 700,
            "icon_path": "assets/app_icon.png"
        }
        
        logger.info("Applied default settings to autoclicker")
        
        # Show splash screen first
        self._show_splash_screen()
        
        # Create the main window
        self.main_window = MainWindow(
            autoclicker=self.autoclicker,
            ui_settings=self.ui_settings
        )
        
        logger.info("Application initialized")
        
    def _show_splash_screen(self):
        """Show the splash screen"""
        splash_path = resource_path("assets/splash.png")
        
        if os.path.exists(splash_path):
            logger.info(f"Showing splash screen: {splash_path}")
            splash = SplashScreen(splash_path, display_time=2.5, scale_factor=0.85)
            splash_thread = threading.Thread(target=splash.show)
            splash_thread.start()
            splash_thread.join()  # Wait for splash screen to finish
        else:
            logger.warning(f"Splash image not found: {splash_path}")
        
    def run(self) -> None:
        """
        Run the application main loop
        """
        logger.info("Starting application")
        self.main_window.run() 