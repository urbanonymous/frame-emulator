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
    FrameDataTypePrefixes,
    FRAME_DATA_PREFIX,
)


class BluetoothManager:
    """Manages Bluetooth functionality for the Frame Emulator."""

    def __init__(self, host="localhost", port=5555):
        """Initialize Bluetooth manager."""
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.state = BluetoothState.UNPAIRED
        self.virtual_fs: Dict[str, bytes] = {}
        self.receive_callback = None
        self.script_running = False
        
        # Buffer for accumulating chunked data
        self.data_buffer = bytearray()
        self.receiving_long_data = False
        self.expected_length = 0
        
        # Thread management
        self.running = True
        self.accept_thread = None
        self.receive_thread = None
        
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
        while self.running:
            try:
                # Set a timeout so we can check if we're still running
                self.server_socket.settimeout(1.0)
                try:
                    client_socket, addr = self.server_socket.accept()
                    print(f"[Bluetooth] Connection from {addr}")
                    
                    # Close any existing client connection
                    if self.client_socket:
                        try:
                            self.client_socket.close()
                        except:
                            pass
                    
                    self.client_socket = client_socket
                    self.state = BluetoothState.CONNECTED

                    # Start receiving data from this client
                    if self.receive_thread and self.receive_thread.is_alive():
                        # Wait for previous thread to finish
                        self.receive_thread.join(timeout=1.0)
                        
                    self.receive_thread = threading.Thread(target=self._receive_data)
                    self.receive_thread.daemon = True
                    self.receive_thread.start()
                except socket.timeout:
                    # This is expected, just continue the loop
                    continue
            except Exception as e:
                if self.running:  # Only log if we're supposed to be running
                    print(f"[Bluetooth] Connection error: {e}")
                time.sleep(1)

    def _receive_data(self):
        """Receive data from connected client."""
        while self.running and self.state == BluetoothState.CONNECTED:
            try:
                # Set a short timeout to check if we're still running
                self.client_socket.settimeout(0.5)
                try:
                    # Read 2-byte length prefix
                    length_bytes = self.client_socket.recv(2)
                    if not length_bytes or len(length_bytes) < 2:
                        print("[Bluetooth] Connection closed (incomplete header)")
                        break
                    
                    length = int.from_bytes(length_bytes, "big")
                    print(f"[Bluetooth] Expecting message of length: {length} bytes")
                    
                    if length > 0:
                        # Read the full data (may need multiple recv calls)
                        received_data = bytearray()
                        remaining = length
                        
                        while remaining > 0 and self.running:
                            try:
                                chunk = self.client_socket.recv(min(4096, remaining))
                                if not chunk:
                                    print("[Bluetooth] Connection closed during data transfer")
                                    break
                                
                                received_data.extend(chunk)
                                remaining -= len(chunk)
                            except socket.timeout:
                                # Check if we should continue
                                continue
                        
                        if len(received_data) == length:
                            print(f"[Bluetooth] Received complete message ({length} bytes)")
                            self._handle_received_data(bytes(received_data))
                        else:
                            print(f"[Bluetooth] Received incomplete message: {len(received_data)}/{length} bytes")
                except socket.timeout:
                    # This is expected, just continue the loop
                    continue
            except Exception as e:
                if self.running:  # Only log if we're supposed to be running
                    print(f"[Bluetooth] Receive error: {e}")
                break
        
        # Close the connection when the loop exits
        self.disconnect()

    def _handle_received_data(self, data: bytes):
        """Handle received data based on its prefix."""
        try:
            # More detailed logging for debugging
            first_bytes = ' '.join([f"{b:02x}" for b in data[:10]]) if data else ""
            print(f"[Bluetooth] Received data: {data[:20]}... (first bytes: {first_bytes})")
            
            # Special handling for Lua code
            # If it starts with newline or ASCII characters, treat as Lua code
            if len(data) > 0:
                first_byte = data[0]
                # Check if it's likely Lua code (starts with whitespace, ASCII characters, or common Lua constructs)
                is_lua_code = (
                    (first_byte in (0x0A, 0x0D, 0x09, 0x20))  # Whitespace: newline, CR, tab, space
                    or (first_byte >= 0x21 and first_byte <= 0x7E)  # Printable ASCII
                    or (len(data) > 2 and data[:2] == b'--')  # Lua comment
                    or (len(data) > 5 and data[:5] in (b'local', b'print', b'frame'))  # Common Lua keywords
                )
                
                if is_lua_code:
                    print(f"[Bluetooth] Identified as Lua code (length: {len(data)})")
                    if len(data) > 50:
                        print(f"[Bluetooth] Lua code preview: {data[:50].decode('utf-8', errors='replace')}...")
                    else:
                        print(f"[Bluetooth] Lua code: {data.decode('utf-8', errors='replace')}")
                    
                    try:
                        # Try to decode and execute the Lua code
                        lua_code = data.decode('utf-8')
                        print(f"[Bluetooth] Executing Lua code...")
                        
                        # Process using the receive callback if set
                        if self.receive_callback:
                            self.receive_callback(data)
                            print(f"[Bluetooth] Lua execution completed")
                        else:
                            print(f"[Bluetooth] No receive callback set!")
                    except Exception as e:
                        print(f"[Bluetooth] Error processing Lua code: {e}")
                        import traceback
                        traceback.print_exc()
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

                if prefix == FRAME_DATA_PREFIX:
                    if len(payload) > 0:
                        data_type = payload[0]
                        data_content = payload[1:]

                        if data_type == FrameDataTypePrefixes.LONG_DATA.value:
                            # Start or continue receiving chunked data
                            self.receiving_long_data = True
                            self.data_buffer.extend(data_content)
                            print(f"[Bluetooth] Received data chunk ({len(data_content)} bytes)")
                            self._send_response(
                                bytes(
                                    [
                                        FRAME_DATA_PREFIX,
                                        FrameDataTypePrefixes.LONG_DATA.value,
                                    ]
                                )
                                + b"OK"
                            )
                        elif data_type == FrameDataTypePrefixes.LONG_DATA_END.value:
                            # Final chunk of data
                            self.receiving_long_data = False
                            
                            # Extract count if present (before the actual data)
                            count_end = 0
                            for i, b in enumerate(data_content):
                                if b < ord('0') or b > ord('9'):
                                    count_end = i
                                    break
                            
                            if count_end > 0:
                                try:
                                    count = int(data_content[:count_end].decode())
                                    print(f"[Bluetooth] Final chunk of {count} total chunks")
                                except ValueError:
                                    print("[Bluetooth] Error parsing chunk count")
                            
                            # Add the final data to buffer
                            self.data_buffer.extend(data_content[count_end:])
                            
                            # Process the complete data
                            if self.receive_callback and self.data_buffer:
                                self.receive_callback(bytes(self.data_buffer))
                            
                            # Clear buffer for next time
                            self.data_buffer.clear()
                            
                            self._send_response(
                                bytes(
                                    [
                                        FRAME_DATA_PREFIX,
                                        FrameDataTypePrefixes.LONG_DATA_END.value,
                                    ]
                                )
                                + b"OK"
                            )

        except Exception as e:
            print(f"[Bluetooth] Error handling data: {e}")

    def _send_response(self, data: bytes):
        """Send a response with proper length prefix."""
        if self.state == BluetoothState.CONNECTED and self.client_socket:
            try:
                length_bytes = len(data).to_bytes(2, "big")
                self.client_socket.sendall(length_bytes + data)
            except Exception as e:
                print(f"[Bluetooth] Error sending response: {e}")

    def pair(self) -> bool:
        """Simulate pairing with the Frame device."""
        if self.state == BluetoothState.UNPAIRED:
            self.state = BluetoothState.PAIRED
            print("[Bluetooth] Device paired successfully")
            return True
        return False

    def connect(self) -> bool:
        """Wait for client connection."""
        return self.state == BluetoothState.CONNECTED

    def disconnect(self) -> bool:
        """Disconnect current client."""
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
            self.client_socket = None
        self.state = BluetoothState.UNPAIRED
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
            self.server_socket = None
        self.state = BluetoothState.UNPAIRED
        print("[Bluetooth] Device unpaired")
        return True
    
    def shutdown(self) -> None:
        """Completely shut down the Bluetooth manager and all threads."""
        # Signal threads to stop
        self.running = False
        
        # Disconnect client
        self.disconnect()
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None
        
        # Wait for threads to finish (with timeout)
        if self.accept_thread and self.accept_thread.is_alive():
            self.accept_thread.join(timeout=2.0)
            
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=2.0)
        
        print("[Bluetooth] Manager shutdown complete")

    def enable_notifications(self) -> bool:
        """Enable notifications for the RX characteristic."""
        if self.state == BluetoothState.CONNECTED:
            print("[Bluetooth] RX notifications enabled")
            return True
        return False

    def send(self, data: Any) -> bool:
        """Send data to connected client."""
        if self.state != BluetoothState.CONNECTED or not self.client_socket:
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
