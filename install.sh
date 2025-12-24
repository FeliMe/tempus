#!/bin/bash
# Tempus Installation Script
# Double-click to run or execute: ./install.sh

cd "$(dirname "$0")"

echo "=== Installing Tempus ==="
echo ""

# Run setup (installs mise, uv, Qt6 dev libraries)
echo "Running setup..."
make setup

echo ""
echo "=== Installation Complete ==="
read -p "Press Enter to close..."
