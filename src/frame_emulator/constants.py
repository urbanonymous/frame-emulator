"""Constants and enums for the Frame Emulator."""

from enum import Enum

# Bluetooth Service and Characteristic UUIDs
BLE_SERVICE_UUID = "7A230001-5475-A6A4-654C-8431F6AD49C4"
BLE_RX_CHAR_UUID = "7A230002-5475-A6A4-654C-8431F6AD49C4"
BLE_TX_CHAR_UUID = "7A230003-5475-A6A4-654C-8431F6AD49C4"

# Bluetooth Control Characters
BLE_CONTROL_TERMINATE = b"\x03"  # Terminate running script
BLE_CONTROL_RESTART = b"\x04"  # Clear variables and run main.lua

# Bluetooth Data Types
BLE_DATA_RAW = b"\x01"  # Raw byte data prefix
BLE_DATA_FINAL = b"\x02"  # Final chunk marker


class BluetoothState(Enum):
    """Bluetooth connection states."""

    UNPAIRED = "unpaired"
    PAIRED = "paired"
    CONNECTED = "connected"


class PaletteColors(Enum):
    """Color palette matching the Frame SDK."""

    VOID = 0
    WHITE = 1
    GRAY = 2
    RED = 3
    PINK = 4
    DARKBROWN = 5
    BROWN = 6
    ORANGE = 7
    YELLOW = 8
    DARKGREEN = 9
    GREEN = 10
    LIGHTGREEN = 11
    NIGHTBLUE = 12
    SEABLUE = 13
    SKYBLUE = 14
    CLOUDBLUE = 15


class FrameDataTypePrefixes(Enum):
    """Frame data type prefixes for different kinds of data."""

    LONG_DATA = 0x01
    LONG_DATA_END = 0x02
    WAKE = 0x03
    TAP = 0x04
    MIC_DATA = 0x05
    DEBUG_PRINT = 0x06
    LONG_TEXT = 0x0A
    LONG_TEXT_END = 0x0B


# Common Frame Data prefix
FRAME_DATA_PREFIX = 1


class Alignment(Enum):
    """Text alignment options matching the Frame SDK."""

    TOP_LEFT = "top_left"
    TOP_CENTER = "top_center"
    TOP_RIGHT = "top_right"
    MIDDLE_LEFT = "middle_left"
    MIDDLE_CENTER = "middle_center"
    MIDDLE_RIGHT = "middle_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_CENTER = "bottom_center"
    BOTTOM_RIGHT = "bottom_right"


# Character width mapping for text rendering based on Frame SDK
CHAR_WIDTH_MAPPING = {
    0x000020: 13,
    0x000021: 5,
    0x000022: 13,
    0x000023: 19,
    0x000024: 17,
    0x000025: 34,
    0x000026: 20,
    0x000027: 5,
    0x000028: 10,
    0x000029: 11,
    0x00002A: 21,
    0x00002B: 19,
    0x00002C: 8,
    0x00002D: 17,
    0x00002E: 6,
    0x00002F: 15,
    0x000030: 18,
    0x000031: 16,
    0x000032: 16,
    0x000033: 15,
    0x000034: 18,
    0x000035: 15,
    0x000036: 17,
    0x000037: 15,
    0x000038: 18,
    0x000039: 17,
    0x00003A: 6,
    0x00003B: 8,
    0x00003C: 19,
    0x00003D: 19,
    0x00003E: 19,
    0x00003F: 14,
    0x000040: 31,
    0x000041: 22,
    0x000042: 18,
    0x000043: 16,
    0x000044: 19,
    0x000045: 17,
    0x000046: 17,
    0x000047: 18,
    0x000048: 19,
    0x000049: 12,
    0x00004A: 14,
    0x00004B: 19,
    0x00004C: 16,
    0x00004D: 23,
    0x00004E: 19,
    0x00004F: 20,
    0x000050: 18,
    0x000051: 22,
    0x000052: 20,
    0x000053: 17,
    0x000054: 20,
    0x000055: 19,
    0x000056: 21,
    0x000057: 23,
    0x000058: 21,
    0x000059: 23,
    0x00005A: 17,
    0x00005B: 9,
    0x00005C: 15,
    0x00005D: 10,
    0x00005E: 20,
    0x00005F: 25,
    0x000060: 11,
    0x000061: 19,
    0x000062: 18,
    0x000063: 13,
    0x000064: 18,
    0x000065: 16,
    0x000066: 15,
    0x000067: 20,
    0x000068: 18,
    0x000069: 5,
    0x00006A: 11,
    0x00006B: 18,
    0x00006C: 8,
    0x00006D: 28,
    0x00006E: 18,
    0x00006F: 18,
    0x000070: 18,
    0x000071: 18,
    0x000072: 11,
    0x000073: 15,
    0x000074: 14,
    0x000075: 17,
    0x000076: 19,
    0x000077: 30,
    0x000078: 20,
    0x000079: 20,
    0x00007A: 16,
    0x00007B: 12,
    0x00007C: 5,
    0x00007D: 12,
    0x00007E: 17,
}

# Default color palette
DEFAULT_COLOR_PALETTE = {
    PaletteColors.VOID: (0, 0, 0),
    PaletteColors.WHITE: (255, 255, 255),
    PaletteColors.GRAY: (157, 157, 157),
    PaletteColors.RED: (190, 38, 51),
    PaletteColors.PINK: (224, 111, 139),
    PaletteColors.DARKBROWN: (73, 60, 43),
    PaletteColors.BROWN: (164, 100, 34),
    PaletteColors.ORANGE: (235, 137, 49),
    PaletteColors.YELLOW: (247, 226, 107),
    PaletteColors.DARKGREEN: (47, 72, 78),
    PaletteColors.GREEN: (68, 137, 26),
    PaletteColors.LIGHTGREEN: (163, 206, 39),
    PaletteColors.NIGHTBLUE: (27, 38, 50),
    PaletteColors.SEABLUE: (0, 87, 132),
    PaletteColors.SKYBLUE: (49, 162, 242),
    PaletteColors.CLOUDBLUE: (178, 220, 239),
}
