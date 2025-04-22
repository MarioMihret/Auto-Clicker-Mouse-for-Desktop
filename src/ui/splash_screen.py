"""
Splash Screen - Shows a splash image during application startup
"""

import tkinter as tk
from PIL import Image, ImageTk
import os
import time
import logging
import customtkinter as ctk
from ..core.utils import resource_path

logger = logging.getLogger(__name__)

class SplashScreen:
    """Splash screen shown during application startup"""
    
    def __init__(self, image_path, display_time=2.0, scale_factor=0.4):
        """
        Initialize the splash screen
        
        Args:
            image_path: Path to the splash image
            display_time: Time to display the splash screen in seconds
            scale_factor: How large the splash should be relative to screen size (0-1)
        """
        self.image_path = image_path
        self.display_time = display_time
        self.scale_factor = scale_factor
        self.root = None
        
    def show(self):
        """Show the splash screen and return after the specified time"""
        if not os.path.exists(self.image_path):
            logger.warning(f"Splash image not found: {self.image_path}")
            return

        try:
            # Create the splash window
            self.root = tk.Tk()
            self.root.overrideredirect(True)  # No window decorations
            
            # Get screen dimensions
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Load the image
            original_img = Image.open(self.image_path)
            orig_width, orig_height = original_img.size
            
            # Calculate target size based on screen dimensions
            # Use the smaller dimension (width or height) to determine scale
            screen_min_dimension = min(screen_width, screen_height)
            target_size = int(screen_min_dimension * self.scale_factor)
            
            # Calculate scale factor to maintain aspect ratio
            if orig_width >= orig_height:
                # Landscape or square image
                target_width = target_size
                target_height = int(orig_height * (target_width / orig_width))
            else:
                # Portrait image
                target_height = target_size
                target_width = int(orig_width * (target_height / orig_height))
            
            # Resize image with high quality
            img = original_img.resize((target_width, target_height), Image.LANCZOS)
            width, height = img.size
            
            # Create PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Calculate position to center on screen
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            
            # Position and size the window
            self.root.geometry(f"{width}x{height}+{x}+{y}")
            
            # Create canvas for the image
            canvas = tk.Canvas(self.root, width=width, height=height, highlightthickness=0)
            canvas.pack()
            canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            
            # Show the window
            self.root.update()
            
            # Keep the splash visible for the specified time
            self.root.after(int(self.display_time * 1000), self.close)
            self.root.mainloop()
            
        except Exception as e:
            logger.error(f"Error displaying splash screen: {e}")
            if self.root:
                self.close()
            
    def close(self):
        """Close the splash screen"""
        if self.root:
            self.root.destroy()
            self.root = None 