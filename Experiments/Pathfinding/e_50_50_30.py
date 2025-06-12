import os, random, time, heapq
from collections import deque

import pandas as pd
import matplotlib.pyplot as plt


def generate_grid(w, h, density, rng):
    grid = [[0 for _ in range(w)] for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if (x, y) in [(0, 0), (w - 1, h - 1)]:
                continue
            if rng.random() < density:
                grid[y][x] = 1
    return grid

def neighbors(x, y, w, h, grid):
    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
        nx, ny = x+dx, y+dy
        if 0 <= nx < w and 0 <= ny < h and grid[ny][nx]==0:
            yield nx, ny

def reconstruct_length(parent, goal):
    length, node = 0, goal
    while node:
        node = parent[node]
        length += 1
    return length

def bfs(grid):
    h, w = len(grid), len(grid[0])
    start, goal = (0,0), (w-1, h-1)
    q, parent, visited = deque([start]), {start:None}, 0
    t0 = time.perf_counter()
    while q:
        x, y = q.popleft(); visited += 1
        if (x, y) == goal:
            break
        for nx, ny in neighbors(x,y,w,h,grid):
            if (nx,ny) not in parent:
                parent[(nx,ny)] = (x,y)
                q.append((nx,ny))
    elapsed = time.perf_counter() - t0
    if goal not in parent:      # 无解
        return None, visited, elapsed
    return reconstruct_length(parent, goal), visited, elapsed

def dijkstra(grid):
    h, w = len(grid), len(grid[0])
    start, goal = (0,0), (w-1, h-1)
    dist, parent = {start:0}, {start:None}
    pq, visited = [(0,start)], 0
    t0 = time.perf_counter()
    while pq:
        d,(x,y) = heapq.heappop(pq); visited += 1
        if (x,y)==goal: break
        for nx, ny in neighbors(x,y,w,h,grid):
            nd = d+1
            if nd < dist.get((nx,ny), float('inf')):
                dist[(nx,ny)] = nd
                parent[(nx,ny)] = (x,y)
                heapq.heappush(pq,(nd,(nx,ny)))
    elapsed = time.perf_counter() - t0
    if goal not in parent:
        return None, visited, elapsed
    return dist[goal]+1, visited, elapsed

def _a_star_variant(grid, weight=1.0, greedy=False):
    h, w = len(grid), len(grid[0])
    start, goal = (0,0), (w-1,h-1)
    def heuristic(x,y): gx,gy=goal; return abs(x-gx)+abs(y-gy)
    g, f, parent = {start:0}, {start:heuristic(*start)}, {start:None}
    pq, visited = [(f[start], start)], 0
    t0 = time.perf_counter()
    while pq:
        _, (x,y) = heapq.heappop(pq); visited += 1
        if (x,y)==goal: break
        for nx, ny in neighbors(x,y,w,h,grid):
            tentative_g = g[(x,y)] + 1
            if tentative_g < g.get((nx,ny), float('inf')):
                g[(nx,ny)] = tentative_g
                hcost = heuristic(nx,ny)
                score = (0 if greedy else tentative_g) + weight * hcost
                f[(nx,ny)] = score
                parent[(nx,ny)] = (x,y)
                heapq.heappush(pq,(score,(nx,ny)))
    elapsed = time.perf_counter() - t0
    if goal not in parent:
        return None, visited, elapsed
    return g[goal]+1, visited, elapsed

def astar(grid):
    return _a_star_variant(grid, weight=1.0, greedy=False)

def greedy_best_first(grid):
    return _a_star_variant(grid, weight=0.0, greedy=True)

def weighted_astar(grid):
    return _a_star_variant(grid, weight=1.5, greedy=False)


w = h = 50
density = 0.3
seed = 42
rng = random.Random(seed)


for _ in range(100):
    grid = generate_grid(w, h, density, rng)
    if bfs(grid)[0] is not None:
        break
else:
    grid = [[0]*w for _ in range(h)]

algos = {
    "A*": astar,
    "BFS": bfs,
    "Dijkstra": dijkstra,
    "Greedy": greedy_best_first,
    "WeightedA*": weighted_astar,
}

records = []
opt_path_len, *_ = bfs(grid)

for name, fn in algos.items():
    path_len, visited, elapsed = fn(grid)
    records.append({
        "Algorithm": name,
        "Time (ms)": round(elapsed*1000, 2),
        "Nodes Visited": visited,
        "Path Optimality (1=shortest)": round(path_len/opt_path_len, 2)
    })

df = pd.DataFrame(records).sort_values("Time (ms)")
print("\n===  Key metrics (50x50, 30% obstacles)  ===")
print(df.to_string(index=False))

df.to_csv("key_metrics_50x50_d30.csv", index=False)

out_dir = "figures"
os.makedirs(out_dir, exist_ok=True)


plt.figure(figsize=(6,3))
bars = plt.bar(df["Algorithm"], df["Time (ms)"], color="skyblue")
plt.ylabel("Median Runtime (ms)")
plt.title("Runtime – 50×50 grid (30% obstacles)")
for bar, val in zip(bars, df["Time (ms)"]):
    plt.text(bar.get_x()+bar.get_width()/2, val+0.05, f"{val:.2f}",
             ha="center", va="bottom", fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(out_dir, "runtime_50x50_d30.png"), dpi=300)


plt.figure(figsize=(6,3))
bars = plt.bar(df["Algorithm"], df["Nodes Visited"], color="orange")
plt.ylabel("Median Nodes Visited")
plt.title("Exploration Cost – 50×50 grid (30% obstacles)")
for bar, val in zip(bars, df["Nodes Visited"]):
    plt.text(bar.get_x()+bar.get_width()/2, val+20, str(int(val)),
             ha="center", va="bottom", fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(out_dir, "nodes_50x50_d30.png"), dpi=300)

print("\nImages saved to ./figures/")
