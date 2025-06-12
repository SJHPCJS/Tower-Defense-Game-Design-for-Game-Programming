import json, os
from settings import GRID_W, GRID_H
from resource_manager import ResourceManager

def load_grid(filename: str) -> list[list[int]]:
    """Load 0/1 grid from levels/filename (must be 20×15)."""
    try:
        level_path = ResourceManager.get_level_path(filename)
        with open(level_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['grid']
    except UnicodeDecodeError:
        level_path = ResourceManager.get_level_path(filename)
        with open(level_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        return data['grid']

# Create a default empty grid (all grass)
GRID_MAP: list[list[int]] = [[1 for _ in range(GRID_W)] for _ in range(GRID_H)]

def update_grid_map(new_grid):
    """Update global grid map"""
    global GRID_MAP
    GRID_MAP = new_grid

def walkable(gx: int, gy: int) -> bool:
    return GRID_MAP[gy][gx] == 0

# Load default grid map
try:
    GRID_MAP: list[list[int]] = load_grid('Level5Path.json')
except:
    # Fallback grid if file not found
    GRID_MAP = [[1 for _ in range(GRID_W)] for _ in range(GRID_H)]
    # Create a simple path down the middle
    for y in range(GRID_H):
        GRID_MAP[y][GRID_W//2] = 0
