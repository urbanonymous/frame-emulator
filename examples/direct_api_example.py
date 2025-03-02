#!/usr/bin/env python3
"""
Example script showing how to use the Frame Emulator Python API directly without Lua.

This example demonstrates how to:
1. Import the Frame Emulator library
2. Configure the emulator
3. Draw directly to the display using Python
"""

import os
import sys
import math
import time
from frame_emulator.emulator import FrameEmulator, EmulatorConfig

class FrameDemo:
    """Demo application for Frame Emulator."""
    
    def __init__(self):
        """Initialize the demo."""
        # Create config
        config = EmulatorConfig(
            width=640,
            height=400,
            scale=1.5,
            fps=60,
            title="Frame Emulator Direct API Demo"
        )
        
        # Create the emulator
        self.emulator = FrameEmulator(config)
        self.frame_count = 0
        self.start_time = time.time()
        
    def run(self):
        """Run the demo."""
        print("Starting Frame Emulator Direct API Demo")
        print("Press Ctrl+C to exit or close the window.")
        
        try:
            # Main loop
            while self.emulator.running:
                self.update()
                self.render()
                self.emulator.render_frame()
                
        except KeyboardInterrupt:
            print("Demo stopped by user")
        finally:
            self.emulator.stop()
    
    def update(self):
        """Update demo state."""
        self.frame_count += 1
        
    def render(self):
        """Render current frame."""
        # Choose a demo based on time
        elapsed = time.time() - self.start_time
        demo_index = int(elapsed / 5) % 4
        
        if demo_index == 0:
            self.draw_rainbow()
        elif demo_index == 1:
            self.draw_rectangles()
        elif demo_index == 2:
            self.draw_text()
        else:
            self.draw_animation()
    
    def draw_rainbow(self):
        """Draw a rainbow gradient."""
        width = self.emulator.width
        height = self.emulator.height
        
        # Draw a gradient based on row position
        for y in range(height):
            hue = (y / height) * 360
            
            # Convert HSV to RGB
            h = hue / 60
            i = int(h)
            f = h - i
            p = 0
            q = 1 - f
            t = f
            
            r, g, b = 0, 0, 0
            
            if i == 0:
                r, g, b = 1, t, p
            elif i == 1:
                r, g, b = q, 1, p
            elif i == 2:
                r, g, b = p, 1, t
            elif i == 3:
                r, g, b = p, q, 1
            elif i == 4:
                r, g, b = t, p, 1
            else:
                r, g, b = 1, p, q
            
            # Convert to 0-255 range
            r, g, b = int(r * 255), int(g * 255), int(b * 255)
            
            # Draw a horizontal line with this color
            for x in range(width):
                self.emulator.set_pixel(x, y, (r << 16) | (g << 8) | b)
    
    def draw_rectangles(self):
        """Draw colored rectangles."""
        # Clear screen
        self.emulator.clear(0x000000)
        
        # Draw some rectangles with different colors
        self.emulator.fill_rect(50, 50, 100, 100, 0xFF0000)   # Red
        self.emulator.fill_rect(200, 50, 100, 100, 0x00FF00)  # Green
        self.emulator.fill_rect(350, 50, 100, 100, 0x0000FF)  # Blue
        
        # Animate a rectangle
        t = time.time() - self.start_time
        x = 100 + int(100 * math.sin(t))
        self.emulator.fill_rect(x, 200, 100, 100, 0xFFFF00)   # Yellow
    
    def draw_text(self):
        """Draw text demo."""
        # Clear screen
        self.emulator.clear(0x000000)
        
        # Draw title
        self.emulator.draw_text(120, 50, "Frame Emulator Python API", 0xFFFFFF, 24)
        
        # Draw some example text in different colors
        self.emulator.draw_text(100, 120, "Hello from Python!", 0xFF0000, 20)
        self.emulator.draw_text(100, 160, "This is a text demo", 0x00FF00, 20)
        self.emulator.draw_text(100, 200, "Direct API access", 0x0000FF, 20)
        self.emulator.draw_text(100, 240, "No Lua required", 0xFFFF00, 20)
        
        # Draw footer with frame count
        fps = self.frame_count / (time.time() - self.start_time)
        self.emulator.draw_text(160, 320, f"Frame: {self.frame_count} (FPS: {fps:.1f})", 0xFFFFFF, 16)
    
    def draw_animation(self):
        """Draw an animated pattern."""
        # Clear screen
        self.emulator.clear(0x000000)
        
        # Draw parameters
        center_x = 320
        center_y = 200
        radius = 100
        max_dots = 12
        
        # Timing
        t = time.time() - self.start_time
        
        # Draw spinning dots
        for i in range(max_dots):
            angle = (t * 2) + (i * (2 * math.pi / max_dots))
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            # Calculate color based on position
            r = 128 + int(127 * math.sin(angle))
            g = 128 + int(127 * math.sin(angle + 2))
            b = 128 + int(127 * math.sin(angle + 4))
            
            # Draw the dot
            size = 10 + int(5 * math.sin(t + i))
            self.emulator.fill_rect(int(x - size/2), int(y - size/2), size, size, (r << 16) | (g << 8) | b)
        
        # Draw title
        self.emulator.draw_text(220, 50, "Animation Demo", 0xFFFFFF, 20)


if __name__ == "__main__":
    demo = FrameDemo()
    demo.run() 