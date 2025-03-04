"""
Core implementation of the Frame Glasses Emulator.

This module provides the main functionality for rendering Frame Glasses
display output using Pygame and executing Lua scripts using Lupa.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import pygame

from .bluetooth import BluetoothManager
from .config import EmulatorConfig
from .constants import (
    CHAR_WIDTH_MAPPING,
    DEFAULT_COLOR_PALETTE,
    Alignment,
    BluetoothState,
    PaletteColors,
)
from .display import DisplayManager
from .lua_runtime import LuaManager


class FrameEmulator:
    """Main emulator class that coordinates all components."""

    def __init__(self, config: EmulatorConfig):
        """
        Initialize the Frame Emulator.
        
        Args:
            config: Configuration for the emulator
        """
        pygame.init()
        
        self.config = config
        self.display = DisplayManager(config.width, config.height, config.scale)
        self.bluetooth = BluetoothManager()
        self.lua = LuaManager(self)
        
        self.key_states: Dict[int, bool] = {}
        self.running = False
        
    def is_key_pressed(self, key: int) -> bool:
        """Check if a key is currently pressed."""
        return self.key_states.get(key, False)
        
    def run(self, script_path: Optional[str] = None) -> None:
        """
        Run the emulator with the given script.
        
        Args:
            script_path: Optional path to a Lua script to execute
        """
        self.running = True
        
        # Set up Lua environment
        self.lua.setup_lua_environment()
        
        # Simulate Bluetooth pairing and connection
        if self.bluetooth.pair():
            print("Bluetooth ready")
            self.bluetooth.connect()
            self.bluetooth.enable_notifications()
            
            # Set up callback to execute received Lua code
            def receive_callback(data):
                if isinstance(data, bytes):
                    try:
                        # First few bytes may contain control characters, try to clean
                        lua_code = data.decode('utf-8', errors='ignore').strip()
                        
                        # Display some useful debug information
                        print(f"[Bluetooth] Received data length: {len(data)} bytes")
                        print(f"[Bluetooth] First 50 bytes: {data[:50]}")
                        print(f"[Bluetooth] Executing Lua code...")
                        
                        # Execute the Lua code
                        self.lua.execute(lua_code)
                        print(f"[Bluetooth] Lua code executed successfully")
                    except UnicodeDecodeError as e:
                        print(f"[Bluetooth] Error decoding Lua code: {e}")
                    except Exception as e:
                        print(f"[Bluetooth] Error executing Lua code: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"[Bluetooth] Received non-bytes data: {type(data)}")
            
            # Register the callback
            self.bluetooth.set_receive_callback(receive_callback)
        
        clock = pygame.time.Clock()
        frame_count = 0
        
        try:
            # Start script execution if provided
            if script_path:
                self.lua.run_script(script_path)
            
            # Main event loop
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        self.key_states[event.key] = True
                    elif event.type == pygame.KEYUP:
                        self.key_states[event.key] = False
                
                # Update display
                self.display.render_frame(self.config.title, frame_count, clock)
                frame_count += 1
                clock.tick(self.config.fps)
        
        except Exception as e:
            print(f"Error in emulator: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Clean up resources
            pygame.quit()
            
            # Properly shutdown Bluetooth if initialized
            if hasattr(self, 'bluetooth') and self.bluetooth:
                self.bluetooth.shutdown()
