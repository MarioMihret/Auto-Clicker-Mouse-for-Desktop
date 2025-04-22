"""
Position Picker - Helper for selecting click positions
"""

import threading
import time
import logging
from typing import Callable, Tuple, List
from pynput import mouse
from pynput import keyboard
import tkinter as tk

logger = logging.getLogger(__name__)

class PositionPicker:
    """
    Helper class for picking positions on the screen
    """
    def __init__(self, on_complete: Callable[[List[Tuple[int, int]]], None], on_cancel: Callable[[], None]):
        """
        Initialize the position picker
        
        Args:
            on_complete: Callback when positions are picked, receives list of (x, y) coordinates
            on_cancel: Callback when position picking is canceled
        """
        self.on_complete = on_complete
        self.on_cancel = on_cancel
        self.picking = False
        self.positions = []
        self.markers = []
        
    def start(self):
        """
        Start the position picking process
        """
        if self.picking:
            return
            
        self.picking = True
        self.positions = []
        self.markers = []
        logger.info("Position picking started, click to select positions, press Enter to finish...")
        
        # Start a thread to wait for the clicks
        threading.Thread(target=self._pick_position_thread, daemon=True).start()
        
    def _pick_position_thread(self):
        """Background thread for position picking"""
        try:
            # Wait a moment for the window to minimize
            time.sleep(0.5)
            
            # Create a mouse listener that waits for clicks
            def on_click(x, y, button, pressed):
                if not pressed and button == mouse.Button.left:  # On left button release
                    self.positions.append((x, y))
                    logger.info(f"Position added: ({x}, {y}), total positions: {len(self.positions)}")
                    self._show_marker(x, y)
                    return True  # Continue listening
            
            # Create a keyboard listener for Enter key
            def on_release(key):
                if key == keyboard.Key.enter:
                    logger.info(f"Enter pressed, finalizing selection with {len(self.positions)} positions")
                    return False  # Stop listening
                if key == keyboard.Key.esc:
                    logger.info("Escape pressed, canceling selection")
                    self.positions = []
                    self.picking = False
                    self._remove_all_markers()
                    self.on_cancel()
                    return False  # Stop listening
                return True  # Continue listening
                    
            # Start both listeners
            mouse_listener = mouse.Listener(on_click=on_click)
            keyboard_listener = keyboard.Listener(on_release=on_release)
            
            mouse_listener.start()
            keyboard_listener.start()
            
            # Wait for keyboard listener to finish (Enter or Esc pressed)
            keyboard_listener.join()
            
            # Stop the mouse listener
            mouse_listener.stop()
            
            # If we have positions and we're still in picking mode
            if self.positions and self.picking:
                self.picking = False
                self._remove_all_markers()
                self.on_complete(self.positions)
                
        except Exception as e:
            logger.error(f"Error in position picking: {e}")
            self.picking = False
            self._remove_all_markers()
            self.on_cancel()
            
    def _show_marker(self, x, y):
        """Display a visual marker at the clicked position"""
        marker = tk.Toplevel()
        marker.overrideredirect(True)  # No window decorations
        marker.attributes('-topmost', True)  # Always on top
        
        # Calculate position (offset by half the size to center)
        size = 20  # Increase marker size for better visibility
        marker.geometry(f"{size}x{size}+{x-size//2}+{y-size//2}")
        
        # Create a canvas with a red circle
        canvas = tk.Canvas(marker, width=size, height=size, bg='white',
                          highlightthickness=0)
                          
        # Create a more visible dot with border for contrast
        canvas.create_oval(2, 2, size-2, size-2, fill='red', outline='black', width=2)
        canvas.pack()
        
        # Try to make the window transparent (platform specific)
        try:
            # For Windows
            marker.attributes('-transparentcolor', 'white')
        except:
            pass
            
        self.markers.append(marker)
        
    def _remove_all_markers(self):
        """Remove all position markers"""
        for marker in self.markers:
            try:
                marker.destroy()
            except:
                pass
        self.markers = []
            
    def cancel(self):
        """Cancel the position picking process"""
        if self.picking:
            self.picking = False
            self.positions = []
            self._remove_all_markers()
            self.on_cancel() 