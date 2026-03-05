#!/bin/bash
# Build Verax for macOS

set -e

cd "$(dirname "$0")/.."

echo "Building Verax for macOS..."
python -m PyInstaller packaging/verax.spec --distpath=dist/macos

echo "Build complete. Application: dist/macos/Verax.app"
