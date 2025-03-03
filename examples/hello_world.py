#!/usr/bin/env python3

import time

from frame_emulator.frame_sdk import Frame


def main():
    # Connect to Frame emulator
    print("Connecting to Frame emulator...")
    frame = Frame()  # Default localhost:5555
    if not frame.connect():
        print("Failed to connect to Frame emulator")
        return
    print("Connected!")

    # Clear the screen and set up our text
    lua_commands = """
    -- Clear the screen to black
    frame.display.clear()
    
    -- Calculate center position for text
    local text = "Hello World!"
    local x = (640 - frame.display.get_text_width(text)) / 2
    local y = (400 - frame.display.get_text_height(text)) / 2
    
    -- Draw the text in white at the center
    frame.display.text(text, x, y, {color='WHITE'})
    
    -- Show the changes
    frame.display.show()
    """

    # Send the Lua commands
    print("Sending Lua commands...")
    frame.send(lua_commands)

    # Keep the script running
    print("Press Ctrl+C to exit")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDisconnecting...")
        frame.disconnect()


if __name__ == "__main__":
    main()
