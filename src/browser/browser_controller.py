"""
Browser Controller - Manages multiple browser instances and tasks
"""

import logging
import threading
import time
import json
import os
from typing import List, Callable, Dict, Any, Optional, Union
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# Import necessary browser automation libraries
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

logger = logging.getLogger(__name__)


class BrowserType(Enum):
    """Browser type enumeration"""
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"


class TaskAction(Enum):
    """Task action types for recording"""
    NAVIGATE = "navigate"
    CLICK = "click"
    FILL = "fill"
    WAIT = "wait"
    SCROLL = "scroll"
    CUSTOM = "custom"


class BrowserTask:
    """Represents a task to be executed in a browser"""
    def __init__(self, name: str, func: Callable, args: tuple = (), kwargs: Dict[str, Any] = None,
                action_type: TaskAction = TaskAction.CUSTOM, description: str = None):
        """
        Initialize a browser task
        
        Args:
            name: Task name for identification
            func: Function to execute
            args: Positional arguments to pass to the function
            kwargs: Keyword arguments to pass to the function
            action_type: Type of action for recording purposes
            description: Human-readable description of the task
        """
        self.name = name
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.result = None
        self.error = None
        self.completed = False
        self.action_type = action_type
        self.description = description or name
        self.start_time = None
        self.end_time = None
        
    def execute(self, browser) -> Any:
        """Execute the task with the given browser instance"""
        try:
            self.start_time = time.time()
            self.result = self.func(browser, *self.args, **self.kwargs)
            self.end_time = time.time()
            self.completed = True
            logger.info(f"Task '{self.name}' completed in {self.end_time - self.start_time:.2f}s")
            return self.result
        except Exception as e:
            self.error = e
            self.end_time = time.time()
            logger.error(f"Error executing task {self.name}: {e}")
            raise
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for recording"""
        return {
            "name": self.name,
            "action_type": self.action_type.value,
            "description": self.description,
            "args": self.args,
            "kwargs": {k: v for k, v in self.kwargs.items() if isinstance(v, (str, int, float, bool, list, dict))},
            "completed": self.completed,
            "execution_time": round(self.end_time - self.start_time, 2) if self.end_time and self.start_time else None
        }


class BrowserSession:
    """Represents a single browser session"""
    def __init__(self, browser, index: int, url: str = None):
        """Initialize browser session"""
        self.browser = browser
        self.index = index
        self.initial_url = url
        self.tasks_history = []
        self.start_time = datetime.now()
        
    def add_task_record(self, task: BrowserTask, browser_index: int) -> None:
        """Add a task to history"""
        task_record = task.to_dict()
        task_record["browser_index"] = browser_index
        task_record["timestamp"] = datetime.now().isoformat()
        self.tasks_history.append(task_record)


class BrowserController:
    """
    Controls multiple browser instances for automation
    """
    def __init__(self, recording_enabled: bool = True, recording_dir: str = "browser_recordings"):
        """Initialize the browser controller"""
        self.browsers = []
        self.browser_sessions = []
        self.tasks = []
        self.running = False
        self.executor = None
        self.recording_enabled = recording_enabled
        self.recording_dir = recording_dir
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create recordings directory if it doesn't exist
        if recording_enabled and not os.path.exists(recording_dir):
            os.makedirs(recording_dir)
            logger.info(f"Created recording directory: {recording_dir}")
        
        # Check if Selenium is available
        if not SELENIUM_AVAILABLE:
            logger.warning("Selenium is not installed. Please install it with: pip install selenium")
        
    def create_browsers(self, count: int = 1, browser_type: BrowserType = BrowserType.CHROME, 
                       headless: bool = False, urls: List[str] = None) -> List[Any]:
        """
        Create multiple browser instances
        
        Args:
            count: Number of browser instances to create
            browser_type: Type of browser to create
            headless: Whether to run browsers in headless mode
            urls: Initial URLs to open for each browser
            
        Returns:
            List of browser instances
        """
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is required for browser automation. Install with: pip install selenium")
        
        if urls and len(urls) != count:
            raise ValueError("If provided, the number of URLs must match the number of browsers")
            
        browsers = []
        
        for i in range(count):
            try:
                # Set up browser options
                if browser_type == BrowserType.CHROME:
                    options = Options()
                    if headless:
                        options.add_argument("--headless=new")  # Use new headless mode if available
                    options.add_argument("--no-sandbox")
                    options.add_argument("--disable-dev-shm-usage")
                    options.add_argument("--disable-extensions")
                    options.add_argument("--disable-gpu")
                    options.add_argument("--window-size=1920,1080")
                    
                    # Create browser instance
                    browser = webdriver.Chrome(options=options)
                    
                    # Set window position to avoid overlap
                    browser.set_window_position(i * 50, i * 50)
                    
                    # Open initial URL if provided
                    initial_url = urls[i] if urls else "about:blank"
                    browser.get(initial_url)
                    
                    # Create browser session
                    session = BrowserSession(browser, i, initial_url)
                    self.browser_sessions.append(session)
                    
                    browsers.append(browser)
                    logger.info(f"Created Chrome browser instance {i+1}/{count}")
                else:
                    # Add support for other browser types as needed
                    logger.warning(f"Browser type {browser_type} not fully supported yet")
            except Exception as e:
                logger.error(f"Failed to create browser instance {i+1}: {e}")
                
        self.browsers = browsers
        return browsers
    
    def add_task(self, task: BrowserTask, browser_index: int) -> None:
        """
        Add a task to be executed on a specific browser
        
        Args:
            task: Task to execute
            browser_index: Index of the browser to execute the task on
        """
        if browser_index >= len(self.browsers):
            raise IndexError(f"Browser index {browser_index} is out of range")
            
        self.tasks.append((task, browser_index))
        
    def execute_all_tasks_threaded(self) -> None:
        """Execute all tasks in parallel using threading"""
        if not self.tasks:
            logger.warning("No tasks to execute")
            return
            
        threads = []
        
        for task, browser_index in self.tasks:
            browser = self.browsers[browser_index]
            thread = threading.Thread(
                target=self._execute_and_record_task,
                args=(task, browser, browser_index),
                name=f"BrowserTask-{task.name}-{browser_index}"
            )
            threads.append(thread)
            
        # Start all threads
        for thread in threads:
            thread.start()
            
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
        logger.info(f"Completed {len(threads)} browser tasks")
        
        # Save recordings if enabled
        if self.recording_enabled:
            self.save_session_recording()
            
    def _execute_and_record_task(self, task, browser, browser_index):
        """Execute a task and record the result"""
        try:
            task.execute(browser)
            # Record task execution
            if self.recording_enabled and browser_index < len(self.browser_sessions):
                self.browser_sessions[browser_index].add_task_record(task, browser_index)
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
        
    async def execute_all_tasks_async(self) -> List[Any]:
        """Execute all tasks in parallel using asyncio and threading"""
        if not self.tasks:
            logger.warning("No tasks to execute")
            return []
            
        loop = asyncio.get_event_loop()
        self.executor = ThreadPoolExecutor(max_workers=len(self.tasks))
        results = []
        
        # Create futures for each task
        futures = []
        for task, browser_index in self.tasks:
            browser = self.browsers[browser_index]
            future = loop.run_in_executor(
                self.executor,
                self._execute_and_record_task,
                task,
                browser,
                browser_index
            )
            futures.append(future)
            
        # Wait for all futures to complete
        await asyncio.gather(*futures, return_exceptions=True)
        
        # Save recordings if enabled
        if self.recording_enabled:
            self.save_session_recording()
            
        return results
    
    def save_session_recording(self) -> str:
        """Save the session recording to a file"""
        if not self.recording_enabled:
            return None
            
        # Prepare recording data
        recording_data = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "browser_count": len(self.browsers),
            "browser_sessions": []
        }
        
        # Add browser session data
        for session in self.browser_sessions:
            session_data = {
                "browser_index": session.index,
                "initial_url": session.initial_url,
                "start_time": session.start_time.isoformat(),
                "tasks": session.tasks_history
            }
            recording_data["browser_sessions"].append(session_data)
            
        # Save to file
        filename = os.path.join(self.recording_dir, f"browser_session_{self.session_id}.json")
        with open(filename, "w") as f:
            json.dump(recording_data, f, indent=2)
            
        logger.info(f"Saved session recording to {filename}")
        return filename
    
    def load_session_recording(self, filename: str) -> Dict[str, Any]:
        """Load a session recording from a file"""
        with open(filename, "r") as f:
            recording_data = json.load(f)
            
        logger.info(f"Loaded session recording from {filename}")
        return recording_data
        
    def close_all_browsers(self) -> None:
        """Close all browser instances"""
        for i, browser in enumerate(self.browsers):
            try:
                browser.quit()
                logger.info(f"Closed browser instance {i+1}")
            except Exception as e:
                logger.error(f"Error closing browser instance {i+1}: {e}")
                
        self.browsers = []
        
        # Clean up executor if it exists
        if self.executor:
            self.executor.shutdown(wait=True)
            self.executor = None
            
    def __del__(self):
        """Clean up resources on deletion"""
        self.close_all_browsers()


# Example browser automation tasks
def navigate_to_url(browser, url: str) -> None:
    """Navigate to a URL"""
    browser.get(url)
    
def click_element(browser, selector: str, by: By = By.CSS_SELECTOR, timeout: int = 10) -> None:
    """Click an element on the page"""
    element = WebDriverWait(browser, timeout).until(
        EC.element_to_be_clickable((by, selector))
    )
    element.click()
    
def fill_form_field(browser, selector: str, text: str, by: By = By.CSS_SELECTOR, timeout: int = 10) -> None:
    """Fill a form field with text"""
    element = WebDriverWait(browser, timeout).until(
        EC.element_to_be_clickable((by, selector))
    )
    element.clear()
    element.send_keys(text) 