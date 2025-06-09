import pygame
import random
from pathlib import Path
from settings import *
from grid import GRID_MAP

class StartSprite:
    """START sprite sheet animation class, supports 4 random state switches"""
    
    def __init__(self):
        self.load_sprite_sheet()
        self.current_state = 0  # current state index (0-3)
        self.state_timer = 0.0
        self.state_interval = 30.0  # switch state every 30 seconds
        
        # 4 state frame indices (2x2 sprite sheet)
        self.states = [0, 1, 2, 3]  # top-left, top-right, bottom-left, bottom-right
        
        # randomly select initial state
        self.current_state = random.randint(0, 3)
        
        print(f"START sprite initialized with state {self.current_state}")
    
    def load_sprite_sheet(self):
        """Load START sprite sheet and cut into frames"""
        try:
            assets_path = Path(__file__).parent.parent / 'assets' / 'sprite'
            sheet = pygame.image.load(assets_path / 'START.png').convert_alpha()
            
            # assume sprite sheet is 2x2 format, each frame same size
            sheet_w, sheet_h = sheet.get_size()
            frame_w = sheet_w // 2
            frame_h = sheet_h // 2
            
            # cut frames: [top-left, top-right, bottom-left, bottom-right]
            self.sprite_frames = []
            positions = [(0, 0), (frame_w, 0), (0, frame_h), (frame_w, frame_h)]
            
            for x, y in positions:
                rect = pygame.Rect(x, y, frame_w, frame_h)
                frame = sheet.subsurface(rect).copy()
                self.sprite_frames.append(frame)
                
            print(f"START sprite loaded: {len(self.sprite_frames)} frames, {frame_w}x{frame_h} each")
            
        except Exception as e:
            print(f"Failed to load START sprite: {e}")
            # create default squares as fallback
            self.sprite_frames = []
            for color in [(0, 255, 0), (0, 200, 255), (255, 0, 255), (255, 255, 0)]:
                surf = pygame.Surface((GRID_SIZE, GRID_SIZE))
                surf.fill(color)
                self.sprite_frames.append(surf)
    
    def update(self, dt):
        """Update state switching"""
        self.state_timer += dt
        
        if self.state_timer >= self.state_interval:
            # randomly select new state (ensure different from current state)
            available_states = [s for s in self.states if s != self.current_state]
            self.current_state = random.choice(available_states)
            self.state_timer = 0.0
            print(f"START state switched to: {self.current_state}")
    
    def get_current_sprite(self, size):
        """Get current frame sprite, scaled to specified size"""
        sprite = self.sprite_frames[self.current_state]
        
        if size != sprite.get_size():
            return pygame.transform.scale(sprite, size)
        return sprite

