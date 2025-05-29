import pygame
from settings import *
from pathfinding import a_star

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
            self.path = a_star(path_or_start, end)
            if not self.path:
                raise ValueError("No path found!")
        
        self.step = 0
        self.path_index = 0  # Compatibility with new version
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
        
        # Enemy size
        self.size = 32  # Fixed size for simplicity
        
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()

        # Set initial position
        gx, gy = self.path[0]
        px, py = grid_to_px(gx, gy)
        self.rect.center = (px + GRID_SIZE//2, py + GRID_SIZE//2)

    def _tile_center(self, gx, gy):
        """Get the center point of a grid tile"""
        px, py = grid_to_px(gx, gy)
        return pygame.Vector2(px + GRID_SIZE//2, py + GRID_SIZE//2)

    def hit(self, dmg):
        self.health -= dmg
        self.hp = self.health  # Sync with new version attribute
        self.flash_time = 0.1
        self.hit_flash = 0.1  # Sync with new version attribute
        if self.health <= 0:
            self.is_dead = True
            self.kill()

    def update(self, dt):
        if self.step < len(self.path):
            gx, gy = self.path[self.step]
            target = self._tile_center(gx, gy)
            pos = pygame.Vector2(self.rect.center)
            diff = target - pos
            dist = diff.length()
            
            # Movement speed
            mv = self.speed * dt
                
            if dist <= mv:
                self.rect.center = (target.x, target.y)
                self.step += 1
                self.path_index = self.step  # Sync with new version attribute
            else:
                diff.scale_to_length(mv)
                self.rect.center = (pos.x + diff.x, pos.y + diff.y)
        else:
            self.reached_end = True

        if self.flash_time > 0:
            self.flash_time = max(0, self.flash_time - dt)
        if self.hit_flash > 0:
            self.hit_flash = max(0, self.hit_flash - dt)
    
    def draw(self, surf):
        """Draw the enemy with compatibility for new version"""
        surf.blit(self.image, self.rect)
        
        # Draw health bar
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
