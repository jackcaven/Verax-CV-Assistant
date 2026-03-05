#!/bin/bash
# Build Verax for Linux

set -e

cd "$(dirname "$0")/.."

echo "Building Verax for Linux..."
python -m PyInstaller packaging/verax.spec --distpath=dist/linux

echo "Build complete. Executable: dist/linux/Verax/Verax"
