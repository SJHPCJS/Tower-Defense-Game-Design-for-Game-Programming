"""Inspired by ChatGPT"""

import os
import sys
from pathlib import Path


class ResourceManager:
    """Manages resource paths for both development and packaged environments"""
    
    _base_path = None
    
    @classmethod
    def get_base_path(cls):
        """Get the base path for resources"""
        if cls._base_path is None:
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                # PyInstaller packaged environment
                cls._base_path = Path(sys._MEIPASS)
            else:
                # Development environment
                cls._base_path = Path(__file__).parent.parent
        return cls._base_path
    
    @classmethod
    def get_asset_path(cls, relative_path):
        """Get full path to an asset file"""
        return cls.get_base_path() / "assets" / relative_path
    
    @classmethod
    def get_level_path(cls, filename):
        """Get full path to a level file"""
        return cls.get_base_path() / "levels" / filename
    
    @classmethod
    def get_src_path(cls, filename):
        """Get full path to a source file"""
        return cls.get_base_path() / "src" / filename


# Convenience functions for common resource types
def get_sprite_path(category, filename):
    """Get path to a sprite file"""
    return ResourceManager.get_asset_path(f"sprite/{category}/{filename}")

def get_library_path(category, filename):
    """Get path to a library image file"""
    return ResourceManager.get_asset_path(f"library/{category}/{filename}")

def get_bullet_path(filename):
    """Get path to a bullet image file"""
    return ResourceManager.get_asset_path(f"bullet/{filename}")

def get_tiles_path(filename):
    """Get path to a tiles image file"""
    return ResourceManager.get_asset_path(f"tiles/{filename}")

def get_music_path(filename):
    """Get path to a music file"""
    return ResourceManager.get_asset_path(f"music/{filename}")


