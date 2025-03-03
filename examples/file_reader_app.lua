--[[
File Reader App for Frame Glasses

This app receives file content over Bluetooth and displays it.
It handles receiving chunks of file data and assembling them.
]]

-- Frame to phone flags
BATTERY_LEVEL_FLAG = 0x0c

-- Phone to Frame flags
FILE_CONTENT_FLAG = 0x0f  -- Using 0x0f for file content

local app_data = {}
local current_line = 1
local total_lines = 0
local lines = {}
local scroll_position = 0
local max_lines_display = 10
local current_file = nil
local file_path = "/demo_text.txt"  -- Store in root directory

-- Data Handler: called when data arrives, must execute quickly.
function update_app_data(data)
    -- Check if this is file content
    if string.byte(data, 1) == FILE_CONTENT_FLAG then
        if not current_file then
            -- Open file for writing if not already open
            current_file = frame.file.open(file_path, "write")
            if not current_file then
                print("Error: Could not open file for writing")
                return
            end
        end
        -- Write the data (excluding the flag byte)
        current_file:write(string.sub(data, 2))
    end
end

-- Parse the file content
function parse_file_content()
    -- Try to open the file for reading
    local file = frame.file.open(file_path, "read")
    if not file then
        return nil
    end
    
    -- Read the file line by line
    lines = {}
    while true do
        local line = file:read()
        if line == nil then
            break
        end
        table.insert(lines, line)
    end
    file:close()
    
    total_lines = #lines
    current_line = 1
    
    return true
end

-- draw the current file content on the display
function display_file_content()
    frame.display.clear(frame.display.PaletteColors.VOID)
    
    -- Draw title
    frame.display.write_text(
        320, 10, 
        "File Reader", 
        frame.display.PaletteColors.SKYBLUE, 
        20, 
        frame.display.Alignment.TOP_CENTER
    )
    
    -- Check if we have file content
    if #lines == 0 then
        frame.display.write_text(
            320, 200, 
            "Waiting for file content...", 
            frame.display.PaletteColors.WHITE, 
            16,
            frame.display.Alignment.MIDDLE_CENTER
        )
        return
    end
    
    -- Calculate visible lines
    local start_line = current_line
    local end_line = math.min(start_line + max_lines_display - 1, total_lines)
    
    -- Display visible lines
    for i = start_line, end_line do
        local y_pos = 40 + (i - start_line) * 20
        local line_text = lines[i] or ""
        -- Truncate long lines
        if #line_text > 60 then
            line_text = line_text:sub(1, 57) .. "..."
        end
        frame.display.write_text(10, y_pos, line_text, frame.display.PaletteColors.WHITE)
    end
    
    -- Draw navigation info
    frame.display.write_text(
        320, 350, 
        "Line " .. current_line .. " of " .. total_lines, 
        frame.display.PaletteColors.GRAY, 
        12,
        frame.display.Alignment.BOTTOM_CENTER
    )
    
    frame.display.write_text(
        320, 370, 
        "Use up/down arrows to scroll", 
        frame.display.PaletteColors.GRAY, 
        12,
        frame.display.Alignment.BOTTOM_CENTER
    )
    
    frame.display.write_text(
        320, 390, 
        "Showing " .. (end_line - start_line + 1) .. " of " .. total_lines .. " lines", 
        frame.display.PaletteColors.GRAY, 
        12,
        frame.display.Alignment.BOTTOM_CENTER
    )
end

-- Handle input for scrolling
function handle_input()
    if frame.input and frame.input.is_key_pressed then
        if frame.input.is_key_pressed("up") then
            current_line = math.max(1, current_line - 1)
            return true
        elseif frame.input.is_key_pressed("down") then
            current_line = math.min(total_lines - max_lines_display + 1, current_line + 1)
            return true
        end
    end
    return false
end

-- Main app loop
function app_loop()
    local last_batt_update = 0
    local file_received = false
    
    -- Clear display initially
    frame.display.clear(frame.display.PaletteColors.VOID)
    frame.display.write_text(
        320, 200, 
        "File Reader App Started\nWaiting for file content...", 
        frame.display.PaletteColors.WHITE,
        16,
        frame.display.Alignment.MIDDLE_CENTER
    )
    frame.display.show()
    
    while true do
        rc, err = pcall(
            function()
                -- Input handling
                local input_changed = handle_input()
                
                -- Check if we should try to read the file
                if current_file and not file_received then
                    current_file:close()
                    current_file = nil
                    file_received = true
                    
                    -- Try to parse the file
                    if parse_file_content() then
                        display_file_content()
                        frame.display.show()
                    end
                end
                
                -- Update display if input changed
                if input_changed then
                    display_file_content()
                    frame.display.show()
                end
                
                frame.sleep(0.05)  -- Sleep to reduce CPU usage
                
                -- periodic battery level updates
                local t = frame.time.utc()
                if (last_batt_update == 0 or (t - last_batt_update) > 180) then
                    pcall(frame.bluetooth.send, string.char(BATTERY_LEVEL_FLAG) .. string.char(math.floor(frame.battery_level())))
                    last_batt_update = t
                end
            end
        )
        -- Catch the break signal here and clean up the display
        if rc == false then
            -- send the error back on the stdout stream
            print(err)
            frame.display.clear(frame.display.PaletteColors.VOID)
            frame.display.write_text(
                320, 200, 
                "Error: " .. err, 
                frame.display.PaletteColors.RED,
                16,
                frame.display.Alignment.MIDDLE_CENTER
            )
            frame.display.show()
            frame.sleep(0.5)
            break
        end
    end
end

-- register the handler as a callback for all data sent from the host
frame.bluetooth.receive_callback(update_app_data)

-- Show initial welcome screen
frame.display.clear(frame.display.PaletteColors.VOID)
frame.display.write_text(
    320, 200, 
    "File Reader App\nReady to receive file content", 
    frame.display.PaletteColors.WHITE,
    16,
    frame.display.Alignment.MIDDLE_CENTER
)
frame.display.show()

-- run the main app loop
app_loop() 