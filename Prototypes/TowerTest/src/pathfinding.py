import heapq
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
    def __lt__(self, o): return self.f < o.f

def heuristic(a, b):
    return abs(a.x - b[0]) + abs(a.y - b[1])

def a_star(start_xy, end_xy):
    nodes = [[Node(x, y) for y in range(GRID_H)] for x in range(GRID_W)]
    sx, sy = start_xy; ex, ey = end_xy
    start = nodes[sx][sy]
    start.g = 0
    start.h = heuristic(start, end_xy)
    start.f = start.h

    open_heap = [start]
    closed = set()

    while open_heap:
        current = heapq.heappop(open_heap)
        if (current.x, current.y) == end_xy:
            path = []
            while current:
                path.append((current.x, current.y))
                current = current.parent
            return path[::-1]
        closed.add((current.x, current.y))
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = current.x+dx, current.y+dy
            if not walkable(nx, ny) or (nx, ny) in closed:
                continue
            neigh = nodes[nx][ny]
            tg = current.g + 1
            if tg < neigh.g:
                neigh.g = tg
                neigh.h = heuristic(neigh, end_xy)
                neigh.f = tg + neigh.h
                neigh.parent = current
                heapq.heappush(open_heap, neigh)
    return []
