#!/usr/bin/env python3
"""
Forest Guard 2.0 Build Script
Package the game into a standalone executable
This script is written with ChatGPT-4o, but not directly copied from it.
"""

import os
import sys
import subprocess
from pathlib import Path
import shutil

def main():
    print("=" * 60)
    print("Forest Guard 2.0 Build Tool")
    print("=" * 60)

    current_dir = Path(__file__).parent
    print(f"Project directory: {current_dir}")
    
    # Check required files exist
    required_files = ['run_game.py', 'src/', 'assets/', 'levels/']
    missing_files = []
    
    for file_path in required_files:
        if not (current_dir / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"Error: Missing required files/directories: {missing_files}")
        return False
    
    # Install dependencies
    print("\nStep 1: Installing dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, cwd=current_dir)
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False
    
    # Clean old build files
    print("\nStep 2: Cleaning old build files...")
    dist_dir = current_dir / 'dist'
    build_dir = current_dir / 'build'
    spec_file = current_dir / 'run_game.spec'
    
    for dir_path in [dist_dir, build_dir]:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"✓ Cleaned {dir_path.name}")
    
    if spec_file.exists():
        spec_file.unlink()
        print("✓ Cleaned run_game.spec")
    
    # Build PyInstaller command
    print("\nStep 3: Starting build process...")
    
    pyinstaller_cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onedir',  # Package as directory (includes all dependencies)
        '--windowed',  # No console window on Windows
        '--name=ForestGuard2.0',  # Executable name
        '--add-data=assets;assets',  # Include assets directory
        '--add-data=levels;levels',  # Include levels directory
        '--add-data=src;src',  # Include src directory
        '--hidden-import=pygame',  # Ensure pygame is imported
        '--collect-all=pygame',  # Collect all pygame related files
        'run_game.py'
    ]
    
    # Check for icon file and add it if exists
    icon_paths = [
        current_dir / 'assets' / 'icon.ico',
        current_dir / 'assets' / 'icon.png',
        current_dir / 'icon.ico',
        current_dir / 'icon.png'
    ]
    
    icon_found = False
    for icon_path in icon_paths:
        if icon_path.exists():
            pyinstaller_cmd.insert(-1, f'--icon={icon_path}')
            print(f"✓ Found icon: {icon_path}")
            icon_found = True
            break
    
    if not icon_found:
        print("! No icon file found. Executable will use default icon.")
    
    try:
        subprocess.run(pyinstaller_cmd, check=True, cwd=current_dir)
        print("✓ Build completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed: {e}")
        return False
    
    # Check output
    exe_dir = dist_dir / 'ForestGuard2.0'
    if exe_dir.exists():
        print(f"\n🎉 Build successful!")
        print(f"Executable location: {exe_dir}")
        print(f"Main program: {exe_dir / 'ForestGuard2.0.exe'}")
        print("\n📦 Distribution instructions:")
        print("- Copy the entire 'ForestGuard2.0' folder to other computers")
        print("- Run 'ForestGuard2.0.exe' to start the game")
        print("- Ensure target computers support graphics acceleration")
        
        # Create user manual
        readme_content = """Forest Guard 2.0 - Game Instructions

Installation:
1. Copy the entire folder to your desired location
2. Double-click ForestGuard2.0.exe to start the game

System Requirements:
- Windows 10 or higher
- Graphics card with OpenGL support
- At least 512MB available memory

Game Controls:
- ESC: Return to menu
- Mouse: Place towers and make selections

If you encounter any issues, please contact the developer.

Enjoy the game!
"""
        
        with open(exe_dir / "README.txt", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        return True
    else:
        print("\n✗ Build failed: Output files not found")
        return False

if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Build complete! Press Enter to exit...")
    input() 