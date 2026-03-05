#!/bin/bash
# Build Verax for Windows with PyInstaller
# Usage: bash packaging/build_windows.sh

set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=========================================="
echo "Building Verax CV Assistant for Windows"
echo "=========================================="
echo ""

# Check prerequisites
if ! command -v python &> /dev/null; then
    echo "ERROR: Python not found. Please install Python 3.9+"
    exit 1
fi

if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "ERROR: PyInstaller not found. Install with: pip install PyInstaller"
    exit 1
fi

# Clean previous builds (but keep packaging/verax.spec)
echo "Cleaning previous builds..."
rm -rf build dist/windows
rm -f *.spec *.log 2>/dev/null || true

# Build
echo "Running PyInstaller..."
python -m PyInstaller packaging/verax.spec --distpath=dist/windows --clean --noconfirm

echo ""
echo "=========================================="
echo "Build complete!"
echo "=========================================="
echo ""
echo "Executable location:"
echo "  dist/windows/Verax/Verax.exe"
echo ""
echo "To run:"
echo "  ./dist/windows/Verax/Verax.exe"
echo ""
