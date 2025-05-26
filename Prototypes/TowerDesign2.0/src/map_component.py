import pygame
from pathlib import Path
from settings import *
from grid import GRID_MAP

class MapComponent:
    def __init__(self, grid=None, spawn=(0,0), home=(GRID_W-2, GRID_H-2)):
        self.grid  = grid if grid is not None else GRID_MAP
        self.spawn = spawn
        self.home  = home
        self.surface = pygame.Surface((GRID_W*GRID_SIZE, GRID_H*GRID_SIZE))
        self._load_imgs(); self._draw()

    def _load_imgs(self):
        assets = Path(__file__).parent.parent / 'assets' / 'tiles'
        self.img = {
            0: pygame.transform.scale(pygame.image.load(assets/'path.png'),
                                      (GRID_SIZE, GRID_SIZE)),
            1: pygame.transform.scale(pygame.image.load(assets/'grass.png'),
                                      (GRID_SIZE, GRID_SIZE)),
        }

    def _draw(self):
        # tiles
        for y,row in enumerate(self.grid):
            for x,t in enumerate(row):
                self.surface.blit(self.img[t], (x*GRID_SIZE, y*GRID_SIZE))
        # markers
        sx, sy = self.spawn
        hx, hy = self.home
        pygame.draw.rect(self.surface, YELLOW,
                         (sx*GRID_SIZE, sy*GRID_SIZE, GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(self.surface, PINK,
                         (hx*GRID_SIZE, hy*GRID_SIZE, GRID_SIZE, GRID_SIZE))

    def set_grid(self, new_grid):
        self.grid = new_grid
        self.surface.fill((0,0,0))
        self._draw()

    def draw(self, target):
        target.blit(self.surface, (0, UI_HEIGHT))
