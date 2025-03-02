#!/usr/bin/env python3
"""
Example script showing how to use the Frame Emulator Python API to run a Lua script.

This example demonstrates how to:
1. Import the Frame Emulator library
2. Configure the emulator
3. Run a Lua script
"""

import os
import sys
import argparse
from frame_emulator.emulator import FrameEmulator, EmulatorConfig, run_lua_script

def main():
    """Run a Lua script with the Frame Emulator."""
    parser = argparse.ArgumentParser(description="Run a Lua script with Frame Emulator")
    parser.add_argument(
        "script",
        help="Path to Lua script to run"
    )
    parser.add_argument(
        "--width",
        type=int,
        default=640,
        help="Display width in pixels (default: 640)"
    )
    parser.add_argument(
        "--height",
        type=int,
        default=400,
        help="Display height in pixels (default: 400)"
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=1.5,
        help="Initial scale factor (default: 1.5)"
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=60,
        help="Target frames per second (default: 60)"
    )

    args = parser.parse_args()

    # Ensure the script exists
    if not os.path.exists(args.script):
        print(f"Error: Script '{args.script}' not found.")
        return 1

    # Create config from command line arguments
    config = EmulatorConfig(
        width=args.width,
        height=args.height,
        scale=args.scale,
        fps=args.fps
    )

    # Create the emulator
    emulator = FrameEmulator(config)
    
    print(f"Starting Frame Glasses Emulator...")
    print(f"Running script: {args.script}")
    print(f"Display: {config.width}x{config.height} at {config.scale}x scale")
    print("Press Ctrl+C to exit or close the window.")

    try:
        # Start the Lua script
        run_lua_script(args.script, emulator)
        
        # Main loop - keep rendering frames in the main thread
        while emulator.running:
            emulator.render_frame()
            
    except KeyboardInterrupt:
        print("Emulator stopped by user")
    finally:
        emulator.stop()

if __name__ == "__main__":
    sys.exit(main()) 