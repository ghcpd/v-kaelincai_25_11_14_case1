#!/bin/bash
# Setup script for Project B - Enhanced Player

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Setting up Project B - Enhanced Player in: $PROJECT_DIR"

# Create virtual environment
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$PROJECT_DIR/venv"
fi

# Activate virtual environment
source "$PROJECT_DIR/venv/bin/activate"

# Install dependencies
echo "Installing dependencies..."
pip install -r "$PROJECT_DIR/requirements.txt"

# Install playwright browsers
echo "Installing Playwright browsers..."
playwright install

echo "Setup complete for Project B!"
echo "To activate the environment, run: source $PROJECT_DIR/venv/bin/activate"
