# Frame Emulator Examples

This directory contains example scripts demonstrating how to use the Frame emulator.

## Hello World Example

This example shows how to:
1. Start the Frame emulator
2. Connect to it over TCP (emulating Bluetooth)
3. Send Lua commands to display text and graphics

### Running the Example

1. First, start the emulator in one terminal:
```bash
python3 run_emulator.py
```

2. Then, in another terminal, run the hello world client:
```bash
python3 hello_world_client.py
```

The emulator window should show:
- "Welcome to" in red
- "Hello World!" in white
- "Frame Emulator!" in sky blue

All text will be centered on the 640x400 display.

### How it Works

1. `run_emulator.py`:
   - Creates a virtual Frame device with a 640x400 display
   - Starts a TCP server on localhost:5555 to accept connections
   - Handles incoming Lua commands and updates the display

2. `hello_world_client.py`:
   - Connects to the emulator over TCP
   - Sends Lua code that:
     - Clears the screen
     - Calculates center positions for text
     - Draws text in different colors
     - Updates the display
   - Handles any print output from the Frame

### Controls

- Close either window or press Ctrl+C in either terminal to exit
- The client can send a break signal to stop script execution
- The client can send a reset signal to restart the Frame

### Color Reference

The Frame supports 16 colors (0-15):
- 0: VOID (Black)
- 1: WHITE
- 2: GRAY
- 3: RED
- 4: PINK
- 5: DARKBROWN
- 6: BROWN
- 7: ORANGE
- 8: YELLOW
- 9: DARKGREEN
- 10: GREEN
- 11: LIGHTGREEN
- 12: NIGHTBLUE
- 13: SEABLUE
- 14: SKYBLUE
- 15: CLOUDBLUE 