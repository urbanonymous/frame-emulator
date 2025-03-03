#!/usr/bin/env python3
"""
File Reader App Simulator

This script demonstrates running the file reader app and simulating
uploading a file over Bluetooth to the Frame Glasses.
"""

import os
import signal
import sys
import threading
import time
from pathlib import Path

import pygame

# Add parent directory to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from frame_emulator.emulator import EmulatorConfig, FrameEmulator, run_lua_script

# Flags matching the Lua app
FILE_CONTENT_FLAG = 0x0F


def read_file_content(file_path):
    """Read content from a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return f"Error reading file: {e}"


def create_file_packet(data):
    """Create a properly formatted file content packet."""
    # Format: [Flag][Data]
    # Convert string data to bytes and prefix with flag
    return (
        bytes([FILE_CONTENT_FLAG]) + data.encode("utf-8")
        if isinstance(data, str)
        else bytes([FILE_CONTENT_FLAG]) + data
    )


def main():
    print("Frame Emulator - File Reader App Example")

    # Create emulator with configuration
    config = EmulatorConfig(
        width=640, height=400, scale=1.5, title="Frame File Reader App"
    )
    emulator = FrameEmulator(config)

    # Path to Lua script
    script_path = str(Path(__file__).parent / "file_reader_app.lua")

    # Path to text file to upload
    file_path = str(Path(__file__).parent / "demo_text.txt")

    # Start Lua script in a thread
    script_thread = threading.Thread(
        target=run_lua_script, args=(script_path, emulator)
    )
    script_thread.daemon = True
    script_thread.start()

    # Read the file content
    file_content = read_file_content(file_path)
    print(f"Read {len(file_content)} bytes from {file_path}")

    # Schedule file content to be sent after a delay
    # This simulates uploading the file to the device
    def upload_file():
        time.sleep(2)  # Wait for app to initialize

        # Get max transfer size (or use default if not available)
        max_chunk = getattr(emulator, "bluetooth_max_length", lambda: 128)()
        chunk_size = max_chunk - 1  # Leave room for flag byte

        # Split content into lines to match Frame's file reading behavior
        lines = file_content.splitlines()

        # Send each line as a separate chunk
        for line in lines:
            # Add newline back to preserve formatting
            line_data = line + "\n"

            # Split long lines into chunks if needed
            for i in range(0, len(line_data), chunk_size):
                chunk = line_data[i : i + chunk_size]
                packet = create_file_packet(chunk)

                # Send chunk through Bluetooth callback
                if emulator.bluetooth_receive_callback:
                    emulator.bluetooth_receive_callback(packet)
                time.sleep(0.05)  # Small delay between chunks

    file_thread = threading.Thread(target=upload_file)
    file_thread.daemon = True
    file_thread.start()

    # Main rendering loop
    try:
        # Track key states for handling input
        key_states = {pygame.K_UP: False, pygame.K_DOWN: False}

        # Helper function to safely process events in main thread
        def process_events():
            nonlocal key_states
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    emulator.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        key_states[pygame.K_UP] = True
                    elif event.key == pygame.K_DOWN:
                        key_states[pygame.K_DOWN] = True
                    elif event.key == pygame.K_ESCAPE:
                        emulator.running = False
                elif event.type == pygame.KEYUP:
                    if event.key in key_states:
                        key_states[event.key] = False

            # Update input state in emulator
            emulator.update_key_state("up", key_states.get(pygame.K_UP, False))
            emulator.update_key_state("down", key_states.get(pygame.K_DOWN, False))

        # Set a timeout for demo mode
        start_time = time.time()
        timeout = 10  # 10 seconds for demo

        while emulator.running and (time.time() - start_time < timeout):
            # Process events in main thread
            process_events()

            # Render frame in main thread
            emulator.render_frame()

    except KeyboardInterrupt:
        print("Emulator stopped by user")
    finally:
        emulator.stop()


if __name__ == "__main__":
    main()