class HomeSprite:
    """HOME sprite sheet animation class, supports multiple states and mask effects"""
    
    def __init__(self):
        self.load_sprite_sheet()
        self.current_frame = 0
        self.frame_timer = 0.0
        self.frame_interval = 0.3  # animation frame interval (seconds) - slightly faster
        
        # state system
        self.state = "idle"  # idle(normal), active(enemies nearby), hit(being attacked)
        self.hit_timer = 0.0
        self.hit_duration = 1.2  # hit state duration (slightly longer)
        
        # mask flashing system
        self.mask_timer = 0.0
        self.mask_flash_duration = 0.5  # flash cycle
        self.show_mask = False  # whether to show mask currently
        
        # frame index definitions (2x2 sprite sheet)
        self.frames = {
            "idle": [1],        # top-right: normal state
            "active": [0, 2],   # top-left, bottom-left: alternating when enemies present
            "hit": [3],         # bottom-right: being attacked
            "checking": [1]     # check state: temporarily show normal state
        }
    
    def load_sprite_sheet(self):
        """Load HOME sprite sheet and cut into frames"""
        try:
            assets_path = Path(__file__).parent.parent / 'assets' / 'sprite'
            sheet = pygame.image.load(assets_path / 'HOME.png').convert_alpha()
            
            # assume sprite sheet is 2x2 format, each frame same size
            sheet_w, sheet_h = sheet.get_size()
            frame_w = sheet_w // 2
            frame_h = sheet_h // 2
            
            # cut frames: [top-left, top-right, bottom-left, bottom-right]
            self.sprite_frames = []
            positions = [(0, 0), (frame_w, 0), (0, frame_h), (frame_w, frame_h)]
            
            for x, y in positions:
                rect = pygame.Rect(x, y, frame_w, frame_h)
                frame = sheet.subsurface(rect).copy()
                self.sprite_frames.append(frame)
                
            print(f"HOME sprite loaded: {len(self.sprite_frames)} frames, {frame_w}x{frame_h} each")
            
        except Exception as e:
            print(f"Failed to load HOME sprite: {e}")
            # create default squares as fallback
            self.sprite_frames = []
            for color in [(0, 255, 0), (255, 255, 0), (255, 165, 0), (255, 0, 0)]:
                surf = pygame.Surface((GRID_SIZE, GRID_SIZE))
                surf.fill(color)
                self.sprite_frames.append(surf)
    
    def set_state(self, new_state):
        """Set HOME state"""
        if new_state != self.state:
            self.state = new_state
            self.current_frame = 0
            self.frame_timer = 0.0
            self.mask_timer = 0.0  # reset mask timer
            
            if new_state == "hit":
                self.hit_timer = 0.0
    
    def on_enemy_near(self):
        """Called when enemies are approaching"""
        if self.state != "hit":
            self.set_state("active")
    
    def on_no_enemies(self):
        """Called when no enemies present"""
        if self.state != "hit":
            self.set_state("idle")
    
    def on_hit(self):
        """Called when being attacked"""
        self.set_state("hit")
    
    def update(self, dt):
        """Update animation state and mask flashing"""
        # update hit state timer
        if self.state == "hit":
            self.hit_timer += dt
            if self.hit_timer >= self.hit_duration:
                # hit state ended, need to recheck surrounding enemy status
                # cannot directly set to idle, should let MapComponent recheck
                self.hit_timer = 0.0
                self.state = "checking"  # temporary state, waiting for MapComponent check
                return
        
        # update mask flashing (only in active and hit states)
        if self.state in ["active", "hit"]:
            self.mask_timer += dt
            if self.mask_timer >= self.mask_flash_duration:
                self.mask_timer = 0.0
                self.show_mask = not self.show_mask
        else:
            self.show_mask = False  # idle state does not show mask
        
        # update animation frame
        current_frames = self.frames[self.state]
        if len(current_frames) > 1:  # only multi-frame animations need switching
            self.frame_timer += dt
            if self.frame_timer >= self.frame_interval:
                self.frame_timer = 0.0
                self.current_frame = (self.current_frame + 1) % len(current_frames)
    
    def get_current_sprite(self, size):
        """Get current frame sprite, scaled to specified size"""
        current_frames = self.frames[self.state]
        frame_index = current_frames[self.current_frame]
        sprite = self.sprite_frames[frame_index]
        
        if size != sprite.get_size():
            sprite = pygame.transform.scale(sprite, size)
        
        # if need to show mask, apply color mask
        if self.show_mask:
            mask_surface = pygame.Surface(size, pygame.SRCALPHA)
            if self.state == "active":
                # yellow mask (enemies approaching)
                mask_surface.fill((255, 255, 0, 80))  # semi-transparent yellow
            elif self.state == "hit":
                # red mask (being attacked)
                mask_surface.fill((255, 0, 0, 120))  # semi-transparent red
            
            # create composite image with mask
            combined = sprite.copy()
            combined.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
            return combined
        
        return sprite

