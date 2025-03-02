# Frame Emulator

A Brilliant Labs Frame Glasses screen emulator

## Installation

The Frame Emulator requires Python 3.11 or newer and uses UV for dependency management.

### Prerequisites

1. Ensure you have Python 3.11+ installed:

```bash
python3 --version
```

2. Install UV if you haven't already:

```bash
# On macOS/Linux
curl -fsS https://raw.githubusercontent.com/astral-sh/uv/main/install.sh | bash

# On Windows PowerShell
powershell -c "irm https://raw.githubusercontent.com/astral-sh/uv/main/install.ps1 | iex"
```

### Installing the Frame Emulator

Clone the repository and install with UV:

```bash
# Clone the repository
git clone https://github.com/yourusername/frame-emulator.git
cd frame-emulator

# Create a virtual environment and install dependencies using UV
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

## Usage

There are two main ways to use the Frame Emulator:

### 1. As a Python Library

Import the library in your Python code and use it directly:

```python
from frame_emulator.emulator import FrameEmulator, EmulatorConfig

# Create a configuration
config = EmulatorConfig(width=640, height=400, scale=1.5)

# Initialize the emulator
emulator = FrameEmulator(config)

# Draw directly to the screen
emulator.clear(0x000000)  # Clear to black
emulator.set_pixel(320, 200, 0xFF0000)  # Red pixel at center
emulator.write_text(100, 100, "Hello Frame!", 0xFFFFFF)

# Run the main loop
while emulator.running:
    emulator.render_frame()  # Update the display
```

### 2. Run Lua Scripts

You can run Lua scripts compatible with the Frame SDK:

```python
from frame_emulator.emulator import FrameEmulator, EmulatorConfig, run_lua_script

# Create a configuration
config = EmulatorConfig(width=640, height=400, scale=1.5)

# Initialize the emulator
emulator = FrameEmulator(config)

# Run a Lua script
run_lua_script("path/to/script.lua", emulator)

# Main loop
while emulator.running:
    emulator.render_frame()
```

Or using the provided example script:

```bash
# With Python directly
python examples/run_lua_example.py examples/app.lua

# Or using make targets
make run        # Run app.lua demo
make pixel-art  # Run pixel_art.lua example
make direct-api # Run pure Python API demo
```

## Example Scripts

The project includes example scripts:

### Lua Examples
- `examples/app.lua` - A comprehensive Lua demo showing various capabilities
- `examples/pixel_art.lua` - A simple pixel art example in Lua

### Python Examples
- `examples/run_lua_example.py` - Shows how to load and run Lua scripts
- `examples/direct_api_example.py` - A pure Python demo using the emulator API directly

## Frame SDK Display API

The emulator supports all the Frame SDK display functions:

### Basic Drawing
- `clear(color)` - Clear the screen with a color
- `set_pixel(x, y, color)` - Set a pixel at x,y coordinates
- `draw_line(x1, y1, x2, y2, color)` - Draw a line
- `draw_rect(x, y, width, height, color)` - Draw a rectangle outline
- `fill_rect(x, y, width, height, color)` - Fill a rectangle
- `draw_rect_filled(x, y, width, height, border_width, border_color, fill_color)` - Draw a filled rectangle with a border
- `bitmap(x, y, width, mode, color, data)` - Draw bitmap data

### Text Handling
- `write_text(x, y, text, color, size, alignment)` - Draw text with alignment
- `get_text_width(text)` - Get the pixel width of text
- `get_text_height(text)` - Get the pixel height of text
- `wrap_text(text, max_width)` - Wrap text to fit within a width

### Color Management
- `set_palette(palette_index, rgb_color)` - Set a color in the palette

### Display Control
- `show()` - Update the display buffer (must be called to see changes)

### Color Options

There are three ways to specify colors:

1. **Palette Index** - An integer from 0-15 that references the color palette
   ```lua
   frame.display.clear(1)  -- Clear to WHITE (palette index 1)
   ```

2. **RGB Integer** - A 24-bit integer value (e.g., `0xFF0000` for red)
   ```lua
   frame.display.fill_rect(10, 10, 100, 50, 0xFF0000)  -- Red rectangle
   ```

3. **RGB Table** - A table with r, g, b keys (in Lua) or RGB tuple (in Python)
   ```lua
   frame.display.write_text(10, 10, "Hello", {r=255, g=0, b=0})  -- Red text
   ```

### Color Palette

The emulator supports the 16-color palette from the Frame SDK:

| Index | Color Name | Default RGB Value |
|-------|------------|------------------|
| 0 | VOID | (0, 0, 0) |
| 1 | WHITE | (255, 255, 255) |
| 2 | GRAY | (157, 157, 157) |
| 3 | RED | (190, 38, 51) |
| 4 | PINK | (224, 111, 139) |
| 5 | DARKBROWN | (73, 60, 43) |
| 6 | BROWN | (164, 100, 34) |
| 7 | ORANGE | (235, 137, 49) |
| 8 | YELLOW | (247, 226, 107) |
| 9 | DARKGREEN | (47, 72, 78) |
| 10 | GREEN | (68, 137, 26) |
| 11 | LIGHTGREEN | (163, 206, 39) |
| 12 | NIGHTBLUE | (27, 38, 50) |
| 13 | SEABLUE | (0, 87, 132) |
| 14 | SKYBLUE | (49, 162, 242) |
| 15 | CLOUDBLUE | (178, 220, 239) |

You can also reference these in Lua using `frame.display.PaletteColors.NAME`:

```lua
-- Clear screen to SKYBLUE
frame.display.clear(frame.display.PaletteColors.SKYBLUE)
```

### Text Alignment

The emulator supports the following text alignment options:

```lua
-- Text alignment options
TOP_LEFT
TOP_CENTER
TOP_RIGHT
MIDDLE_LEFT
MIDDLE_CENTER
MIDDLE_RIGHT
BOTTOM_LEFT
BOTTOM_CENTER
BOTTOM_RIGHT
```

Example:
```lua
-- Draw centered text
frame.display.write_text(320, 200, "Centered Text", 1, 20, frame.display.Alignment.MIDDLE_CENTER)
```

## Development

To develop the Frame Emulator:

```bash
# Clone and setup
git clone https://github.com/yourusername/frame-emulator.git
cd frame-emulator
make setup

