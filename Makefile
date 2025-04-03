# Python project Makefile
.PHONY: run test install lint clean develop

# Default target executed when no arguments are given to make
default: start

# Run the application
start:
	python main.py

dev:
	watchmedo auto-restart --patterns="*.py" --ignore-patterns="*.pyc,__pycache__/*" --recursive  --debounce-interval=1.0 -- python ./main.py

# Run tests
test:
	pytest

# Run type checking
tc:
	mypy .

# Install dependencies
install:
	pip install -r requirements.txt

# Lint and format code
lint:
	flake8 .
	black .

# Clean up temporary files
clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf *.egg-info
	rm -rf build/
	rm -rf dist/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Create a virtualenv
venv:
	python -m venv venv
	@echo "Run 'source venv/bin/activate' to activate the virtual environment"

# Help command
help:
	@echo "Available commands:"
	@echo "  make              Run the application"
	@echo "  make run          Run the application" 
	@echo "  make test         Run tests"
	@echo "  make install      Install dependencies"
	@echo "  make install-dev  Install development dependencies"
	@echo "  make lint         Lint and format code"
	@echo "  make clean        Clean up temporary files"
	@echo "  make venv         Create a virtual environment" 