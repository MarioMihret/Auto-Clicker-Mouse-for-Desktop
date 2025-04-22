"""
AutoClicker - Core clicking functionality
"""

import time
import threading
import logging
from typing import Optional, Callable, Literal, Tuple, List

import pyautogui
from pynput import keyboard

# Configure pyautogui
pyautogui.FAILSAFE = True  # Move mouse to corner to abort

# Configure logging
logger = logging.getLogger(__name__)

class AutoClicker:
    """
    Main class that handles the automatic clicking functionality
    """
    def __init__(self, interval: int = 1000):
        """
        Initialize the AutoClicker
        
        Args:
            interval: Time between clicks in milliseconds (default: 1000ms)
        """
        self.interval = interval  # in milliseconds
        self.positions: List[Tuple[int, int]] = []
        self.is_running = False
        self.stop_flag = threading.Event()
        self.click_thread = None
        self.click_threads = []
        self.duration = 0  # in seconds (0 = indefinite)
        self.multi_click_enabled = False
        self.running = False
        self.click_type: Literal["single", "double"] = "single"
        self.stop_event = threading.Event()
        self.fixed_positions: List[Tuple[int, int]] = []
        self.use_fixed_positions = False
        self.current_position_index = 0
        self.on_stop_callback = None
        # For multiple clicks
        self.multi_clicking = False
        self.keyboard_listener = None
        
        logger.info(f"AutoClicker initialized with interval={interval}ms")
        
    def set_on_stop_callback(self, callback: Callable):
        """
        Set a callback function to be called when the autoclicker is stopped
        
        Args:
            callback: Function to call when autoclicker stops
        """
        self.on_stop_callback = callback
        
    def start(self) -> None:
        """
        Start the auto-clicking process
        """
        if self.is_running:
            logger.info("AutoClicker is already running")
            return
            
        self.is_running = True
        self.stop_flag.clear()
        self.current_position_index = 0
        
        if self.multi_click_enabled and self.positions:
            # Start a separate thread for each position
            for position in self.positions:
                thread = threading.Thread(
                    target=self._position_clicking_loop,
                    args=(position,),
                    daemon=True
                )
                thread.start()
                self.click_threads.append(thread)
            logger.info(f"Started multi-clicking at {len(self.positions)} positions")
        else:
            # Start a single clicking thread
            self.click_thread = threading.Thread(
                target=self._clicking_loop,
                daemon=True
            )
            self.click_thread.start()
            
            if self.positions:
                logger.info(f"Started clicking at {len(self.positions)} fixed positions")
            else:
                logger.info("Started clicking at cursor position")
        
        # Start global keyboard listener for Escape key
        self._start_keyboard_listener()
        
        # If duration is set, start a timer to stop the clicker
        if self.duration > 0:
            stop_timer = threading.Timer(self.duration, self.stop)
            stop_timer.daemon = True
            stop_timer.start()
            logger.debug(f"Started auto-stop timer for {self.duration} seconds")
        
    def _clicking_loop(self) -> None:
        """
        Private method that runs the clicking loop in a separate thread
        """
        start_time = time.time()
        
        try:
            while not self.stop_flag.is_set():
                if self.positions:
                    # Click at each fixed position in sequence
                    for position in self.positions:
                        if self.stop_flag.is_set():
                            break
                        self._perform_click(position)
                        time.sleep(self.interval / 1000)
                else:
                    # Click at current cursor position
                    self._perform_click()
                    # Wait for the specified interval
                    time.sleep(self.interval / 1000)
                
                # Check if we've reached the duration limit
                if self.duration > 0 and (time.time() - start_time) >= self.duration:
                    logger.info(f"Clicking stopped after duration of {self.duration} seconds")
                    self.is_running = False
                    break
        except Exception as e:
            logger.error(f"Error in clicking loop: {e}")
            self.is_running = False
        
    def _position_clicking_loop(self, position):
        """Clicking loop for a specific position, used in multi-click mode"""
        start_time = time.time()
        
        try:
            while not self.stop_flag.is_set():
                self._perform_click(position)
                time.sleep(self.interval / 1000)
                
                # Check if we've reached the duration limit
                if self.duration > 0 and (time.time() - start_time) >= self.duration:
                    break
        except Exception as e:
            logger.error(f"Error in position clicking loop: {e}")
    
    def _perform_click(self, position=None):
        """Perform the actual mouse click"""
        try:
            if position:
                # Move to the specific position and click
                pyautogui.click(x=position[0], y=position[1])
            else:
                # Click at current position
                pyautogui.click()
        except Exception as e:
            logger.error(f"Failed to perform click: {e}")
        
    def stop(self) -> None:
        """
        Stop the auto-clicking process
        """
        if not self.is_running:
            logger.info("AutoClicker is not running")
            return
            
        logger.info("Stopping AutoClicker")
        self.is_running = False
        self.stop_flag.set()
        
        # Stop keyboard listener
        self._stop_keyboard_listener()
        
        # Wait for clicking thread to finish
        if self.click_thread and self.click_thread.is_alive():
            self.click_thread.join(timeout=1.0)
        
        # Wait for all multi-click threads
        for thread in self.click_threads:
            if thread.is_alive():
                thread.join(timeout=1.0)
        self.click_threads = []
            
        # Call the stop callback if set
        if self.on_stop_callback:
            self.on_stop_callback()
            
    def _start_keyboard_listener(self):
        """Start keyboard listener for escape key"""
        def on_key_release(key):
            try:
                if key == keyboard.Key.esc and self.is_running:
                    logger.info("Escape key pressed, stopping autoclicker")
                    self.stop()
                    return True
            except Exception as e:
                logger.error(f"Error handling keyboard event: {e}")
            return True
        
        # Create keyboard listener
        self.keyboard_listener = keyboard.Listener(on_release=on_key_release)
        self.keyboard_listener.daemon = True
        self.keyboard_listener.start()
        logger.debug("Started global keyboard listener")
    
    def _stop_keyboard_listener(self):
        """Stop keyboard listener if active"""
        if hasattr(self, 'keyboard_listener') and self.keyboard_listener and hasattr(self.keyboard_listener, 'is_alive') and self.keyboard_listener.is_alive():
            self.keyboard_listener.stop()
            self.keyboard_listener = None
            logger.debug("Stopped global keyboard listener")
            
    def toggle(self) -> bool:
        """
        Toggle between starting and stopping
        
        Returns:
            bool: True if now running, False if now stopped
        """
        if self.is_running:
            self.stop()
            return False
        else:
            self.start()
            return True
            
    def set_interval(self, interval_ms: int) -> None:
        """
        Set the interval between clicks in milliseconds
        
        Args:
            interval_ms: Interval in milliseconds
        """
        if interval_ms < 100:
            logger.warning(f"Interval too small ({interval_ms}ms), setting to minimum (100ms)")
            interval_ms = 100
            
        logger.info(f"Setting click interval to {interval_ms}ms")
        self.interval = interval_ms
        
    def set_positions(self, positions: List[Tuple[int, int]]) -> None:
        """
        Set fixed positions for clicking
        
        Args:
            positions: List of (x, y) coordinates
        """
        self.positions = positions
        self.multi_click_enabled = len(positions) > 0
        if self.multi_click_enabled:
            logger.info(f"Set {len(positions)} fixed positions")
        else:
            logger.info("No positions set, will use cursor position")
        
    def clear_positions(self) -> None:
        """
        Clear the fixed positions and use cursor position
        """
        self.positions = []
        self.multi_click_enabled = False
        logger.info("Cleared fixed positions")
        
    def set_duration(self, minutes: int) -> None:
        """
        Set the duration for clicking in minutes (0 = indefinite)
        
        Args:
            minutes: Duration in minutes, 0 means run indefinitely
        """
        if minutes < 0:
            logger.warning(f"Invalid duration ({minutes} minutes), setting to 0 (indefinite)")
            minutes = 0
            
        self.duration = minutes * 60 if minutes > 0 else 0
        logger.info(f"Duration set to {minutes} minutes ({self.duration} seconds)")
        
    def set_multi_clicking(self, enabled: bool) -> None:
        """
        Set whether to use multi-clicking mode (separate threads for each position)
        
        Args:
            enabled: Whether to enable multi-clicking mode
        """
        self.multi_clicking = enabled
        logger.info(f"Multi-clicking mode {'enabled' if enabled else 'disabled'}") 