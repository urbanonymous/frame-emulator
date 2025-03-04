"""Lua runtime and script execution for the Frame Emulator."""

import time
from typing import Any, Dict, Optional

from lupa import LuaRuntime

from .constants import Alignment, PaletteColors


class LuaManager:
    """Manages Lua runtime and script execution for the Frame Emulator."""

    def __init__(self, emulator):
        """
        Initialize Lua manager.

        Args:
            emulator: FrameEmulator instance to use
        """
        self.emulator = emulator
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua_callbacks: Dict[str, Any] = {}
        self.start_time = time.time()
        self.battery_level = 100

    def setup_lua_environment(self) -> None:
        """Set up the Lua environment with Frame SDK compatibility."""
        # Create global frame object
        frame = self.lua.globals().frame = self.lua.eval("{}")

        # Set up display module
        display = self.lua.eval("{}")
        frame.display = display

        # Create PaletteColors table in Lua
        palette_colors = self.lua.eval("{}")
        for color in PaletteColors:
            palette_colors[color.name] = color.value
        frame.display.PaletteColors = palette_colors

        # Create Alignment table in Lua
        alignment = self.lua.eval("{}")
        for align in Alignment:
            alignment[align.name] = align.value
        frame.display.Alignment = alignment

        # Bind display functions
        display.set_pixel = self.emulator.display.set_pixel
        display.draw_line = self.emulator.display.draw_line
        display.draw_rect = self.emulator.display.draw_rect
        display.fill_rect = self.emulator.display.fill_rect
        display.draw_rect_filled = self.emulator.display.draw_rect_filled
        display.write_text = self.emulator.display.write_text
        display.clear = self.emulator.display.clear
        display.show = self.emulator.display.show
        display.bitmap = self.emulator.display.bitmap
        display.set_palette = self.emulator.display.set_palette
        display.get_text_width = self.emulator.display.get_text_width
        display.get_text_height = self.emulator.display.get_text_height
        display.wrap_text = self.emulator.display.wrap_text
        display.text = self.emulator.display.write_text
        display.assign_color = self.emulator.display.assign_color
        display.assign_color_ycbcr = self.emulator.display.assign_color_ycbcr
        display.set_brightness = self.emulator.display.set_brightness
        display.write_register = self.emulator.display.write_register
        display.power_save = self.emulator.display.power_save

        # Set up input module
        input_module = self.lua.eval("{}")
        frame.input = input_module
        input_module.is_key_pressed = self.emulator.is_key_pressed

        # Set up file system module
        file_module = self.lua.eval("{}")
        frame.file = file_module

        class FileHandle:
            def __init__(self, path: str, mode: str, emulator):
                self.path = path
                self.mode = mode
                self.data = bytearray()
                self.callback = None
                self.emulator = emulator

            def write(self, data: Any) -> None:
                if self.mode != "write":
                    raise RuntimeError("File not opened for writing")
                if isinstance(data, str):
                    data = data.encode("utf-8")
                self.data.extend(data)

            def read(self) -> Optional[bytes]:
                if self.mode != "read":
                    raise RuntimeError("File not opened for reading")
                if self.path in self.emulator.bluetooth.virtual_fs:
                    return self.emulator.bluetooth.virtual_fs[self.path]
                return None

            def close(self) -> None:
                if self.mode == "write":
                    # Save the file to emulator's virtual filesystem
                    self.emulator.bluetooth.virtual_fs[self.path] = bytes(self.data)
                    self.callback = None

        def file_open(path: str, mode: str):
            """Open a file in read or write mode."""
            if mode == "read" and path not in self.emulator.bluetooth.virtual_fs:
                return None
            handle = FileHandle(path, mode, self.emulator)
            if mode == "write":
                # For write mode, we need to set up the Bluetooth callback
                def write_callback(data):
                    handle.write(data)

                handle.callback = write_callback
                # Register the callback for receiving data
                self.emulator.bluetooth.set_receive_callback(write_callback)
            return handle

        def file_remove(path: str) -> bool:
            """Remove a file from the virtual filesystem."""
            if path in self.emulator.bluetooth.virtual_fs:
                del self.emulator.bluetooth.virtual_fs[path]
                return True
            return False

        def file_exists(path: str) -> bool:
            """Check if a file exists in the virtual filesystem."""
            return path in self.emulator.bluetooth.virtual_fs

        def print_complete_file(path: str) -> bool:
            """Print the complete contents of a file (used by read_file)."""
            if path in self.emulator.bluetooth.virtual_fs:
                data = self.emulator.bluetooth.virtual_fs[path]
                # Send the data in chunks if needed
                self.emulator.bluetooth.send(data)
                return True
            return False

        file_module.open = file_open
        file_module.remove = file_remove
        file_module.exists = file_exists
        self.lua.globals()["printCompleteFile"] = print_complete_file

        # Set up Bluetooth module
        bluetooth = self.lua.eval("{}")
        frame.bluetooth = bluetooth

        def bluetooth_send(data: Any) -> bool:
            """Send data over Bluetooth."""
            return self.emulator.bluetooth.send(data)

        def bluetooth_max_length() -> int:
            """Get maximum MTU length."""
            return self.emulator.bluetooth.max_length()

        def bluetooth_receive_callback(callback: Any) -> bool:
            """Register callback for receiving data."""
            self.emulator.bluetooth.set_receive_callback(callback)
            self.emulator.bluetooth.enable_notifications()
            return True

        # Bind Bluetooth functions
        bluetooth.send = bluetooth_send
        bluetooth.max_length = bluetooth_max_length
        bluetooth.receive_callback = bluetooth_receive_callback

        # Set up battery and time functions
        frame.battery_level = lambda: self.battery_level

        # Set up time module
        time_module = self.lua.eval("{}")
        frame.time = time_module
        time_module.utc = lambda: int(time.time() - self.start_time)

        # Set up sleep function
        frame.sleep = time.sleep

        # Add any registered callbacks
        for name, callback in self.lua_callbacks.items():
            self.lua.globals()[name] = callback

    def run_script(self, script_path: str) -> None:
        """
        Run a Lua script.

        Args:
            script_path: Path to the Lua script to execute
        """
        try:
            self.emulator.bluetooth.script_running = True
            with open(script_path, "r") as f:
                script = f.read()
            self.lua.execute(script)
        except Exception as e:
            print(f"Error executing Lua script: {e}")
            import traceback

            traceback.print_exc()  # Print full traceback for better debugging
        finally:
            self.emulator.bluetooth.script_running = False

    def execute(self, lua_code: str) -> None:
        """
        Execute Lua code directly.
        
        Args:
            lua_code: Lua code to execute
        """
        try:
            print(f"[LuaManager] Executing Lua code ({len(lua_code)} bytes)")
            code_preview = lua_code[:100] + "..." if len(lua_code) > 100 else lua_code
            print(f"[LuaManager] Code preview: {code_preview}")
            
            self.emulator.bluetooth.script_running = True
            self.lua.execute(lua_code)
            print(f"[LuaManager] Lua code executed successfully")
        except Exception as e:
            print(f"[LuaManager] Error executing Lua code: {e}")
            import traceback
            traceback.print_exc()  # Print full traceback for better debugging
            
            # Try to print the Lua code that caused the error
            lines = lua_code.split('\n')
            print(f"[LuaManager] Lua code that caused the error:")
            for i, line in enumerate(lines):
                print(f"{i+1}: {line}")
        finally:
            self.emulator.bluetooth.script_running = False

    def register_callback(self, name: str, callback: Any) -> None:
        """
        Register a callback that can be called from Lua code.

        Args:
            name: Name of the callback as it will be available in Lua
            callback: Python function to be called
        """
        self.lua_callbacks[name] = callback
        self.lua.globals()[name] = callback
