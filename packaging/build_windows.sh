#!/bin/bash
# Build Verax for Windows

set -e

cd "$(dirname "$0")/.."

echo "Building Verax for Windows..."
python -m PyInstaller packaging/verax.spec --distpath=dist/windows

echo "Build complete. Executable: dist/windows/Verax/Verax.exe"
