#!/usr/bin/env python3

from frame_emulator.emulator import EmulatorConfig, FrameEmulator


def main():
    # Create default config (640x400)
    config = EmulatorConfig()

    # Create and start emulator
    emulator = FrameEmulator(config)

    # Run the emulator (this will block until closed)
    emulator.run(None)  # No script path since we'll send commands over BT


if __name__ == "__main__":
    main()
