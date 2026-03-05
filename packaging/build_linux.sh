#!/bin/bash
# Build Verax for Linux with PyInstaller
# Usage: bash packaging/build_linux.sh

set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=========================================="
echo "Building Verax CV Assistant for Linux"
echo "=========================================="
echo ""

# Check prerequisites
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Install with: sudo apt install python3 python3-pip"
    exit 1
fi

if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "ERROR: PyInstaller not found. Install with: pip install PyInstaller"
    exit 1
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist/linux *.spec *.log

# Build
echo "Running PyInstaller..."
python3 -m PyInstaller packaging/verax.spec --distpath=dist/linux --clean --noconfirm

echo ""
echo "=========================================="
echo "Build complete!"
echo "=========================================="
echo ""
echo "Executable location:"
echo "  dist/linux/Verax/Verax"
echo ""
echo "To run:"
echo "  ./dist/linux/Verax/Verax"
echo ""
echo "Optional: Create a .AppImage or .deb package"
echo "  For AppImage: pip install linuxdeploy"
echo "  For .deb: pip install py2deb"
echo ""
