#!/usr/bin/env python3
"""
Simple Text Display Client

This script connects to the Frame emulator and sends the simple_text_display.lua
script which directly displays text without needing to receive file content.

Run this after starting 'python examples/run_emulator.py' in another terminal.
"""

import asyncio
import sys
import time
from pathlib import Path

from frame_emulator.frame_sdk import Frame


async def print_handler(text: str):
    """Handle print output from Frame."""
    print(f"Frame output: {text}")


def read_file_content(file_path):
    """Read content from a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None


async def main():
    # Path to the Lua script
    lua_script_path = str(Path(__file__).parent / "simple_text_display.lua")
    
    # Read the Lua script
    lua_script = read_file_content(lua_script_path)
    if not lua_script:
        print("Failed to read the Lua script file!")
        return 1
    
    print(f"Read {len(lua_script)} bytes from simple_text_display.lua")
    
    # Create Frame client
    frame = Frame("localhost", 5555)
    frame.set_debugging(True)  # Enable debug output
    frame.set_print_response_handler(print_handler)

    # Connect to emulator with retry logic
    print("Connecting to Frame emulator...")
    connection_attempts = 0
    max_attempts = 5
    
    while connection_attempts < max_attempts:
        if frame.connect(retries=1, retry_delay=0.5):
            break
        
        connection_attempts += 1
        if connection_attempts < max_attempts:
            print(f"Connection attempt {connection_attempts} failed. Retrying in 2 seconds...")
            await asyncio.sleep(2)
        else:
            print("Failed to connect after multiple attempts!")
            print("Make sure the emulator is running (examples/run_emulator.py)")
            return 1
    
    print("Connected! Sending Lua script...")
    
    # Send Lua script with retry logic
    send_attempts = 0
    max_send_attempts = 3
    
    while send_attempts < max_send_attempts:
        if frame.send(lua_script):
            break
            
        send_attempts += 1
        if send_attempts < max_send_attempts:
            print(f"Script send attempt {send_attempts} failed. Retrying in 1 second...")
            await asyncio.sleep(1)
        else:
            print("Failed to send Lua script after multiple attempts!")
            frame.disconnect()
            return 1
    
    print("\nLua script sent successfully!")
    print("The emulator window should now show the text display")
    print("You can use UP/DOWN arrow keys or SPACE to scroll through the text")
    print("\nKeeping connection alive to receive output...")
    print("Press Ctrl+C to exit...")

    try:
        # Keep the connection alive to receive output
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nDisconnecting...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Always ensure we disconnect properly
        frame.disconnect()
        print("Disconnected.")
    
    return 0


if __name__ == "__main__":
    try:
        # Run the async main function
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
        sys.exit(0) 