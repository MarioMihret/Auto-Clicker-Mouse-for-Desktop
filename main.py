#!/usr/bin/env python3
"""
Autoclicker - Main Entry Point
A utility for automating mouse clicks at configurable intervals
"""

import sys


import os



# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.gui import AutoClickerApp

def main():
    """
    Main entry point for the application
    """
    app = AutoClickerApp()
    app.run()

if __name__ == "__main__":
    main() 