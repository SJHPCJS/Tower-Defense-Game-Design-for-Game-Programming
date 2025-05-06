import pygame
from settings import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_pos, target, damage):
        super().__init__()
        self.image = pygame.Surface((6,6), pygame.SRCALPHA)
        pygame.draw.circle(self.image, BLACK, (3,3), 3)
        self.rect   = self.image.get_rect(center=start_pos)
        self.pos    = pygame.Vector2(self.rect.topleft)
        self.target = target
        self.speed  = 300
        self.damage = damage
        vec = pygame.Vector2(target.rect.center) - pygame.Vector2(start_pos)
        self.dir = vec.normalize() if vec.length() else pygame.Vector2()

    def update(self, dt):
        self.pos += self.dir * self.speed * dt
        self.rect.topleft = self.pos
        if self.rect.colliderect(self.target.rect):
            self.target.hit(self.damage)
            self.kill()
