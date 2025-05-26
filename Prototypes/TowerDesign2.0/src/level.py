import pygame
from settings import *
from enemy import Enemy

class Level:
    def __init__(self):
        self.enemies     = pygame.sprite.Group()
        self.timer       = 0.0
        self.delay       = 2.0
        self.start       = (0,0)
        self.end         = (GRID_W-2, GRID_H-2)
        self.base_hp     = 10

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.delay:
            self.timer -= self.delay
            self.enemies.add(Enemy(self.start, self.end))

        self.enemies.update(dt)
        for e in list(self.enemies):
            if e.reached_end:
                self.base_hp -= e.damage_to_base
                e.kill()

    def draw(self, surf):
        for e in self.enemies:
            surf.blit(e.image, e.rect)
            hb_w = GRID_SIZE-8
            x, y = e.rect.x, e.rect.y-6
            back  = pygame.Rect(x,y,hb_w,4)
            front = pygame.Rect(x,y,int(hb_w*e.health/e.max_health),4)
            pygame.draw.rect(surf, RED, back)
            pygame.draw.rect(surf, GREEN, front)
            if e.flash_time>0:
                overlay = pygame.Surface((e.rect.w,e.rect.h), pygame.SRCALPHA)
                overlay.fill((255,255,255,120))
                surf.blit(overlay, e.rect.topleft)
