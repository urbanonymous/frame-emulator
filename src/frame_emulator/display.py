"""Display functionality for the Frame Emulator."""

import threading
from typing import Any, Dict, Tuple, Union

import pygame

from .constants import (
    CHAR_WIDTH_MAPPING,
    DEFAULT_COLOR_PALETTE,
    Alignment,
    PaletteColors,
)


class DisplayManager:
    """Manages display functionality for the Frame Emulator."""

    def __init__(self, width: int, height: int, scale: float):
        """
        Initialize display manager.

        Args:
            width: Display width in pixels
            height: Display height in pixels
            scale: Initial display scale factor
        """
        self.width = width
        self.height = height
        self.scale = scale

        # Calculate initial window size based on scale
        window_width = int(width * scale)
        window_height = int(height * scale)

        # Set up the display window
        self.screen = pygame.display.set_mode(
            (window_width, window_height), pygame.RESIZABLE
        )

        # Create frame buffer for pixel manipulation
        self.frame_buffer = pygame.Surface((width, height))

        # Initialize thread synchronization
        self.lock = threading.Lock()

        # Text rendering properties
        self.line_height = 60
        self.char_spacing = 4
        self.fonts: Dict[int, pygame.font.Font] = {}

        # Color palette
        self.color_palette = DEFAULT_COLOR_PALETTE.copy()

        # Power save state
        self.power_save_enabled = False

    def _is_lua_table(self, obj: Any) -> bool:
        """Check if an object is a Lua table."""
        try:
            return hasattr(obj, "__pairs") or hasattr(obj, "r") or hasattr(obj, "keys")
        except Exception:
            return False

    def _get_color(self, color: Union[int, PaletteColors, Any]) -> Tuple[int, int, int]:
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
                if hasattr(color, "r") and hasattr(color, "g") and hasattr(color, "b"):
                    return (int(color.r), int(color.g), int(color.b))
                # Try dictionary-like access (object['r'])
                elif "r" in color and "g" in color and "b" in color:
                    return (int(color["r"]), int(color["g"]), int(color["b"]))
            except Exception:
                pass
        # Default to white if color can't be determined
        return (255, 255, 255)

    def get_font(self, size: int) -> pygame.font.Font:
        """Get or create a font of the specified size."""
        if size not in self.fonts:
            self.fonts[size] = pygame.font.SysFont("arial", size)
        return self.fonts[size]

    def render_frame(
        self, title: str, frame_count: int, fps_clock: pygame.time.Clock
    ) -> None:
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
            scaled_buffer = pygame.transform.scale(
                self.frame_buffer, (scaled_width, scaled_height)
            )
            self.screen.fill((30, 30, 30))  # Dark gray background
            self.screen.blit(scaled_buffer, (x_pos, y_pos))

            # Show FPS in the corner for debugging
            if frame_count % 30 == 0:  # Update FPS display every 30 frames
                pygame.display.set_caption(f"{title} - FPS: {fps_clock.get_fps():.1f}")

        pygame.display.flip()

    def set_pixel(self, x: int, y: int, color: Union[int, PaletteColors, Any]) -> None:
        """Set a pixel on the frame buffer with the given color."""
        x, y = int(x), int(y)
        if 0 <= x < self.width and 0 <= y < self.height:
            rgb = self._get_color(color)
            with self.lock:
                self.frame_buffer.set_at((x, y), rgb)

    def draw_line(
        self, x1: int, y1: int, x2: int, y2: int, color: Union[int, PaletteColors, Any]
    ) -> None:
        """Draw a line on the frame buffer."""
        rgb = self._get_color(color)
        with self.lock:
            pygame.draw.line(
                self.frame_buffer, rgb, (int(x1), int(y1)), (int(x2), int(y2))
            )

    def draw_rect(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        color: Union[int, PaletteColors, Any],
    ) -> None:
        """Draw a rectangle outline on the frame buffer."""
        rgb = self._get_color(color)
        with self.lock:
            pygame.draw.rect(
                self.frame_buffer,
                rgb,
                pygame.Rect(int(x), int(y), int(width), int(height)),
                1,  # Width of 1 pixel
            )

    def fill_rect(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        color: Union[int, PaletteColors, Any],
    ) -> None:
        """Fill a rectangle on the frame buffer."""
        rgb = self._get_color(color)
        with self.lock:
            pygame.draw.rect(
                self.frame_buffer,
                rgb,
                pygame.Rect(int(x), int(y), int(width), int(height)),
            )

    def draw_rect_filled(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        border_width: int,
        border_color: Union[int, PaletteColors, Any],
        fill_color: Union[int, PaletteColors, Any],
    ) -> None:
        """Draw a filled rectangle with a border."""
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

    def get_text_width(self, text: str) -> int:
        """Get the width of text in pixels."""
        width = 0
        for char in text:
            width += CHAR_WIDTH_MAPPING.get(ord(char), 25) + self.char_spacing
        return width

    def get_text_height(self, text: str) -> int:
        """Get the height of text in pixels."""
        num_lines = text.count("\n") + 1
        return num_lines * self.line_height

    def wrap_text(self, text: str, max_width: int) -> str:
        """Wrap text to fit within a specified width."""
        if not text:
            return ""

        lines = text.split("\n")
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

    def write_text(
        self,
        x: int,
        y: int,
        text: str,
        color: Union[int, PaletteColors, Any],
        size: int = 16,
        alignment: Alignment = Alignment.TOP_LEFT,
    ) -> None:
        """Draw text on the frame buffer with alignment."""
        rgb = self._get_color(color)
        font = self.get_font(size)

        # Split text into lines
        lines = text.split("\n")
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

            if alignment in (
                Alignment.TOP_CENTER,
                Alignment.MIDDLE_CENTER,
                Alignment.BOTTOM_CENTER,
            ):
                pos_x = x - text_width // 2
            elif alignment in (
                Alignment.TOP_RIGHT,
                Alignment.MIDDLE_RIGHT,
                Alignment.BOTTOM_RIGHT,
            ):
                pos_x = x - text_width

            if alignment in (
                Alignment.MIDDLE_LEFT,
                Alignment.MIDDLE_CENTER,
                Alignment.MIDDLE_RIGHT,
            ):
                pos_y = y - text_height // 2 + i * self.line_height
            elif alignment in (
                Alignment.BOTTOM_LEFT,
                Alignment.BOTTOM_CENTER,
                Alignment.BOTTOM_RIGHT,
            ):
                pos_y = y - text_height + i * self.line_height

            with self.lock:
                self.frame_buffer.blit(text_surface, (int(pos_x), int(pos_y)))

    def draw_text(
        self,
        x: int,
        y: int,
        text: str,
        color: Union[int, PaletteColors, Any],
        size: int = 16,
    ) -> None:
        """Legacy method for drawing text at a position. Calls write_text with TOP_LEFT alignment."""
        self.write_text(x, y, text, color, size, Alignment.TOP_LEFT)

    def clear(self, color: Union[int, PaletteColors, Any] = 0) -> None:
        """Clear the frame buffer with the specified color."""
        rgb = self._get_color(color)
        with self.lock:
            self.frame_buffer.fill(rgb)

    def show(self) -> None:
        """Update the display manually."""
        pygame.display.flip()

    def bitmap(
        self,
        x: int,
        y: int,
        width: int,
        color_format: int,
        palette_offset: int,
        data: Union[str, bytes],
    ) -> None:
        """Draw a bitmap on the screen."""
        # Convert 1-indexed coordinates to 0-indexed
        x = x - 1
        y = y - 1

        # Validate color format
        if color_format not in (2, 4, 16):
            raise ValueError("Color format must be 2, 4, or 16")

        # Validate palette offset
        palette_offset = max(0, min(15, palette_offset))

        # Calculate pixels per byte based on color format
        pixels_per_byte = {
            2: 8,  # 1 bit per pixel
            4: 4,  # 2 bits per pixel
            16: 2,  # 4 bits per pixel
        }[color_format]

        # Convert data string to bytes
        data_bytes = data.encode("latin1") if isinstance(data, str) else data

        # Calculate height based on data length and width
        total_pixels = len(data_bytes) * pixels_per_byte
        height = total_pixels // width

        with self.lock:
            byte_index = 0
            pixel_x = 0
            pixel_y = 0

            while byte_index < len(data_bytes) and pixel_y < height:
                byte = data_bytes[byte_index]

                # Process each pixel in the byte
                for bit_index in range(pixels_per_byte):
                    if pixel_x >= width:
                        pixel_x = 0
                        pixel_y += 1
                        if pixel_y >= height:
                            break

                    # Extract color index based on format
                    if color_format == 2:
                        color_index = (byte >> (7 - bit_index)) & 0x01
                    elif color_format == 4:
                        color_index = (byte >> (6 - bit_index * 2)) & 0x03
                    else:  # color_format == 16
                        color_index = (byte >> (4 - bit_index * 4)) & 0x0F

                    # Apply palette offset if color is not VOID (0)
                    if color_index > 0:
                        color_index = (color_index + palette_offset) % 16

                    # Draw the pixel
                    if 0 <= x + pixel_x < self.width and 0 <= y + pixel_y < self.height:
                        self.set_pixel(x + pixel_x, y + pixel_y, color_index)

                    pixel_x += 1

                byte_index += 1

    def set_brightness(self, brightness: int) -> None:
        """Set the display brightness."""
        # Clamp brightness to valid range
        brightness = max(-2, min(2, brightness))
        # In a real implementation, this would adjust the display hardware
        print(f"[Display] Brightness set to {brightness}")

    def write_register(self, register: int, value: int) -> None:
        """Write to a display register."""
        # Clamp values to 8 bits
        register = register & 0xFF
        value = value & 0xFF
        # In a real implementation, this would write to display hardware
        print(f"[Display] Register 0x{register:02X} set to 0x{value:02X}")

    def power_save(self, enable: bool) -> None:
        """Set display power save mode."""
        self.power_save_enabled = bool(enable)
        # In a real implementation, this would control display power
        print(f"[Display] Power save {'enabled' if enable else 'disabled'}")

    def assign_color(
        self, color: Union[str, int, PaletteColors], r: int, g: int, b: int
    ) -> None:
        """Change a palette color using RGB values."""
        # Convert RGB to YCbCr (simplified conversion)
        y = int(0.299 * r + 0.587 * g + 0.114 * b)
        cb = int(128 - 0.168736 * r - 0.331264 * g + 0.5 * b)
        cr = int(128 + 0.5 * r - 0.418688 * g - 0.081312 * b)

        # Scale to 10-bit YCbCr (4:3:3 bits)
        y = (y >> 4) & 0x0F  # 4 bits
        cb = (cb >> 5) & 0x07  # 3 bits
        cr = (cr >> 5) & 0x07  # 3 bits

        self.assign_color_ycbcr(color, y, cb, cr)

    def assign_color_ycbcr(
        self, color: Union[str, int, PaletteColors], y: int, cb: int, cr: int
    ) -> None:
        """Change a palette color using YCbCr values."""
        # Get color enum from name or index
        if isinstance(color, str):
            try:
                color = PaletteColors[color.upper()]
            except KeyError:
                return
        elif isinstance(color, int):
            try:
                color = PaletteColors(color)
            except ValueError:
                return

        # Clamp values to valid ranges
        y = max(0, min(15, y))
        cb = max(0, min(7, cb))
        cr = max(0, min(7, cr))

        # Convert YCbCr back to RGB (simplified)
        y = (y << 4) | y  # Expand to 8 bits
        cb = (cb << 5) | (cb << 2) | (cb >> 1)  # Expand to 8 bits
        cr = (cr << 5) | (cr << 2) | (cr >> 1)  # Expand to 8 bits

        r = max(0, min(255, int(y + 1.402 * (cr - 128))))
        g = max(0, min(255, int(y - 0.344136 * (cb - 128) - 0.714136 * (cr - 128))))
        b = max(0, min(255, int(y + 1.772 * (cb - 128))))

        # Update the palette
        self.color_palette[color] = (r, g, b)
