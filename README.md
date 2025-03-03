# Frame Emulator

A Brilliant Labs Frame Glasses screen emulator

## Installation

The Frame Emulator requires Python 3.11 or newer and uses UV for dependency management.

### Prerequisites

1. Ensure you have Python 3.11+ installed:

```bash
python3 --version
```

### Installing the Frame Emulator

Clone the repository and install with UV:

```bash
# Clone the repository
git clone https://github.com/yourusername/frame-emulator.git
cd frame-emulator

# Create a virtual environment and install dependencies
make setup
```

## Examples

The Frame Emulator includes two main examples that demonstrate different ways to use the emulator:

### 1. Direct API Example

Shows how to use the Frame Emulator directly from Python without Lua scripts. This example demonstrates:
- Basic drawing and shapes
- Text rendering with different colors and alignments
- Color palette usage
- Display updates and animations

To run:
```bash
make direct-api
```

### 2. File Reader Example

Demonstrates a complete Frame app that uses Lua scripts and simulates Bluetooth file transfer. This example shows:
- Lua script execution
- Bluetooth data transfer simulation
- File system operations
- Text display with scrolling
- User input handling

To run:
```bash
make file-reader
```

## Frame SDK Display API

The emulator supports the Frame SDK display functions:

### Basic Drawing
- `clear(color)` - Clear the screen with a color
- `set_pixel(x, y, color)` - Set a pixel at x,y coordinates
- `draw_line(x1, y1, x2, y2, color)` - Draw a line
- `draw_rect(x, y, width, height, color)` - Draw a rectangle outline
- `fill_rect(x, y, width, height, color)` - Fill a rectangle
- `draw_rect_filled(x, y, width, height, border_width, border_color, fill_color)` - Draw a filled rectangle with a border

### Text Handling
- `write_text(x, y, text, color, size, alignment)` - Draw text with alignment
- `get_text_width(text)` - Get the pixel width of text
- `get_text_height(text)` - Get the pixel height of text
- `wrap_text(text, max_width)` - Wrap text to fit within a width

### Color Options

Colors can be specified in three ways:

1. **Palette Index** (0-15):
```python
emulator.clear(1)  # Clear to WHITE (palette index 1)
```

2. **RGB Integer**:
```python
emulator.fill_rect(10, 10, 100, 50, 0xFF0000)  # Red rectangle
```

3. **RGB Table** (in Lua) or RGB Values (in Python):
```python
emulator.write_text(10, 10, "Hello", (255, 0, 0))  # Red text
```

### Color Palette

The emulator supports the 16-color Frame SDK palette:

| Index | Color Name | RGB Value |
|-------|------------|-----------|
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

### Text Alignment

Available text alignment options:
- TOP_LEFT, TOP_CENTER, TOP_RIGHT
- MIDDLE_LEFT, MIDDLE_CENTER, MIDDLE_RIGHT
- BOTTOM_LEFT, BOTTOM_CENTER, BOTTOM_RIGHT

Example:
```python
emulator.write_text(320, 200, "Centered Text", 1, 20, emulator.Alignment.MIDDLE_CENTER)
```

## Development

```bash
# Setup development environment
make setup

# Run linting
make lint

# Clean up build artifacts
make clean
```

For more information about the Frame SDK, visit https://docs.brilliant.xyz/frame/building-apps-sdk/

