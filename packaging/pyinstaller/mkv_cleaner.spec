# -*- mode: python ; coding: utf-8 -*-
# Enhanced PyInstaller spec for completely standalone MKV Cleaner

import sys
import os
from PyInstaller.utils.hooks import collect_all, collect_submodules

# Collect all data and hidden imports for standalone operation
tkinter_datas, tkinter_binaries, tkinter_hiddenimports = collect_all('tkinter')
flask_datas, flask_binaries, flask_hiddenimports = collect_all('flask')

# Get Python installation path for bundling system libraries
python_base = sys.base_prefix

a = Analysis(
    ['../../desktop/main.py'],
    pathex=['../..'],
    binaries=tkinter_binaries + flask_binaries,
    datas=[
        ('../../core', 'core'), 
        ('../../desktop', 'desktop'),
        ('../../web', 'web'),
        # Bundle complete Tcl/Tk installation for tkinter
        (os.path.join(python_base, 'tcl'), 'tcl'),
        (os.path.join(python_base, 'DLLs'), 'DLLs'),
    ] + tkinter_datas + flask_datas,
    hiddenimports=[
        # Core tkinter modules
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'tkinter.font',
        'tkinter.scrolledtext',
        '_tkinter',
        # Flask/web modules
        'flask',
        'werkzeug',
        'jinja2',
    ] + tkinter_hiddenimports + flask_hiddenimports + collect_submodules('core') + collect_submodules('desktop') + collect_submodules('web'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
    ],
    noarchive=False,
    optimize=2,  # Optimize bytecode
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MKV_Cleaner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress executable
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Add icon if available
    icon='../../assets/icon.ico' if os.path.exists('../../assets/icon.ico') else None,
)
