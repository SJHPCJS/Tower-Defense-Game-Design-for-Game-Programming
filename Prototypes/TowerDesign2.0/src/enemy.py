import pygame
from settings import *
from pathfinding import a_star
from grid import GRID_MAP

class Enemy(pygame.sprite.Sprite):
    def __init__(self, path_or_start, end=None, enemy_type='normal'):
        super().__init__()
        
        # Support two initialization methods:
        # 1. Enemy(path) - New method, directly pass the path
        # 2. Enemy(start, end) - Old method, pass start and end points
        if end is None:
            if isinstance(path_or_start, list) and len(path_or_start) > 0:
                self.path = path_or_start
            else:
                raise ValueError("Invalid path provided!")
        else:
            # Calculate path using current grid for each enemy individually
            # This ensures random path selection when multiple paths exist
            self.path = a_star(path_or_start, end, GRID_MAP)
            if not self.path:
                raise ValueError("No path found!")
        
        self.step = 0
        self.path_index = 0  # Compatibility with new version
        self.progress = 0.0  # Progress between current and next waypoint (0.0 to 1.0)
        self.speed = 50
        self.max_health = 100
        self.health = self.max_health
        self.hp = self.max_health  # Compatibility with new version
        self.max_hp = self.max_health  # Compatibility with new version
        self.flash_time = 0.0
        self.hit_flash = 0.0  # Compatibility with new version
        self.reached_end = False
        self.damage_to_base = 1
        self.is_dead = False  # Used for kill reward determination
        self.reward_given = False  # Ensure kill reward is only given once
        
        # Enemy size (base size, will be scaled)
        self.base_size = 32
        self.size = self.base_size
        
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()

        # Set initial position (will be updated properly in update method)
        self._update_position_and_size()
        
        # Set initial position at the first path point
        if self.path:
            gx, gy = self.path[0]
            initial_pos = self._tile_center(gx, gy)
            self.rect.center = (initial_pos.x, initial_pos.y)

    def _update_position_and_size(self):
        """Update enemy size and position based on current screen scaling"""
        screen = pygame.display.get_surface()
        if screen:
            screen_w, screen_h = screen.get_size()
            scaled_grid_size = get_scaled_grid_size(screen_w, screen_h)
            # Scale enemy size proportionally
            scale_factor = scaled_grid_size / GRID_SIZE
            self.size = max(int(self.base_size * scale_factor), 8)  # Minimum size 8
            
            # Recreate image with new size
            self.image = pygame.Surface((self.size, self.size))
            self.image.fill(BLUE)
            
            # Recalculate position based on current path progress
            if self.step < len(self.path):
                if self.step + 1 < len(self.path):
                    # Interpolate between current and next waypoint
                    current_gx, current_gy = self.path[self.step]
                    next_gx, next_gy = self.path[self.step + 1]
                    
                    current_pos = self._tile_center(current_gx, current_gy)
                    next_pos = self._tile_center(next_gx, next_gy)
                    
                    # Interpolate position based on progress
                    interp_x = current_pos.x + (next_pos.x - current_pos.x) * self.progress
                    interp_y = current_pos.y + (next_pos.y - current_pos.y) * self.progress
                    
                    self.rect = self.image.get_rect()
                    self.rect.center = (interp_x, interp_y)
                else:
                    # At the last waypoint
                    gx, gy = self.path[self.step]
                    pos = self._tile_center(gx, gy)
                    self.rect = self.image.get_rect()
                    self.rect.center = (pos.x, pos.y)
            else:
                # Beyond the path
                self.rect = self.image.get_rect()

    def _tile_center(self, gx, gy):
        """Get the center point of a grid tile with proper scaling"""
        screen = pygame.display.get_surface()
        if screen:
            screen_w, screen_h = screen.get_size()
            px, py = grid_to_px(gx, gy, screen_w, screen_h)
            scaled_grid_size = get_scaled_grid_size(screen_w, screen_h)
            return pygame.Vector2(px + scaled_grid_size//2, py + scaled_grid_size//2)
        else:
            # Fallback to default scaling
            px, py = grid_to_px(gx, gy)
            return pygame.Vector2(px + GRID_SIZE//2, py + GRID_SIZE//2)

    def hit(self, dmg):
        self.health -= dmg
        self.hp = self.health  # Sync with new version attribute
        self.flash_time = 0.1
        self.hit_flash = 0.1  # Sync with new version attribute
        if self.health <= 0 and not self.reward_given:
            self.is_dead = True
            self.reward_given = True  # Mark reward as given
            # Trigger kill reward callback if set
            if hasattr(self, 'kill_callback') and self.kill_callback:
                self.kill_callback(self)
            self.kill()

    def update(self, dt):
        # Update size and position based on current screen scaling
        self._update_position_and_size()
        
        if self.step < len(self.path):
            # Calculate movement for this frame
            if self.step + 1 < len(self.path):
                current_gx, current_gy = self.path[self.step]
                next_gx, next_gy = self.path[self.step + 1]
                
                current_pos = self._tile_center(current_gx, current_gy)
                next_pos = self._tile_center(next_gx, next_gy)
                
                # Calculate distance between waypoints
                segment_distance = (next_pos - current_pos).length()
                
                if segment_distance > 0:
                    # Movement speed (scale with screen size for consistent movement)
                    screen = pygame.display.get_surface()
                    if screen:
                        screen_w, screen_h = screen.get_size()
                        scale_factor = get_scaled_grid_size(screen_w, screen_h) / GRID_SIZE
                        scaled_speed = self.speed * scale_factor
                    else:
                        scaled_speed = self.speed
                    
                    # Calculate progress increment based on speed and segment distance
                    progress_increment = (scaled_speed * dt) / segment_distance
                    self.progress += progress_increment
                    
                    if self.progress >= 1.0:
                        # Reached next waypoint
                        self.step += 1
                        self.path_index = self.step  # Sync with new version attribute
                        self.progress = 0.0
                else:
                    # Zero distance, move to next step immediately
                    self.step += 1
                    self.path_index = self.step
                    self.progress = 0.0
            else:
                # At the last waypoint
                self.progress = 1.0
        else:
            self.reached_end = True

        if self.flash_time > 0:
            self.flash_time = max(0, self.flash_time - dt)
        if self.hit_flash > 0:
            self.hit_flash = max(0, self.hit_flash - dt)
    
    def draw(self, surf):
        """Draw the enemy with compatibility for new version"""
        surf.blit(self.image, self.rect)
        
        # Draw health bar (scale with enemy size)
        hb_w = self.size
        x, y = self.rect.x, self.rect.y - 6
        back = pygame.Rect(x, y, hb_w, 4)
        front = pygame.Rect(x, y, int(hb_w * self.health / self.max_health), 4)
        pygame.draw.rect(surf, RED, back)
        pygame.draw.rect(surf, GREEN, front)
        
        # Flash effect
        if self.flash_time > 0 or self.hit_flash > 0:
            overlay = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 120))
            surf.blit(overlay, self.rect.topleft)

class EnemyWithGrid(Enemy):
    """Enemy class that accepts a grid parameter for path calculation"""
    def __init__(self, start, end, grid, enemy_type='normal'):
        # Store grid for pathfinding
        self.grid = grid
        
        # Calculate path using the provided grid
        path = a_star(start, end, grid)
        if not path:
            raise ValueError("No path found!")
        
        # Initialize using the base Enemy class with the calculated path
        super().__init__(path, None, enemy_type)

    def calculate_path(self, start, end):
        """Calculate path using the provided grid"""
        return a_star(start, end, self.grid)
