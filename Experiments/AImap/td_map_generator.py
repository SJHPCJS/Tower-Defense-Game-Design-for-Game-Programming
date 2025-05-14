

import random, time, csv, os, sys
from collections import deque
from typing import List, Tuple

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

WIDTH, HEIGHT = 20, 15
SPAWN = (0, 0)
HOME = (WIDTH - 2, HEIGHT - 2)
RUNS_PER_ALGO = 20

GRASS_TILE_PATH = r"G:\常嘉硕\大学\中南大学\Games Programming\Pygame\TowerDesign\Prototypes\TowerTest\assets\tiles\grass.png"
PATH_TILE_PATH  = r"G:\常嘉硕\大学\中南大学\Games Programming\Pygame\TowerDesign\Prototypes\TowerTest\assets\tiles\path1.png"

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def neighbors4(x: int, y: int, w: int = WIDTH, h: int = HEIGHT):
    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h:
            yield nx, ny

def bfs_exists(grid: List[List[int]], start: Tuple[int,int] = SPAWN, goal: Tuple[int,int] = HOME) -> bool:
    if grid[start[1]][start[0]] or grid[goal[1]][goal[0]]:
        return False
    dq = deque([start])
    seen = {start}
    while dq:
        x, y = dq.popleft()
        if (x, y) == goal:
            return True
        for nx, ny in neighbors4(x, y):
            if grid[ny][nx] == 0 and (nx, ny) not in seen:
                seen.add((nx, ny))
                dq.append((nx, ny))
    return False

def branch_points(grid):
    return sum(
        1 for y in range(HEIGHT) for x in range(WIDTH)
        if grid[y][x]==0 and sum(grid[ny][nx]==0 for nx, ny in neighbors4(x,y)) >= 3
    )

def path_tiles(grid):
    return sum(v==0 for row in grid for v in row)


def algo_tower_path():
    path = {SPAWN}
    x, y = SPAWN
    max_steps = WIDTH * HEIGHT * 4
    while (x, y) != HOME and len(path) < max_steps:
        dirs = list(neighbors4(x, y))
        random.shuffle(dirs)
        dirs.sort(key=lambda p: (abs(p[0]-HOME[0])+abs(p[1]-HOME[1])) + random.randint(-2,2))
        moved = False
        for nx, ny in dirs:
            if (nx, ny) not in path:
                x, y = nx, ny
                path.add((x, y))
                moved = True
                break
        if not moved:
            if x < HOME[0]: x += 1
            elif x > HOME[0]: x -= 1
            elif y < HOME[1]: y += 1
            elif y > HOME[1]: y -= 1
            path.add((x,y))
    path.add(HOME)
    grid = [[1]*WIDTH for _ in range(HEIGHT)]
    for px, py in path:
        grid[py][px] = 0

    for _ in range(random.randint(3,8)):
        bx, by = random.choice(tuple(path))
        length = random.randint(2,5)
        dir = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        nx, ny = bx, by
        for _ in range(length):
            nx += dir[0]; ny += dir[1]
            if not (0 <= nx < WIDTH and 0 <= ny < HEIGHT): break
            grid[ny][nx] = 0
            if random.random() < 0.25:
                dir = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
    return grid

