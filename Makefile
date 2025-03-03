.PHONY: setup clean deep-clean examples lint format isort check

# Setup virtual environment and install dependencies
setup:
	uv venv
	uv pip install -e .

# Run the hello world example
hello-world: setup
	@echo "Starting Frame emulator..."
	uv run python examples/run_emulator.py &
	@sleep 2  # Give emulator time to start
	@echo "Running hello world client..."
	uv run python examples/hello_world_client.py

# Clean up build artifacts and cache files
clean:
	@echo "Cleaning up build artifacts and cache files..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".DS_Store" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	@echo "Clean complete!"

# Deep clean (including virtual environment)
deep-clean: clean
	@echo "Removing virtual environment..."
	rm -rf .venv
	@echo "Deep clean complete!"

# Sort imports
isort: setup
	@echo "Installing isort..."
	uv pip install isort
	@echo "Sorting imports..."
	uv run isort src/ examples/
	@echo "Import sorting complete!"

# Format code (sort imports first, then black)
format: isort
	@echo "Installing black..."
	uv pip install black
	@echo "Formatting code..."
	uv run black src/ examples/
	@echo "Code formatting complete!"

# Run static type checking
check: setup
	@echo "Installing type checking tools..."
	uv pip install mypy
	@echo "Running type checks..."
	uv run mypy src/ examples/
	@echo "Type checking complete!"

# Install dev dependencies and run linting (clean + format + check)
lint: clean format check
	@echo "Linting complete! All code is clean and formatted."

# Help message
help:
	@echo "Available commands:"
	@echo "  make setup        - Create virtual environment and install dependencies"
	@echo "  make hello-world  - Run the hello world example"
	@echo "  make clean        - Clean up build artifacts and cache files"
	@echo "  make deep-clean   - Clean everything including virtual environment"
	@echo "  make isort        - Sort Python imports"
	@echo "  make format       - Format code with isort and black"
	@echo "  make check        - Run type checking with mypy"
	@echo "  make lint         - Clean, format, and check code quality" 