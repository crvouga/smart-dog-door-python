# Python project Makefile
.PHONY: run test install lint clean develop

PYTHON_MIN_VERSION = 3.10
PYTHON_VERSION := $(shell python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")


# Default target executed when no arguments are given to make
default: start

# Run the application
start:
	clear
	python main.py

dev:
	watchmedo auto-restart --patterns="*.py" --ignore-patterns="*.pyc,__pycache__/*" --recursive  --debounce-interval=1.0 -- python ./main.py

# Run tests
test:
	clear
	pytest

# Run type checking
tc:
	clear
	mypy .

check:
	clear
	mypy .
	pytest

# Install dependencies
install:
	pip install -r requirements.txt

# Lint and format code
lint:
	flake8 .
	black .



# Start Docker Compose services
infra-up:
	docker-compose -f infra/docker-compose.yml up -d

# Stop Docker Compose services
infra-down:
	docker-compose -f infra/docker-compose.yml down

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