"""
Interactive Browser Module - Enables user-driven click position selection and automation
"""

import logging
import time
import threading
from typing import Callable, Tuple, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

logger = logging.getLogger(__name__)

def setup_interactive_browser(browser, browser_index: int, callback: Callable[[int, int, int], None]) -> None:
    """
    Set up browser for interactive coordinate selection
    
    Args:
        browser: Selenium WebDriver instance
        browser_index: Index of the browser instance
        callback: Function that will be called when coordinates are selected
                 Takes browser_index, x, y as parameters
    """
    try:
        # First clean up any previous setup to avoid duplications
        cleanup_interactive_browser(browser)
        
        # Inject JavaScript to capture click coordinates
        js_code = """
        // Remove any previous event handlers
        if (window._getCoordinatesHandler) {
            document.removeEventListener('click', window._getCoordinatesHandler);
        }
        
        // Create message container if it doesn't exist
        let msgContainer = document.getElementById('getu-clicker-message');
        if (!msgContainer) {
            msgContainer = document.createElement('div');
            msgContainer.id = 'getu-clicker-message';
            msgContainer.style.position = 'fixed';
            msgContainer.style.top = '10px';
            msgContainer.style.left = '50%';
            msgContainer.style.transform = 'translateX(-50%)';
            msgContainer.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
            msgContainer.style.color = 'white';
            msgContainer.style.padding = '10px 15px';
            msgContainer.style.borderRadius = '5px';
            msgContainer.style.zIndex = '9999';
            msgContainer.style.fontFamily = 'Arial, sans-serif';
            document.body.appendChild(msgContainer);
        }
        
        // Create crosshair overlay
        let overlay = document.getElementById('getu-clicker-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'getu-clicker-overlay';
            overlay.style.position = 'fixed';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.width = '100%';
            overlay.style.height = '100%';
            overlay.style.zIndex = '9998';
            overlay.style.background = 'transparent';
            overlay.style.cursor = 'crosshair';
            overlay.style.pointerEvents = 'auto';
            document.body.appendChild(overlay);
        }
        
        // Display instructions
        msgContainer.textContent = 'Click anywhere on this page to select a position for automated clicking';
        
        // Clear any previous coordinates
        window._selectedCoordinates = null;
        
        // Handler function for click events
        window._getCoordinatesHandler = function(e) {
            // Prevent default behavior
            e.preventDefault();
            e.stopPropagation();
            
            // Get coordinates relative to the viewport
            const x = e.clientX;
            const y = e.clientY;
            
            // Show selected position
            msgContainer.textContent = `Selected position: (${x}, ${y})`;
            
            // Store the coordinates in window object for retrieval
            window._selectedCoordinates = {
                browserIndex: window._browserIndex,
                x: x,
                y: y
            };
            
            // Show visual feedback
            const feedback = document.createElement('div');
            feedback.style.position = 'absolute';
            feedback.style.left = (x - 5) + 'px';
            feedback.style.top = (y - 5) + 'px';
            feedback.style.width = '10px';
            feedback.style.height = '10px';
            feedback.style.borderRadius = '50%';
            feedback.style.backgroundColor = 'red';
            feedback.style.zIndex = '9999';
            document.body.appendChild(feedback);
            
            // Fade out and remove after a delay
            setTimeout(() => {
                feedback.style.transition = 'opacity 0.5s ease-out';
                feedback.style.opacity = '0';
                setTimeout(() => document.body.removeChild(feedback), 500);
            }, 1000);
            
            // If using overlay, remove it after selection
            if (overlay) {
                overlay.style.pointerEvents = 'none';
                setTimeout(() => {
                    if (overlay && overlay.parentNode) {
                        overlay.parentNode.removeChild(overlay);
                    }
                }, 500);
            }
            
            return true;
        };
        
        // Store browser index in window object
        window._browserIndex = arguments[0];
        
        // Add click event handler to the overlay
        overlay.addEventListener('click', window._getCoordinatesHandler);
        
        // Return success
        return true;
        """
        
        # Execute JavaScript and set up browser index
        browser.execute_script(js_code, browser_index)
        
        logger.info(f"Interactive browser {browser_index} set up for coordinate selection")
        
        # Start a polling thread to check for coordinates
        def polling_thread():
            try:
                attempts = 0
                while getattr(browser, '_polling_active', True) and attempts < 100:  # Limit polling attempts
                    # Check if coordinates have been selected
                    coords = browser.execute_script("return window._selectedCoordinates;")
                    if coords and 'x' in coords and 'y' in coords:
                        # Reset stored coordinates
                        browser.execute_script("window._selectedCoordinates = null;")
                        # Call the callback
                        callback(browser_index, coords['x'], coords['y'])
                        # Clean up the UI after coordinates are selected
                        cleanup_interactive_browser(browser)
                        break
                    # Sleep to avoid high CPU usage
                    time.sleep(0.1)
                    attempts += 1
            except Exception as e:
                if not "has been closed" in str(e):  # Ignore errors when browser is closed
                    logger.error(f"Error in coordinate polling thread: {e}")
        
        # Start the polling thread
        browser._polling_active = True
        browser._polling_thread = threading.Thread(target=polling_thread, daemon=True)
        browser._polling_thread.start()
        
    except Exception as e:
        logger.error(f"Error setting up interactive browser {browser_index}: {e}")
        cleanup_interactive_browser(browser)
        
