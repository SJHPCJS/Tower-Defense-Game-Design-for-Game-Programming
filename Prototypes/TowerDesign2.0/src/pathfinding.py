import heapq
import random
from settings import GRID_W, GRID_H
from grid import walkable

class Node:
    __slots__ = ("x","y","g","h","f","parent")
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.g = float("inf")
        self.h = 0
        self.f = float("inf")
        self.parent = None
    def __lt__(self, other):
        return self.f < other.f

def heuristic(a, b):
    # Manhattan distance
    return abs(a.x - b[0]) + abs(a.y - b[1])

def a_star(start_xy, end_xy):
    # initialize nodes
    nodes = [[Node(x, y) for y in range(GRID_H)] for x in range(GRID_W)]
    sx, sy = start_xy
    ex, ey = end_xy

    start = nodes[sx][sy]
    start.g = 0
    start.h = heuristic(start, end_xy)
    start.f = start.h

    open_heap = []
    heapq.heappush(open_heap, start)
    closed = set()

    while open_heap:
        current = heapq.heappop(open_heap)
        # reached goal
        if (current.x, current.y) == end_xy:
            path = []
            while current:
                path.append((current.x, current.y))
                current = current.parent
            return path[::-1]

        closed.add((current.x, current.y))

        # shuffle neighbor order so ties go random
        neighbors = [(1,0),(-1,0),(0,1),(0,-1)]
        random.shuffle(neighbors)

        for dx, dy in neighbors:
            nx, ny = current.x + dx, current.y + dy
            if not walkable(nx, ny) or (nx, ny) in closed:
                continue

            neighbor = nodes[nx][ny]
            tentative_g = current.g + 1
            if tentative_g < neighbor.g:
                neighbor.g = tentative_g
                neighbor.h = heuristic(neighbor, end_xy)
                neighbor.f = neighbor.g + neighbor.h
                neighbor.parent = current
                # push even if already in heap; ties broken by random neighbor order
                heapq.heappush(open_heap, neighbor)

    # no path found
    return []
