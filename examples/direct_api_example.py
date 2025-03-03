#!/usr/bin/env python3
"""
Direct API Example

This example demonstrates using the Frame Emulator directly from Python,
without using Lua scripts. It shows basic drawing, text rendering,
and color manipulation.
"""

import sys
import tempfile
import time
from pathlib import Path

# Add parent directory to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from frame_emulator.emulator import EmulatorConfig, run_emulator


def main():
    print("Frame Emulator - Direct API Example")

    # Create a temporary Lua script with our demo
    lua_script = """
    -- Demo content
    local text = [[The Frame Emulator can be used directly from Python!
    
This example shows:
- Text rendering with different colors
- Basic shapes and drawing
- Color palette usage
- Display updates
    ]]
    
    local frame_count = 0
    local start_time = frame.time.utc()
    
    while frame.time.utc() - start_time < 10 do  -- Run for 10 seconds
        -- Clear screen
        frame.display.clear(frame.display.PaletteColors.VOID)
        
        -- Draw title
        frame.display.write_text(
            320, 20,
            "Frame Direct API Demo",
            frame.display.PaletteColors.SKYBLUE,
            24,
            frame.display.Alignment.TOP_CENTER
        )
        
        -- Draw multiline text
        local y = 80
        for line in text:gmatch("[^\\n]+") do
            frame.display.write_text(
                20, y,
                line:match("^%s*(.-)%s*$"),  -- Trim whitespace
                frame.display.PaletteColors.WHITE,
                16
            )
            y = y + 30
        end
        
        -- Draw some shapes
        -- Animated rectangle with border
        local pulse = (frame.time.utc() * 2) % 1  -- 0 to 1 pulse
        local border_width = math.floor(2 + pulse * 4)  -- 2 to 6 pixels
        
        frame.display.draw_rect_filled(
            40, 250,
            200, 100,
            border_width,
            frame.display.PaletteColors.PINK,
            frame.display.PaletteColors.NIGHTBLUE
        )
        
        -- Color palette demo
        local x = 280
        local y = 250
        local square_size = 30
        local gap = 5
        
        frame.display.write_text(
            x, y - 20,
            "Color Palette:",
            frame.display.PaletteColors.WHITE,
            16
        )
        
        for i = 0, 15 do  -- 16 colors in palette
            local color_x = x + (i % 8) * (square_size + gap)
            local color_y = y + math.floor(i / 8) * (square_size + gap)
            
            -- Draw color square
            frame.display.fill_rect(
                color_x, color_y,
                square_size, square_size,
                i
            )
            
            -- Draw color index
            local text_color = i == 1 and 0 or 1  -- Black on white, white on others
            frame.display.write_text(
                color_x + square_size/2,
                color_y + square_size/2,
                tostring(i),
                text_color,
                12,
                frame.display.Alignment.MIDDLE_CENTER
            )
        end
        
        -- Show frame counter
        frame.display.write_text(
            320, 380,
            "Frame: " .. frame_count,
            frame.display.PaletteColors.GRAY,
            12,
            frame.display.Alignment.BOTTOM_CENTER
        )
        
        -- Update display
        frame.display.show()
        frame_count = frame_count + 1
        
        -- Add a small delay to control frame rate
        frame.sleep(1/60)  -- Target 60 FPS
    end
    """

    # Create a temporary file for the Lua script
    with tempfile.NamedTemporaryFile(mode="w", suffix=".lua", delete=False) as f:
        f.write(lua_script)
        script_path = f.name

    try:
        # Create emulator with configuration
        config = EmulatorConfig(
            width=640, height=400, scale=1.5, title="Frame Direct API Demo"
        )

        # Run the emulator with our script
        run_emulator(script_path, config)

    finally:
        # Clean up the temporary script file
        Path(script_path).unlink()


if __name__ == "__main__":
    main()
