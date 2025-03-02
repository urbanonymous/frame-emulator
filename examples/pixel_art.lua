-- Pixel Art Example for Frame Glasses
-- This script demonstrates how to create simple pixel art

-- Clear the screen to black
frame.display.clear(0x000000)

-- Draw a simple smiley face pixel art
function drawSmileyFace()
    -- Define colors
    local yellow = 0xFFFF00
    local black = 0x000000
    
    -- Face dimensions
    local faceSize = 100
    local centerX = 320
    local centerY = 200
    
    -- Draw the yellow circle face
    for y = -faceSize, faceSize do
        for x = -faceSize, faceSize do
            local distSq = x*x + y*y
            if distSq <= faceSize*faceSize then
                frame.display.setPixel(centerX + x, centerY + y, yellow)
            end
        end
    end
    
    -- Draw the eyes
    local eyeOffsetX = 30
    local eyeOffsetY = -20
    local eyeSize = 15
    
    -- Left eye
    for y = -eyeSize, eyeSize do
        for x = -eyeSize, eyeSize do
            local distSq = x*x + y*y
            if distSq <= eyeSize*eyeSize then
                frame.display.setPixel(centerX - eyeOffsetX + x, centerY + eyeOffsetY + y, black)
            end
        end
    end
    
    -- Right eye
    for y = -eyeSize, eyeSize do
        for x = -eyeSize, eyeSize do
            local distSq = x*x + y*y
            if distSq <= eyeSize*eyeSize then
                frame.display.setPixel(centerX + eyeOffsetX + x, centerY + eyeOffsetY + y, black)
            end
        end
    end
    
    -- Draw the smile (semi-circle)
    local smileOffsetY = 30
    local smileWidth = 60
    local smileHeight = 30
    
    for y = 0, smileHeight do
        for x = -smileWidth, smileWidth do
            local normalizedX = x / smileWidth
            local normalizedY = y / smileHeight
            
            -- Equation for semi-circle: x^2 + y^2 = 1, y >= 0
            local distSq = normalizedX*normalizedX + (normalizedY-1)*(normalizedY-1)
            
            if distSq >= 0.95 and distSq <= 1.05 and normalizedY >= 0 then
                frame.display.setPixel(centerX + x, centerY + smileOffsetY + y, black)
            end
        end
    end
end

-- Draw a simple landscape
function drawLandscape()
    -- Clear the screen
    frame.display.clear(0x87CEEB) -- Sky blue
    
    -- Draw sun
    local sunX = 100
    local sunY = 80
    local sunRadius = 30
    local sunColor = 0xFFFF00
    
    for y = -sunRadius, sunRadius do
        for x = -sunRadius, sunRadius do
            local distSq = x*x + y*y
            if distSq <= sunRadius*sunRadius then
                frame.display.setPixel(sunX + x, sunY + y, sunColor)
            end
        end
    end
    
    -- Draw mountains
    local mountainColor = 0x8B4513 -- Saddle brown
    local mountainPeaks = {
        {x = 100, height = 150},
        {x = 250, height = 200},
        {x = 400, height = 180},
        {x = 550, height = 120}
    }
    
    -- Draw each mountain
    for i, peak in ipairs(mountainPeaks) do
        local prevX = i > 1 and mountainPeaks[i-1].x or 0
        local width = (peak.x - prevX) * 1.5
        
        for x = 0, width do
            local normalizedX = x / width
            -- Mountain shape using sine function
            local height = peak.height * math.sin(normalizedX * math.pi)
            
            -- Draw vertical line for this mountain slice
            for y = 0, height do
                local screenX = prevX + x
                local screenY = 400 - y
                if screenX >= 0 and screenX < 640 and screenY >= 0 and screenY < 400 then
                    frame.display.setPixel(screenX, screenY, mountainColor)
                end
            end
        end
    end
    
    -- Draw ground
    local groundColor = 0x32CD32 -- Lime green
    local groundHeight = 80
    
    for y = 0, groundHeight do
        for x = 0, 639 do
            frame.display.setPixel(x, 400 - y, groundColor)
        end
    end
    
    -- Draw a simple house
    local houseX = 400
    local houseY = 320
    local houseWidth = 80
    local houseHeight = 60
    
    -- House body
    for y = 0, houseHeight do
        for x = 0, houseWidth do
            frame.display.setPixel(houseX + x, houseY - y, 0xA52A2A) -- Brown
        end
    end
    
    -- Roof (triangle)
    for y = 0, 40 do
        local width = (houseWidth / 40) * (40 - y)
        for x = -width, width do
            frame.display.setPixel(houseX + houseWidth/2 + x, houseY - houseHeight - y, 0x800000) -- Maroon
        end
    end
    
    -- Window
    for y = 0, 15 do
        for x = 0, 15 do
            frame.display.setPixel(houseX + 20 + x, houseY - 20 - y, 0x87CEFA) -- Light sky blue
        end
    end
    
    -- Door
    for y = 0, 30 do
        for x = 0, 20 do
            frame.display.setPixel(houseX + 50 + x, houseY - y, 0x8B4513) -- Saddle brown
        end
    end
end

-- Run the examples
print("Drawing smiley face...")
drawSmileyFace()
os.execute("sleep 3")

print("Drawing landscape...")
frame.display.clear(0)
drawLandscape()

-- Keep the screen active
print("Demo complete! Press Ctrl+C to exit.") 