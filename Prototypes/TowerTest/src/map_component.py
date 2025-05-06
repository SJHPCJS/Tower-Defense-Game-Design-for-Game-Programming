import pygame
from pathlib import Path
from settings import *
from grid import GRID_MAP

class MapComponent:
    def __init__(self):
        self.surface = pygame.Surface((GRID_W*GRID_SIZE, GRID_H*GRID_SIZE))
        self._load_tiles()
        self._build()

    def _load_tiles(self):
        assets = Path(__file__).parent.parent / "assets" / "tiles"
        grass_img = pygame.image.load(assets / "grass.png")
        self.grass = pygame.transform.scale(grass_img, (GRID_SIZE, GRID_SIZE))
        self.path  = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.path.fill(WHITE)

    def _build(self):
        for y, row in enumerate(GRID_MAP):
            for x, cell in enumerate(row):
                img = self.grass if cell else self.path
                px, py = x*GRID_SIZE, y*GRID_SIZE
                self.surface.blit(img, (px, py))
                pygame.draw.rect(self.surface, BLACK,
                                 (px, py, GRID_SIZE, GRID_SIZE), 1)

    def draw(self, dest):
        dest.blit(self.surface, (0, UI_HEIGHT))
