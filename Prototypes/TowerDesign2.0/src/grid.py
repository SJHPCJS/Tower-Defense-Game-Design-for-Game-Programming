import json, os
from settings import GRID_W, GRID_H

def load_grid(filename: str) -> list[list[int]]:
    """Load 0/1 grid from levels/filename (must be 20×15)."""
    fpath = os.path.join(os.path.dirname(__file__), '..', 'levels', filename)
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except UnicodeDecodeError:
        # Fallback to other encodings if UTF-8 fails
        with open(fpath, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    grid = data.get('grid')
    if len(grid) != GRID_H or any(len(r) != GRID_W for r in grid):
        raise ValueError("Level size must be 20×15")
    return grid

# Create a default empty grid (all grass)
GRID_MAP: list[list[int]] = [[1 for _ in range(GRID_W)] for _ in range(GRID_H)]

def update_grid_map(new_grid: list[list[int]]):
    """Update the global GRID_MAP with new grid data"""
    global GRID_MAP
    if len(new_grid) == GRID_H and all(len(r) == GRID_W for r in new_grid):
        GRID_MAP = [row[:] for row in new_grid]  # Deep copy
    else:
        raise ValueError("Grid size must be 20×15")

def walkable(x: int, y: int) -> bool:
    return 0 <= x < GRID_W and 0 <= y < GRID_H and GRID_MAP[y][x] == 0
