#!/usr/bin/env python3

import asyncio

from frame_emulator.frame_sdk import Frame


async def print_handler(text: str):
    """Handle print output from Frame."""
    print(f"Frame output: {text}")


async def main():
    # Create Frame client
    frame = Frame("localhost", 5555)
    frame.set_debugging(True)  # Enable debug output
    frame.set_print_response_handler(print_handler)

    # Connect to emulator
    print("Connecting to Frame emulator...")
    if not frame.connect():
        print("Failed to connect!")
        return

    print("Connected! Sending Lua code...")

    # Send Lua code to display hello world
    lua_code = """
    -- Clear the screen to black (color 0)
    frame.display.clear(0)
    
    -- Set up our text
    local text = "Hello World!"
    
    -- Calculate center position
    -- Note: Frame display is 640x400
    local x = (640 - frame.display.get_text_width(text)) / 2
    local y = (400 - frame.display.get_text_height(text)) / 2
    
    -- Draw white text (color 1) centered on screen
    frame.display.text(text, x, y, {color=1})
    
    -- Add some color!
    frame.display.text("Welcome to", x, y - 40, {color=3})  -- Red
    frame.display.text("Frame Emulator!", x, y + 40, {color=14})  -- Sky Blue
    
    -- Show everything
    frame.display.show()
    
    -- Print some debug info
    print("Hello World displayed!")
    """

    # Send the code
    if not frame.send(lua_code):
        print("Failed to send Lua code!")
        return

    print("\nLua code sent successfully!")
    print("The emulator window should now show the hello world message")
    print("\nPress Ctrl+C to exit...")

    try:
        # Keep the connection alive
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nDisconnecting...")
        frame.disconnect()


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