def perform_click_at_coordinates(browser, x: int, y: int) -> None:
    """
    Perform a click at the specified coordinates in the browser
    
    Args:
        browser: Selenium WebDriver instance
        x: X coordinate (pixels from left)
        y: Y coordinate (pixels from top)
    """
    try:
        # Use JavaScript to create and dispatch a click event at the specified coordinates
        js_code = """
        // Function to perform a click at coordinates
        function clickAtCoordinates(x, y) {
            // Create a mouse click event
            const clickEvent = new MouseEvent('click', {
                view: window,
                bubbles: true,
                cancelable: true,
                clientX: x,
                clientY: y
            });
            
            // Get the element at the coordinates
            const element = document.elementFromPoint(x, y);
            
            // Show visual feedback (optional)
            const feedback = document.createElement('div');
            feedback.style.position = 'absolute';
            feedback.style.left = (x - 5) + 'px';
            feedback.style.top = (y - 5) + 'px';
            feedback.style.width = '10px';
            feedback.style.height = '10px';
            feedback.style.borderRadius = '50%';
            feedback.style.backgroundColor = 'red';
            feedback.style.zIndex = '9999';
            feedback.style.pointerEvents = 'none';
            document.body.appendChild(feedback);
            
            // Animate and remove the feedback element
            setTimeout(() => {
                feedback.style.transition = 'opacity 0.5s';
                feedback.style.opacity = '0';
                setTimeout(() => {
                    if (feedback.parentNode) {
                        feedback.parentNode.removeChild(feedback);
                    }
                }, 500);
            }, 500);
            
            // If we found an element, dispatch the click
            if (element) {
                try {
                    // Try to click directly on the element (more reliable)
                    element.click();
                } catch (e) {
                    // Fall back to dispatching a click event
                    element.dispatchEvent(clickEvent);
                }
                return true;
            } else {
                return false;
            }
        }
        
        // Execute the click
        return clickAtCoordinates(arguments[0], arguments[1]);
        """
        
        # Execute the JavaScript to perform the click
        result = browser.execute_script(js_code, x, y)
        
        if result:
            logger.debug(f"Clicked at coordinates ({x}, {y})")
        else:
            # Try alternative method with ActionChains
            try:
                actions = ActionChains(browser)
                actions.move_by_offset(x, y)
                actions.click()
                actions.perform()
                logger.debug(f"Clicked at coordinates ({x}, {y}) using ActionChains")
            except Exception as e:
                logger.warning(f"No element found at coordinates ({x}, {y}): {e}")
            
    except Exception as e:
        logger.error(f"Error performing click at coordinates ({x}, {y}): {e}")
        raise

def cleanup_interactive_browser(browser) -> None:
    """
    Clean up browser after interactive coordinate selection
    
    Args:
        browser: Selenium WebDriver instance
    """
    try:
        # Stop the polling thread if it exists
        if hasattr(browser, '_polling_active'):
            browser._polling_active = False
            
        # Remove message container and event listeners
        browser.execute_script("""
        // Remove event listeners
        if (window._getCoordinatesHandler) {
            document.removeEventListener('click', window._getCoordinatesHandler);
            
            // If overlay exists, remove its event listener too
            const overlay = document.getElementById('getu-clicker-overlay');
            if (overlay) {
                overlay.removeEventListener('click', window._getCoordinatesHandler);
                overlay.parentNode.removeChild(overlay);
            }
            
            delete window._getCoordinatesHandler;
        }
        
        // Remove message container
        const msgContainer = document.getElementById('getu-clicker-message');
        if (msgContainer && msgContainer.parentNode) {
            msgContainer.parentNode.removeChild(msgContainer);
        }
        
        return true;
        """)
            
        logger.info("Interactive browser cleaned up")
        
    except Exception as e:
        logger.error(f"Error cleaning up interactive browser: {e}") 