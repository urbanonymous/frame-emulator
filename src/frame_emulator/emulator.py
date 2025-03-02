"""
Core implementation of the Frame Glasses Emulator.

This module provides the main functionality for rendering Frame Glasses
display output using Pygame and executing Lua scripts using Lupa.
"""

import pygame
import lupa
from lupa import LuaRuntime
import threading
import argparse
import os
import sys
from typing import Union, Dict, Any, Optional, Tuple, Callable, List
from enum import Enum
from pydantic import BaseModel, Field, field_validator
import time


class PaletteColors(Enum):
    """Color palette matching the Frame SDK."""
    VOID = 0
    WHITE = 1
    GRAY = 2
    RED = 3
    PINK = 4
    DARKBROWN = 5
    BROWN = 6
    ORANGE = 7
    YELLOW = 8
    DARKGREEN = 9
    GREEN = 10
    LIGHTGREEN = 11
    NIGHTBLUE = 12
    SEABLUE = 13
    SKYBLUE = 14
    CLOUDBLUE = 15


class Alignment(Enum):
    """Text alignment options matching the Frame SDK."""
    TOP_LEFT = 'top_left'
    TOP_CENTER = 'top_center'
    TOP_RIGHT = 'top_right'
    MIDDLE_LEFT = 'middle_left'
    MIDDLE_CENTER = 'middle_center'
    MIDDLE_RIGHT = 'middle_right'
    BOTTOM_LEFT = 'bottom_left'
    BOTTOM_CENTER = 'bottom_center'
    BOTTOM_RIGHT = 'bottom_right'


class EmulatorConfig(BaseModel):
    """Configuration for the Frame Emulator."""
    width: int = Field(default=640, ge=1, description="Display width in pixels")
    height: int = Field(default=400, ge=1, description="Display height in pixels")
    fps: int = Field(default=60, ge=1, le=240, description="Target frames per second")
    title: str = Field(default="Frame Glasses Emulator", description="Window title")
    scale: float = Field(default=1.0, ge=0.25, le=10.0, description="Initial display scale factor")
    
    @field_validator('width', 'height')
    @classmethod
    def dimensions_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Dimensions must be positive")
        return v
    
    model_config = {
        'validate_assignment': True
    }


