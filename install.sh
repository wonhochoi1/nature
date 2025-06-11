#!/bin/bash

# Get the absolute path of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Make the nature script executable
chmod +x "$SCRIPT_DIR/nature"

# Create a symlink in /usr/local/bin (requires sudo)
echo "Creating symlink in /usr/local/bin..."
sudo ln -sf "$SCRIPT_DIR/nature" /usr/local/bin/nature

# Check if the symlink was created successfully
if [ $? -eq 0 ]; then
    echo "Installation successful! You can now use 'nature' command from anywhere."
    echo "Example: nature examples/demo.nature"
else
    echo "Installation failed. You might need to run this script with sudo."
    exit 1
fi 