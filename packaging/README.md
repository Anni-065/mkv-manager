# MKV Manager - Build & Packaging

This directory contains all files needed to build and package the MKV Manager application for distribution.

## Structure

```
packaging/
├── nsis/                   # NSIS installer configuration
│   └── installer.nsi       # NSIS installer script
├── pyinstaller/            # PyInstaller configuration
│   └── mkv_cleaner.spec    # PyInstaller specification
├── build.bat               # Windows build script
├── build.py                # Cross-platform build script
└── README.md               # This file
```

## Prerequisites

### Required Software

- **Python 3.7+** with all project dependencies installed
- **PyInstaller** - `pip install pyinstaller`
- **NSIS (Nullsoft Scriptable Install System)** - Download from https://nsis.sourceforge.io/

### NSIS Installation

- Download and install NSIS from the official website
- Default installation path: `C:\Program Files (x86)\NSIS\`
- Make sure `makensis.exe` is accessible

## Building the Application

### Windows

```bash
packaging\build.bat
```

### Cross-Platform (not tested)

```bash
python packaging\build.py
```

This will:

- Create the installer using PyInstaller and NSIS
- Output `MKV_Cleaner_Installer.exe` in the project root

## Manual Build (Advanced Users)

If you need to build manually:

1. **Build executable:**

   ```bash
   # From project root
   pyinstaller packaging\pyinstaller\mkv_cleaner.spec
   ```

2. **Create installer:**

   ```bash
   "C:\Program Files (x86)\NSIS\makensis.exe" packaging\nsis\installer.nsi
   ```

3. **Clean up (recommended):**
   ```bash
   rmdir /s /q build
   rmdir /s /q dist
   ```

The installer will be saved in the project root.

## Troubleshooting

### Common Issues

1. **NSIS not found**

   - Verify NSIS installation path in `build.bat`
   - Update path if NSIS is installed elsewhere

2. **PyInstaller import errors**

   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check virtual environment activation

3. **Missing files in build**
   - Review `mkv_cleaner.spec` for missing data files
   - Add missing dependencies to the spec file

### Build Artifacts to Ignore

The following should be in `.gitignore`:

```gitignore
# Build outputs
dist/
build/
*.exe
*.msi
```

## GitHub Release Workflow

1. **Create release tag**: `git tag v1.0.0`
2. **Build installer**: Run `packaging\build.bat`
3. **Upload to GitHub Releases**: Upload `MKV_Cleaner_Installer.exe`
4. **Clean repository**: Remove build artifacts from repo
