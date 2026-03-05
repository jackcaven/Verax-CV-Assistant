#!/bin/bash
# Build Verax for macOS with PyInstaller
# Usage: bash packaging/build_macos.sh

set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=========================================="
echo "Building Verax CV Assistant for macOS"
echo "=========================================="
echo ""

# Check prerequisites
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.9+ (e.g., via Homebrew)"
    exit 1
fi

if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "ERROR: PyInstaller not found. Install with: pip install PyInstaller"
    exit 1
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist/macos *.spec *.log

# Build
echo "Running PyInstaller..."
python3 -m PyInstaller packaging/verax.spec --distpath=dist/macos --clean --noconfirm

echo ""
echo "=========================================="
echo "Build complete!"
echo "=========================================="
echo ""
echo "Application location:"
echo "  dist/macos/Verax/Verax.app"
echo ""
echo "To run:"
echo "  open dist/macos/Verax/Verax.app"
echo ""
echo "Optional: Create a .dmg installer"
echo "  pip install dmg-builder"
echo "  dmg-builder dist/macos/Verax/Verax.app Verax-installer.dmg"
echo ""
