@echo off
echo ==========================================
echo Forest Guard 2.0 Build Tool
echo ==========================================
echo.

cd /d "%~dp0"

echo Starting build process...
python build_executable.py

echo.
echo Build complete! 
pause 