class FrameEmulator:
    """
    Emulator for Frame Glasses display.
    
    This class provides a virtual 640x400 display that can render output from
    Lua scripts written for Frame Glasses.
    """
    
    # Character width mapping for text rendering based on Frame SDK
    CHAR_WIDTH_MAPPING = {
        0x000020: 13, 0x000021: 5, 0x000022: 13, 0x000023: 19, 0x000024: 17, 
        0x000025: 34, 0x000026: 20, 0x000027: 5, 0x000028: 10, 0x000029: 11, 
        0x00002A: 21, 0x00002B: 19, 0x00002C: 8, 0x00002D: 17, 0x00002E: 6, 
        0x00002F: 15, 0x000030: 18, 0x000031: 16, 0x000032: 16, 0x000033: 15, 
        0x000034: 18, 0x000035: 15, 0x000036: 17, 0x000037: 15, 0x000038: 18, 
        0x000039: 17, 0x00003A: 6, 0x00003B: 8, 0x00003C: 19, 0x00003D: 19, 
        0x00003E: 19, 0x00003F: 14, 0x000040: 31, 0x000041: 22, 0x000042: 18, 
        0x000043: 16, 0x000044: 19, 0x000045: 17, 0x000046: 17, 0x000047: 18, 
        0x000048: 19, 0x000049: 12, 0x00004A: 14, 0x00004B: 19, 0x00004C: 16, 
        0x00004D: 23, 0x00004E: 19, 0x00004F: 20, 0x000050: 18, 0x000051: 22, 
        0x000052: 20, 0x000053: 17, 0x000054: 20, 0x000055: 19, 0x000056: 21, 
        0x000057: 23, 0x000058: 21, 0x000059: 23, 0x00005A: 17, 0x00005B: 9, 
        0x00005C: 15, 0x00005D: 10, 0x00005E: 20, 0x00005F: 25, 0x000060: 11, 
        0x000061: 19, 0x000062: 18, 0x000063: 13, 0x000064: 18, 0x000065: 16, 
        0x000066: 15, 0x000067: 20, 0x000068: 18, 0x000069: 5, 0x00006A: 11, 
        0x00006B: 18, 0x00006C: 8, 0x00006D: 28, 0x00006E: 18, 0x00006F: 18, 
        0x000070: 18, 0x000071: 18, 0x000072: 11, 0x000073: 15, 0x000074: 14, 
        0x000075: 17, 0x000076: 19, 0x000077: 30, 0x000078: 20, 0x000079: 20, 
        0x00007A: 16, 0x00007B: 12, 0x00007C: 5, 0x00007D: 12, 0x00007E: 17
    }
    
    def __init__(
        self, 
        config: Optional[EmulatorConfig] = None
    ):
        """
        Initialize the Frame Emulator.
        
        Args:
            config: Optional configuration for the emulator.
                   If not provided, default values will be used.
        """
        pygame.init()
        
        # Initialize with default config if none provided
        self.config = config or EmulatorConfig()
        
        self.width = self.config.width
        self.height = self.config.height
        
        # Calculate initial window size based on scale
        window_width = int(self.width * self.config.scale)
        window_height = int(self.height * self.config.scale)
        
        # Set up the display window
        self.screen = pygame.display.set_mode(
            (window_width, window_height), 
            pygame.RESIZABLE
        )
        pygame.display.set_caption(self.config.title)
        
        # Create frame buffer for pixel manipulation
        self.frame_buffer = pygame.Surface((self.width, self.height))
        
        # Initialize thread synchronization
        self.lock = threading.Lock()
        self.running = True
        
        # Additional state
        self.fps_clock = pygame.time.Clock()
        self.frame_count = 0
        self.lua_callbacks = {}

        # Color palette matching Frame SDK default colors
        self.color_palette = {
            PaletteColors.VOID: (0, 0, 0),
            PaletteColors.WHITE: (255, 255, 255),
            PaletteColors.GRAY: (157, 157, 157),
            PaletteColors.RED: (190, 38, 51),
            PaletteColors.PINK: (224, 111, 139),
            PaletteColors.DARKBROWN: (73, 60, 43),
            PaletteColors.BROWN: (164, 100, 34),
            PaletteColors.ORANGE: (235, 137, 49),
            PaletteColors.YELLOW: (247, 226, 107),
            PaletteColors.DARKGREEN: (47, 72, 78),
            PaletteColors.GREEN: (68, 137, 26),
            PaletteColors.LIGHTGREEN: (163, 206, 39),
            PaletteColors.NIGHTBLUE: (27, 38, 50),
            PaletteColors.SEABLUE: (0, 87, 132),
            PaletteColors.SKYBLUE: (49, 162, 242),
            PaletteColors.CLOUDBLUE: (178, 220, 239)
        }
        
        # Text rendering properties
        self.line_height = 60
        self.char_spacing = 4
        self.fonts = {}  # Cache for fonts at different sizes
        
        # Bluetooth emulation
        self.bluetooth_data_queue = []
        self.bluetooth_receive_callback = None
        self.battery_level_value = 100  # Default battery level is 100%
        self.start_time = time.time()  # Used for time.utc() simulation

    def _is_lua_table(self, obj):
        """Check if an object is a Lua table."""
        try:
            return hasattr(obj, '__pairs') or hasattr(obj, 'r') or hasattr(obj, 'keys')
        except Exception:
            return False

    def _get_color(self, color):
        """
        Convert a color value to RGB tuple.
        
        Args:
            color: Either a PaletteColors enum value, integer RGB color, or Lua table
        
        Returns:
            Tuple of (r, g, b) values
        """
        if isinstance(color, (int, float)):
            color = int(color)
            # Check if it's a palette index
            if 0 <= color < 16:
                return self.color_palette[PaletteColors(color)]
            # Otherwise treat as RGB color
            r = (color >> 16) & 0xFF
            g = (color >> 8) & 0xFF
            b = color & 0xFF
            return (r, g, b)
        elif isinstance(color, PaletteColors):
            return self.color_palette[color]
        elif self._is_lua_table(color):
            # Handle both attribute and key access for Lua tables
            try:
                # Try attribute access first (object.r)
                if hasattr(color, 'r') and hasattr(color, 'g') and hasattr(color, 'b'):
                    return (int(color.r), int(color.g), int(color.b))
                # Try dictionary-like access (object['r'])
                elif 'r' in color and 'g' in color and 'b' in color:
                    return (int(color['r']), int(color['g']), int(color['b']))
            except Exception:
                pass
        # Default to white if color can't be determined
        return (255, 255, 255)

    def render_frame(self):
        """Update the display with the current frame buffer content."""
        with self.lock:
            # Get current window size
            window_size = self.screen.get_size()
            
            # Scale the frame buffer to window size while preserving aspect ratio
            w_scale = window_size[0] / self.width
            h_scale = window_size[1] / self.height
            scale = min(w_scale, h_scale)
            
            scaled_width = int(self.width * scale)
            scaled_height = int(self.height * scale)
            
            # Center the scaled buffer
            x_pos = (window_size[0] - scaled_width) // 2
            y_pos = (window_size[1] - scaled_height) // 2
            
            # Scale and blit
            scaled_buffer = pygame.transform.scale(self.frame_buffer, (scaled_width, scaled_height))
            self.screen.fill((30, 30, 30))  # Dark gray background
            self.screen.blit(scaled_buffer, (x_pos, y_pos))
            
            # Show FPS in the corner for debugging
            self.frame_count += 1
            if self.frame_count % 30 == 0:  # Update FPS display every 30 frames
                pygame.display.set_caption(f"{self.config.title} - FPS: {self.fps_clock.get_fps():.1f}")
        
        pygame.display.flip()
        self.fps_clock.tick(self.config.fps)
        
        # Don't process events here - leave that to the main thread

    # Frame SDK compatible methods
    def set_palette(self, palette_index, rgb_color):
        """
        Set a color in the palette.
        
        Args:
            palette_index: Index in the palette (0-15)
            rgb_color: Tuple of (r, g, b) values or Lua table with r, g, b keys
        """
        if isinstance(palette_index, (int, float)):
            palette_index = int(palette_index) % 16
            palette_color = PaletteColors(palette_index)
        elif isinstance(palette_index, PaletteColors):
            palette_color = palette_index
        else:
            # Try to get palette color from string name
            try:
                palette_color = PaletteColors[str(palette_index).upper()]
            except (KeyError, ValueError):
                palette_color = PaletteColors.WHITE
        
        # Get RGB values
        if self._is_lua_table(rgb_color):
            if hasattr(rgb_color, 'r'):
                r, g, b = int(rgb_color.r), int(rgb_color.g), int(rgb_color.b)
            else:
                r, g, b = int(rgb_color[0]), int(rgb_color[1]), int(rgb_color[2])
        elif isinstance(rgb_color, (list, tuple)) and len(rgb_color) >= 3:
            r, g, b = int(rgb_color[0]), int(rgb_color[1]), int(rgb_color[2])
        else:
            # Default fallback
            r, g, b = 255, 255, 255
        
        # Clamp values to valid range
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        
        # Update palette
        self.color_palette[palette_color] = (r, g, b)

    def set_pixel(self, x, y, color):
        """
        Set a pixel on the frame buffer with the given color.
        
        Args:
            x: X coordinate (0 to width-1)
            y: Y coordinate (0 to height-1)
            color: Color value (palette index, RGB int, or Lua table)
        """
        x, y = int(x), int(y)
        if 0 <= x < self.width and 0 <= y < self.height:
            rgb = self._get_color(color)
            with self.lock:
                self.frame_buffer.set_at((x, y), rgb)

    def draw_line(self, x1, y1, x2, y2, color):
        """
        Draw a line on the frame buffer.
        
        Args:
            x1, y1: Starting coordinates
            x2, y2: Ending coordinates
            color: Color value (palette index, RGB int, or Lua table)
        """
        rgb = self._get_color(color)
        with self.lock:
            pygame.draw.line(
                self.frame_buffer, 
                rgb, 
                (int(x1), int(y1)), 
                (int(x2), int(y2))
            )

    def draw_rect(self, x, y, width, height, color):
        """
        Draw a rectangle outline on the frame buffer.
        
        Args:
            x, y: Top-left coordinates
            width, height: Dimensions of the rectangle
            color: Color value (palette index, RGB int, or Lua table)
        """
        rgb = self._get_color(color)
        with self.lock:
            pygame.draw.rect(
                self.frame_buffer, 
                rgb, 
                pygame.Rect(int(x), int(y), int(width), int(height)),
                1  # Width of 1 pixel
            )

    def fill_rect(self, x, y, width, height, color):
        """
        Fill a rectangle on the frame buffer.
        
        Args:
            x, y: Top-left coordinates
            width, height: Dimensions of the rectangle
            color: Color value (palette index, RGB int, or Lua table)
        """
        rgb = self._get_color(color)
        with self.lock:
            pygame.draw.rect(
                self.frame_buffer, 
                rgb, 
                pygame.Rect(int(x), int(y), int(width), int(height))
            )

    def draw_rect_filled(self, x, y, width, height, border_width, border_color, fill_color):
        """
        Draw a filled rectangle with a border.
        
        Args:
            x, y: Top-left coordinates
            width, height: Dimensions of the rectangle
            border_width: Width of the border in pixels
            border_color: Color for the border
            fill_color: Color for the fill
        """
        border_rgb = self._get_color(border_color)
        fill_rgb = self._get_color(fill_color)
        
        rect = pygame.Rect(int(x), int(y), int(width), int(height))
        border_width = int(border_width)
        
        with self.lock:
            # Draw the fill
            pygame.draw.rect(self.frame_buffer, fill_rgb, rect)
            
            # Draw the border if needed
            if border_width > 0:
                pygame.draw.rect(self.frame_buffer, border_rgb, rect, border_width)

    def get_font(self, size):
        """Get or create a font of the specified size."""
        if size not in self.fonts:
            self.fonts[size] = pygame.font.SysFont("arial", size)
        return self.fonts[size]

    def get_text_width(self, text):
        """
        Get the width of text in pixels.
        
        Args:
            text: Text string to measure
            
        Returns:
            Width of the text in pixels
        """
        width = 0
        for char in text:
            width += self.CHAR_WIDTH_MAPPING.get(ord(char), 25) + self.char_spacing
        return width

    def get_text_height(self, text):
        """
        Get the height of text in pixels.
        
        Args:
            text: Text string to measure
            
        Returns:
            Height of the text in pixels
        """
        num_lines = text.count('\n') + 1
        return num_lines * self.line_height

    def wrap_text(self, text, max_width):
        """
        Wrap text to fit within a specified width.
        
        Args:
            text: Text to wrap
            max_width: Maximum width in pixels
            
        Returns:
            Wrapped text with newlines
        """
        if not text:
            return ""
            
        lines = text.split('\n')
        output = ""
        
        for line in lines:
            if self.get_text_width(line) <= max_width:
                output += line + "\n"
            else:
                this_line = ""
                words = line.split(" ")
                for word in words:
                    if len(this_line) == 0:
                        this_line = word
                    elif self.get_text_width(this_line + " " + word) > max_width:
                        output += this_line + "\n"
                        this_line = word
                    else:
                        this_line += " " + word
                if len(this_line) > 0:
                    output += this_line + "\n"
        
        return output.rstrip("\n")

    def write_text(self, x, y, text, color, size=16, alignment=Alignment.TOP_LEFT):
        """
        Draw text on the frame buffer with alignment.
        
        Args:
            x, y: Coordinates (interpretation depends on alignment)
            text: Text to display
            color: Color value (palette index, RGB int, or Lua table)
            size: Font size in pixels
            alignment: Text alignment from Alignment enum
        """
        rgb = self._get_color(color)
        font = self.get_font(size)
        
        # Split text into lines
        lines = text.split('\n')
        text_height = len(lines) * self.line_height
        
        # Calculate alignment offsets
        if isinstance(alignment, str):
            try:
                alignment = Alignment(alignment)
            except (ValueError, TypeError):
                alignment = Alignment.TOP_LEFT
        
        for i, line in enumerate(lines):
            text_surface = font.render(str(line), True, rgb)
            text_width = text_surface.get_width()
            
            # Calculate position based on alignment
            pos_x, pos_y = x, y + i * self.line_height
            
            if alignment in (Alignment.TOP_CENTER, Alignment.MIDDLE_CENTER, Alignment.BOTTOM_CENTER):
                pos_x = x - text_width // 2
            elif alignment in (Alignment.TOP_RIGHT, Alignment.MIDDLE_RIGHT, Alignment.BOTTOM_RIGHT):
                pos_x = x - text_width
            
            if alignment in (Alignment.MIDDLE_LEFT, Alignment.MIDDLE_CENTER, Alignment.MIDDLE_RIGHT):
                pos_y = y - text_height // 2 + i * self.line_height
            elif alignment in (Alignment.BOTTOM_LEFT, Alignment.BOTTOM_CENTER, Alignment.BOTTOM_RIGHT):
                pos_y = y - text_height + i * self.line_height
            
            with self.lock:
                self.frame_buffer.blit(text_surface, (int(pos_x), int(pos_y)))

    def draw_text(self, x, y, text, color, size=16):
        """
        Legacy method for drawing text at a position. Calls write_text with TOP_LEFT alignment.
        
        Args:
            x, y: Top-left coordinates
            text: Text to display
            color: Color value (palette index, RGB int, or Lua table)
            size: Font size in pixels
        """
        self.write_text(x, y, text, color, size, Alignment.TOP_LEFT)

    def clear(self, color=0):
        """
        Clear the frame buffer with the specified color.
        
        Args:
            color: Color value (palette index, RGB int, or Lua table)
        """
        rgb = self._get_color(color)
        with self.lock:
            self.frame_buffer.fill(rgb)

    def show(self):
        """
        Update the display manually.
        This simulates the frame.display.show() function in the Frame SDK.
        """
        self.render_frame()

    def bitmap(self, x, y, width, mode, color, data):
        """
        Draw a bitmap on the screen.
        
        Args:
            x, y: Top-left coordinates
            width: Width of the bitmap in pixels
            mode: Bitmap mode (1 or 2)
            color: Color palette index
            data: Bitmap data string
        """
        # This is a simplified implementation - full bitmap support would
        # need to decode the binary data format used by Frame SDK
        rgb = self._get_color(color)
        
        # Just draw a rectangle as a placeholder
        with self.lock:
            # Scale height based on the data length
            if isinstance(data, str):
                height = len(data)
            else:
                height = 10  # Default height
                
            pygame.draw.rect(
                self.frame_buffer,
                rgb,
                pygame.Rect(int(x), int(y), int(width), height)
            )

    def register_lua_callback(self, name, callback):
        """
        Register a callback that can be called from Lua code.
        
        Args:
            name: Name of the callback as it will be available in Lua
            callback: Python function to be called
        """
        self.lua_callbacks[name] = callback

    def stop(self):
        """Stop the emulator and clean up resources."""
        self.running = False
        pygame.quit()

    # Frame Bluetooth API simulation
    def bluetooth_send(self, data):
        """
        Simulate sending data over Bluetooth.
        
        Args:
            data: String data to send
        """
        print(f"[Bluetooth] Sending data: {data.encode('utf-8').hex()}")
        return True
    
    def bluetooth_receive_callback(self, callback):
        """
        Register a callback for bluetooth data reception.
        
        Args:
            callback: Function to call when data is received
        """
        self.bluetooth_receive_callback = callback
        print("[Bluetooth] Receive callback registered")
    
    def simulate_bluetooth_receive(self, data):
        """
        Simulate receiving data over Bluetooth.
        This method can be called manually to test the app.
        
        Args:
            data: String or bytes data to simulate receiving
        """
        if self.bluetooth_receive_callback:
            # Handle both string and bytes data
            if isinstance(data, bytes):
                print(f"[Bluetooth] Received data: {data.hex()}")
                # Convert bytes to a string for Lua
                data_str = data.decode('utf-8', errors='replace')
                self.bluetooth_receive_callback(data_str)
            else:
                print(f"[Bluetooth] Received data: {data.encode('utf-8').hex()}")
                self.bluetooth_receive_callback(data)
    
    # Frame Battery API simulation
    def battery_level(self):
        """
        Get the current battery level (simulated).
        
        Returns:
            Battery level percentage (0-100)
        """
        return self.battery_level_value
    
    def set_battery_level(self, level):
        """
        Set the simulated battery level for testing.
        
        Args:
            level: Battery level percentage (0-100)
        """
        self.battery_level_value = max(0, min(100, level))
    
    # Frame Time API simulation
    def time_utc(self):
        """
        Get the current UTC time in seconds since emulator start.
        
        Returns:
            Number of seconds since emulator start
        """
        return int(time.time() - self.start_time)
    
    # Frame sleep API
    def sleep(self, seconds):
        """
        Sleep for the specified number of seconds.
        
        Args:
            seconds: Time to sleep in seconds
        """
        time.sleep(seconds)


