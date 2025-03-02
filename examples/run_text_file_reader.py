#!/usr/bin/env python3
"""
Text File Reader App Runner

This script runs the text file reader Lua app which displays content from a text file.
"""

import os
import sys
import time
import signal
from pathlib import Path

# Add parent directory to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from frame_emulator.emulator import FrameEmulator, EmulatorConfig, run_lua_script

def main():
    print("Frame Emulator - Text File Reader Example")
    
    # Create emulator with configuration
    config = EmulatorConfig(width=640, height=400, scale=1.5, title="Frame Text File Reader")
    emulator = FrameEmulator(config)
    
    # Path to Lua script
    script_path = str(Path(__file__).parent / "text_file_reader.lua")
    
    # Run Lua script in main thread
    try:
        # Import pygame here to avoid circular import
        import pygame
        
        # Start Lua script in a thread
        import threading
        script_thread = threading.Thread(target=run_lua_script, args=(script_path, emulator))
        script_thread.daemon = True
        script_thread.start()
        
        # Main rendering loop
        pygame_events = []  # Shared list for storing events
        
        # Helper function to safely process events in main thread
        def process_events():
            nonlocal pygame_events
            pygame_events = pygame.event.get()
            
            for event in pygame_events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        # Simulate scrolling up
                        print("Up arrow pressed - would scroll up")
                    elif event.key == pygame.K_DOWN:
                        # Simulate scrolling down
                        print("Down arrow pressed - would scroll down")
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
    main() 