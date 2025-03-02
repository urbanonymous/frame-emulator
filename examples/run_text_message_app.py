#!/usr/bin/env python3
"""
Text Message App Simulator

This script demonstrates running the text message app and simulating
Bluetooth data being sent to the Frame Glasses.
"""

import os
import sys
import time
import signal
import threading
from pathlib import Path

# Add parent directory to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from frame_emulator.emulator import FrameEmulator, EmulatorConfig, run_lua_script

# Flags from the Lua script
TEXT_FLAG = 0x0A

def create_text_message(text):
    """Create a properly formatted text message packet."""
    # Format: [Flag][Size MSB][Size LSB][Data]
    data_bytes = text.encode('utf-8')
    size = len(data_bytes)
    
    # Create the message packet
    packet = bytes([TEXT_FLAG, (size >> 8) & 0xFF, size & 0xFF]) + data_bytes
    return packet

def send_bluetooth_data(emulator, data, delay_seconds=0):
    """Send data to the emulator after an optional delay."""
    if delay_seconds > 0:
        time.sleep(delay_seconds)
    emulator.simulate_bluetooth_receive(data)

def main():
    print("Frame Emulator - Text Message App Example")
    
    # Create emulator with configuration
    config = EmulatorConfig(width=640, height=400, scale=1.5, title="Frame Text Message App")
    emulator = FrameEmulator(config)
    
    # Path to Lua script
    script_path = str(Path(__file__).parent / "text_message_app.lua")
    
    # Start Lua script in a thread
    script_thread = threading.Thread(target=run_lua_script, args=(script_path, emulator))
    script_thread.daemon = True
    script_thread.start()
    
    # Schedule some messages to be sent after delays
    message_thread1 = threading.Thread(
        target=send_bluetooth_data,
        args=(emulator, create_text_message("Hello from your phone!\nThis is a test message."), 3)
    )
    message_thread1.daemon = True
    message_thread1.start()
    
    message_thread2 = threading.Thread(
        target=send_bluetooth_data,
        args=(emulator, create_text_message("This is a second message.\nIt has multiple lines\nto demonstrate scrolling."), 6)
    )
    message_thread2.daemon = True
    message_thread2.start()
    
    # Main rendering loop
    try:
        pygame_events = []  # Shared list for storing events
        
        # Helper function to safely process events in main thread
        def process_events():
            nonlocal pygame_events
            pygame_events = pygame.event.get()
            
            for event in pygame_events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Send a custom message when space is pressed
                        msg = create_text_message("Message sent by pressing SPACE!\nTime: " + time.strftime("%H:%M:%S"))
                        emulator.simulate_bluetooth_receive(msg)
                elif event.type == pygame.QUIT:
                    emulator.running = False
        
        while emulator.running:
            # Process events in main thread
            process_events()
            
            # Render frame in main thread
            emulator.render_frame()
            
    except KeyboardInterrupt:
        print("Emulator stopped by user")
    finally:
        emulator.stop()

if __name__ == "__main__":
    # Import pygame here to avoid circular import
    import pygame
    main() 