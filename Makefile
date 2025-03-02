.PHONY: setup clean run test lint python-api direct-api demo-all frame-sdk-demo text-message-app text-file-reader

# Default virtual environment path
VENV_DIR := .venv
PYTHON := $(VENV_DIR)/bin/python
UV := uv

# Setup virtual environment and install dependencies
setup:
	$(UV) venv
	$(UV) pip install -e .
	chmod +x examples/run_lua_example.py
	chmod +x examples/direct_api_example.py
	chmod +x examples/demo_all.py
	chmod +x examples/run_text_message_app.py

# Run the emulator with the demo app using Python API
run:
	$(PYTHON) examples/run_lua_example.py examples/app.lua

# Run with pixel art example using Python API
pixel-art:
	$(PYTHON) examples/run_lua_example.py examples/pixel_art.lua

# Run the Frame SDK demo example
frame-sdk-demo:
	$(PYTHON) examples/run_lua_example.py examples/frame_sdk_demo.lua

# Run the text message app example
text-message-app:
	$(PYTHON) examples/run_text_message_app.py

# Run the pure Python API example (no Lua)
direct-api:
	$(PYTHON) examples/direct_api_example.py

# Run all demos sequentially (10 seconds each)
demo-all:
	$(PYTHON) examples/demo_all.py

# Run the text file reader app
text-file-reader: setup
	@echo "Running Text File Reader App..."
	./examples/run_text_file_reader.py

# Clean up build artifacts and virtual environment
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf $(VENV_DIR)/
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	rm -rf src/frame_emulator/__pycache__/

# Install dev dependencies and run linting
lint:
	$(UV) pip install black isort mypy
	black src/
	isort src/
	mypy src/

# Help message
help:
	@echo "Available commands:"
	@echo "  make setup          - Create virtual environment and install dependencies"
	@echo "  make run            - Run the emulator with the demo app using Python API"
	@echo "  make pixel-art      - Run the emulator with the pixel art example using Python API"
	@echo "  make frame-sdk-demo - Run the emulator with the Frame SDK display API demo"
	@echo "  make text-message-app - Run the text message app with Bluetooth simulation"
	@echo "  make direct-api     - Run the pure Python API example (no Lua)"
	@echo "  make demo-all       - Run all demos sequentially (10 seconds each)"
	@echo "  make text-file-reader - Run the text file reader app example"
	@echo "  make clean          - Clean up build artifacts and virtual environment"
	@echo "  make lint           - Run code quality checks" 