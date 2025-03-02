#!/usr/bin/env python3
"""
Demo script showing how to run all the different examples of the Frame Emulator.

This script will run each example for 10 seconds, then move to the next one.
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path

EXAMPLES_DIR = Path(__file__).parent
ROOT_DIR = EXAMPLES_DIR.parent
VENV_PYTHON = ROOT_DIR / ".venv" / "bin" / "python"

# Time to run each demo (seconds)
DEMO_TIME = 10

def run_command(cmd, timeout):
    """Run a command for a specific amount of time, then terminate it."""
    print(f"\n\n{'='*50}")
    print(f"Running: {' '.join(cmd)}")
    print(f"{'='*50}\n")
    
    try:
        process = subprocess.Popen(cmd)
        time.sleep(timeout)
        process.send_signal(signal.SIGINT)  # Send Ctrl+C
        process.wait(timeout=2)  # Give it 2 seconds to clean up
        if process.poll() is None:
            # If still running, terminate it
            process.terminate()
            process.wait(timeout=1)
    except KeyboardInterrupt:
        print("\nDemo stopped by user")
        if process.poll() is None:
            process.terminate()
        sys.exit(0)

def main():
    """Run all the different examples of the Frame Emulator."""
    print("Frame Emulator Demo - All Examples")
    print("Each example will run for 10 seconds, then move to the next one.")
    print("Press Ctrl+C to stop the demo at any time.")
    
    # Ensure we're in the right directory
    if Path.cwd().name != "frame-emulator":
        print("Please run this script from the root of the frame-emulator repository")
        sys.exit(1)
        
    python = sys.executable
    
    # Example 1: Run Python API example
    print("Running Python API example...")
    run_command([python, str(EXAMPLES_DIR / "python_api.py")], DEMO_TIME)
    
    # Example 2: Run Frame SDK demo
    print("Running Frame SDK demo...")
    run_command([python, str(EXAMPLES_DIR / "run_frame_sdk_demo.py")], DEMO_TIME)
    
    # Example 3: Run a custom example
    print("Running custom Lua example...")
    run_command([python, str(EXAMPLES_DIR / "run_custom_example.py")], DEMO_TIME)
    
    # Example 4: Run direct Python API (no Lua)
    print("Running direct Python API example...")
    run_command([python, str(EXAMPLES_DIR / "direct_api.py")], DEMO_TIME)
    
    # Example 5: Run Text Message App
    print("Running Text Message App...")
    run_command([python, str(EXAMPLES_DIR / "run_text_message_app.py")], DEMO_TIME)
    
    # Example 6: Run Text File Reader App
    print("Running Text File Reader App...")
    run_command([python, str(EXAMPLES_DIR / "run_text_file_reader.py")], DEMO_TIME)
    
    print("\n\nAll demos completed!")

if __name__ == "__main__":
    main() 