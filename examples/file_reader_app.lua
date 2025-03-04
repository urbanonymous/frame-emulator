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
local last_display_update = 0
local debug_mode = true

-- Simple debug printing function
function debug_print(msg)
    if debug_mode then
        print("[DEBUG] " .. tostring(msg))
    end
end

-- Data Handler: called when data arrives, must execute quickly.
function update_app_data(data)
    debug_print("Received data, length: " .. #data)
    
    -- Check if this is file content
    if string.byte(data, 1) == FILE_CONTENT_FLAG then
        debug_print("File content packet received")
        
        if not current_file then
            -- Open file for writing if not already open
            debug_print("Opening file for writing: " .. file_path)
            current_file = frame.file.open(file_path, "write")
            if not current_file then
                print("Error: Could not open file for writing")
                return
            end
        end
        
        -- Write the data (excluding the flag byte)
        local content = string.sub(data, 2)
        debug_print("Writing " .. #content .. " bytes to file")
        current_file:write(content)
        
        -- Force update display after receiving data
        last_display_update = 0
    else
        debug_print("Received non-file data: " .. string.byte(data, 1))
    end
end

-- Parse the file content
function parse_file_content()
    debug_print("Parsing file content...")
    
    -- Try to open the file for reading
    local file = frame.file.open(file_path, "read")
    if not file then
        print("Error: Could not open file for reading")
        return nil
    end
    
    -- Read the file line by line
    lines = {}
    local line_count = 0
    
    debug_print("Reading file line by line...")
    while true do
        local line = file:read()
        if line == nil then
            break
        end
        table.insert(lines, line)
        line_count = line_count + 1
        
        if line_count % 5 == 0 then
            debug_print("Read " .. line_count .. " lines so far")
        end
    end
    
    file:close()
    
    total_lines = #lines
    current_line = 1
    
    debug_print("File parsed. Total lines: " .. total_lines)
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
        debug_print("No lines to display")
        return
    end
    
    -- Calculate visible lines
    local start_line = current_line
    local end_line = math.min(start_line + max_lines_display - 1, total_lines)
    
    debug_print("Displaying lines " .. start_line .. " to " .. end_line)
    
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
    
    -- Updated navigation instructions for Frame Glasses
    frame.display.write_text(
        320, 370, 
        "Tap to scroll down, Double-tap to scroll up", 
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
    
    -- Actually show the display
    frame.display.show()
end

-- Handle input for scrolling using tap events instead of keys
function handle_input()
    -- For emulator, use keyboard
    if frame.input and frame.input.is_key_pressed then
        if frame.input.is_key_pressed("up") then
            debug_print("Up key pressed, scrolling up")
            current_line = math.max(1, current_line - 1)
            return true
        elseif frame.input.is_key_pressed("down") then
            debug_print("Down key pressed, scrolling down")
            current_line = math.min(total_lines - max_lines_display + 1, current_line + 1)
            return true
        end
    end
    
    -- For real Frame Glasses, we would use tap events
    -- Since this is just an emulator, we'll keep the key events but
    -- will update the instructions to reflect the real device interaction
    
    return false
end

-- Main app loop
function app_loop()
    local last_batt_update = 0
    local file_received = false
    local display_timer = 0
    
    debug_print("Starting app loop")
    
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
        local success, error_msg = pcall(
            function()
                -- Input handling
                local input_changed = handle_input()
                
                -- Check if we should try to read the file
                if current_file and not file_received then
                    debug_print("File received, closing file handle")
                    current_file:close()
                    current_file = nil
                    file_received = true
                    
                    -- Try to parse the file
                    debug_print("Attempting to parse file")
                    if parse_file_content() then
                        debug_print("File parsed successfully, updating display")
                        display_file_content()
                    else
                        debug_print("Failed to parse file")
                    end
                end
                
                -- Update display if input changed
                if input_changed then
                    debug_print("Input changed, updating display")
                    display_file_content()
                end
                
                -- Periodically refresh display regardless of input (for debugging)
                display_timer = display_timer + 1
                if display_timer >= 100 then  -- About every 5 seconds
                    debug_print("Periodic display refresh")
                    if #lines > 0 then
                        display_file_content()
                    end
                    display_timer = 0
                end
                
                frame.sleep(0.05)  -- Sleep to reduce CPU usage
                
                -- periodic battery level updates
                local t = frame.time.utc()
                if (last_batt_update == 0 or (t - last_batt_update) > 180) then
                    if frame.battery_level and frame.bluetooth and frame.bluetooth.send then
                        pcall(frame.bluetooth.send, string.char(BATTERY_LEVEL_FLAG) .. string.char(math.floor(frame.battery_level())))
                        last_batt_update = t
                    end
                end
            end
        )
        
        -- Catch the break signal here and clean up the display
        if not success then
            -- send the error back on the stdout stream
            print("Error in app loop: " .. tostring(error_msg))
            debug_print("Error stack trace: " .. debug.traceback())
            
            frame.display.clear(frame.display.PaletteColors.VOID)
            frame.display.write_text(
                320, 200, 
                "Error: " .. tostring(error_msg), 
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

-- Print initial debug info
debug_print("File Reader App starting")
debug_print("Checking for bluetooth functionality...")

-- register the handler as a callback for all data sent from the host
if frame.bluetooth and frame.bluetooth.receive_callback then
    debug_print("Bluetooth receive_callback available, registering handler")
    frame.bluetooth.receive_callback(update_app_data)
else
    print("ERROR: Bluetooth receive_callback not available!")
end

-- Show initial welcome screen
debug_print("Displaying welcome screen")
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
debug_print("Starting main app loop")
app_loop() 