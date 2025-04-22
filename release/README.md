# Getu Clicker

A professional auto-clicking tool developed by Mario M.

![Getu Clicker](assets/splash.png)

## Features

- Multiple position clicking support
- Sequential or simultaneous clicking modes
- Configurable click interval (0.05 to 5 seconds)
- Duration setting for auto-stopping
- Keyboard shortcuts (F6 to toggle, Esc to stop)
- Mobile-responsive interface with scrolling support

## Installation

### Option 1: Download the Executable (Recommended)

1. Download the latest release from the [Releases](https://github.com/mariom/getuclicker/releases) page
2. Extract the ZIP file
3. Run `GetuClicker.exe` (Windows) or `GetuClicker` (macOS/Linux)

### Option 2: Run from Source

1. Clone the repository: `git clone https://github.com/mariom/getuclicker.git`
2. Navigate to the project directory: `cd getuclicker`
3. Install the dependencies: `pip install -r requirements.txt`
4. Run the application: `python main.py`

### Option 3: Build from Source

1. Clone the repository: `git clone https://github.com/mariom/getuclicker.git`
2. Navigate to the project directory: `cd getuclicker`
3. Run the build script: `python build.py`
4. The executable will be in the `dist` folder

## Usage

1. **Select Positions**: Click the "Select Positions" button and click on the screen where you want clicks to occur. Press Enter to confirm.
2. **Configure Settings**:
   - Set the click interval (time between clicks) using the slider
   - Set the duration (how long to run) in minutes (0 = indefinite)
   - Toggle "Multi-click Mode" to click all positions simultaneously
3. **Start/Stop Clicking**:
   - Click the "Start" button or press F6 to begin
   - Click the "Stop" button, press F6 again, or press Esc to stop

## Keyboard Shortcuts

- **F6**: Start/Stop clicking
- **Esc**: Emergency stop (works even when the app is in the background)
- **Enter**: Confirm position selection
- **F8**: Exit application

## Requirements

- Windows, macOS, or Linux
- Python 3.8+ (if running from source)
- Required packages (if running from source):
  - customtkinter
  - pyautogui
  - pynput
  - pillow

## License

© 2025 Mario M. All rights reserved. 