class MapComponent:
    def __init__(self, grid=None, spawn=(0,0), home=(GRID_W-2, GRID_H-2)):
        self.grid  = grid if grid is not None else GRID_MAP
        self.spawn = spawn
        self.home  = home
        self._load_imgs()
        
        # create START and HOME animation sprites
        self.start_sprite = StartSprite()
        self.home_sprite = HomeSprite()
        
        # enemy detection related
        self.enemies_near_home = False
        
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

    def update_enemy_status(self, enemies):
        """Update enemy status, affecting HOME animation"""
        # check if enemies are approaching HOME (distance threshold adjustable)
        enemies_near = False
        home_x, home_y = self.home
        
        for enemy in enemies:
            if hasattr(enemy, 'gx') and hasattr(enemy, 'gy'):
                # calculate distance between enemy and HOME
                distance = abs(enemy.gx - home_x) + abs(enemy.gy - home_y)
                if distance <= 5:  # within 5 grids considered approaching (increased detection range)
                    enemies_near = True
                    break
            elif hasattr(enemy, 'path') and hasattr(enemy, 'step'):
                # for enemies using path system, check path position
                if enemy.step < len(enemy.path):
                    gx, gy = enemy.path[enemy.step]
                    distance = abs(gx - home_x) + abs(gy - home_y)
                    if distance <= 5:  # within 5 grids considered approaching
                        enemies_near = True
                        break
        
        # handle HOME state switching
        current_state = self.home_sprite.state
        
        # if HOME is in checking state, redetermine correct state
        if current_state == "checking":
            if enemies_near:
                self.home_sprite.set_state("active")
                self.enemies_near_home = True
                print(f"HOME status: post-hit check, enemies found, switching to active state")
            else:
                self.home_sprite.set_state("idle")
                self.enemies_near_home = False
                print(f"HOME status: post-hit check, no enemies, switching to idle state")
        # normal state check logic
        elif current_state != "hit":  # hit state won't be interrupted
            if enemies_near and not self.enemies_near_home:
                self.home_sprite.on_enemy_near()
                self.enemies_near_home = True
                print(f"HOME status: enemies approaching, switching to active state")
            elif not enemies_near and self.enemies_near_home:
                self.home_sprite.on_no_enemies()
                self.enemies_near_home = False
                print(f"HOME status: enemies moving away, switching to idle state")
    
    def on_home_hit(self):
        """Called when HOME is being attacked"""
        self.home_sprite.on_hit()
    
    def update(self, dt, enemies=None):
        """Update map component"""
        if enemies:
            self.update_enemy_status(enemies)
        
        # update START and HOME animations
        self.start_sprite.update(dt)
        self.home_sprite.update(dt)

    def _draw(self, screen_w, screen_h):
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
        
        # Create game area surface with background color fill
        game_surface = pygame.Surface((int(scaled_width), int(scaled_height)))
        game_surface.fill((173, 216, 230))  # Fill with light blue background to avoid black borders
        
        # Draw tiles
        for y, row in enumerate(self.grid):
            for x, t in enumerate(row):
                pos_x = x * scaled_grid_size
                pos_y = y * scaled_grid_size
                game_surface.blit(scaled_imgs[t], (pos_x, pos_y))
        
        # Draw markers with 1.25x scaling and centering
        sx, sy = self.spawn
        hx, hy = self.home
        
        # Calculate 1.25x scaled size
        marker_size = int(scaled_grid_size * 1.25)
        
        # START marker - use sprite animation, 1.25x scaled and centered
        start_sprite = self.start_sprite.get_current_sprite((marker_size, marker_size))
        start_offset_x = (scaled_grid_size - marker_size) // 2
        start_offset_y = (scaled_grid_size - marker_size) // 2
        start_pos = (sx * scaled_grid_size + start_offset_x, sy * scaled_grid_size + start_offset_y)
        game_surface.blit(start_sprite, start_pos)
        
        # HOME marker - use sprite animation, 1.25x scaled and centered
        home_sprite = self.home_sprite.get_current_sprite((marker_size, marker_size))
        home_offset_x = (scaled_grid_size - marker_size) // 2
        home_offset_y = (scaled_grid_size - marker_size) // 2
        home_pos = (hx * scaled_grid_size + home_offset_x, hy * scaled_grid_size + home_offset_y)
        game_surface.blit(home_sprite, home_pos)
        
        return game_surface, (int(offset_x), int(offset_y))

    def set_grid(self, new_grid):
        self.grid = new_grid

    def draw(self, target):
        screen_w, screen_h = target.get_size()
        game_surface, offset = self._draw(screen_w, screen_h)
        target.blit(game_surface, offset)