# Run linting
make lint

# Clean up build artifacts
make clean
```

## Architecture Decision Record: Frame Glasses Screen Emulator Implementation

### Title
Implementation of an Open-Source Emulator for Frame Glasses Screen

### Context
We are tasked with developing an open-source emulator for the 640x400 pixel screen of the frame glasses, a wearable device by Brilliant Labs. The emulator must meet the following requirements:

- **Lua Script Execution**: Execute Lua scripts written for the frame glasses, adhering to the frame_sdk (documented at https://docs.brilliant.xyz/frame/building-apps-sdk/).
- **Display Rendering**: Render the graphical output of these scripts to a virtual 640x400 display on a computer.
- **API Compatibility**: Mimic the display-related functions of the frame_sdk (e.g., setPixel, clear) to ensure compatibility with applications designed for the actual device.
- **Developer Tool**: Serve as a practical tool for developers to test and debug their applications without requiring physical frame glasses hardware.
- **Python Library**: Provide a Python library that can be used programmatically.

The emulator will focus primarily on screen rendering. Other features like Bluetooth or sensor inputs will be stubbed out or ignored unless they directly affect the display output.

### Decision
The emulator will be implemented as a Python library with the following components:

- **Lua Execution**: Use the lupa library to integrate a Lua interpreter within Python, enabling execution of Lua scripts designed for the frame glasses.
- **Display Rendering**: Use the Pygame library to render the 640x400 screen in a resizable window, preserving the 16:10 aspect ratio.
- **API Emulation**: Provide a Python-based implementation of the frame.display module, replicating the display functions from the frame_sdk. These functions will update a shared frame buffer, which Pygame will render.
- **Main Thread Rendering**: Keep Pygame rendering in the main thread to avoid cross-thread UI issues, especially on macOS.
- **Color Format**: Support 24-bit RGB color, with flexibility to handle both integer color values (e.g., 0xFF0000 for red) and Lua tables (e.g., {r=255, g=0, b=0}), based on the frame_sdk specifications.
- **Direct API Access**: Allow direct access to the emulator functions from Python, enabling pure Python applications without Lua.
- **Minimal Scope**: Focus initially on display emulation, stubbing out or omitting non-display features (e.g., input handling, networking) unless they are required for display-related functionality.

### Status
Implemented

### Consequences

#### Pros
- **Ease of Integration**: A Python library integrates seamlessly into development workflows, allowing developers to test Lua applications locally.
- **Developer-Friendly**: Python and Pygame offer a simple environment for rapid development and prototyping.
- **Performance**: Pygame can efficiently render a 640x400 screen at 60 FPS, meeting most application needs.
- **Thread Safety**: Keeping Pygame rendering in the main thread avoids cross-thread UI issues.
- **Dual Usage**: Can be used both with Lua scripts or directly from Python code.
- **Open-Source**: Released as open-source to encourage community contributions and collaboration.

#### Cons
- **Language Dependency**: Being Python-based, it may not directly integrate with applications in other languages. However, since Lua is the primary language for frame glasses apps, this is a minor issue.
- **Color Format Assumptions**: The initial 24-bit RGB assumption may need adjustment if the actual device uses a different color depth (e.g., 16-bit or monochrome).
- **Simplified Hardware Simulation**: The emulator doesn't replicate hardware-specific timing or performance, which could matter for real-time applications.

### Alternatives Considered

#### Separate Process with Inter-Process Communication (IPC)
- **Description**: Run the emulator as a separate process, using sockets or IPC to communicate with the application.
- **Pros**: Language-agnostic, usable with any programming language.
- **Cons**: Adds setup complexity and potential latency.
- **Reason for Rejection**: The complexity outweighs benefits for a development tool where direct integration is preferred.

#### Web-based Emulator Using HTML5 Canvas
- **Description**: Build a web application using HTML5 Canvas for rendering.
- **Pros**: Easy deployment and no installation required.
- **Cons**: Potential performance issues for pixel-level rendering at 60 FPS, and complex native Lua integration.
- **Reason for Rejection**: Too complex for a local development tool within this project's scope.

#### C++ Implementation with SDL
- **Description**: Use C++ and SDL for a high-performance, low-level implementation.
- **Pros**: Better performance and closer to hardware-level codebases.
- **Cons**: Longer development time due to lower-level programming.
- **Reason for Rejection**: Python and Pygame offer sufficient performance with faster development.

## Solution Details

### Prerequisites
Install the following Python libraries:
- **pygame**: For rendering the emulated screen.
- **lupa**: For executing Lua scripts within Python.

You can install them using pip:
```bash
pip install pygame lupa
```

### Implementation Overview
- **Pygame Window**: Create a resizable window to display the 640x400 screen, scaling the frame buffer while maintaining the aspect ratio.
- **Frame Buffer**: Use a Pygame.Surface to store pixel data, updated by emulated display functions.
- **Rendering Thread**: Run a background thread to refresh the display at 60 FPS, ensuring smooth visuals without blocking Lua execution.
- **Lua Integration**: Use lupa to execute Lua scripts and bind Python functions to the frame.display module, mimicking the frame_sdk API.
- **Display API**: Implement functions like setPixel and clear in Python, exposing them to Lua and updating the frame buffer.

3. Run the emulator:

```bash
python frame_emulator.py
```

### Extending the Emulator
- **Additional API Functions**: Add more display functions (e.g., drawLine, fillRect, showText) based on the frame_sdk documentation.
- **Text Rendering**: Use pygame.font to emulate text display if supported by the SDK.
- **Color Depth**: Adjust color handling if the device uses a different format (e.g., 16-bit color).
- **Stubbing Other Modules**: Add dummy implementations for non-display modules (e.g., frame.bluetooth) if Lua scripts require them.

### Verification
To ensure accuracy:
- **Check SDK Documentation**: Verify API functions and signatures at https://docs.brilliant.xyz/frame/building-apps-sdk/.
- **Review Codebase**: Examine the frame glasses codebase at https://github.com/brilliantlabsAR/frame-codebase, especially source/application/lua, for display function details.

### Additional Notes
- **Color Format**: The emulator supports both integer color values and Lua tables. Confirm the actual format used by the frame_sdk.
- **Performance**: Targets 60 FPS, adjustable if needed.
- **Open-Source License**: Release under a permissive license (e.g., MIT) to encourage community contributions.

This ADR provides a comprehensive guide to build the open-source emulator. Follow the code and steps above, and extend as needed based on your findings from the SDK and codebase.

