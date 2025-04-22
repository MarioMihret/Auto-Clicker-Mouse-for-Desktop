"""
Example demonstrating browser automation with multiple Chrome instances
"""

import time
import asyncio
import logging
import argparse
import os
from typing import List

from .browser_controller import (
    BrowserController, BrowserTask, BrowserType, TaskAction,
    navigate_to_url, click_element, fill_form_field
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def perform_search(browser, search_term: str) -> None:
    """Perform a Google search"""
    # Navigate to Google
    browser.get("https://www.google.com")
    
    try:
        # Accept cookies if prompt appears (for EU users)
        click_element(browser, "button[id='L2AGLb']", timeout=2)
    except Exception:
        logger.info("No cookie consent needed or already accepted")
    
    # Find the search input and type the search term
    fill_form_field(browser, "input[name='q']", search_term)
    
    # Press enter (submit the form)
    fill_form_field(browser, "input[name='q']", "\n")
    
    # Wait for results to load
    time.sleep(2)
    
    logger.info(f"Completed search for '{search_term}'")


def scroll_page(browser, scroll_amount: int = 800) -> None:
    """Scroll the page down"""
    browser.execute_script(f"window.scrollBy(0, {scroll_amount});")
    time.sleep(1)


async def run_browser_example(headless: bool = False, record: bool = True):
    """Run the browser automation example"""
    logger.info("Starting browser automation example")
    
    # Create browser controller with recording enabled
    controller = BrowserController(recording_enabled=record)
    
    # Define URLs for each browser
    websites = [
        "https://www.example.com",
        "https://www.wikipedia.org",
        "https://www.github.com"
    ]
    
    try:
        # Create multiple browser instances
        browsers = controller.create_browsers(
            count=3,
            browser_type=BrowserType.CHROME,
            headless=headless,
            urls=websites
        )
        
        logger.info(f"Created {len(browsers)} browser instances")
        
        # Define tasks for each browser with proper task action types
        tasks = [
            # Browser 1: Perform search
            BrowserTask(
                name="search_task",
                func=perform_search,
                args=("automation tutorial",),
                action_type=TaskAction.CUSTOM,
                description="Search for 'automation tutorial' on Google"
            ),
            
            # Browser 2: Navigate and click
            BrowserTask(
                name="navigation_task",
                func=navigate_to_url,
                args=("https://www.wikipedia.org",),
                action_type=TaskAction.NAVIGATE,
                description="Navigate to Wikipedia"
            ),
            
            # Browser 2: Click English Wikipedia
            BrowserTask(
                name="click_en_wiki",
                func=click_element,
                args=("a#js-link-box-en",),
                kwargs={"timeout": 5},
                action_type=TaskAction.CLICK,
                description="Click on English Wikipedia link"
            ),
            
            # Browser 3: Multiple actions as separate tasks
            BrowserTask(
                name="github_navigate",
                func=navigate_to_url,
                args=("https://github.com",),
                action_type=TaskAction.NAVIGATE,
                description="Navigate to GitHub"
            ),
            
            BrowserTask(
                name="github_search",
                func=fill_form_field,
                args=("input[name='q']", "python automation"),
                action_type=TaskAction.FILL,
                description="Search for 'python automation' on GitHub"
            ),
            
            BrowserTask(
                name="github_submit",
                func=fill_form_field,
                args=("input[name='q']", "\n"),
                action_type=TaskAction.FILL,
                description="Submit GitHub search"
            ),
            
            BrowserTask(
                name="github_scroll",
                func=scroll_page,
                args=(500,),
                action_type=TaskAction.SCROLL,
                description="Scroll down GitHub search results"
            )
        ]
        
        # Add tasks to controller with proper browser indices
        # First task to browser 0
        controller.add_task(tasks[0], 0)
        
        # Second and third tasks to browser 1
        controller.add_task(tasks[1], 1)
        controller.add_task(tasks[2], 1)
        
        # Remaining tasks to browser 2
        for task in tasks[3:]:
            controller.add_task(task, 2)
        
        # Execute tasks in parallel
        logger.info("Executing browser tasks in parallel")
        await controller.execute_all_tasks_async()
        
        # Leave browsers open for a moment to observe results
        logger.info("Tasks completed, waiting 5 seconds before closing browsers")
        await asyncio.sleep(5)
        
        # Get the recording file if recording was enabled
        if record:
            recording_file = controller.save_session_recording()
            logger.info(f"Session recorded to: {recording_file}")
            return recording_file
        
    except Exception as e:
        logger.error(f"Error in browser automation example: {e}")
        
    finally:
        # Clean up
        controller.close_all_browsers()
        logger.info("Browser automation example completed")


async def replay_recorded_session(recording_file: str, headless: bool = False):
    """Replay a previously recorded browser session"""
    logger.info(f"Replaying recorded session from {recording_file}")
    
    if not os.path.exists(recording_file):
        logger.error(f"Recording file not found: {recording_file}")
        return
    
    # Create a new browser controller
    controller = BrowserController(recording_enabled=False)
    
    try:
        # Load the recording
        recording = controller.load_session_recording(recording_file)
        
        # Count browsers needed
        browser_count = recording.get("browser_count", 3)
        
        # Create browsers
        browsers = controller.create_browsers(
            count=browser_count,
            browser_type=BrowserType.CHROME,
            headless=headless
        )
        
        logger.info(f"Created {len(browsers)} browser instances for replay")
        
        # Process each browser session
        for session in recording["browser_sessions"]:
            browser_index = session["browser_index"]
            
            # Skip if browser index is out of range
            if browser_index >= len(browsers):
                logger.warning(f"Browser index {browser_index} out of range, skipping")
                continue
            
            # Get the browser
            browser = browsers[browser_index]
            
            # Navigate to initial URL if provided
            if session["initial_url"] and session["initial_url"] != "about:blank":
                logger.info(f"Navigating browser {browser_index} to {session['initial_url']}")
                browser.get(session["initial_url"])
            
            # Process tasks
            for task_data in session["tasks"]:
                logger.info(f"Replaying task: {task_data['description']}")
                
                # Create a corresponding task based on action type
                if task_data["action_type"] == TaskAction.NAVIGATE.value:
                    # Navigate task
                    url = task_data["args"][0]
                    task = BrowserTask(
                        name=f"replay_{task_data['name']}",
                        func=navigate_to_url,
                        args=(url,),
                        action_type=TaskAction.NAVIGATE,
                        description=f"Replay: {task_data['description']}"
                    )
                    
                elif task_data["action_type"] == TaskAction.CLICK.value:
                    # Click task
                    selector = task_data["args"][0]
                    timeout = task_data["kwargs"].get("timeout", 10)
                    task = BrowserTask(
                        name=f"replay_{task_data['name']}",
                        func=click_element,
                        args=(selector,),
                        kwargs={"timeout": timeout},
                        action_type=TaskAction.CLICK,
                        description=f"Replay: {task_data['description']}"
                    )
                    
                elif task_data["action_type"] == TaskAction.FILL.value:
                    # Fill form task
                    selector = task_data["args"][0]
                    text = task_data["args"][1] if len(task_data["args"]) > 1 else ""
                    timeout = task_data["kwargs"].get("timeout", 10)
                    task = BrowserTask(
                        name=f"replay_{task_data['name']}",
                        func=fill_form_field,
                        args=(selector, text),
                        kwargs={"timeout": timeout},
                        action_type=TaskAction.FILL,
                        description=f"Replay: {task_data['description']}"
                    )
                    
                elif task_data["action_type"] == TaskAction.SCROLL.value:
                    # Scroll task
                    amount = task_data["args"][0] if task_data["args"] else 300
                    task = BrowserTask(
                        name=f"replay_{task_data['name']}",
                        func=scroll_page,
                        args=(amount,),
                        action_type=TaskAction.SCROLL,
                        description=f"Replay: {task_data['description']}"
                    )
                    
                else:
                    # Skip unknown action types
                    logger.warning(f"Unknown action type: {task_data['action_type']}, skipping")
                    continue
                
                # Add task to controller
                controller.add_task(task, browser_index)
                
        # Execute all tasks
        if controller.tasks:
            logger.info(f"Executing {len(controller.tasks)} replay tasks")
            await controller.execute_all_tasks_async()
            
            # Wait a bit to observe results
            logger.info("Replay completed, waiting 5 seconds before closing browsers")
            await asyncio.sleep(5)
        else:
            logger.warning("No tasks to replay")
            
    except Exception as e:
        logger.error(f"Error replaying session: {e}")
        
    finally:
        # Clean up
        controller.close_all_browsers()
        logger.info("Session replay completed")


async def main(args):
    """Main entry point for examples"""
    if args.replay:
        # Replay a specific recording
        await replay_recorded_session(args.replay, args.headless)
    else:
        # Run a new example
        recording_file = await run_browser_example(args.headless, not args.no_record)
        
        # Offer to replay the session
        if recording_file and args.auto_replay:
            logger.info("Auto-replaying the recorded session...")
            await asyncio.sleep(2)  # Brief pause before replay
            await replay_recorded_session(recording_file, args.headless)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Browser Automation Examples")
    parser.add_argument("--headless", action="store_true", help="Run browsers in headless mode")
    parser.add_argument("--no-record", action="store_true", help="Disable session recording")
    parser.add_argument("--replay", type=str, help="Replay a specific recording file")
    parser.add_argument("--auto-replay", action="store_true", help="Automatically replay the session after recording")
    return parser.parse_args()


if __name__ == "__main__":
    asyncio.run(main(parse_args())) 