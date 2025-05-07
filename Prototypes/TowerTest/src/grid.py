import json, os
from settings import GRID_W, GRID_H

def load_grid(filename: str) -> list[list[int]]:
    """Load 0/1 grid from levels/filename (must be 20×15)."""
    fpath = os.path.join(os.path.dirname(__file__), '..', 'levels', filename)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    grid = data.get('grid')
    if len(grid) != GRID_H or any(len(r) != GRID_W for r in grid):
        raise ValueError("Level size must be 20×15")
    return grid

# default grid at boot
GRID_MAP: list[list[int]] = load_grid('level1.json')

def walkable(x: int, y: int) -> bool:
    return 0 <= x < GRID_W and 0 <= y < GRID_H and GRID_MAP[y][x] == 0
