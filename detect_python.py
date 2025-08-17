#!/usr/bin/env python3
"""
Cross-platform Python and tkinter detection utility
This script helps find the correct Python executable with tkinter support
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path


def find_python_executables():
    """Find all available Python executables"""
    executables = []

    if os.name == 'nt':
        user_python_dir = Path.home() / "AppData" / "Local" / "Programs" / "Python"
        if user_python_dir.exists():
            for python_dir in user_python_dir.iterdir():
                if python_dir.is_dir() and python_dir.name.startswith("Python"):
                    python_exe = python_dir / "python.exe"
                    if python_exe.exists():
                        executables.append(str(python_exe))

        for version in ["313", "312", "311", "310", "39"]:
            system_python = Path(f"C:/Python{version}/python.exe")
            if system_python.exists():
                executables.append(str(system_python))

    path_python = shutil.which("python")
    if path_python:
        executables.append(path_python)

    path_python3 = shutil.which("python3")
    if path_python3:
        executables.append(path_python3)

    seen = set()
    unique_executables = []
    for exe in executables:
        if exe not in seen:
            seen.add(exe)
            unique_executables.append(exe)

    return unique_executables


def test_tkinter(python_exe):
    """Test if a Python executable has working tkinter"""
    try:
        test_code = '''
import tkinter as tk
root = tk.Tk()
root.withdraw()
root.destroy()
print("SUCCESS")
'''

        result = subprocess.run([python_exe, "-c", test_code],
                                capture_output=True, text=True, timeout=10)

        if result.returncode == 0 and "SUCCESS" in result.stdout:
            return True, None
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)


def get_python_version(python_exe):
    """Get Python version string"""
    try:
        result = subprocess.run([python_exe, "--version"],
                                capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()
        return "Unknown version"
    except:
        return "Unknown version"


def main():
    print("🔍 Searching for Python installations with tkinter support...")
    print("=" * 60)

    executables = find_python_executables()

    if not executables:
        print("❌ No Python executables found!")
        print("\nPlease install Python from: https://www.python.org/downloads/")
        return

    working_pythons = []

    for i, python_exe in enumerate(executables, 1):
        print(f"\n{i}. Testing: {python_exe}")
        version = get_python_version(python_exe)
        print(f"   Version: {version}")

        has_tkinter, error = test_tkinter(python_exe)

        if has_tkinter:
            print("   tkinter: ✅ Working")
            working_pythons.append(python_exe)
        else:
            print("   tkinter: ❌ Not working")
            if error:
                print(f"   Error: {error[:100]}...")

    print("\n" + "=" * 60)

    if working_pythons:
        print(
            f"✅ Found {len(working_pythons)} Python installation(s) with tkinter:")
        for i, python_exe in enumerate(working_pythons, 1):
            print(f"   {i}. {python_exe}")

        print(f"\n🚀 Recommended command to run desktop GUI:")
        generic_cmd = working_pythons[0].replace(
            str(Path.home()), "%USERPROFILE%")
        print(f'   "{generic_cmd}" desktop_gui.py')

        batch_content = f'''@echo off
echo Starting MKV Cleaner Desktop GUI...
echo.
echo Using: {working_pythons[0]}
echo.
"{working_pythons[0]}" desktop_gui.py
echo.
echo Press any key to exit...
pause >nul
'''

        batch_content = batch_content.replace(
            str(Path.home()), "%USERPROFILE%")
        batch_content = batch_content.replace(
            str(Path.home()).replace("\\", "/"), "%USERPROFILE%")

        with open("start_desktop_gui_auto.bat", "w") as f:
            f.write(batch_content)

        print(f"\n📝 Created generic batch file: start_desktop_gui_auto.bat")
        print("   You can double-click this file to run the desktop GUI!")
        print("   (Uses %USERPROFILE% environment variable - no personal information)")
        print("\n⚠️  Note: start_desktop_gui_auto.bat is added to .gitignore")
        print("   This prevents accidentally committing personal paths.")

    else:
        print("❌ No Python installations with working tkinter found!")
        print("\nPossible solutions:")
        print("1. Reinstall Python from https://www.python.org/downloads/")
        print("2. Make sure to check 'Add Python to PATH' during installation")
        print("3. Use the standard Python installer (not Microsoft Store version)")


if __name__ == "__main__":
    main()
