@echo off
echo Starting MKV Desktop GUI...
echo.

:: Try to find Python installation automatically
set PYTHON_EXE=

:: Check common Python locations
if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python313\python.exe" (
    set PYTHON_EXE=%USERPROFILE%\AppData\Local\Programs\Python\Python313\python.exe
) else if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe" (
    set PYTHON_EXE=%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe
) else if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe" (
    set PYTHON_EXE=%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe
) else if exist "C:\Python313\python.exe" (
    set PYTHON_EXE=C:\Python313\python.exe
) else if exist "C:\Python312\python.exe" (
    set PYTHON_EXE=C:\Python312\python.exe
) else if exist "C:\Python311\python.exe" (
    set PYTHON_EXE=C:\Python311\python.exe
) else (
    :: Try system PATH
    where python >nul 2>&1
    if %errorlevel% == 0 (
        set PYTHON_EXE=python
    ) else (
        echo ❌ Python not found! Please install Python 3.11+ from https://python.org
        pause
        exit /b 1
    )
)

echo Using Python: %PYTHON_EXE%
echo.

:: Run the desktop GUI
"%PYTHON_EXE%" main.py

echo.
echo Press any key to exit...
pause >nul
