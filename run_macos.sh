#!/bin/bash

# macOS-specific startup script for Image Lab
echo "Starting Image Lab on macOS..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Please install pip3 first."
    exit 1
fi

# Install/upgrade required packages
echo "Installing required packages..."
pip3 install --upgrade -r requirements.txt

# Check if theme file exists
if [ ! -f "assets/theme.json" ]; then
    echo "Warning: theme.json not found. App will use default theme."
fi

# Run the application
echo "Launching Image Lab..."
python3 main.py
