import pygame
from settings import *
from bullet import Bullet

class Tower(pygame.sprite.Sprite):
    RANGE = 120

    def __init__(self, gx, gy, props):
        super().__init__()
        self.damage = props['damage']
        self.rof    = props['rof']
        size = GRID_SIZE-6

        self.image = pygame.Surface((size,size))
        self.image.fill(props['color'])
        px, py = grid_to_px(gx, gy)
        self.rect = self.image.get_rect(topleft=(px+3, py+3))
        self.cool = 0.0

    def update(self, dt, enemies, bullets):
        self.cool -= dt
        if self.cool > 0 or not enemies:
            return
        cx, cy = self.rect.center
        nearest = min(enemies,
                      key=lambda e:(cx-e.rect.centerx)**2+(cy-e.rect.centery)**2)
        if (cx-nearest.rect.centerx)**2 + (cy-nearest.rect.centery)**2 <= self.RANGE**2:
            bullets.add(Bullet(self.rect.center, nearest, self.damage))
            self.cool = self.rof
