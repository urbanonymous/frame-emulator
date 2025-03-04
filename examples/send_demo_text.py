#!/usr/bin/env python3
"""
File Reader Demo Client

This script connects to the Frame emulator and:
1. Sends the file_reader_app.lua script to be executed
2. Sends the content of demo_text.txt for display

Run this after starting 'python examples/run_emulator.py' in another terminal.
"""

import asyncio
import sys
import time
from pathlib import Path

from frame_emulator.frame_sdk import Frame

# Flag for file content (must match the one in file_reader_app.lua)
FILE_CONTENT_FLAG = 0x0F


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
    # Paths to the files
    lua_script_path = str(Path(__file__).parent / "file_reader_app.lua")
    demo_text_path = str(Path(__file__).parent / "demo_text.txt")
    
    # Read the Lua script
    lua_script = read_file_content(lua_script_path)
    if not lua_script:
        print("Failed to read the Lua script file!")
        return 1
    
    print(f"Read {len(lua_script)} bytes from file_reader_app.lua")
    
    # Read the demo text file
    demo_content = read_file_content(demo_text_path)
    if not demo_content:
        print("Failed to read the demo text file!")
        return 1
    
    print(f"Read {len(demo_content)} bytes from demo_text.txt")
    
    # Create Frame client
    frame = Frame("localhost", 5555)
    frame.set_debugging(True)  # Enable debug output
    frame.set_print_response_handler(print_handler)

    # Connect to emulator with retry logic
    print("Connecting to Frame emulator...")
    connection_attempts = 0
    max_attempts = 10  # Increased max attempts
    
    while connection_attempts < max_attempts:
        if frame.connect(retries=2, retry_delay=1.0):  # Increased retries and delay
            break
        
        connection_attempts += 1
        if connection_attempts < max_attempts:
            print(f"Connection attempt {connection_attempts} failed. Retrying in 3 seconds...")
            await asyncio.sleep(3)  # Increased wait time
        else:
            print("Failed to connect after multiple attempts!")
            print("Make sure the emulator is running (examples/run_emulator.py)")
            return 1
    
    print("Connected! Sending Lua script...")
    
    # Send Lua script with retry logic
    send_attempts = 0
    max_send_attempts = 5  # Increased max attempts
    
    while send_attempts < max_send_attempts:
        print(f"Sending Lua script, attempt {send_attempts + 1}/{max_send_attempts}...")
        if frame.send(lua_script):
            break
            
        send_attempts += 1
        if send_attempts < max_send_attempts:
            print(f"Script send attempt {send_attempts} failed. Retrying in 2 seconds...")
            await asyncio.sleep(2)  # Increased wait time
        else:
            print("Failed to send Lua script after multiple attempts!")
            frame.disconnect()
            return 1
    
    print("Lua script sent successfully!")
    print("Waiting for script initialization (10 seconds)...")
    await asyncio.sleep(10)  # Longer initialization time to ensure script is running
    
    print("Starting new connection for sending file content...")
    # Reconnect to ensure clean state
    frame.disconnect()
    await asyncio.sleep(2)
    
    # Connect again
    print("Reconnecting to send file content...")
    connection_attempts = 0
    
    while connection_attempts < max_attempts:
        if frame.connect(retries=2, retry_delay=1.0):
            break
        
        connection_attempts += 1
        if connection_attempts < max_attempts:
            print(f"Reconnection attempt {connection_attempts} failed. Retrying in 3 seconds...")
            await asyncio.sleep(3)
        else:
            print("Failed to reconnect after multiple attempts!")
            return 1
    
    print("Reconnected successfully!")
    print("Sending text file content...")
    
    # Split content into lines to match Frame's file reading behavior
    lines = demo_content.splitlines()
    
    # Send each line with the proper file content flag
    successful_lines = 0
    for i, line in enumerate(lines):
        # Add newline to preserve formatting, except for the last line
        line_data = line + "\n"
        
        # Format packet with flag
        packet = bytes([FILE_CONTENT_FLAG]) + line_data.encode('utf-8')
        
        print(f"Sending line {i+1}/{len(lines)}: {len(packet)} bytes")
        
        # Send data with retry logic
        send_attempts = 0
        max_line_attempts = 5  # More retries per line
        
        while send_attempts < max_line_attempts:
            if frame.send_data(packet):
                successful_lines += 1
                break
                
            send_attempts += 1
            if send_attempts < max_line_attempts:
                print(f"Send attempt {i+1}/{len(lines)} failed. Retrying ({send_attempts}/{max_line_attempts})...")
                await asyncio.sleep(1.0)  # Longer delay between retries
            else:
                print(f"Failed to send line {i+1} after multiple attempts!")
                frame.disconnect()
                return 1
                
        print(f"Successfully sent line {i+1}/{len(lines)}")
        await asyncio.sleep(0.2)  # Longer delay between lines
    
    print(f"\nFile content sent successfully! ({successful_lines}/{len(lines)} lines)")
    print("The emulator window should now show the text file content")
    print("You can use tap gestures to navigate through the text")
    print("\nWaiting for 30 seconds to keep connection alive...")
    
    # Keep connection alive longer to ensure all data is processed
    try:
        for i in range(30):
            print(f"Keeping connection alive... {30-i} seconds remaining", end="\r")
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nDisconnecting early due to user interrupt...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        # Always ensure we disconnect properly
        print("\nDisconnecting...")
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