def algo_maze_loops():
    loop_fraction = random.uniform(0.05,0.35)
    grid = [[1]*WIDTH for _ in range(HEIGHT)]
    stack = [(0,0)]
    grid[0][0] = 0
    while stack:
        x, y = stack[-1]
        dirs = [(2,0),(-2,0),(0,2),(0,-2)]
        random.shuffle(dirs)
        moved = False
        for dx, dy in dirs:
            nx, ny = x+dx, y+dy
            if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and grid[ny][nx]==1:
                grid[ny][nx]=0
                grid[y+dy//2][x+dx//2]=0
                stack.append((nx,ny))
                moved=True
                break
        if not moved:
            stack.pop()
    walls = [(x,y) for y in range(HEIGHT) for x in range(WIDTH) if grid[y][x]==1]
    random.shuffle(walls)
    for x,y in walls[:int(len(walls)*loop_fraction)]:
        if sum(grid[ny][nx]==0 for nx,ny in neighbors4(x,y))>=2:
            grid[y][x]=0
    grid[HOME[1]][HOME[0]]=0
    return grid

def algo_prim_loops():
    loop_chance = random.uniform(0.15,0.4)
    grid = [[1]*WIDTH for _ in range(HEIGHT)]
    frontier=[(0,0)]
    grid[0][0]=0
    while frontier:
        x,y=random.choice(frontier)
        frontier.remove((x,y))
        dirs=[(2,0),(-2,0),(0,2),(0,-2)]
        random.shuffle(dirs)
        for dx,dy in dirs:
            nx,ny=x+dx,y+dy
            if 0<=nx<WIDTH and 0<=ny<HEIGHT and grid[ny][nx]==1:
                grid[y+dy//2][x+dx//2]=0
                grid[ny][nx]=0
                frontier.append((nx,ny))
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if grid[y][x]==1 and random.random()<loop_chance and sum(grid[ny][nx]==0 for nx,ny in neighbors4(x,y))>=2:
                grid[y][x]=0
    grid[HOME[1]][HOME[0]]=0
    return grid

ALGOS = {
    "tower_path": algo_tower_path,
    "maze_loops": algo_maze_loops,
    "prim_loops": algo_prim_loops,
}


def save_grid_image_tiles(grid, path):
    try:
        grass = Image.open(GRASS_TILE_PATH).convert("RGBA")
        path_tile = Image.open(PATH_TILE_PATH).convert("RGBA")
    except FileNotFoundError as e:
        print("Tile image not found:", e)
        print("Fallback to grayscale preview.")
        return save_grid_image_fallback(grid, path)

    tw, th = grass.size
    out = Image.new("RGBA", (WIDTH*tw, HEIGHT*th))
    for y in range(HEIGHT):
        for x in range(WIDTH):
            tile = path_tile if grid[y][x]==0 else grass
            out.paste(tile, (x*tw, y*th))
    out.save(path)

def save_grid_image_fallback(grid, path):
    arr = np.array(grid)
    plt.figure(figsize=(4,3))
    plt.imshow(arr, cmap="Greys", origin="upper")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


def main():
    csv_records=[]
    mean_time={}
    random.seed()
    for algo_name,func in ALGOS.items():
        times=[]
        for run in range(1, RUNS_PER_ALGO+1):
            t0=time.perf_counter()
            grid=func()
            t_ms=(time.perf_counter()-t0)*1000
            times.append(t_ms)
            valid=bfs_exists(grid)
            csv_records.append({
                "algorithm":algo_name,
                "run":run,
                "time_ms":round(t_ms,3),
                "valid":valid,
                "branch_pts":branch_points(grid),
                "path_tiles":path_tiles(grid)
            })
            if run==1:
                img_path=os.path.join(OUT_DIR,f"{algo_name}_sample.png")
                save_grid_image_tiles(grid,img_path)
        mean_time[algo_name]=sum(times)/len(times)

    csv_path=os.path.join(OUT_DIR,"map_gen_results.csv")
    with open(csv_path,"w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=csv_records[0].keys())
        writer.writeheader()
        writer.writerows(csv_records)

    plt.figure(figsize=(6,4))
    plt.bar(mean_time.keys(),mean_time.values())
    plt.ylabel("Mean Generation Time (ms)")
    plt.title("Forest Guard TD Map Generation – Avg Time")
    plt.tight_layout()
    bar_path=os.path.join(OUT_DIR,"average_time.png")
    plt.savefig(bar_path,dpi=200)
    plt.close()

    print("=== Tower‑Defense Map Generator ===")
    print(f"CSV -> {csv_path}")
    print(f"Preview PNGs & bar chart saved in {OUT_DIR}")
    print("Mean generation time (ms):")
    for k,v in mean_time.items():
        print(f"  {k:12s}: {v:.3f}")
    print("Done!")



if __name__=="__main__":
    main()
