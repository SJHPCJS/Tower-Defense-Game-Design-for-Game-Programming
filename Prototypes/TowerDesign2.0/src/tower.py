import pygame
from settings import *
from bullet import Bullet

class Tower(pygame.sprite.Sprite):
    RANGE = 120

    def __init__(self, gx, gy, props):
        super().__init__()
        self.gx = gx  # Grid coordinates
        self.gy = gy
        self.tower_type = props  # Store tower type information
        self.damage = props['damage']
        self.rof    = props['rof']
        self.color = props['color']
        
        # Initial image (will be scaled in the draw method based on screen size)
        self.base_size = GRID_SIZE - 6
        self.image = pygame.Surface((self.base_size, self.base_size))
        self.image.fill(self.color)
        
        # Initial position (will be updated in update_position method)
        px, py = grid_to_px(gx, gy)
        self.rect = self.image.get_rect(topleft=(px+3, py+3))
        self.cool = 0.0

    def update_position(self, screen_width, screen_height):
        """Update tower position and size based on screen dimensions"""
        scaled_grid_size = get_scaled_grid_size(screen_width, screen_height)
        size = max(scaled_grid_size - 6, 10)  # Minimum size is 10
        
        # Recreate image
        self.image = pygame.Surface((size, size))
        self.image.fill(self.color)
        
        # Update position
        px, py = grid_to_px(self.gx, self.gy, screen_width, screen_height)
        offset = 3 * (scaled_grid_size / GRID_SIZE)  # Scale offset proportionally
        self.rect = self.image.get_rect(topleft=(px + offset, py + offset))

    def update(self, dt, enemies, bullets):
        self.cool -= dt
        if self.cool > 0 or not enemies:
            return
        cx, cy = self.rect.center
        
        # Calculate scaled range
        screen = pygame.display.get_surface()
        if screen:
            screen_w, screen_h = screen.get_size()
            scale = get_scaled_grid_size(screen_w, screen_h) / GRID_SIZE
            scaled_range = self.RANGE * scale
        else:
            scaled_range = self.RANGE
        
        nearest = min(enemies,
                      key=lambda e:(cx-e.rect.centerx)**2+(cy-e.rect.centery)**2)
        if (cx-nearest.rect.centerx)**2 + (cy-nearest.rect.centery)**2 <= scaled_range**2:
            bullets.add(Bullet(self.rect.center, nearest, self.damage))
            self.cool = self.rof

    def draw(self, screen):
        """Custom draw method to ensure tower is at the correct position and size"""
        screen_w, screen_h = screen.get_size()
        self.update_position(screen_w, screen_h)
        screen.blit(self.image, self.rect)
