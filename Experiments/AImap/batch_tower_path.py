
import os, random, sys
from importlib import import_module
from datetime import datetime


td = import_module('td_map_generator')

WIDTH, HEIGHT = td.WIDTH, td.HEIGHT
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
BATCH_DIR = os.path.join(OUT_DIR, "tower_path_batch")
os.makedirs(BATCH_DIR, exist_ok=True)

print("Generating 25 tower_path maps ...")

for i in range(1, 26):
    grid = td.algo_tower_path()
    img_name = f"tower_path_{i:02d}.png"
    img_path = os.path.join(BATCH_DIR, img_name)
    td.save_grid_image_tiles(grid, img_path)
    print(f"  [{i:02d}/25] -> {img_path}")

print("All maps saved to", BATCH_DIR)
