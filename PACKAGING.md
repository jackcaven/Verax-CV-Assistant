# Verax CV Assistant — Packaging & Distribution Guide

This document provides step-by-step instructions for building and distributing Verax across Windows, macOS, and Linux platforms.

## Overview

Verax uses **PyInstaller** to bundle the Python application with all dependencies into self-contained executables. Users can run Verax without installing Python.

## Prerequisites

All platforms require:
- Python 3.9 or higher
- PyInstaller 6.0+
- All project dependencies installed

```bash
# Install dependencies
pip install -e ".[dev]"

# Verify PyInstaller
python -m PyInstaller --version
```

## Building

### Windows Build

```bash
bash packaging/build_windows.sh
```

**Output:**
- Single executable: `dist/windows/Verax.exe` (~78 MB)
- Folder bundle: `dist/windows/Verax/` (with DLLs if needed)

**Requirements:**
- No additional dependencies beyond PyInstaller

**Test run:**
```bash
./dist/windows/Verax.exe
```

### macOS Build

```bash
bash packaging/build_macos.sh
```

**Output:**
- Application bundle: `dist/macos/Verax/Verax.app`
- Can be launched via Finder or:
  ```bash
  open dist/macos/Verax/Verax.app
  ```

**Requirements:**
- macOS 10.13+
- Code signing (optional, required for distribution):
  ```bash
  codesign -s - dist/macos/Verax/Verax.app
  ```

### Linux Build

```bash
bash packaging/build_linux.sh
```

**Output:**
- Executable: `dist/linux/Verax/Verax`

**Test run:**
```bash
./dist/linux/Verax/Verax
```

## Distribution Methods

### 1. Self-Contained Executables (MVP)

Simply distribute the compiled executable or folder. Users unzip and run.

**Pros:**
- No installation needed
- Works anywhere with correct OS + architecture
- Minimal user friction

**Cons:**
- Large file size (~78 MB for Windows)
- Not registered with system (no Start Menu entry on Windows)
- Updates require replacing entire file

**Distribution:**
```bash
# Windows: Zip the Verax.exe or dist/windows/Verax folder
# macOS: Zip the Verax.app bundle
# Linux: Zip or tar.gz the dist/linux/Verax folder
```

### 2. Native Installers (Recommended for Production)

#### Windows: NSIS Installer (Optional)

Install NSIS and create a professional installer:

```bash
# 1. Install NSIS (Nullsoft Scriptable Install System)
#    Download from https://nsis.sourceforge.io/

# 2. Create packaging/verax.nsi
# 3. Build installer:
makensis packaging/verax.nsi
```

**Result:** `Verax-Setup.exe` (installer, users click to install)

#### macOS: DMG Image (Optional)

Create a distributable .dmg (Disk Image):

```bash
# Install dmg-builder
pip install dmg-builder

# Create DMG
dmg-builder dist/macos/Verax/Verax.app Verax-installer.dmg
```

**Result:** `Verax-installer.dmg` (double-click to mount, drag to Applications)

#### Linux: .deb Package (Optional)

Create a Debian package for Ubuntu/Debian:

```bash
# Install tools
pip install py2deb

# Create .deb
py2deb --name verax --version 0.1.0 dist/linux/Verax/

# Result: verax_0.1.0_amd64.deb
# Users: sudo apt install ./verax_0.1.0_amd64.deb
```

Alternatively, create an AppImage:

```bash
# Download appimagetool from https://github.com/AppImage/AppImageKit/releases
# Package the executable
./appimagetool dist/linux/Verax/ Verax-0.1.0.AppImage

# Result: Verax-0.1.0.AppImage (portable, works on any Linux)
```

## Build Customization

### Icons

To add a custom icon to the Windows .exe or macOS app:

1. **Prepare icon:**
   - Windows: `.ico` file (256×256 px)
   - macOS: `.icns` file (1024×1024 px)

2. **Update spec file:**
   ```python
   # packaging/verax.spec
   exe = EXE(
       pyz,
       ...,
       icon='path/to/icon.ico',  # Windows
   )
   ```

3. **Rebuild:**
   ```bash
   bash packaging/build_windows.sh
   ```

