#!/usr/bin/env python3
"""
MKV Manager Build Script for Linux/macOS
Creates a standalone executable using PyInstaller
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
import tempfile
import urllib.request
import stat
import importlib.util


def run_command(cmd, shell=False):
    """Run a command and handle errors"""
    try:
        result = subprocess.run(cmd, shell=shell, check=True,
                                capture_output=True, text=True)
        print(f"✅ {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command FAILED: {e}")
        print(f"   Output: {e.stdout}")
        print(f"   Error: {e.stderr}")
        sys.exit(1)


def setup_build_environment():
    """Set up a virtual environment for building if needed"""
    project_root = Path(__file__).parent.parent
    venv_path = project_root / ".build_venv"
    
    # Check if we're already in a virtual environment or if PyInstaller is available
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Already in virtual environment")
        return sys.executable
    
    # Check if PyInstaller is available in current environment
    if importlib.util.find_spec("PyInstaller") is not None:
        print("✅ PyInstaller available in current environment")
        return sys.executable
    
    # Check if we need to create/use virtual environment
    venv_python = venv_path / "bin" / "python"
    if not venv_python.exists():
        print("Creating build virtual environment...")
        
        # Check if python3-venv is available
        try:
            subprocess.run([sys.executable, "-m", "venv", "--help"], 
                          capture_output=True, check=True)
        except subprocess.CalledProcessError:
            print("❌ python3-venv not available. Please install it:")
            print("   sudo apt install python3-venv")
            sys.exit(1)
        
        # Create virtual environment
        run_command([sys.executable, "-m", "venv", str(venv_path)])
        print(f"✅ Virtual environment created at {venv_path}")
    else:
        print(f"✅ Using existing virtual environment at {venv_path}")
    
    return str(venv_python)


def check_dependencies(python_executable):
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    # Install required packages for the build
    required_packages = ["pyinstaller", "pillow"]
    
    for package in required_packages:
        try:
            # Check if package is installed
            result = subprocess.run([python_executable, "-c", f"import {package.replace('pillow', 'PIL')}"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {package.title()} is installed")
            else:
                raise ImportError()
        except (subprocess.CalledProcessError, ImportError):
            print(f"❌ {package.title()} not found. Installing...")
            try:
                run_command([python_executable, "-m", "pip", "install", package])
            except SystemExit:
                print(f"⚠️  Standard pip install failed for {package}. Trying with --user flag...")
                try:
                    run_command([python_executable, "-m", "pip", "install", "--user", package])
                except SystemExit:
                    print(f"❌ Failed to install {package}. Please install manually:")
                    print(f"   {python_executable} -m pip install {package}")
                    sys.exit(1)
    
    # Check if MKVToolNix is available
    try:
        result = subprocess.run(["mkvmerge", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ MKVToolNix (mkvmerge) is available")
        else:
            print("⚠️  MKVToolNix not found in PATH. The built application will need it installed.")
    except FileNotFoundError:
        print("⚠️  MKVToolNix not found in PATH. The built application will need it installed.")


def build_executable(python_executable):
    """Build the standalone executable"""
    print("Building standalone executable...")
    
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Determine output name based on platform
    system = platform.system().lower()
    exec_name = f"mkv-manager-{system}"
    
    # Convert PNG icon to formats that work better with tkinter on Linux
    icon_path = project_root / "assets" / "icon.png"
    converted_icon = None
    
    if icon_path.exists():
        print("Converting icon for Linux compatibility...")
        try:
            # Create XBM format using Pillow (works natively with tkinter)
            xbm_path = project_root / "assets" / "icon.xbm"
            
            # Use Pillow to convert PNG to XBM
            convert_cmd = f"""
