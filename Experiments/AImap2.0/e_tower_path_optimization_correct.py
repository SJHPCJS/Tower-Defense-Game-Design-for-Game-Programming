import os, random, time, csv
from collections import deque
from typing import List, Tuple, Set
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import heapq

# Grid configuration
WIDTH, HEIGHT = 20, 15
SPAWN = (0, 0)
HOME = (WIDTH - 2, HEIGHT - 2)
RUNS_PER_ALGO = 25

# Tile paths for visualization
GRASS_TILE_PATH = r"G:\常嘉硕\大学\中南大学\Games Programming\Pygame\TowerDesign\Prototypes\TowerTest\assets\tiles\grass.png"
PATH_TILE_PATH = r"G:\常嘉硕\大学\中南大学\Games Programming\Pygame\TowerDesign\Prototypes\TowerTest\assets\tiles\path1.png"

# Output directories
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
BATCH_DIR = os.path.join(OUT_DIR, "tower_path_optimization_correct_batch")
FIGURES_DIR = os.path.join(OUT_DIR, "figures")
os.makedirs(BATCH_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

def neighbors4(x: int, y: int, w: int = WIDTH, h: int = HEIGHT):
    """Get 4-directional neighbors within grid bounds"""
    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h:
            yield nx, ny

def algo_tower_path():
    """Original tower path algorithm from AImap"""
    path = {SPAWN}
    x, y = SPAWN
    max_steps = WIDTH * HEIGHT * 4
    
    # Generate main path to HOME
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
    
    # Create grid
    grid = [[1]*WIDTH for _ in range(HEIGHT)]
    for px, py in path:
        grid[py][px] = 0

    # Add random branches
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

def heuristic(a, b):
    """Manhattan distance heuristic"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def find_shortest_path_length(grid: List[List[int]], start: Tuple[int,int], goal: Tuple[int,int]) -> int:
    """Find the shortest path length using A*"""
    if grid[start[1]][start[0]] != 0 or grid[goal[1]][goal[0]] != 0:
        return -1
    
    open_set = [(0, start)]
    g_score = {start: 0}
    
    while open_set:
        current_f, current = heapq.heappop(open_set)
        
        if current == goal:
            return g_score[current]
        
        for nx, ny in neighbors4(current[0], current[1]):
            if grid[ny][nx] != 0:  # Can only move on path tiles
                continue
                
            tentative_g = g_score[current] + 1
            
            if (nx, ny) not in g_score or tentative_g < g_score[(nx, ny)]:
                g_score[(nx, ny)] = tentative_g
                f_score = tentative_g + heuristic((nx, ny), goal)
                heapq.heappush(open_set, (f_score, (nx, ny)))
    
    return -1  # No path found

def find_all_optimal_path_nodes(grid: List[List[int]], start: Tuple[int,int], goal: Tuple[int,int]) -> Set[Tuple[int,int]]:
    """Find all nodes that are part of ANY optimal (shortest) path from start to goal"""
    # First find the shortest path length
    shortest_length = find_shortest_path_length(grid, start, goal)
    if shortest_length == -1:
        return set()
    
    # Now find all nodes that can be part of an optimal path
    # A node (x,y) is part of an optimal path if:
    # distance(start, (x,y)) + distance((x,y), goal) == shortest_length
    
    optimal_nodes = set()
    
    # Calculate distances from start to all reachable nodes
    distances_from_start = {}
    queue = deque([(start, 0)])
    distances_from_start[start] = 0
    
    while queue:
        (x, y), dist = queue.popleft()
        
        for nx, ny in neighbors4(x, y):
            if grid[ny][nx] != 0:  # Can only move on path tiles
                continue
            if (nx, ny) not in distances_from_start:
                distances_from_start[(nx, ny)] = dist + 1
                queue.append(((nx, ny), dist + 1))
    
    # Calculate distances from goal to all reachable nodes (backward search)
    distances_to_goal = {}
    queue = deque([(goal, 0)])
    distances_to_goal[goal] = 0
    
    while queue:
        (x, y), dist = queue.popleft()
        
        for nx, ny in neighbors4(x, y):
            if grid[ny][nx] != 0:  # Can only move on path tiles
                continue
            if (nx, ny) not in distances_to_goal:
                distances_to_goal[(nx, ny)] = dist + 1
                queue.append(((nx, ny), dist + 1))
    
    # Find nodes that are part of optimal paths
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if grid[y][x] == 0:  # Is a path tile
                pos = (x, y)
                if (pos in distances_from_start and 
                    pos in distances_to_goal and
                    distances_from_start[pos] + distances_to_goal[pos] == shortest_length):
                    optimal_nodes.add(pos)
    
    return optimal_nodes

def find_all_reasonable_path_nodes(grid: List[List[int]], start: Tuple[int,int], goal: Tuple[int,int], tolerance: int = 2) -> Set[Tuple[int,int]]:
    """Find all nodes that are part of any reasonably short path (within tolerance of optimal)"""
    shortest_length = find_shortest_path_length(grid, start, goal)
    if shortest_length == -1:
        return set()
    
    max_allowed_length = shortest_length + tolerance
    reasonable_nodes = set()
    
    # Calculate distances from start
    distances_from_start = {}
    queue = deque([(start, 0)])
    distances_from_start[start] = 0
    
    while queue:
        (x, y), dist = queue.popleft()
        for nx, ny in neighbors4(x, y):
            if grid[ny][nx] != 0:
                continue
            if (nx, ny) not in distances_from_start:
                distances_from_start[(nx, ny)] = dist + 1
                queue.append(((nx, ny), dist + 1))
    
    # Calculate distances to goal
    distances_to_goal = {}
    queue = deque([(goal, 0)])
    distances_to_goal[goal] = 0
    
    while queue:
        (x, y), dist = queue.popleft()
        for nx, ny in neighbors4(x, y):
            if grid[ny][nx] != 0:
                continue
            if (nx, ny) not in distances_to_goal:
                distances_to_goal[(nx, ny)] = dist + 1
                queue.append(((nx, ny), dist + 1))
    
    # Find nodes on reasonable paths
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if grid[y][x] == 0:
                pos = (x, y)
                if (pos in distances_from_start and 
                    pos in distances_to_goal and
                    distances_from_start[pos] + distances_to_goal[pos] <= max_allowed_length):
                    reasonable_nodes.add(pos)
    
    return reasonable_nodes

def optimize_tower_path(grid: List[List[int]], strategy: str = "optimal") -> Tuple[List[List[int]], int]:
    """Optimize the tower path by removing useless path tiles"""
    optimized_grid = [row[:] for row in grid]
    
    if strategy == "optimal":
        useful_nodes = find_all_optimal_path_nodes(grid, SPAWN, HOME)
    else:  # reasonable
        useful_nodes = find_all_reasonable_path_nodes(grid, SPAWN, HOME, tolerance=3)
    
    # Clean up useless path tiles
    cleaned_count = 0
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if grid[y][x] == 0 and (x, y) not in useful_nodes:
                optimized_grid[y][x] = 1  # Convert back to grass
                cleaned_count += 1
    
    return optimized_grid, cleaned_count

def path_tiles(grid):
    """Count total path tiles in grid"""
    return sum(v==0 for row in grid for v in row)

def branch_points(grid):
    """Count branch points (path tiles with 3+ path neighbors)"""
    return sum(
        1 for y in range(HEIGHT) for x in range(WIDTH)
        if grid[y][x]==0 and sum(grid[ny][nx]==0 for nx, ny in neighbors4(x,y)) >= 3
    )

def save_grid_image_tiles(grid, path):
    """Save grid as image using tile graphics"""
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
    """Fallback method to save grid as grayscale image"""
    arr = np.array(grid)
    plt.figure(figsize=(4,3))
    plt.imshow(arr, cmap="Greys", origin="upper")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()

def run_experiment():
    """Run the corrected tower path optimization experiment"""
    print("Running Tower Path Optimization Experiment (Correct Version)...")
    print("Finding all nodes that are part of optimal paths on generated maps...")
    print(f"Grid size: {WIDTH}x{HEIGHT}")
    print(f"Number of map pairs to generate: {RUNS_PER_ALGO}")
    print()
    
    # Test both strategies
    strategies = ["optimal", "reasonable"]
    
    for strategy in strategies:
        print(f"=== Testing {strategy.upper()} strategy ===")
        
        original_stats = []
        optimized_stats = []
        cleaned_counts = []
        runtimes = []
        
        for i in range(RUNS_PER_ALGO):
            print(f"Generating map pair {i+1:02d}/{RUNS_PER_ALGO}...")
            
            # Generate original map
            start_time = time.perf_counter()
            original_grid = algo_tower_path()
            generation_time = time.perf_counter() - start_time
            
            # Optimize the map
            start_time = time.perf_counter()
            optimized_grid, cleaned = optimize_tower_path(original_grid, strategy)
            optimization_time = time.perf_counter() - start_time
            
            total_time = generation_time + optimization_time
            runtimes.append(total_time)
            
            # Calculate statistics
            orig_paths = path_tiles(original_grid)
            orig_branches = branch_points(original_grid)
            opt_paths = path_tiles(optimized_grid)
            opt_branches = branch_points(optimized_grid)
            
            original_stats.append({'paths': orig_paths, 'branches': orig_branches})
            optimized_stats.append({'paths': opt_paths, 'branches': opt_branches})
            cleaned_counts.append(cleaned)
            
            # Save both maps
            original_name = f"map_{i+1:02d}_{strategy}_original.png"
            optimized_name = f"map_{i+1:02d}_{strategy}_optimized.png"
            
            original_path = os.path.join(BATCH_DIR, original_name)
            optimized_path = os.path.join(BATCH_DIR, optimized_name)
            
            save_grid_image_tiles(original_grid, original_path)
            save_grid_image_tiles(optimized_grid, optimized_path)
            
            print(f"  Original: {orig_paths} paths, {orig_branches} branches")
            print(f"  Optimized: {opt_paths} paths, {opt_branches} branches, {cleaned} cleaned")
            print()
        
        # Calculate statistics for this strategy
        avg_orig_paths = np.mean([s['paths'] for s in original_stats])
        avg_orig_branches = np.mean([s['branches'] for s in original_stats])
        avg_opt_paths = np.mean([s['paths'] for s in optimized_stats])
        avg_opt_branches = np.mean([s['branches'] for s in optimized_stats])
        avg_cleaned = np.mean(cleaned_counts)
        avg_runtime = np.mean(runtimes) * 1000
        
        # Create results DataFrame
        results = [
            {
                "Strategy": strategy.title(),
                "Algorithm": "Original",
                "Avg Time (ms)": round(avg_runtime / 2, 3),
                "Avg Path Tiles": round(avg_orig_paths, 1),
                "Avg Branch Points": round(avg_orig_branches, 1),
                "Avg Cleaned Tiles": 0.0
            },
            {
                "Strategy": strategy.title(),
                "Algorithm": "Optimized",
                "Avg Time (ms)": round(avg_runtime, 3),
                "Avg Path Tiles": round(avg_opt_paths, 1),
                "Avg Branch Points": round(avg_opt_branches, 1),
                "Avg Cleaned Tiles": round(avg_cleaned, 1)
            }
        ]
        
        df = pd.DataFrame(results)
        print(f"=== {strategy.upper()} Strategy Results ===")
        print(df.to_string(index=False))
        print()
        
        # Save CSV results
        csv_path = os.path.join(OUT_DIR, f"tower_path_optimization_{strategy}_results.csv")
        df.to_csv(csv_path, index=False)
        
        # Generate charts for this strategy
        generate_charts(df, original_stats, optimized_stats, cleaned_counts, strategy)
    
    print(f"\nAll map pairs saved to: {BATCH_DIR}")
    print(f"Charts saved to: {FIGURES_DIR}")

def generate_charts(df, original_stats, optimized_stats, cleaned_counts, strategy):
    """Generate comparison charts for a specific strategy"""
    
    # Chart 1: Path tiles comparison
    plt.figure(figsize=(8, 5))
    algorithms = df["Algorithm"]
    path_counts = df["Avg Path Tiles"]
    bars = plt.bar(algorithms, path_counts, color=["lightgreen", "orange"])
    plt.ylabel("Average Path Tiles")
    plt.title(f"Path Tiles Count Comparison ({strategy.title()} Strategy)")
    for bar, val in zip(bars, path_counts):
        plt.text(bar.get_x()+bar.get_width()/2, val+0.5, f"{val:.1f}",
                 ha="center", va="bottom", fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, f"path_tiles_comparison_{strategy}.png"), dpi=300)
    plt.close()
    
    # Chart 2: Distribution of cleaned tiles
    plt.figure(figsize=(8, 5))
    if max(cleaned_counts) > 0:
        plt.hist(cleaned_counts, bins=10, alpha=0.7, color="purple", edgecolor="black")
        plt.axvline(np.mean(cleaned_counts), color="red", linestyle="--", 
                    label=f"Mean: {np.mean(cleaned_counts):.1f}")
        plt.legend()
    else:
        plt.text(0.5, 0.5, "No tiles were cleaned", ha="center", va="center", transform=plt.gca().transAxes)
    plt.xlabel("Number of Cleaned (Useless) Tiles")
    plt.ylabel("Frequency")
    plt.title(f"Distribution of Cleaned Tiles ({strategy.title()} Strategy)")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, f"cleaned_tiles_distribution_{strategy}.png"), dpi=300)
    plt.close()

if __name__ == "__main__":
    run_experiment() 