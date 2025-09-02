#!/usr/bin/env python3
"""
MKV Manager Build Script - Installer-Only Distribution
Creates a Windows installer while ensuring license compliance through mandatory installation process.
"""

import os
import sys
import subprocess
import platform
import tempfile
import shutil
from pathlib import Path


def run_command(cmd, shell=False):
    """Run a command and handle errors"""
    try:
        result = subprocess.run(cmd, shell=shell, check=True,
                                capture_output=True, text=True)
        print(f"✅ {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"   Command FAILED: {e}")
        print(f"   Output: {e.stdout}")
        print(f"   ERROR: {e.stderr}")
        sys.exit(1)


def ensure_windows_icon(project_root: Path):
    """Ensure a Windows .ico exists in `assets/` by converting icon.png if necessary.

    Returns the Path to the .ico file or None if not available.
    """
    assets_dir = project_root / "assets"
    png = assets_dir / "icon.png"
    ico = assets_dir / "icon.ico"

    if ico.exists():
        return ico

    if not png.exists():
        print("⚠️  No icon.png found in assets; continuing without custom icon.")
        return None

    try:
        # Try to import Pillow; install automatically if missing
        try:
            from PIL import Image
        except Exception:
            print("Pillow not found; attempting to install Pillow via pip...")
            run_command([sys.executable, "-m", "pip", "install", "Pillow"])
            from PIL import Image

        img = Image.open(png)
        # Save multiple sizes into a single ICO file for best compatibility
        sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
        img.save(ico, format="ICO", sizes=sizes)
        print(f"✅ Created Windows icon: {ico}")
        return ico

    except Exception as e:
        print(f"⚠️  Failed to create .ico from {png}: {e}")
        return None


def build_executable():
    """Build executable for installer packaging"""
    print("Building executable (installer packaging mode)...")

    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Ensure a Windows .ico exists so the PyInstaller spec can include it
    ico_path = ensure_windows_icon(project_root)
    if ico_path:
        print(f"Using icon: {ico_path}")

    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temporary build directory: {temp_dir}")

        spec_path = "packaging/pyinstaller/mkv_cleaner.spec"

        temp_spec = Path(temp_dir) / "mkv_cleaner_temp.spec"
        with open(spec_path, 'r') as f:
            spec_content = f.read()

        modified_content = spec_content.replace(
            "name='MKV_Cleaner'",
            f"name='MKV_Cleaner',\n    distpath='{temp_dir}/dist'"
        )

        # If we created an icon.ico in assets, patch the spec so the icon path
        # is an absolute path. This avoids relative-path issues when the spec
        # is executed from a temporary directory.
        if ico_path and ico_path.exists():
            abs_ico = ico_path.resolve().as_posix()
            # Replace the conditional expression in the spec with an absolute path
            modified_content = modified_content.replace(
                "icon='../../assets/icon.ico' if os.path.exists('../../assets/icon.ico') else None,",
                f"icon=r'{abs_ico}',"
            )

        with open(temp_spec, 'w') as f:
            f.write(modified_content)

        run_command([sys.executable, "-m", "PyInstaller", str(temp_spec)])

        temp_exe = Path(temp_dir) / "dist" / "MKV_Cleaner.exe"
        final_exe = project_root / "dist" / "MKV_Cleaner.exe"

        final_exe.parent.mkdir(exist_ok=True)

        shutil.copy2(temp_exe, final_exe)
        print(f"Executable ready for installer packaging")


def build_installer_windows():
    """Build Windows installer using NSIS"""
    print("Building Windows installer with NSIS...")

    nsis_paths = [
        r"C:\Program Files (x86)\NSIS\makensis.exe",
        r"C:\Program Files\NSIS\makensis.exe",
        r"makensis.exe"
    ]

    nsis_exe = None
    for path in nsis_paths:
        if os.path.exists(path) or path == "makensis.exe":
            nsis_exe = path
            break

    if not nsis_exe:
        print("❌ NSIS not found. Please install NSIS from https://nsis.sourceforge.io/")
        sys.exit(1)

    nsi_script = "packaging/nsis/installer.nsi"
    
    # Check if custom icon exists and pass it to NSIS
    project_root = Path(__file__).parent.parent
    ico_path = project_root / "assets" / "icon.ico"
    
    cmd = [nsis_exe]
    if ico_path.exists():
        cmd.extend([f"/DCUSTOM_ICON={ico_path.resolve()}"])
        print(f"Using custom icon for installer: {ico_path}")
    
    cmd.append(nsi_script)
    run_command(cmd)


def cleanup_build_artifacts():
    """Remove build artifacts"""
    print("Cleaning up build artifacts...")

    project_root = Path(__file__).parent.parent

    dist_dir = project_root / "dist"
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
        print("✅ Removed dist/ directory")

    build_dir = project_root / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print("✅ Removed build/ directory")


def main():
    """Main build function to create installer"""
    print("MKV Manager Build Script")
    print("=" * 40)
    print("Building installer distribution")
    print()

    system = platform.system()
    print(f"Detected platform: {system}")

    if system != "Windows":
        print("❌ This build script currently supports Windows only")
        print("  For other platforms, use PyInstaller directly")
        sys.exit(1)

    try:
        build_executable()
        build_installer_windows()
        cleanup_build_artifacts()

        print("✅ Windows installer created: MKV_Cleaner_Installer.exe")

    except Exception as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