import sys
sys.path.insert(0, '{project_root}')
from PIL import Image
img = Image.open('{icon_path}')
img = img.resize((32, 32), Image.Resampling.LANCZOS)
img = img.convert('1')  # Convert to monochrome bitmap
img.save('{xbm_path}')
print('✅ Created XBM icon with Pillow')
"""
            
            result = subprocess.run([python_executable, "-c", convert_cmd], 
                                  capture_output=True, text=True, check=False)
            
            if result.returncode == 0 and xbm_path.exists():
                converted_icon = xbm_path
                print(f"✅ Created XBM icon: {xbm_path}")
            else:
                print(f"❌ Pillow conversion failed: {result.stderr}")
                print("❌ NO XBM ICON CREATED - SYSTEM TRAY ICON WILL NOT WORK!")
                    
        except Exception as e:
            print(f"❌ Icon conversion failed: {e}")
            print("❌ NO XBM ICON CREATED - SYSTEM TRAY ICON WILL NOT WORK!")
    
    def collect_tcl_tk_adddata():
        """Detect Tcl/Tk library directories and return list of add-data strings.

        Returns items in the form expected by PyInstaller: 'SRC:DEST' (uses
        os.pathsep to be platform-correct).
        """
        candidates = []
        adddata = []

        # Common locations relative to Python installation
        base = Path(sys.base_prefix)
        candidates += [
            base / 'lib' / 'tcl8.6',
            base / 'lib' / 'tcl8.5',
            base / 'lib' / 'tcl',
            base / 'lib' / 'tk8.6',
            base / 'lib' / 'tk8.5',
            base / 'lib' / 'tk',
        ]

        # Common system locations
        candidates += [
            Path('/usr/lib') / 'tcl8.6',
            Path('/usr/lib') / 'tcl8.5',
            Path('/usr/lib') / 'tk8.6',
            Path('/usr/lib') / 'tk8.5',
            Path('/usr/share') / 'tcltk',
            Path('/usr/share') / 'tcl8.6',
            Path('/usr/share') / 'tk8.6',
        ]

        # Try to locate via tkinter module if available
        try:
            import tkinter
            tfile = Path(tkinter.__file__)
            # tcl/tk runtime files may live near the tkinter package
            candidates.append(tfile.parent.parent / 'tcl')
            candidates.append(tfile.parent.parent / 'tk')
        except Exception:
            # ignore import errors; we still have other candidates
            pass

        seen = set()
        for p in candidates:
            try:
                p = p.resolve()
            except Exception:
                continue
            if p.exists() and p.is_dir() and str(p) not in seen:
                seen.add(str(p))
                # Use a simple destination name inside the bundle (tcl/, tk/ etc)
                dest_name = p.name
                adddata.append(f"{p}{os.pathsep}{dest_name}")

        return adddata


    # Build command
    cmd = [
        python_executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        f"--name={exec_name}",
        "--add-data=core:core",
        "--add-data=desktop:desktop",
        "--add-data=assets:assets",  # Include assets folder for runtime access
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=tkinter.font",
        "--hidden-import=tkinterdnd2",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=PIL.ImageTk",
        "--hidden-import=PIL.ImageOps",
        "--hidden-import=Pillow",
        "--collect-all=PIL",
        "--exclude-module=matplotlib",
        "--exclude-module=numpy",
        "--exclude-module=pandas",
        "--exclude-module=scipy",
        "desktop/main.py"
    ]
    
    # Add icon if available
    icon_path = project_root / "assets" / "icon.png"
    if icon_path.exists():
        cmd.extend([f"--icon={icon_path}"])

    # Add Tcl/Tk data directories if found (makes the binary more self-contained)
    tcl_adddata = collect_tcl_tk_adddata()
    for ad in tcl_adddata:
        cmd.append(f"--add-data={ad}")
    
    run_command(cmd)
    
    # Check if executable was created
    dist_dir = project_root / "dist"
    executable = dist_dir / exec_name
    
    if executable.exists():
        print(f"✅ Executable created: {executable}")
        print(f"   Size: {executable.stat().st_size / (1024*1024):.1f} MB")
        
        # Make executable (Linux/macOS)
        if system in ['linux', 'darwin']:
            os.chmod(executable, 0o755)
            print("✅ Executable permissions set")
            
        return executable
    else:
        print("❌ Executable not found after build")
        sys.exit(1)


def create_desktop_entry(executable_path):
    """Create desktop entry for Linux"""
    if platform.system() != "Linux":
        return
        
    try:
        desktop_dir = Path.home() / ".local" / "share" / "applications"
        desktop_dir.mkdir(parents=True, exist_ok=True)
        
        desktop_file = desktop_dir / "mkv-manager.desktop"
        icon_path = executable_path.parent.parent / "assets" / "icon.png"
        
        desktop_content = f"""[Desktop Entry]
Name=MKV Manager
Comment=Professional MKV file processing tool
Exec={executable_path}
Icon={icon_path if icon_path.exists() else 'video-x-generic'}
Terminal=false
Type=Application
Categories=AudioVideo;Video;
StartupNotify=true
"""
        
        with open(desktop_file, 'w') as f:
            f.write(desktop_content)
            
        print(f"✅ Desktop entry created: {desktop_file}")
        print("   The application should now appear in your application menu")
        
    except Exception as e:
        print(f"⚠️  Could not create desktop entry: {e}")


def create_appimage(executable_path, exec_name, desktop_name="MKV Manager"):
    """Create a minimal AppImage from the built executable.

    Steps:
    - Create an AppDir layout
    - Copy executable, desktop file and icon
    - Use appimagetool to build the AppImage
    """
    if platform.system() != "Linux":
        print("AppImage generation skipped: not running on Linux")
        return None

    project_root = Path(__file__).parent.parent
    appdir = project_root / f"{exec_name}.AppDir"

    try:
        # Prepare directories
        usr_bin = appdir / "usr" / "bin"
        icons_dir = appdir / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps"
        apps_dir = appdir / "usr" / "share" / "applications"

        for d in (usr_bin, icons_dir, apps_dir):
            d.mkdir(parents=True, exist_ok=True)

        # Copy executable
        target_exec = usr_bin / exec_name
        shutil.copy2(executable_path, target_exec)
        target_exec.chmod(0o755)

        # Desktop file for AppDir root
        desktop_file = appdir / f"{exec_name}.desktop"
        icon_src = project_root / "assets" / "icon.png"
        
        # Copy icon to AppDir root for AppImage compatibility
        if icon_src.exists():
            shutil.copy2(icon_src, appdir / "icon.png")
            icon_name = "icon"
        else:
            icon_name = "video-x-generic"
            
        desktop_content = f"""[Desktop Entry]