### Code Signing (macOS/Windows)

#### macOS

```bash
codesign -s - dist/macos/Verax/Verax.app  # Ad-hoc signing
codesign -s "Developer ID" dist/macos/Verax/Verax.app  # Production
```

#### Windows

Requires code signing certificate. Use signtool.exe:

```bash
signtool sign /f mycert.pfx /p password /t http://timestamp.server dist/windows/Verax.exe
```

## Size Optimization

**Windows executable is ~78 MB.** To reduce:

1. **UPX compression** (enabled by default in spec):
   ```bash
   pip install upx
   # PyInstaller will compress automatically
   ```

2. **Exclude unused modules** (edit spec file):
   ```python
   excludedimports=[
       'matplotlib', 'numpy', 'pandas', 'scipy',
       'torch', 'tensorflow',  # Add heavy libraries not used
   ]
   ```

3. **Strip binaries** (Linux):
   ```python
   COLLECT(..., strip=True, ...)
   ```

## Testing Builds

### Quick Test

```bash
# Windows
./dist/windows/Verax.exe

# macOS
open dist/macos/Verax/Verax.app

# Linux
./dist/linux/Verax/Verax
```

### Full Integration Test

```bash
pytest tests/integration/
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build & Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - run: pip install -e ".[dev]"
      - run: |
          case "${{ matrix.os }}" in
            ubuntu-latest) bash packaging/build_linux.sh ;;
            macos-latest) bash packaging/build_macos.sh ;;
            windows-latest) bash packaging/build_windows.sh ;;
          esac

      - uses: actions/upload-artifact@v3
        with:
          name: ${{ matrix.os }}-build
          path: dist/
```

## Troubleshooting

### "module not found" errors

**Problem:** Built executable fails with `ModuleNotFoundError`

**Solution:** Add to `hiddenimports` in spec file:
```python
hiddenimports=['customtkinter', 'pdfplumber', ...]
```

Then rebuild:
```bash
python -m PyInstaller packaging/verax.spec --clean --noconfirm
```

### LibreOffice not found (PDF export)

**Problem:** PDF export not available in built app

**Solution:** Check for LibreOffice:
```bash
# Windows
where soffice
# or
ls "C:\Program Files\LibreOffice\program\soffice.exe"

# macOS
ls /Applications/LibreOffice.app/Contents/MacOS/soffice

# Linux
which soffice
```

If missing, install LibreOffice. It will be detected at runtime.

### Security warnings on Windows

**Problem:** Windows SmartScreen warns "unknown publisher"

**Solution:**
1. Code sign the executable (requires certificate)
2. Or tell users to click "Run anyway"
3. Distribute via Microsoft Store (enterprise only)

### File not found on startup

**Problem:** Bundled files (fonts, templates) not found

**Solution:** Check `datas` in spec file:
```python
datas=[
    ('../src/verax/template/fallback.docx', 'verax/template'),
]
```

Rebuild and verify bundle includes files:
```bash
# Windows
ls dist/windows/Verax/
# macOS
ls dist/macos/Verax/Verax.app/Contents/MacOS/verax/
# Linux
ls dist/linux/Verax/verax/
```

## Release Checklist

Before distributing a new version:

- [ ] Update version in `pyproject.toml`
- [ ] Update CHANGELOG.md
- [ ] Run full test suite: `pytest`
- [ ] Build all platforms: `bash packaging/build_*.sh`
- [ ] Test each executable on native OS
- [ ] Verify PDF export works (if LibreOffice available)
- [ ] Sign/notarize builds (production only)
- [ ] Create release notes
- [ ] Upload to GitHub Releases or distribution site
- [ ] Update download links in README

## References

- **PyInstaller Docs:** https://pyinstaller.org/
- **PyInstaller Hooks:** https://github.com/pyinstaller/pyinstaller-hooks-contrib
- **NSIS (Windows Installer):** https://nsis.sourceforge.io/
- **DMG Creator (macOS):** https://github.com/dmgbuild/dmgbuild
- **AppImage (Linux):** https://appimage.org/

---

**Last Updated:** 2026-03-05
**Status:** Phase 12 Complete — Ready for Distribution
