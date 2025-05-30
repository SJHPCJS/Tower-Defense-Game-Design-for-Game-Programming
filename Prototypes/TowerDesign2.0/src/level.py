import pygame
from settings import *
from enemy import Enemy, EnemyWithGrid
from pathfinding import a_star
from grid import GRID_MAP

class Level:
    def __init__(self):
        self.enemies = pygame.sprite.Group()
        self.timer = 0.0
        self.delay = 2.0
        self.base_hp = 10
        self.name = "Default Level"
        self.grid = None
        
        # Initialize path
        self.recalculate_path()
    
    def recalculate_path(self):
        """Recalculate path, called when the level changes"""
        # Use level-specific grid data
        grid_to_use = self.grid if self.grid is not None else GRID_MAP
        
        # Automatically find start and end points
        self.start = self.find_start_point(grid_to_use)
        self.end = self.find_end_point(grid_to_use)
        
        print(f"Level: Start point {self.start}, End point {self.end}")  # Debug info
        
        # Calculate path
        self.path = a_star(self.start, self.end, grid_to_use)
        if not self.path:
            # If pathfinding fails, create a simple straight path
            self.path = [self.start, self.end]
            print(f"Level: Pathfinding failed, using simple path")
        else:
            print(f"Level: Pathfinding successful, path length {len(self.path)}")
    
    def find_start_point(self, grid):
        """Find start point (path tile) from the first row"""
        for x in range(GRID_W):
            if grid[0][x] == 0:  # 0 indicates path
                return (x, 0)
        
        # If no path in the first row, search from the left
        for y in range(GRID_H):
            if grid[y][0] == 0:
                return (0, y)
        
        # Default start point
        return (0, 0)
    
    def find_end_point(self, grid):
        """Find end point (path tile)"""
        # Find the path point farthest from the start in the grid
        start = self.find_start_point(grid)
        max_distance = -1
        best_end = None
        
        for y in range(GRID_H):
            for x in range(GRID_W):
                if grid[y][x] == 0:  # Is path
                    # Calculate Manhattan distance
                    distance = abs(x - start[0]) + abs(y - start[1])
                    if distance > max_distance:
                        max_distance = distance
                        best_end = (x, y)
        
        if best_end:
            return best_end
        
        # If no path point found, return start point
        return start

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.delay:
            self.timer -= self.delay
            # Create enemy with start and end points so each enemy calculates its own path
            # This restores random path selection for enemies
            if self.start and self.end:
                # Create enemy with grid context
                enemy = EnemyWithGrid(self.start, self.end, self.grid if self.grid is not None else GRID_MAP)
                self.enemies.add(enemy)

        self.enemies.update(dt)
        
        # Check if enemies have reached the end
        for e in list(self.enemies):
            # Check new version enemy's end reached logic
            if hasattr(e, 'path_index') and e.path_index >= len(e.path) - 1:
                self.base_hp -= 1
                e.kill()
            # Compatibility with old version enemy
            elif hasattr(e, 'reached_end') and e.reached_end:
                self.base_hp -= getattr(e, 'damage_to_base', 1)
                e.kill()

    def draw(self, surf):
        for e in self.enemies:
            # Use new version enemy's draw method
            if hasattr(e, 'draw'):
                e.draw(surf)
            else:
                # Compatibility with old version enemy's draw
                surf.blit(e.image, e.rect)
                
                # Draw health bar
                if hasattr(e, 'hp') and hasattr(e, 'max_hp'):
                    hb_w = getattr(e, 'size', GRID_SIZE-8)
                    x, y = e.rect.x, e.rect.y-6
                    back = pygame.Rect(x, y, hb_w, 4)
                    front = pygame.Rect(x, y, int(hb_w * e.hp / e.max_hp), 4)
                    pygame.draw.rect(surf, RED, back)
                    pygame.draw.rect(surf, GREEN, front)
                elif hasattr(e, 'health') and hasattr(e, 'max_health'):
                    hb_w = GRID_SIZE-8
                    x, y = e.rect.x, e.rect.y-6
                    back = pygame.Rect(x, y, hb_w, 4)
                    front = pygame.Rect(x, y, int(hb_w * e.health / e.max_health), 4)
                    pygame.draw.rect(surf, RED, back)
                    pygame.draw.rect(surf, GREEN, front)
                
                # Flash effect
                if hasattr(e, 'hit_flash') and e.hit_flash > 0:
                    overlay = pygame.Surface((e.rect.w, e.rect.h), pygame.SRCALPHA)
                    overlay.fill((255, 255, 255, 120))
                    surf.blit(overlay, e.rect.topleft)
                elif hasattr(e, 'flash_time') and e.flash_time > 0:
                    overlay = pygame.Surface((e.rect.w, e.rect.h), pygame.SRCALPHA)
                    overlay.fill((255, 255, 255, 120))
                    surf.blit(overlay, e.rect.topleft)
