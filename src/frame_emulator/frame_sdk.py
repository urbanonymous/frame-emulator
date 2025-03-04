"""Frame SDK for connecting to the emulator."""

import asyncio
import socket
import time
from typing import Callable, Dict, Optional

from .constants import (
    BLE_CONTROL_RESTART,
    BLE_CONTROL_TERMINATE,
    BLE_DATA_FINAL,
    BLE_DATA_RAW,
    FrameDataTypePrefixes,
    FRAME_DATA_PREFIX,
)


class Frame:
    """Frame SDK for connecting to the emulator."""

    def __init__(self, host="localhost", port=5555):
        """Initialize Frame SDK."""
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self._max_payload_size = 512
        self._print_debugging = False
        self._last_print_response = ""
        self._print_response_event = asyncio.Event()
        self._user_print_response_handler = lambda _: None

    def connect(self, retries=5, retry_delay=1.0) -> bool:
        """Connect to the Frame emulator."""
        for attempt in range(retries):
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
                print(f"Connected to Frame emulator at {self.host}:{self.port}")
                return True
            except ConnectionRefusedError:
                if attempt < retries - 1:
                    print(
                        f"Connection attempt {attempt + 1} failed, retrying in {retry_delay}s..."
                    )
                    time.sleep(retry_delay)
                self.socket = None
        print("Failed to connect to Frame emulator")
        return False

    def disconnect(self) -> None:
        """Disconnect from the Frame emulator."""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

    def _send_with_length(self, data: bytes) -> bool:
        """Send data with length prefix."""
        if not self.socket:
            print("Not connected to Frame emulator")
            return False

        try:
            length_bytes = len(data).to_bytes(2, "big")
            self.socket.sendall(length_bytes + data)
            return True
        except Exception as e:
            print(f"Error sending data: {e}")
            return False

    def send(self, lua_code: str) -> bool:
        """Send Lua code to the Frame emulator."""
        return self._send_with_length(lua_code.encode("utf-8"))

    def send_break(self) -> bool:
        """Send break signal to stop script execution."""
        return self._send_with_length(b"\x03")

    def send_reset(self) -> bool:
        """Send reset signal to restart the Frame."""
        return self._send_with_length(b"\x04")

    def send_data(self, data: bytes, chunked: bool = False) -> bool:
        """Send raw data to the Frame emulator."""
        if not chunked or len(data) <= self._max_payload_size:
            # Send as single chunk
            return self._send_with_length(bytes([FRAME_DATA_PREFIX]) + data)
        else:
            # Send as multiple chunks
            chunk_size = self._max_payload_size - 2  # Account for prefix bytes
            chunks = [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]

            # Send each chunk
            for chunk in chunks[:-1]:
                prefix = bytes(
                    [FRAME_DATA_PREFIX, FrameDataTypePrefixes.LONG_DATA.value]
                )
                if not self._send_with_length(prefix + chunk):
                    return False

            # Send final chunk with count
            prefix = bytes(
                [FRAME_DATA_PREFIX, FrameDataTypePrefixes.LONG_DATA_END.value]
            )
            return self._send_with_length(
                prefix + str(len(chunks)).encode() + chunks[-1]
            )

    def set_print_response_handler(self, handler: Callable[[str], None]) -> None:
        """Set handler for print responses."""
        self._user_print_response_handler = handler if handler else lambda _: None

    def set_debugging(self, enabled: bool) -> None:
        """Enable/disable debug printing."""
        self._print_debugging = enabled
