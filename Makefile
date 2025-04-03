# Python project Makefile
.PHONY: run test install lint clean develop version-check

PYTHON_MIN_VERSION = 3.10
PYTHON_VERSION := $(shell python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

# Version check target
version-check:
	@echo "Checking Python version..."
	@python -c "import sys; min_ver='$(PYTHON_MIN_VERSION)'; cur_ver=f'{sys.version_info.major}.{sys.version_info.minor}'; exit(0 if float(cur_ver) >= float(min_ver) else print(f'Error: Python {min_ver}+ required, but {cur_ver} found') or 1)"

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

check:
	clear
	make tc
	make test

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

# Info about Python version
python-info:
	@echo "Required Python version: $(PYTHON_MIN_VERSION)+"
	@echo "Current Python version: $(PYTHON_VERSION)"
	@python --version

# Help command
help:
	@echo "Available commands:"
	@echo "  make              Run the application (with version check)"
	@echo "  make dev          Run with auto-restart on file changes"
	@echo "  make test         Run tests"
	@echo "  make tc           Run type checking"
	@echo "  make check        Run type checking and tests"
	@echo "  make install      Install dependencies"
	@echo "  make lint         Lint and format code"
	@echo "  make clean        Clean up temporary files"
	@echo "  make venv         Create a virtual environment"
	@echo "  make python-info  Show Python version information" 