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
                
        finally:
            # Clean up
            self.bluetooth.disconnect()
            self.bluetooth.unpair()
            pygame.quit()
