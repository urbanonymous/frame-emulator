--[[
Frame SDK Display API Demo

This example demonstrates the full Frame SDK display API capabilities
including:
- Color palette and custom colors
- Text rendering with alignment
- Drawing rectangles with borders
- Drawing lines and pixels
]]

-- Set up a 1-second animation loop
local frame_count = 0
local last_time = os.time()

-- Helper to convert HSV to RGB
function hsv_to_rgb(h, s, v)
    h = h % 360
    s = math.max(0, math.min(1, s))
    v = math.max(0, math.min(1, v))
    
    local c = v * s
    local x = c * (1 - math.abs((h / 60) % 2 - 1))
    local m = v - c
    
    local r, g, b = 0, 0, 0
    if h < 60 then
        r, g, b = c, x, 0
    elseif h < 120 then
        r, g, b = x, c, 0
    elseif h < 180 then
        r, g, b = 0, c, x
    elseif h < 240 then
        r, g, b = 0, x, c
    elseif h < 300 then
        r, g, b = x, 0, c
    else
        r, g, b = c, 0, x
    end
    
    return {
        r = math.floor((r + m) * 255 + 0.5),
        g = math.floor((g + m) * 255 + 0.5),
        b = math.floor((b + m) * 255 + 0.5)
    }
end

-- Main animation loop
while true do
    -- Calculate animation parameters
    local t = frame_count / 60 -- Time in seconds
    local pulse = (math.sin(t * 3) + 1) / 2 -- 0 to 1 pulse

    -- Clear the screen
    frame.display.clear(frame.display.PaletteColors.VOID)
    
    -- Draw title with alignment
    frame.display.write_text(
        320, 40, 
        "Frame SDK Display Demo", 
        frame.display.PaletteColors.WHITE, 
        24, 
        frame.display.Alignment.TOP_CENTER
    )

    -- Section 1: Color palette demo
    frame.display.write_text(
        20, 80, 
        "Standard Palette Colors:", 
        frame.display.PaletteColors.WHITE, 
        16
    )
    
    -- Draw palette color squares
    local square_size = 30
    local gap = 5
    for i = 0, 15 do
        local x = 20 + (i % 8) * (square_size + gap)
        local y = 100 + math.floor(i / 8) * (square_size + gap)
        frame.display.fill_rect(x, y, square_size, square_size, i)
        
        -- Add color index
        frame.display.write_text(
            x + square_size/2, 
            y + square_size/2, 
            tostring(i), 
            (i == 1) and 0 or 1, -- Black on white, white on others
            12,
            frame.display.Alignment.MIDDLE_CENTER
        )
    end
    
    -- Section 2: Custom colors
    frame.display.write_text(
        320, 80, 
        "Custom Rainbow Palette:", 
        frame.display.PaletteColors.WHITE, 
        16
    )
    
    -- Create a rainbow gradient and assign to custom palette
    for i = 0, 7 do
        local hue = (t * 30 + i * 45) % 360
        local rgb = hsv_to_rgb(hue, 1, 1)
        -- Assign to upper half of palette (8-15)
        frame.display.set_palette(i + 8, rgb)
        
        -- Draw a colored rectangle
        local x = 320 + (i % 4) * (square_size + gap)
        local y = 100 + math.floor(i / 4) * (square_size + gap)
        frame.display.fill_rect(x, y, square_size, square_size, i + 8)
    end
    
    -- Section 3: Text alignment demo
    frame.display.write_text(
        20, 180, 
        "Text Alignment:", 
        frame.display.PaletteColors.WHITE, 
        16
    )
    
    -- Set up a grid for text alignment demo
    local alignments = {
        {frame.display.Alignment.TOP_LEFT, "TL"},
        {frame.display.Alignment.TOP_CENTER, "TC"},
        {frame.display.Alignment.TOP_RIGHT, "TR"},
        {frame.display.Alignment.MIDDLE_LEFT, "ML"},
        {frame.display.Alignment.MIDDLE_CENTER, "MC"},
        {frame.display.Alignment.MIDDLE_RIGHT, "MR"},
        {frame.display.Alignment.BOTTOM_LEFT, "BL"},
        {frame.display.Alignment.BOTTOM_CENTER, "BC"},
        {frame.display.Alignment.BOTTOM_RIGHT, "BR"}
    }
    
    -- Draw alignment grid
    local grid_x, grid_y = 140, 200
    local cell_width, cell_height = 80, 60
    
    -- Draw grid
    for row = 0, 2 do
        for col = 0, 2 do
            local x = grid_x + col * cell_width
            local y = grid_y + row * cell_height
            
            -- Draw cell
            frame.display.draw_rect(x, y, cell_width, cell_height, frame.display.PaletteColors.GRAY)
            
            -- Get alignment for this cell
            local index = row * 3 + col + 1
            local alignment = alignments[index][1]
            local label = alignments[index][2]
            
            -- Draw label at the cell's reference point with the right alignment
            frame.display.write_text(
                x + cell_width/2, 
                y + cell_height/2, 
                label, 
                frame.display.PaletteColors.SKYBLUE, 
                16,
                alignment
            )
        end
    end
    
    -- Section 4: Drawing functions demo
    frame.display.write_text(
        320, 180, 
        "Drawing Functions:", 
        frame.display.PaletteColors.WHITE, 
        16
    )
    
    -- Rectangle with border
    local border_pulse = math.floor(pulse * 10) + 1
    frame.display.draw_rect_filled(
        400, 200, 
        100, 80, 
        border_pulse, 
        frame.display.PaletteColors.PINK, 
        frame.display.PaletteColors.NIGHTBLUE
    )
    
    -- Star pattern with lines
    local center_x, center_y = 350, 240
    local radius = 30 + pulse * 10
    local points = 8
    
    for i = 0, points-1 do
        local angle1 = (i / points) * 2 * math.pi
        local angle2 = ((i + points/2) % points / points) * 2 * math.pi
        
        local x1 = center_x + math.cos(angle1 + t) * radius
        local y1 = center_y + math.sin(angle1 + t) * radius
        local x2 = center_x + math.cos(angle2 + t) * radius
        local y2 = center_y + math.sin(angle2 + t) * radius
        
        -- Get a color from our custom rainbow palette
        local color = 8 + (i % 8)
        
        -- Draw line
        frame.display.draw_line(x1, y1, x2, y2, color)
    end
    
    -- Wrap text example
    local lorem = "This is an example of wrapped text that automatically fits within a specified width."
    local wrapped = frame.display.wrap_text(lorem, 150)
    
    frame.display.write_text(
        20, 320, 
        "Text Wrapping:", 
        frame.display.PaletteColors.WHITE, 
        16
    )
    
    frame.display.write_text(
        20, 340, 
        wrapped, 
        frame.display.PaletteColors.YELLOW, 
        14
    )
    
    -- Display frame rate at bottom
    local current_time = os.time()
    local fps = current_time ~= last_time and frame_count or 0
    if current_time ~= last_time then
        frame_count = 0
        last_time = current_time
    end
    
    frame.display.write_text(
        320, 380, 
        "FPS: " .. fps .. " | Frame: " .. frame_count, 
        frame.display.PaletteColors.WHITE, 
        12,
        frame.display.Alignment.BOTTOM_CENTER
    )
    
    -- Show the frame
    frame.display.show()
    
    -- Increment frame counter
    frame_count = frame_count + 1
end 