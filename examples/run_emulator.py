#!/usr/bin/env python3

from frame_emulator.emulator import FrameEmulator
from frame_emulator.config import EmulatorConfig


def main():
    # Create emulator config with default settings (640x400)
    config = EmulatorConfig(
        width=640, height=400, title="Frame Emulator - Hello World Example"
    )

    # Create and start emulator
    print("Starting Frame emulator...")
    print("Waiting for connection on localhost:5555")

    # Create emulator instance
    emulator = FrameEmulator(config)

    try:
        # Run emulator directly (this blocks until closed)
        emulator.run(None)  # No script path since we'll send commands over TCP
    except KeyboardInterrupt:
        print("\nShutting down emulator...")


if __name__ == "__main__":
    main()
