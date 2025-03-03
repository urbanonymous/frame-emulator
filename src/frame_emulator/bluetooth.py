"""Bluetooth functionality for the Frame Emulator."""

import socket
import threading
import time
from enum import Enum
from typing import Any, Callable, Dict, Optional

from .constants import (
    BLE_CONTROL_RESTART,
    BLE_CONTROL_TERMINATE,
    BLE_DATA_FINAL,
    BLE_DATA_RAW,
    BluetoothState,
)


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


_FRAME_DATA_PREFIX = 1


class BluetoothManager:
    """Manages Bluetooth functionality for the Frame Emulator."""

    def __init__(self, host="localhost", port=5555):
        """Initialize Bluetooth manager."""
        self.state = "unpaired"
        self.mtu = 512  # Configurable MTU size
        self.data_queue = []
        self.receive_callback = None
        self.chunk_count = 0
        self.script_running = False
        self.notifications_enabled = False
        self.virtual_fs: Dict[str, bytes] = {}

        # TCP socket setup
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self._start_server()

    def _start_server(self):
        """Start TCP server to accept connections."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)

            # Start accepting connections in a separate thread
            self.accept_thread = threading.Thread(target=self._accept_connections)
            self.accept_thread.daemon = True
            self.accept_thread.start()

            print(f"[Bluetooth] Emulator listening on {self.host}:{self.port}")
        except Exception as e:
            print(f"[Bluetooth] Error starting server: {e}")

    def _accept_connections(self):
        """Accept incoming connections."""
        while True:
            try:
                client_socket, addr = self.server_socket.accept()
                print(f"[Bluetooth] Connection from {addr}")
                self.client_socket = client_socket
                self.state = "connected"

                # Start receiving data from this client
                self.receive_thread = threading.Thread(target=self._receive_data)
                self.receive_thread.daemon = True
                self.receive_thread.start()
            except Exception as e:
                print(f"[Bluetooth] Connection error: {e}")
                time.sleep(1)

    def _receive_data(self):
        """Receive data from connected client."""
        while self.state == "connected":
            try:
                # Read 2-byte length prefix
                length_bytes = self.client_socket.recv(2)
                if not length_bytes:
                    break

                length = int.from_bytes(length_bytes, "big")
                if length > 0:
                    # Read the actual data
                    data = self.client_socket.recv(length)
                    if not data:
                        break
                    self._handle_received_data(data)
            except Exception as e:
                print(f"[Bluetooth] Receive error: {e}")
                break
        self.disconnect()

    def _handle_received_data(self, data: bytes):
        """Handle received data based on its prefix."""
        try:
            # Handle Lua code (no special prefix)
            if len(data) > 0 and data[0] not in [
                p.value for p in FrameDataTypePrefixes
            ]:
                if self.receive_callback:
                    self.receive_callback(data)
                return

            # Handle control signals
            if data == b"\x03":  # Break signal
                print("[Bluetooth] Break signal received")
                self.script_running = False
                return

            if data == b"\x04":  # Reset signal
                print("[Bluetooth] Reset signal received")
                self.script_running = False
                # TODO: Implement reset functionality
                return

            # Handle prefixed data
            if len(data) > 1:
                prefix = data[0]
                payload = data[1:]

                if prefix == _FRAME_DATA_PREFIX:
                    if len(payload) > 0:
                        data_type = payload[0]
                        data_content = payload[1:]

                        if data_type == FrameDataTypePrefixes.LONG_DATA.value:
                            # Handle chunked data
                            self._send_response(
                                bytes(
                                    [
                                        _FRAME_DATA_PREFIX,
                                        FrameDataTypePrefixes.LONG_DATA.value,
                                    ]
                                )
                                + b"OK"
                            )
                        elif data_type == FrameDataTypePrefixes.LONG_DATA_END.value:
                            # Handle end of chunked data
                            self._send_response(
                                bytes(
                                    [
                                        _FRAME_DATA_PREFIX,
                                        FrameDataTypePrefixes.LONG_DATA_END.value,
                                    ]
                                )
                                + b"OK"
                            )

        except Exception as e:
            print(f"[Bluetooth] Error handling data: {e}")

    def _send_response(self, data: bytes):
        """Send a response with proper length prefix."""
        if self.state == "connected" and self.client_socket:
            try:
                length_bytes = len(data).to_bytes(2, "big")
                self.client_socket.sendall(length_bytes + data)
            except Exception as e:
                print(f"[Bluetooth] Error sending response: {e}")

    def pair(self) -> bool:
        """Simulate pairing with the Frame device."""
        if self.state == "unpaired":
            self.state = "paired"
            print("[Bluetooth] Device paired successfully")
            return True
        return False

    def connect(self) -> bool:
        """Wait for client connection."""
        return self.state == "connected"

    def disconnect(self) -> bool:
        """Disconnect current client."""
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
            self.client_socket = None
        self.state = "paired"
        print("[Bluetooth] Device disconnected")
        return True

    def unpair(self) -> bool:
        """Unpair and stop server."""
        self.disconnect()
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        self.state = "unpaired"
        print("[Bluetooth] Device unpaired")
        return True

    def enable_notifications(self) -> bool:
        """Enable notifications for the RX characteristic."""
        if self.state == "connected":
            self.notifications_enabled = True
            print("[Bluetooth] RX notifications enabled")
            return True
        return False

    def send(self, data: Any) -> bool:
        """Send data to connected client."""
        if self.state != "connected" or not self.client_socket:
            print("[Bluetooth] Error: Device not connected")
            return False

        try:
            # Convert string data to bytes if needed
            if isinstance(data, str):
                data = data.encode("utf-8")

            # Send with length prefix
            length_bytes = len(data).to_bytes(2, "big")
            self.client_socket.sendall(length_bytes + data)
            return True

        except Exception as e:
            print(f"[Bluetooth] Error sending data: {e}")
            return False

    def handle_data(self, data: Any) -> None:
        """Handle incoming data from client."""
        if isinstance(data, str):
            data = data.encode("utf-8")

        # Check for control characters
        if data == BLE_CONTROL_TERMINATE:
            self.script_running = False
            print("[Bluetooth] Script terminated")
            return

        if data == BLE_CONTROL_RESTART:
            self.script_running = False
            if "main.lua" in self.virtual_fs:
                print("[Bluetooth] Restarting main.lua")
                # TODO: Implement main.lua execution
            return

        # Handle raw data
        if data.startswith(BLE_DATA_RAW):
            if self.receive_callback:
                self.receive_callback(data[1:])
            return

        # Handle Lua strings
        if not self.script_running:
            try:
                # Pass to Lua runtime through callback
                if self.receive_callback:
                    self.receive_callback(data)
            except Exception as e:
                print(f"[Bluetooth] Lua execution error: {e}")

    def set_receive_callback(self, callback: Optional[Callable]) -> None:
        """Set the callback for receiving data."""
        self.receive_callback = callback
