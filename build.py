"""
Build script for Getu Clicker - Creates standalone executable
"""

import os
import sys
import shutil
import subprocess
import platform

def main():
    """Main build function"""
    # Make sure PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Create build directory if it doesn't exist
    if not os.path.exists("build"):
        os.makedirs("build")
    
    # Clean dist directory if it exists
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # Build command
    cmd = [
        "pyinstaller",
        "--name=GetuClicker",
        "--onefile",
        "--noconsole",
        "--add-data=assets/*;assets/",
        "--clean",
        "--log-level=INFO",
        "main.py"
    ]
    
    # Add icon if available
    icon_path = "assets/app_icon.ico" if platform.system() == "Windows" else "assets/app_icon.png"
    if os.path.exists(icon_path):
        cmd.insert(3, f"--icon={icon_path}")
        print(f"Using icon: {icon_path}")
    else:
        print(f"Icon not found at {icon_path}, proceeding without custom icon")
    
    # Run PyInstaller
    print(f"Building GetuClicker with command: {' '.join(cmd)}")
    subprocess.check_call(cmd)
    
    print("\nBuild complete! Executable is in the 'dist' folder.")
    print("For Windows: dist/GetuClicker.exe")
    print("For macOS/Linux: dist/GetuClicker")

if __name__ == "__main__":
    main() 