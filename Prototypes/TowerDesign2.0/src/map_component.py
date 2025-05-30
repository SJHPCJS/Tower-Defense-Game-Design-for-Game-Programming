import pygame
from pathlib import Path
from settings import *
from grid import GRID_MAP

class MapComponent:
    def __init__(self, grid=None, spawn=(0,0), home=(GRID_W-2, GRID_H-2)):
        self.grid  = grid if grid is not None else GRID_MAP
        self.spawn = spawn
        self.home  = home
        self._load_imgs()

    def _load_imgs(self):
        assets = Path(__file__).parent.parent / 'assets' / 'tiles'
        self.base_imgs = {
            0: pygame.image.load(assets/'path.png'),
            1: pygame.image.load(assets/'grass.png'),
        }

    def set_spawn_and_home(self, spawn, home):
        """Set the spawn and home positions"""
        self.spawn = spawn
        self.home = home

    def _draw(self, screen_w, screen_h):
        # Don't override self.grid - use the one set during initialization
        # self.grid = GRID_MAP  # Remove this line!
        
        # Calculate scaling
        scaled_grid_size = get_scaled_grid_size(screen_w, screen_h)
        
        # Create scaled images
        scaled_imgs = {}
        for key, img in self.base_imgs.items():
            scaled_imgs[key] = pygame.transform.scale(img, (scaled_grid_size, scaled_grid_size))
        
        # Calculate the position and size of the game area
        game_area_height = screen_h - UI_HEIGHT
        scale_x = screen_w / (GRID_W * GRID_SIZE)
        scale_y = game_area_height / (GRID_H * GRID_SIZE)
        scale = min(scale_x, scale_y)
        
        scaled_width = GRID_W * GRID_SIZE * scale
        scaled_height = GRID_H * GRID_SIZE * scale
        offset_x = (screen_w - scaled_width) // 2
        offset_y = UI_HEIGHT + (game_area_height - scaled_height) // 2
        
        # Create game area surface
        game_surface = pygame.Surface((int(scaled_width), int(scaled_height)))
        
        # Draw tiles
        for y, row in enumerate(self.grid):
            for x, t in enumerate(row):
                pos_x = x * scaled_grid_size
                pos_y = y * scaled_grid_size
                game_surface.blit(scaled_imgs[t], (pos_x, pos_y))
        
        # Draw markers
        sx, sy = self.spawn
        hx, hy = self.home
        
        # Start marker (green)
        start_rect = pygame.Rect(sx * scaled_grid_size, sy * scaled_grid_size, scaled_grid_size, scaled_grid_size)
        pygame.draw.rect(game_surface, GREEN, start_rect)
        pygame.draw.rect(game_surface, BLACK, start_rect, 2)
        
        # End marker (red)
        end_rect = pygame.Rect(hx * scaled_grid_size, hy * scaled_grid_size, scaled_grid_size, scaled_grid_size)
        pygame.draw.rect(game_surface, RED, end_rect)
        pygame.draw.rect(game_surface, BLACK, end_rect, 2)
        
        return game_surface, (int(offset_x), int(offset_y))

    def set_grid(self, new_grid):
        self.grid = new_grid

    def draw(self, target):
        screen_w, screen_h = target.get_size()
        game_surface, offset = self._draw(screen_w, screen_h)
        target.blit(game_surface, offset)