def run_lua_script(lua_script_path, emulator):
    """
    Run a Lua script with the emulator.
    
    Args:
        lua_script_path: Path to the Lua script to execute
        emulator: FrameEmulator instance to use
    """
    # Import time module for sleep function
    import time
    
    # Set up Lua runtime
    lua = LuaRuntime(unpack_returned_tuples=True)
    
    # Create global frame object
    frame = lua.globals().frame = lua.eval('{}')
    
    # Set up display module
    display = lua.eval('{}')
    frame.display = display
    
    # Create PaletteColors table in Lua
    palette_colors = lua.eval('{}')
    for color in PaletteColors:
        palette_colors[color.name] = color.value
    frame.display.PaletteColors = palette_colors
    
    # Create Alignment table in Lua
    alignment = lua.eval('{}')
    for align in Alignment:
        alignment[align.name] = align.value
    frame.display.Alignment = alignment
    
    # Bind Python methods to Lua, using the same naming conventions as Frame SDK
    display.set_pixel = emulator.set_pixel
    display.draw_line = emulator.draw_line
    display.draw_rect = emulator.draw_rect
    display.fill_rect = emulator.fill_rect
    display.draw_rect_filled = emulator.draw_rect_filled
    display.write_text = emulator.write_text
    display.clear = emulator.clear
    display.show = emulator.show
    display.bitmap = emulator.bitmap
    display.set_palette = emulator.set_palette
    display.get_text_width = emulator.get_text_width
    display.get_text_height = emulator.get_text_height
    display.wrap_text = emulator.wrap_text
    
    # Add text as an alias for write_text for compatibility
    display.text = lambda text, x, y, color=1, size=16: emulator.write_text(x, y, text, color, size)
    
    # Provide legacy camelCase functions for backwards compatibility
    display.setPixel = emulator.set_pixel
    display.drawLine = emulator.draw_line
    display.fillRect = emulator.fill_rect
    display.drawText = emulator.draw_text
    
    # Set up Bluetooth module
    bluetooth = lua.eval('{}')
    frame.bluetooth = bluetooth
    bluetooth.send = emulator.bluetooth_send
    
    # Create a wrapper function that will be exposed to Lua
    def bluetooth_receive_callback_wrapper(callback):
        # Register the callback for later use
        emulator.bluetooth_receive_callback = callback
    
    # Bind the wrapper function to Lua
    bluetooth.receive_callback = bluetooth_receive_callback_wrapper
    
    # Set up battery and time functions
    frame.battery_level = emulator.battery_level
    
    # Set up time module
    time_module = lua.eval('{}')
    frame.time = time_module
    time_module.utc = emulator.time_utc
    
    # Set up sleep function
    frame.sleep = emulator.sleep
    
    # Add any registered callbacks
    for name, callback in emulator.lua_callbacks.items():
        lua.globals()[name] = callback
    
    # Run the script
    try:
        with open(lua_script_path, 'r') as f:
            script = f.read()
        lua.execute(script)
    except Exception as e:
        print(f"Error executing Lua script: {e}")
        import traceback
        traceback.print_exc()  # Print full traceback for better debugging


def run_emulator(lua_script_path, config=None):
    """
    Run the emulator with the specified Lua script.
    
    Args:
        lua_script_path: Path to the Lua script to execute
        config: Optional configuration for the emulator
    """
    # Create emulator instance
    emulator = FrameEmulator(config)
    
    print(f"Starting Frame Glasses Emulator...")
    print(f"Running script: {lua_script_path}")
    print(f"Display: {emulator.config.width}x{emulator.config.height} at {emulator.config.scale}x scale")
    print("Press Ctrl+C to exit.")
    
    # Run Lua script
    try:
        # Start Lua script execution in a separate thread
        script_thread = threading.Thread(target=run_lua_script, args=(lua_script_path, emulator))
        script_thread.daemon = True
        script_thread.start()
        
        # Main loop - keep rendering frames in the main thread
        while emulator.running:
            emulator.render_frame()
            
    except KeyboardInterrupt:
        print("Emulator stopped by user")
    finally:
        emulator.stop()
