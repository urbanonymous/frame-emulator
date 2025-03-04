#!/usr/bin/env python3

import asyncio
import sys
import time

from frame_emulator.frame_sdk import Frame


async def print_handler(text: str):
    """Handle print output from Frame."""
    print(f"Frame output: {text}")


async def main():
    # Create Frame client
    frame = Frame("localhost", 5555)
    frame.set_debugging(True)  # Enable debug output
    frame.set_print_response_handler(print_handler)

    # Connect to emulator with retry logic
    print("Connecting to Frame emulator...")
    connection_attempts = 0
    max_attempts = 5
    
    while connection_attempts < max_attempts:
        if frame.connect(retries=1, retry_delay=0.5):
            break
        
        connection_attempts += 1
        if connection_attempts < max_attempts:
            print(f"Connection attempt {connection_attempts} failed. Retrying in 2 seconds...")
            await asyncio.sleep(2)
        else:
            print("Failed to connect after multiple attempts!")
            print("Make sure the emulator is running (examples/run_emulator.py)")
            return 1
    
    print("Connected! Sending Lua code...")

    # Send Lua code to display hello world
    lua_code = """
    -- Clear the screen to black (color 0)
    frame.display.clear(0)
    
    -- Set up our text
    local text = "Hello World!"
    
    -- Calculate center position
    -- Note: Frame display is 640x400
    local x = 320
    local y = 200
    
    -- Draw white text (color 1) centered on screen
    frame.display.write_text(x, y, text, 1, 20, "MIDDLE_CENTER")
    
    -- Add some color!
    frame.display.write_text(x, y - 40, "Welcome to", 3, 16, "MIDDLE_CENTER")  -- Red
    frame.display.write_text(x, y + 40, "Frame Emulator!", 14, 16, "MIDDLE_CENTER")  -- Sky Blue
    
    -- Show everything
    frame.display.show()
    
    -- Print some debug info
    print("Hello World displayed!")
    """

    # Send the code with retry logic
    send_attempts = 0
    max_send_attempts = 3
    
    while send_attempts < max_send_attempts:
        if frame.send(lua_code):
            break
            
        send_attempts += 1
        if send_attempts < max_send_attempts:
            print(f"Send attempt {send_attempts} failed. Retrying in 1 second...")
            await asyncio.sleep(1)
        else:
            print("Failed to send Lua code after multiple attempts!")
            frame.disconnect()
            return 1

    print("\nLua code sent successfully!")
    print("The emulator window should now show the hello world message")
    print("\nPress Ctrl+C to exit...")

    try:
        # Keep the connection alive
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nDisconnecting...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Always ensure we disconnect properly
        frame.disconnect()
        print("Disconnected.")
    
    return 0


if __name__ == "__main__":
    try:
        # Run the async main function
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
        sys.exit(0)
