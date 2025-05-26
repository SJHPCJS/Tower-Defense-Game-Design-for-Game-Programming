import pygame


GRID_SIZE      = 40
GRID_W, GRID_H = 20, 15

UI_HEIGHT   = 80
SCREEN_W    = GRID_W * GRID_SIZE
SCREEN_H    = GRID_H * GRID_SIZE + UI_HEIGHT
FPS         = 60

# colours
WHITE     = (255, 255, 255)
BLACK     = (0,   0,   0)
GREEN     = (0, 255,   0)
RED       = (255, 0,   0)
BLUE      = (0,   0, 255)
BG_COLOUR = (173, 216, 230)
BG_COLOR = BG_COLOUR  # Alias for compatibility
YELLOW = (255, 210,   0)
PINK   = (255,  90, 140)

# Menu colors
FOREST_GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
LIGHT_GREEN = (144, 238, 144)
BROWN = (139, 69, 19)
CREAM = (245, 245, 220)


# tower definitions
TOWER_TYPES = [
    {'name':'Fast',     'damage':10, 'rof':0.3, 'color':(200,200,255)},
    {'name':'Strong',   'damage':30, 'rof':1.2, 'color':(255,200,200)},
    {'name':'Balanced', 'damage':20, 'rof':0.6, 'color':(200,255,200)},
]


def grid_to_px(gx: int, gy: int) -> tuple[int,int]:
    return gx * GRID_SIZE, UI_HEIGHT + gy * GRID_SIZE


pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
clock  = pygame.time.Clock()
pygame.display.set_caption("Tower Defense")
FONT = pygame.font.SysFont(None, 24)
