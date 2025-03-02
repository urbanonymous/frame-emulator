--[[
Text File Reader App

This Lua script loads text from a file (text_text.txt) and displays it on the Frame SDK
with scrolling functionality.
]]

-- Path to the text file to read
local FILE_PATH = "examples/text_text.txt"

-- App state
local app_state = {
    text = "",              -- The full text content
    lines = {},             -- Parsed text lines
    current_top_line = 1,   -- Current top visible line
    visible_lines = 8,      -- Number of visible lines
    title = "Frame Text Reader",
    auto_scroll_timer = 0,  -- Timer for auto-scrolling
    auto_scroll_interval = 2 -- Auto-scroll every 2 seconds
}

-- Key constants since they are not defined in the emulator yet
local KEY_UP = 38    -- ASCII for up arrow
local KEY_DOWN = 40  -- ASCII for down arrow

-- Colors
local COLORS = {
    background = {0, 0, 0},
    text = {255, 255, 255},
    title = {0, 180, 255},
    instructions = {180, 180, 180}
}

-- Function to read a text file
function read_text_file(file_path)
    local file = io.open(file_path, "r")
    if not file then
        return "ERROR: Could not open file: " .. file_path
    end
    
    local content = file:read("*all")
    file:close()
    
    print("Read " .. #content .. " bytes from " .. file_path)
    return content
end

-- Function to parse text into lines that fit the screen
function parse_text_into_lines(text, max_width)
    local lines = {}
    local current_line = ""
    local max_chars = max_width / 8  -- Approximate characters per line based on font size
    
    -- Split by newlines first
    for line in text:gmatch("([^\n]*)\n?") do
        if line ~= "" then
            -- If line is longer than max_chars, split it further
            if #line > max_chars then
                while #line > 0 do
                    local segment = line:sub(1, max_chars)
                    line = line:sub(max_chars + 1)
                    table.insert(lines, segment)
                end
            else
                table.insert(lines, line)
            end
        else
            -- Add empty lines for paragraph breaks
            table.insert(lines, "")
        end
    end
    
    return lines
end

-- Function to render the text on screen
function render_text()
    -- Clear the screen
    frame.display.clear(table.unpack(COLORS.background))
    
    -- Draw title
    frame.display.write_text(10, 10, app_state.title, COLORS.title, 20)
    
    -- Draw text content
    for i = 1, app_state.visible_lines do
        local line_index = app_state.current_top_line + i - 1
        if line_index <= #app_state.lines then
            frame.display.write_text(10, 40 + (i * 20), app_state.lines[line_index], COLORS.text)
        end
    end
    
    -- Draw scroll position and instructions
    local total_lines = #app_state.lines
    local scroll_info = "Line " .. app_state.current_top_line .. " of " .. total_lines
    
    frame.display.write_text(10, 280, scroll_info, COLORS.instructions)
    frame.display.write_text(10, 310, "Auto-scrolling text", COLORS.instructions)
    
    -- Show the updated display
    frame.display.show()
end

-- Function to scroll text up
function scroll_up()
    if app_state.current_top_line > 1 then
        app_state.current_top_line = app_state.current_top_line - 1
        render_text()
    end
end

-- Function to scroll text down
function scroll_down()
    if app_state.current_top_line < (#app_state.lines - app_state.visible_lines + 1) then
        app_state.current_top_line = app_state.current_top_line + 1
        render_text()
    end
end

-- Main application loop
function app_loop()
    -- Load the text file
    app_state.text = read_text_file(FILE_PATH)
    
    -- Parse text into lines
    app_state.lines = parse_text_into_lines(app_state.text, 300)
    
    print("Parsed " .. #app_state.lines .. " lines")
    
    -- Initial render
    render_text()
    
    -- Keep the app running
    while frame.is_running() do
        -- Check if it's time to auto-scroll
        local current_time = os.time()
        if current_time - app_state.auto_scroll_timer >= app_state.auto_scroll_interval then
            scroll_down()
            
            -- If we've reached the end, go back to the top
            if app_state.current_top_line >= (#app_state.lines - app_state.visible_lines + 1) then
                app_state.current_top_line = 1
                render_text()
            end
            
            app_state.auto_scroll_timer = current_time
        end
        
        -- Sleep to avoid consuming too much CPU
        frame.sleep(0.05)
    end
end

-- Start the app
app_loop() 