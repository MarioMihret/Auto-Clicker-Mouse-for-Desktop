import os
import shutil
import sys
import platform
from pathlib import Path

def main():
    print("Preparing release package for Getu Clicker...")
    
    # Determine system type
    system = platform.system()
    is_windows = system == "Windows"
    
    # Create release directory
    release_dir = Path("release")
    if release_dir.exists():
        print(f"Cleaning existing release directory: {release_dir}")
        shutil.rmtree(release_dir)
    
    release_dir.mkdir(exist_ok=True)
    print(f"Created release directory: {release_dir}")
    
    # Copy executable
    executable_name = "GetuClicker.exe" if is_windows else "GetuClicker"
    source_path = Path("dist") / executable_name
    
    if not source_path.exists():
        print(f"Error: Executable not found at {source_path}")
        print("Please run 'python build.py' first to build the application.")
        return 1
    
    shutil.copy(source_path, release_dir)
    print(f"Copied executable to {release_dir / executable_name}")
    
    # Copy browser automation script
    browser_script = "browser_automation.py"
    if Path(browser_script).exists():
        shutil.copy(browser_script, release_dir)
        print(f"Copied {browser_script} to release directory")
    
    # Copy README and other docs
    for doc_file in ["README.md", "LICENSE"]:
        if Path(doc_file).exists():
            shutil.copy(doc_file, release_dir)
            print(f"Copied {doc_file} to release directory")
    
    # Create requirements file for browser automation
    with open(release_dir / "browser_requirements.txt", "w") as f:
        f.write("selenium>=4.15.0\n")
    print("Created browser_requirements.txt in release directory")
    
    # Create version file
    with open(release_dir / "VERSION.txt", "w") as f:
        f.write("Getu Clicker v1.0.0\n")
        f.write("Browser Automation Extension v1.0.0\n")
        f.write(f"Built on {platform.system()} {platform.release()}\n")
    
    print("Release package prepared successfully!")
    print(f"Release files are available in the '{release_dir}' directory")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 