Name={desktop_name}
Exec={exec_name}
Icon={icon_name}
Type=Application
Categories=AudioVideo;Video;
Terminal=false
"""
        desktop_file.write_text(desktop_content, encoding="utf-8")

        # Copy icon if available
        if icon_src.exists():
            shutil.copy2(icon_src, icons_dir / icon_src.name)

        # Try to find appimagetool
        appimagetool = shutil.which("appimagetool")
        downloaded = False
        if not appimagetool:
            print("appimagetool not found in PATH; attempting to download latest AppImage...")
            # Use the continuous release for x86_64; adjust for other archs
            arch = platform.machine()

            if arch in ("x86_64", "amd64"):
                url = "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
            elif arch in ("aarch64", "arm64"):
                url = "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-aarch64.AppImage"
            else:
                url = "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"

            tmp = Path(tempfile.mkdtemp()) / "appimagetool.AppImage"

            try:
                urllib.request.urlretrieve(url, str(tmp))
                tmp.chmod(tmp.stat().st_mode | stat.S_IXUSR)
                appimagetool = str(tmp)
                downloaded = True
                print(f"Downloaded appimagetool to {tmp}")
            except Exception as e:
                print(f"❌ Failed to download appimagetool: {e}")
                return None

        # Build AppImage
        dist_dir = project_root / "dist"
        dist_dir.mkdir(exist_ok=True)
        output_appimage = dist_dir / f"{exec_name}.AppImage"

        cmd = [appimagetool, str(appdir), str(output_appimage)]
        print(f"Running: {' '.join(cmd)}")
        run_command(cmd)

        print(f"✅ AppImage created: {output_appimage}")

        # Remove temporary downloaded appimagetool
        if downloaded:
            try:
                Path(appimagetool).unlink()
            except Exception:
                pass

        return output_appimage

    except Exception as e:
        print(f"❌ AppImage creation failed: {e}")
        return None


def cleanup_build_artifacts():
    """Clean up build artifacts"""
    project_root = Path(__file__).parent.parent    
    build_dir = project_root / "build"

    if build_dir.exists():
        shutil.rmtree(build_dir)
        print("✅ Cleaned up build directory")
    
    # Clean up AppDir (build artifact that shouldn't remain in project)
    appdir_pattern = "*linux.AppDir"
    appdir_paths = list(project_root.glob(appdir_pattern))
    for appdir in appdir_paths:
        if appdir.is_dir():
            shutil.rmtree(appdir)
            print(f"✅ Cleaned up AppDir: {appdir}")
    
    # Keep dist directory but clean up .spec file
    spec_files = list(project_root.glob("*.spec"))

    for spec_file in spec_files:
        spec_file.unlink()
        print(f"✅ Removed {spec_file}")


def main():
    """Main build function"""
    print("MKV Manager Linux/macOS Build Script")
    print("=" * 40)
    
    system = platform.system()
    print(f"Building for: {system}")
    
    # Note about Windows
    if system == "Windows":
        print("⚠️  You're running the Linux build script on Windows.")
        print("   For Windows builds, use: python packaging/build.py")
        print("   This script will continue but create a Linux-style executable.")
    
    print()
    
    try:
        python_executable = setup_build_environment()
        check_dependencies(python_executable)
        executable = build_executable(python_executable)
        
        appimage = None
        if system == "Linux":
            create_desktop_entry(executable)
            # Create AppImage for maximum portability
            appimage = create_appimage(executable, executable.name)

            if appimage:
                print(f"AppImage available at: {appimage}")
        
        cleanup_build_artifacts()
        
        print()
        print("Build completed successfully!")
        print(f"   Executable: {executable}")
        if appimage:
            print(f"   AppImage: {appimage}")
            print()
            print("📦 Distribution:")
            print(f"   • The AppImage can be distributed as a single file")
            print(f"   • Users can download {appimage.name} and run it directly")
            print(f"   • No installation required - just make executable and run")
            print()
            print("🚀 To run the AppImage:")
            print(f"   chmod +x {appimage}")
            print(f"   {appimage}")
        print()
        print("💡 The application is now independent of this source directory")
        
    except Exception as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
