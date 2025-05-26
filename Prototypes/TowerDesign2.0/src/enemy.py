import pygame
from settings import *
from pathfinding import a_star

class Enemy(pygame.sprite.Sprite):
    def __init__(self, start, end):
        super().__init__()
        self.path = a_star(start, end)
        if not self.path:
            raise ValueError("No path!")
        self.step = 0
        self.speed = 60
        self.max_health = 100
        self.health     = self.max_health
        self.flash_time = 0.0
        self.reached_end = False
        self.damage_to_base = 1

        self.image = pygame.Surface((GRID_SIZE-8, GRID_SIZE-8))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()

        gx, gy = self.path[0]
        px, py = grid_to_px(gx, gy)
        self.rect.topleft = (px+4, py+4)

    def _tile_center(self, gx, gy):
        px, py = grid_to_px(gx, gy)
        return pygame.Vector2(px+4, py+4)

    def hit(self, dmg):
        self.health -= dmg
        self.flash_time = 0.1
        if self.health <= 0:
            self.kill()

    def update(self, dt):
        if self.step < len(self.path):
            gx, gy = self.path[self.step]
            target = self._tile_center(gx, gy)
            pos    = pygame.Vector2(self.rect.topleft)
            diff   = target - pos
            dist   = diff.length()
            mv     = self.speed * dt
            if dist <= mv:
                self.rect.topleft = (target.x, target.y)
                self.step += 1
            else:
                diff.scale_to_length(mv)
                self.rect.move_ip(diff)
        else:
            self.reached_end = True

        if self.flash_time > 0:
            self.flash_time = max(0, self.flash_time - dt)
