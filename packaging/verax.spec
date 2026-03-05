# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller specification for Verax CV Assistant.

Build with:
  python -m PyInstaller packaging/verax.spec --distpath=dist/[windows|macos|linux]
"""

import os
import sys

block_cipher = None

# Determine root directory: spec is in packaging/, so go up one level
# PyInstaller is invoked from project root, so cwd is the root
root_dir = os.getcwd()
if not os.path.exists(os.path.join(root_dir, 'src', 'verax', 'main.py')):
    # If invoked from packaging/ directory, go up one level
    root_dir = os.path.dirname(root_dir)

main_py = os.path.join(root_dir, 'src', 'verax', 'main.py')

if not os.path.exists(main_py):
    raise FileNotFoundError(f"Cannot find main.py at {main_py}. Ensure PyInstaller is invoked from project root.")

a = Analysis(
    [main_py],
    pathex=[],
    binaries=[],
    datas=[
        # No external data files needed — templates are base64-encoded in fallback.py
    ],
    hiddenimports=[
        'customtkinter',
        'anthropic',
        'openai',
        'pdfplumber',
        'docx',
        'mammoth',
        'keyring',
        'platformdirs',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludedimports=['matplotlib', 'numpy', 'pandas', 'scipy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Verax',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Verax',
)
