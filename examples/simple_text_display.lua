--[[
Simple Text Display for Frame Glasses

This app directly shows text on the screen without relying on file operations.
It demonstrates basic display functionality with auto-scrolling.
]]

-- Initialize variables
local current_line = 1
local total_lines = 0
local display_lines = {}
local max_lines_display = 7  -- Reduced to accommodate larger font
local scroll_timer = 0
local scroll_speed = 50  -- Lower = faster scroll (frames until next scroll)
local font_size = 18  -- Increased font size from default

-- Text to display (hardcoded for simplicity)
local demo_text = [[
Welcome to the Frame Emulator!

This is a sample text that demonstrates 
basic display functionality.
The text will be displayed with 
auto-scrolling and larger font.

Features of this demo:
- Displays text with proper formatting
- Auto-scrolls through content
- Uses larger font size
- Shows progress info

The Frame SDK provides a 
powerful set of APIs for:
1. Display rendering
2. Bluetooth communication
3. File system operations
4. Input handling

This demo shows how the 
Frame can display text content.
]]

-- Parse text into lines
function parse_text()
    -- Split the demo text into lines
    display_lines = {}
    
    -- Parse each line
    for line in demo_text:gmatch("([^\n]*)\n?") do
        table.insert(display_lines, line)
    end
    
    total_lines = #display_lines
    current_line = 1
    
    print("Text parsed. Total lines: " .. total_lines)
end

-- Display the text
function display_content()
    frame.display.clear(0)  -- Clear to black
    
    -- Draw title
    frame.display.write_text(
        320, 10, 
        "Auto-Scrolling Text", 
        14,  -- SKYBLUE
        24,  -- Larger title font
        frame.display.Alignment.TOP_CENTER
    )
    
    -- Calculate visible lines
    local start_line = current_line
    local end_line = math.min(start_line + max_lines_display - 1, total_lines)
    
    -- Display visible lines
    for i = start_line, end_line do
        local y_pos = 50 + (i - start_line) * 30  -- Increased spacing for larger font
        local line_text = display_lines[i] or ""
        
        -- Truncate long lines
        if #line_text > 40 then  -- Reduced for larger font
            line_text = line_text:sub(1, 37) .. "..."
        end
        
        frame.display.write_text(15, y_pos, line_text, 1, font_size)  -- WHITE, larger font
    end
    
    -- Draw navigation info
    frame.display.write_text(
        320, 350, 
        "Line " .. current_line .. " of " .. total_lines, 
        2,  -- GRAY
        14,  -- Slightly larger footer text
        frame.display.Alignment.BOTTOM_CENTER
    )
    
    frame.display.write_text(
        320, 380, 
        "Auto-scrolling enabled", 
        2,  -- GRAY
        14,  -- Slightly larger footer text
        frame.display.Alignment.BOTTOM_CENTER
    )
    
    -- Actually show the display
    frame.display.show()
end

-- Auto-scroll function
function auto_scroll()
    scroll_timer = scroll_timer + 1
    
    if scroll_timer >= scroll_speed then
        -- Reset timer
        scroll_timer = 0
        
        -- Advance to next line
        current_line = current_line + 1
        
        -- Loop back to beginning if we've reached the end
        if current_line > (total_lines - max_lines_display + 1) then
            current_line = 1
            print("Restarting scroll from beginning")
        end
        
        return true
    end
    
    return false
end

-- Main app loop
function app_loop()
    print("Starting app loop with auto-scroll")
    
    -- Parse the text
    parse_text()
    
    -- Display initial content
    display_content()
    
    local display_timer = 0
    
    while true do
        local success, error_msg = pcall(
            function()
                -- Auto-scrolling
                local scroll_changed = auto_scroll()
                
                -- Update display if scroll changed
                if scroll_changed then
                    print("Auto-scrolled to line " .. current_line)
                    display_content()
                end
                
                -- Periodically refresh display (for debugging)
                display_timer = display_timer + 1
                if display_timer >= 200 then  -- Less frequent refresh for better visibility
                    print("Periodic display refresh")
                    display_content()
                    display_timer = 0
                end
                
                frame.sleep(0.05)  -- Sleep to reduce CPU usage
            end
        )
        
        -- Catch errors
        if not success then
            print("Error in app loop: " .. tostring(error_msg))
            
            frame.display.clear(0)
            frame.display.write_text(
                320, 200, 
                "Error: " .. tostring(error_msg), 
                3,  -- RED
                18,  -- Larger font for error text
                frame.display.Alignment.MIDDLE_CENTER
            )
            frame.display.show()
            frame.sleep(0.5)
            break
        end
    end
end

-- Show initial welcome screen
print("Simple Text Display with auto-scroll starting")
frame.display.clear(0)
frame.display.write_text(
    320, 200, 
    "Auto-Scrolling Text Display\nInitializing...", 
    1,  -- WHITE
    18,  -- Larger font for welcome screen
    frame.display.Alignment.MIDDLE_CENTER
)
frame.display.show()
frame.sleep(1)  -- Short pause for visual feedback

-- Run the main app loop
print("Starting main app loop")
app_loop() 