#!/usr/bin/env python3
"""
Browser Automation Script - Run multiple Chrome browsers in parallel
"""

import os
import sys
import argparse
import logging
import asyncio
from typing import List, Dict, Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the browser automation module
from src.browser.browser_controller import BrowserController, BrowserTask, BrowserType
from src.browser.example import run_browser_example, replay_recorded_session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Browser Automation - Control multiple Chrome instances in parallel"
    )
    
    # Browser configuration
    browser_group = parser.add_argument_group("Browser Configuration")
    browser_group.add_argument(
        "--browsers", "-b",
        type=int,
        default=3,
        help="Number of browser instances to create (default: 3)"
    )
    
    browser_group.add_argument(
        "--headless",
        action="store_true",
        help="Run browsers in headless mode"
    )
    
    # Action selection
    action_group = parser.add_argument_group("Action Selection")
    action_group.add_argument(
        "--example",
        action="store_true",
        help="Run the example automation script"
    )
    
    action_group.add_argument(
        "--replay",
        type=str,
        metavar="FILE",
        help="Replay a recorded browser session from a file"
    )
    
    # Recording options
    recording_group = parser.add_argument_group("Recording Options")
    recording_group.add_argument(
        "--record",
        action="store_true",
        default=True,
        help="Record browser sessions (default: enabled)"
    )
    
    recording_group.add_argument(
        "--no-record",
        action="store_true",
        help="Disable session recording"
    )
    
    recording_group.add_argument(
        "--recording-dir",
        type=str,
        default="browser_recordings",
        help="Directory to store recordings (default: browser_recordings)"
    )
    
    recording_group.add_argument(
        "--auto-replay",
        action="store_true",
        help="Automatically replay the recorded session after completion"
    )
    
    # List recordings
    recording_group.add_argument(
        "--list-recordings",
        action="store_true",
        help="List all available recorded sessions"
    )
    
    return parser.parse_args()


def list_recordings(recording_dir: str):
    """List all recorded sessions"""
    if not os.path.exists(recording_dir):
        logger.info(f"Recording directory {recording_dir} does not exist.")
        return
    
    recordings = []
    
    # Collect all recording files
    for filename in os.listdir(recording_dir):
        if filename.endswith(".json") and filename.startswith("browser_session_"):
            file_path = os.path.join(recording_dir, filename)
            file_size = os.path.getsize(file_path) / 1024  # KB
            mod_time = os.path.getmtime(file_path)
            
            recordings.append({
                "filename": filename,
                "path": file_path,
                "size": file_size,
                "modified": mod_time
            })
    
    # Sort by modification time (newest first)
    recordings.sort(key=lambda x: x["modified"], reverse=True)
    
    # Display recordings
    if recordings:
        logger.info(f"Found {len(recordings)} recordings in {recording_dir}:")
        print("\nAvailable recordings:")
        print("-" * 80)
        print(f"{'Filename':<30} {'Size (KB)':<10} {'Date Modified':<25} {'Full Path'}")
        print("-" * 80)
        
        for rec in recordings:
            from datetime import datetime
            date_str = datetime.fromtimestamp(rec["modified"]).strftime("%Y-%m-%d %H:%M:%S")
            print(f"{rec['filename']:<30} {rec['size']:<10.2f} {date_str:<25} {rec['path']}")
            
        print("-" * 80)
        print(f"To replay a recording, use: python {sys.argv[0]} --replay FILENAME\n")
    else:
        logger.info(f"No recordings found in {recording_dir}")


async def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Handle list recordings request
    if args.list_recordings:
        list_recordings(args.recording_dir)
        return 0
    
    logger.info("Starting browser automation")
    
    try:
        # Check for required Python packages
        try:
            import selenium
            logger.info(f"Using Selenium version {selenium.__version__}")
        except ImportError:
            logger.error("Selenium is required for browser automation")
            logger.error("Install with: pip install selenium")
            return 1
        
        # Determine whether to record
        record = args.record and not args.no_record
        
        if args.replay:
            # Replay a recorded session
            replay_path = args.replay
            if not os.path.isabs(replay_path) and not os.path.exists(replay_path):
                # Try looking in the recordings directory
                alt_path = os.path.join(args.recording_dir, args.replay)
                if os.path.exists(alt_path):
                    replay_path = alt_path
                else:
                    # Try adding .json extension
                    if not args.replay.endswith(".json"):
                        alt_path = os.path.join(args.recording_dir, f"{args.replay}.json")
                        if os.path.exists(alt_path):
                            replay_path = alt_path
                        else:
                            alt_path = os.path.join(args.recording_dir, f"browser_session_{args.replay}.json")
                            if os.path.exists(alt_path):
                                replay_path = alt_path
            
            if not os.path.exists(replay_path):
                logger.error(f"Recording file not found: {replay_path}")
                return 1
                
            logger.info(f"Replaying session from {replay_path}")
            await replay_recorded_session(replay_path, args.headless)
            
        elif args.example:
            # Run the example automation with recording
            logger.info(f"Running example with {args.browsers} browsers, headless: {args.headless}, recording: {record}")
            recording_file = await run_browser_example(args.headless, record)
            
            # Auto-replay if requested
            if args.auto_replay and recording_file:
                logger.info("Auto-replaying the recorded session...")
                await asyncio.sleep(2)  # Brief pause before replay
                await replay_recorded_session(recording_file, args.headless)
        else:
            logger.info("No automation selected. Use --example to run the example script or --replay to replay a recording.")
            logger.info("Use --help for more options.")
            
    except Exception as e:
        logger.error(f"Error in browser automation: {e}")
        return 1
        
    logger.info("Browser automation completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 