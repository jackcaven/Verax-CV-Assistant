# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller specification for Verax CV Assistant.

Build with:
  python -m PyInstaller packaging/verax.spec --distpath=dist/[windows|macos|linux]
"""

block_cipher = None

a = Analysis(
    ['../src/verax/main.py'],
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
        'python-docx',
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
