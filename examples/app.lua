-- Frame Glasses Emulator Demo
-- This script demonstrates the basic display capabilities of the Frame glasses

-- Clear the screen to black
frame.display.clear(0x000000)

-- Helper function to draw a rainbow gradient
function drawRainbow()
    local width = 640
    local height = 400
    
    for y = 0, height - 1 do
        local hue = (y / height) * 360
        
        -- Convert HSV to RGB
        local h = hue / 60
        local i = math.floor(h)
        local f = h - i
        local p = 0
        local q = 1 - f
        local t = f
        
        local r, g, b = 0, 0, 0
        
        if i == 0 then
            r, g, b = 1, t, p
        elseif i == 1 then
            r, g, b = q, 1, p
        elseif i == 2 then
            r, g, b = p, 1, t
        elseif i == 3 then
            r, g, b = p, q, 1
        elseif i == 4 then
            r, g, b = t, p, 1
        else
            r, g, b = 1, p, q
        end
        
        -- Draw a horizontal line with this color
        for x = 0, width - 1 do
            local color = {
                r = r * 255,
                g = g * 255,
                b = b * 255
            }
            frame.display.setPixel(x, y, color)
        end
    end
end

-- Draw a rectangles demo
function drawRectangles()
    -- Clear screen
    frame.display.clear(0x000000)
    
    -- Draw some rectangles with different colors
    frame.display.fillRect(50, 50, 100, 100, 0xFF0000)   -- Red
    frame.display.fillRect(200, 50, 100, 100, 0x00FF00)  -- Green
    frame.display.fillRect(350, 50, 100, 100, 0x0000FF)  -- Blue
    
    -- Draw semi-transparent rectangles (using table format)
    frame.display.fillRect(100, 200, 200, 100, {r=255, g=255, b=0})   -- Yellow
    frame.display.fillRect(250, 150, 200, 100, {r=0, g=255, b=255})   -- Cyan
end

-- Draw text demo
function drawText()
    -- Clear screen
    frame.display.clear(0x000000)
    
    -- Draw title
    frame.display.drawText(120, 50, "Frame Glasses Emulator", 0xFFFFFF, 24)
    
    -- Draw some example text in different colors
    frame.display.drawText(100, 120, "Hello from Lua!", 0xFF0000, 20)
    frame.display.drawText(100, 160, "This is a text demo", 0x00FF00, 20)
    frame.display.drawText(100, 200, "640x400 pixel display", 0x0000FF, 20)
    frame.display.drawText(100, 240, "Perfect for AR applications", 0xFFFF00, 20)
    
    -- Draw footer
    frame.display.drawText(160, 320, "Press Ctrl+C to exit", 0xFFFFFF, 16)
end

-- Draw a simple animation
function drawAnimation()
    local centerX = 320
    local centerY = 200
    local radius = 100
    local maxDots = 12
    
    for frame = 1, 120 do
        -- Clear screen
        frame.display.clear(0x000000)
        
        -- Draw spinning dots
        for i = 1, maxDots do
            local angle = (frame * 0.1) + (i * (2 * math.pi / maxDots))
            local x = centerX + radius * math.cos(angle)
            local y = centerY + radius * math.sin(angle)
            
            -- Calculate color based on position
            local r = 128 + 127 * math.sin(angle)
            local g = 128 + 127 * math.sin(angle + 2)
            local b = 128 + 127 * math.sin(angle + 4)
            
            -- Draw the dot
            local size = 10 + 5 * math.sin(frame * 0.1 + i)
            frame.display.fillRect(x - size/2, y - size/2, size, size, {r=r, g=g, b=b})
        end
        
        -- Draw title
        frame.display.drawText(220, 50, "Animation Demo", 0xFFFFFF, 20)
        
        -- Wait a bit
        os.execute("sleep 0.03")
    end
end

-- Run the demos
print("Starting Frame Emulator Demo")

-- Wait a moment to let the window appear
os.execute("sleep 0.5")

print("Drawing rainbow...")
drawRainbow()
os.execute("sleep 2")

print("Drawing rectangles...")
drawRectangles()
os.execute("sleep 2")

print("Drawing text...")
drawText()
os.execute("sleep 2")

print("Drawing animation...")
drawAnimation()

print("Demo complete!") 