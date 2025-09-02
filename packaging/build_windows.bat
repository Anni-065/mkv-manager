@echo off
echo MKV Manager - Build Script
echo ===============================
echo Building installer-only distribution
echo.

:: Change to project root directory
cd /d "%~dp0\.."

:: Activate virtual environment
call .venv\Scripts\activate

echo Building executable for packaging...
pyinstaller --clean --noconfirm packaging\pyinstaller\mkv_cleaner.spec

echo Creating installer...
"C:\Program Files (x86)\NSIS\makensis.exe" packaging\nsis\installer.nsi

echo Cleaning up build artifacts...
if exist "dist\MKV_Cleaner.exe" del "dist\MKV_Cleaner.exe"
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo Installer created: MKV_Cleaner_Installer.exe
pause
