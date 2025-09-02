# MKV Manager - Build & Packaging

This directory contains all files needed to build and package the MKV Manager application for distribution.

## Structure

```
packaging/
├── nsis/                   # NSIS installer configuration
│   └── installer.nsi       # NSIS installer script
├── pyinstaller/            # PyInstaller configuration
│   └── mkv_cleaner.spec    # PyInstaller specification
├── build_windows.bat       # Windows build script
├── build_windows.py        # Windows build script (Python)
├── build_linux.py          # Linux build script
└── README.md               # This file
```

## Prerequisites

### Required Software

- **Python 3.7+** with all project dependencies installed
- **PyInstaller** - `pip install pyinstaller`

### Windows Only
- **NSIS (Nullsoft Scriptable Install System)** - Download from https://nsis.sourceforge.io/
- Default installation path: `C:\Program Files (x86)\NSIS\`
- Make sure `makensis.exe` is accessible

### Linux Only
- **appimagetool** (automatically downloaded if not available)

## Building the Application

### Windows

```bash
packaging\build_windows.bat
```

This will create `MKV_Cleaner_Installer.exe` in the project root.

### Linux

```bash
python3 packaging/build_linux.py
```

This will create:
- `dist/mkv-manager-linux` - Standalone executable
- `dist/mkv-manager-linux.AppImage` - Portable AppImage

## Manual Build (Advanced Users)

### Windows

1. **Build executable:**
   ```bash
   pyinstaller packaging\pyinstaller\mkv_cleaner.spec
   ```

2. **Create installer:**
   ```bash
   "C:\Program Files (x86)\NSIS\makensis.exe" packaging\nsis\installer.nsi
   ```

### Linux

1. **Build executable:**
   ```bash
   pyinstaller --onefile desktop/main.py
   ```

2. **Create AppImage:**
   Use the build script for proper AppImage creation.

## Troubleshooting

### Windows Issues

1. **NSIS not found**
   - Verify NSIS installation path in `build_windows.bat`
   - Update path if NSIS is installed elsewhere

2. **PyInstaller import errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check virtual environment activation

### Linux Issues

1. **AppImage creation fails**
   - Script will automatically download appimagetool
   - Ensure executable permissions: `chmod +x script`

2. **Missing dependencies**
   - Install required packages: `pip install -r requirements.txt`

### Build Artifacts to Ignore

The following should be in `.gitignore`:

```gitignore
# Build outputs
dist/
build/
*.exe
*.msi
*.AppImage
*.AppDir/
```

## Distribution

### Windows
- Upload `MKV_Cleaner_Installer.exe` to releases
- Users run installer for system installation

### Linux
- Upload `mkv-manager-linux.AppImage` and `install.sh` to releases
- Users run `./install.sh` for system installation
- Or run AppImage directly for portable use
