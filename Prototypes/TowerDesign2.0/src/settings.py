import pygame


GRID_SIZE      = 40
GRID_W, GRID_H = 20, 15

# Increase UI height for a richer interface
UI_HEIGHT   = 120
SCREEN_W    = GRID_W * GRID_SIZE
SCREEN_H    = GRID_H * GRID_SIZE + UI_HEIGHT
FPS         = 60

# Minimum window size
MIN_SCREEN_W = 800
MIN_SCREEN_H = 600

# Get the maximum screen size for default
pygame.init()
info = pygame.display.Info()
MAX_SCREEN_W = info.current_w
MAX_SCREEN_H = info.current_h

# Default window size - use maximized screen size
DEFAULT_SCREEN_W = MAX_SCREEN_W
DEFAULT_SCREEN_H = MAX_SCREEN_H

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
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)

# Menu colors
FOREST_GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
LIGHT_GREEN = (144, 238, 144)
BROWN = (139, 69, 19)
CREAM = (245, 245, 220)

# UI Colors
UI_DARK_BG = (30, 30, 30)
UI_MID_BG = (45, 45, 45)
UI_LIGHT_BG = (60, 60, 60)
UI_ACCENT = (70, 130, 180)
UI_SUCCESS = (40, 180, 99)
UI_WARNING = (255, 193, 7)
UI_DANGER = (220, 53, 69)

# Game settings
STARTING_MONEY = 200
TOWER_COSTS = {
    'Emberwing': 45,
    'Volt Cow': 45,
    'Banana Blaster': 40,
    'Wood Sage': 20,
    'Chrono Cactus': 45
}
WAVE_REWARD = 50
KILL_REWARD = 0

# Enemy colors
ENEMY_COLORS = {
    'normal': BLUE,
    'fast': GREEN,
    'tank': RED
}

# Button colors
BUTTON_COLORS = {
    'normal': FOREST_GREEN,
    'hover': LIGHT_GREEN,
    'pressed': DARK_GREEN
}

# tower definitions - Only the 5 new towers
TOWER_TYPES = [
    {'name':'Emberwing', 'damage':45, 'rof':0.9, 'color':(255,140,100), 'description': 'Fire-based ranged attacker'},
    {'name':'Volt Cow', 'damage':65, 'rof':1.2, 'color':(255,255,100), 'description': 'Electric-powered heavy hitter'},
    {'name':'Banana Blaster', 'damage':25, 'rof':0.3, 'color':(255,255,150), 'description': 'Fast banana projectiles'},
    {'name':'Wood Sage', 'damage':35, 'rof':0.8, 'color':(139,195,74), 'description': 'Nature-powered defender'},
    {'name':'Chrono Cactus', 'damage':0, 'rof':0, 'color':(76,175,80), 'description': 'Slows nearby enemies by 25%', 'slow_range': 5, 'slow_effect': 0.25},
]


def grid_to_px(gx: int, gy: int, screen_width=None, screen_height=None) -> tuple[int,int]:
    """Convert grid coordinates to pixel coordinates, with optional screen scaling"""
    if screen_width is None:
        screen_width = DEFAULT_SCREEN_W
    if screen_height is None:
        screen_height = DEFAULT_SCREEN_H
    
    # Calculate scaling factors
    game_area_height = screen_height - UI_HEIGHT
    scale_x = screen_width / (GRID_W * GRID_SIZE)
    scale_y = game_area_height / (GRID_H * GRID_SIZE)
    scale = min(scale_x, scale_y)  # Maintain aspect ratio
    
    # Calculate offset to center the game area
    scaled_width = GRID_W * GRID_SIZE * scale
    scaled_height = GRID_H * GRID_SIZE * scale
    offset_x = (screen_width - scaled_width) // 2
    offset_y = UI_HEIGHT + (game_area_height - scaled_height) // 2
    
    return int(gx * GRID_SIZE * scale + offset_x), int(gy * GRID_SIZE * scale + offset_y)


def px_to_grid(px: int, py: int, screen_width=None, screen_height=None) -> tuple[int,int]:
    """Convert pixel coordinates to grid coordinates"""
    if screen_width is None:
        screen_width = DEFAULT_SCREEN_W
    if screen_height is None:
        screen_height = DEFAULT_SCREEN_H
    
    game_area_height = screen_height - UI_HEIGHT
    scale_x = screen_width / (GRID_W * GRID_SIZE)
    scale_y = game_area_height / (GRID_H * GRID_SIZE)
    scale = min(scale_x, scale_y)
    
    scaled_width = GRID_W * GRID_SIZE * scale
    scaled_height = GRID_H * GRID_SIZE * scale
    offset_x = (screen_width - scaled_width) // 2
    offset_y = UI_HEIGHT + (game_area_height - scaled_height) // 2
    
    # Adjust for UI offset and scaling
    adjusted_x = (px - offset_x) / scale
    adjusted_y = (py - offset_y) / scale
    
    gx = int(adjusted_x // GRID_SIZE)
    gy = int(adjusted_y // GRID_SIZE)
    
    return gx, gy


def get_scaled_grid_size(screen_width=None, screen_height=None) -> int:
    """Get the scaled grid size for current screen dimensions"""
    if screen_width is None:
        screen_width = DEFAULT_SCREEN_W
    if screen_height is None:
        screen_height = DEFAULT_SCREEN_H
    
    game_area_height = screen_height - UI_HEIGHT
    scale_x = screen_width / (GRID_W * GRID_SIZE)
    scale_y = game_area_height / (GRID_H * GRID_SIZE)
    scale = min(scale_x, scale_y)
    
    return int(GRID_SIZE * scale)


pygame.init()
# Create a maximized resizable window
screen = pygame.display.set_mode((DEFAULT_SCREEN_W, DEFAULT_SCREEN_H), 
                                pygame.RESIZABLE | pygame.DOUBLEBUF)
# Maximize the window on startup (optional fallback)
pygame.display.set_mode((DEFAULT_SCREEN_W, DEFAULT_SCREEN_H), 
                        pygame.RESIZABLE | pygame.DOUBLEBUF)
clock  = pygame.time.Clock()
pygame.display.set_caption("Forest Guard - Tower Defense")
FONT = pygame.font.SysFont(None, 24)

# Fonts dictionary for different UI elements
FONTS = {
    'title': pygame.font.SysFont('Arial', 72, bold=True),
    'subtitle': pygame.font.SysFont('Arial', 24),
    'button': pygame.font.SysFont('Arial', 24, bold=True),
    'hud': pygame.font.SysFont('Arial', 20),
    'small': pygame.font.SysFont('Arial', 16),
    'tiny': pygame.font.SysFont('Arial', 12)
}
