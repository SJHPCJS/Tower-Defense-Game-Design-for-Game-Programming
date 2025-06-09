import pygame
import os
import math
import random
from settings import *
from pathfinding import a_star
from grid import GRID_MAP

# Enemy type definitions
ENEMY_TYPES = {
    'Caffeinj': {
        'name': 'Caffeinj',
        'health': 120,
        'speed': 90,
        'reward': 2,
        'description': 'Fast enemy with low health'
    },
    'Cementum': {
        'name': 'Cementum', 
        'health': 400,
        'speed': 30,
        'reward': 5,
        'description': 'Slow tank enemy with high health'
    },
    'Adframe': {
        'name': 'Adframe',
        'health': 200,
        'speed': 50,
        'reward': 3,
        'dodge_chance': 0.3,
        'description': 'Enemy that can dodge attacks'
    },
    'Boxshot': {
        'name': 'Boxshot',
        'health': 160,
        'speed': 50,  
        'reward': 2,
        'description': 'Standard enemy'
    },
    'Wiregeist': {
        'name': 'Wiregeist',
        'health': 140,
        'speed': 55,
        'reward': 4,
        'aura_range': 2,
        'speed_boost': 0.2,
        'description': 'Boosts nearby enemy speed by 20%'
    }
}

class EnemySprite:
    """Handles enemy sprite loading and animation"""
    def __init__(self, enemy_name):
        self.enemy_name = enemy_name
        self.frames = []
        self.current_frame = 0
        self.animation_timer = 0.0
        self.frame_duration = 0.3  # 0.3 seconds per frame for walking animation
        
        # Load sprite sheet
        sprite_path = f"assets/sprite/enemy/{enemy_name}.png"
        try:
            if os.path.exists(sprite_path):
                self.sprite_sheet = pygame.image.load(sprite_path)
                self.load_frames()
                print(f"Loaded sprite for {enemy_name}")
            else:
                raise FileNotFoundError(f"Sprite file not found: {sprite_path}")
        except (pygame.error, FileNotFoundError, OSError) as e:
            print(f"Could not load sprite: {sprite_path}, using fallback - {e}")
            self.sprite_sheet = None
            self.create_fallback_frames()
    
    def load_frames(self):
        """Load 4 frames from sprite sheet (assuming 4x1 or 2x2 grid)"""
        if not self.sprite_sheet:
            return
            
        sheet_width = self.sprite_sheet.get_width()
        sheet_height = self.sprite_sheet.get_height()
        
        # Try 4x1 layout first
        if sheet_width > sheet_height:
            frame_width = sheet_width // 4
            frame_height = sheet_height
            
            for i in range(4):
                frame_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                frame = self.sprite_sheet.subsurface(frame_rect).copy()
                self.frames.append(frame)
        else:
            # Try 2x2 layout
            frame_width = sheet_width // 2
            frame_height = sheet_height // 2
            
            for row in range(2):
                for col in range(2):
                    frame_rect = pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
                    frame = self.sprite_sheet.subsurface(frame_rect).copy()
                    self.frames.append(frame)
    
    def create_fallback_frames(self):
        """Create simple colored rectangles as fallback"""
        # Get enemy color based on type
        enemy_colors = {
            'Caffeinj': (0, 255, 0),      # Green for fast
            'Cementum': (139, 69, 19),    # Brown for tank
            'Adframe': (128, 0, 128),     # Purple for dodger
            'Boxshot': (0, 0, 255),       # Blue for normal
            'Wiregeist': (255, 255, 0)    # Yellow for aura
        }
        
        color = enemy_colors.get(self.enemy_name, (100, 100, 100))
        
        for i in range(4):
            frame = pygame.Surface((32, 32))
            frame.fill(color)
            
            # Add border
            pygame.draw.rect(frame, (255, 255, 255), frame.get_rect(), 2)
            
            # Add text
            font = pygame.font.SysFont('Arial', 8, bold=True)
            text = font.render(self.enemy_name[:3], True, (255, 255, 255))
            text_rect = text.get_rect(center=(16, 16))
            frame.blit(text, text_rect)
            
            # Add small animation indicator (different position each frame)
            indicator_pos = [(4, 4), (28, 4), (28, 28), (4, 28)]
            pygame.draw.circle(frame, (255, 255, 255), indicator_pos[i], 2)
            
            self.frames.append(frame)
    
    def get_current_frame(self):
        """Get current animation frame"""
        if self.frames:
            return self.frames[self.current_frame % len(self.frames)]
        return pygame.Surface((32, 32))
    
    def update_animation(self, dt):
        """Update animation timer and frame"""
        self.animation_timer += dt
        if self.animation_timer >= self.frame_duration:
            self.animation_timer = 0.0
            self.current_frame = (self.current_frame + 1) % 4

class MissEffect:
    """Visual effect for missed attacks"""
    def __init__(self, pos):
        self.pos = pos
        self.timer = 1.0  # Show for 1 second
        self.font = pygame.font.SysFont('Arial', 32, bold=True)  # 2x larger (16 -> 32)
        self.text = self.font.render("MISS", True, (255, 255, 0))
        self.offset_y = 0
    
    def update(self, dt):
        self.timer -= dt
        self.offset_y += 20 * dt  # Float upward
        return self.timer > 0
    
    def draw(self, screen):
        if self.timer > 0:
            alpha = min(255, int(self.timer * 255))
            text_surface = self.text.copy()
            text_surface.set_alpha(alpha)
            # Adjust position for larger text
            text_rect = text_surface.get_rect()
            pos = (self.pos[0] - text_rect.width//2, self.pos[1] - 30 - self.offset_y)
            screen.blit(text_surface, pos)

class BaseEnemy(pygame.sprite.Sprite):
    """Base enemy class with common functionality"""
    def __init__(self, path_or_start, end=None, enemy_type='Boxshot'):
        super().__init__()
        
        # Support two initialization methods:
        # 1. Enemy(path) - New method, directly pass the path
        # 2. Enemy(start, end) - Old method, pass start and end points
        if end is None:
            if isinstance(path_or_start, list) and len(path_or_start) > 0:
                self.path = path_or_start
            else:
                raise ValueError("Invalid path provided!")
        else:
            # Calculate path using current grid for each enemy individually
            self.path = a_star(path_or_start, end, GRID_MAP)
            if not self.path:
                raise ValueError("No path found!")
        
        # Get enemy stats
        self.enemy_type = enemy_type
        enemy_stats = ENEMY_TYPES.get(enemy_type, ENEMY_TYPES['Boxshot'])
        
        # Basic properties
        self.step = 0
        self.path_index = 0
        self.progress = 0.0
        self.speed = enemy_stats['speed']
        self.original_speed = enemy_stats['speed']
        self.max_health = enemy_stats['health']
        self.health = self.max_health
        self.hp = self.max_health
        self.max_hp = self.max_health
        self.reward = enemy_stats['reward']
        
        # Visual effects
        self.flash_time = 0.0
        self.hit_flash = 0.0
        self.reached_end = False
        self.damage_to_base = 1
        self.is_dead = False
        self.reward_given = False
        
        # Speed modifiers tracking
        self.speed_modifiers = set()
        self.aura_effects = []  # Track aura effects affecting this enemy
        
        # Load sprite and animation
        self.sprite = EnemySprite(enemy_type)
        
        # Size and image setup
        self.base_size = 36  # Increased from 30 to 36 for slightly larger enemies
        self.size = self.base_size
        self.image = self.get_scaled_image()
        self.rect = self.image.get_rect()
        
        # Set initial position
        self._update_position_and_size()
        if self.path:
            gx, gy = self.path[0]
            initial_pos = self._tile_center(gx, gy)
            self.rect.center = (initial_pos.x, initial_pos.y)
        
        # Miss effects
        self.miss_effects = []
        
        # Special effects
        self.burn_effects = []
        self.electric_effects = []

    def get_scaled_image(self):
        """Get current frame scaled to appropriate size"""
        current_frame = self.sprite.get_current_frame()
        screen = pygame.display.get_surface()
        if screen:
            screen_w, screen_h = screen.get_size()
            scaled_grid_size = get_scaled_grid_size(screen_w, screen_h)
            scale_factor = scaled_grid_size / GRID_SIZE
            size = max(int(self.base_size * scale_factor), 8)
        else:
            size = self.base_size
        
        return pygame.transform.scale(current_frame, (size, size))
    
    def _update_position_and_size(self):
        """Update enemy size and position based on current screen scaling"""
        screen = pygame.display.get_surface()
        if screen:
            screen_w, screen_h = screen.get_size()
            scaled_grid_size = get_scaled_grid_size(screen_w, screen_h)
            scale_factor = scaled_grid_size / GRID_SIZE
            self.size = max(int(self.base_size * scale_factor), 8)
            
            self.image = self.get_scaled_image()
            
            # Recalculate position based on current path progress
            if self.step < len(self.path):
                if self.step + 1 < len(self.path):
                    current_gx, current_gy = self.path[self.step]
                    next_gx, next_gy = self.path[self.step + 1]
                    
                    current_pos = self._tile_center(current_gx, current_gy)
                    next_pos = self._tile_center(next_gx, next_gy)
                    
                    interp_x = current_pos.x + (next_pos.x - current_pos.x) * self.progress
                    interp_y = current_pos.y + (next_pos.y - current_pos.y) * self.progress
                    
                    self.rect = self.image.get_rect()
                    self.rect.center = (interp_x, interp_y)
                else:
                    gx, gy = self.path[self.step]
                    pos = self._tile_center(gx, gy)
                    self.rect = self.image.get_rect()
                    self.rect.center = (pos.x, pos.y)
            else:
                self.rect = self.image.get_rect()

    def _tile_center(self, gx, gy):
        """Get the center point of a grid tile with proper scaling"""
        screen = pygame.display.get_surface()
        if screen:
            screen_w, screen_h = screen.get_size()
            px, py = grid_to_px(gx, gy, screen_w, screen_h)
            scaled_grid_size = get_scaled_grid_size(screen_w, screen_h)
            return pygame.Vector2(px + scaled_grid_size//2, py + scaled_grid_size//2)
        else:
            px, py = grid_to_px(gx, gy)
            return pygame.Vector2(px + GRID_SIZE//2, py + GRID_SIZE//2)

    def hit(self, dmg):
        """Take damage - can be overridden by specific enemy types"""
        self.health -= dmg
        self.hp = self.health
        self.flash_time = 0.1
        self.hit_flash = 0.1
        if self.health <= 0 and not self.reward_given:
            self.is_dead = True
            self.reward_given = True
            self.cleanup_speed_modifiers()
            if hasattr(self, 'kill_callback') and self.kill_callback:
                self.kill_callback(self)
            self.kill()
        return True  # Return True to indicate hit was successful
    
    def cleanup_speed_modifiers(self):
        """Clean up speed modifiers when enemy is removed"""
        for tower in list(self.speed_modifiers):
            if hasattr(tower, 'affected_enemies'):
                tower.affected_enemies.discard(self)
        self.speed_modifiers.clear()
        self.aura_effects.clear()

    def apply_aura_effect(self, source_enemy, speed_multiplier):
        """Apply speed boost from another enemy's aura"""
        # Remove any existing effect from the same source
        self.aura_effects = [effect for effect in self.aura_effects if effect[0] != source_enemy]
        
        # Add new effect
        self.aura_effects.append((source_enemy, speed_multiplier))
        self._recalculate_speed()
    
    def remove_aura_effect(self, source_enemy):
        """Remove speed boost from a specific enemy"""
        self.aura_effects = [effect for effect in self.aura_effects if effect[0] != source_enemy]
        self._recalculate_speed()
    
    def _recalculate_speed(self):
        """Recalculate speed based on all active effects"""
        base_speed = self.original_speed
        
        # Apply tower slow effects
        if hasattr(self, 'is_slowed') and self.is_slowed and hasattr(self, 'slowing_tower'):
            base_speed *= 0.75  # 25% slow from towers
        
        # Apply aura effects (multiplicative)
        for source_enemy, multiplier in self.aura_effects:
            base_speed *= (1 + multiplier)
        
        self.speed = base_speed

    def update(self, dt):
        # Update animation
        self.sprite.update_animation(dt)
        
        # Update size and position
        self._update_position_and_size()
        
        # Update miss effects
        self.miss_effects = [effect for effect in self.miss_effects if effect.update(dt)]
        
        # Update burn effects
        self.burn_effects = [effect for effect in self.burn_effects if effect.update(dt, self)]
        
        # Update electric effects
        self.electric_effects = [effect for effect in self.electric_effects if effect.update(dt)]
        
        # Movement logic
        if self.step < len(self.path):
            if self.step + 1 < len(self.path):
                current_gx, current_gy = self.path[self.step]
                next_gx, next_gy = self.path[self.step + 1]
                
                current_pos = self._tile_center(current_gx, current_gy)
                next_pos = self._tile_center(next_gx, next_gy)
                
                segment_distance = (next_pos - current_pos).length()
                
                if segment_distance > 0:
                    screen = pygame.display.get_surface()
                    if screen:
                        screen_w, screen_h = screen.get_size()
                        scale_factor = get_scaled_grid_size(screen_w, screen_h) / GRID_SIZE
                        scaled_speed = self.speed * scale_factor
                    else:
                        scaled_speed = self.speed
                    
                    progress_increment = (scaled_speed * dt) / segment_distance
                    self.progress += progress_increment
                    
                    if self.progress >= 1.0:
                        self.step += 1
                        self.path_index = self.step
                        self.progress = 0.0
                else:
                    self.step += 1
                    self.path_index = self.step
                    self.progress = 0.0
            else:
                self.progress = 1.0
        else:
            self.reached_end = True

        # Update flash effects
        if self.flash_time > 0:
            self.flash_time = max(0, self.flash_time - dt)
        if self.hit_flash > 0:
            self.hit_flash = max(0, self.hit_flash - dt)
    
    def add_miss_effect(self):
        """Add a miss effect at current position"""
        self.miss_effects.append(MissEffect(self.rect.center))
    
    def draw(self, surf):
        """Draw the enemy with all effects"""
        surf.blit(self.image, self.rect)
        
        # Draw health bar
        hb_w = self.size
        x, y = self.rect.x, self.rect.y - 6
        back = pygame.Rect(x, y, hb_w, 4)
        front = pygame.Rect(x, y, int(hb_w * self.health / self.max_health), 4)
        pygame.draw.rect(surf, RED, back)
        pygame.draw.rect(surf, GREEN, front)
        
        # Flash effect
        if self.flash_time > 0 or self.hit_flash > 0:
            overlay = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 120))
            surf.blit(overlay, self.rect.topleft)
        
        # Draw miss effects
        for effect in self.miss_effects:
            effect.draw(surf)
        
        # Draw burn effects
        for effect in self.burn_effects:
            effect.draw(surf)
        
        # Draw electric effects
        for effect in self.electric_effects:
            effect.draw(surf)

class AdframeEnemy(BaseEnemy):
    """Enemy that can dodge attacks"""
    def __init__(self, path_or_start, end=None):
        super().__init__(path_or_start, end, 'Adframe')
        self.dodge_chance = ENEMY_TYPES['Adframe']['dodge_chance']
    
    def hit(self, dmg):
        """Override hit to implement dodge mechanism"""
        if random.random() < self.dodge_chance:
            # Dodged the attack
            self.add_miss_effect()
            return False  # Attack missed
        else:
            # Normal hit
            super().hit(dmg)
            return True  # Attack hit

class WiregeistEnemy(BaseEnemy):
    """Enemy that provides speed boost aura to nearby enemies"""
    def __init__(self, path_or_start, end=None):
        super().__init__(path_or_start, end, 'Wiregeist')
        self.aura_range = ENEMY_TYPES['Wiregeist']['aura_range'] * GRID_SIZE
        self.speed_boost = ENEMY_TYPES['Wiregeist']['speed_boost']
        self.affected_enemies = set()
    
    def update(self, dt):
        super().update(dt)
        self.update_aura_effects()
    
    def update_aura_effects(self):
        """Update speed boost effects on nearby enemies"""
        if not hasattr(self, 'groups') or not self.groups():
            return
        
        # Get all enemies in the same group
        all_enemies = []
        for group in self.groups():
            all_enemies.extend([enemy for enemy in group if enemy != self and hasattr(enemy, 'rect')])
        
        # Calculate scaled range
        screen = pygame.display.get_surface()
        if screen:
            screen_w, screen_h = screen.get_size()
            scale = get_scaled_grid_size(screen_w, screen_h) / GRID_SIZE
            scaled_range = self.aura_range * scale
        else:
            scaled_range = self.aura_range
        
        currently_in_range = set()
        
        # Check each enemy
        for enemy in all_enemies:
            distance_sq = (self.rect.centerx - enemy.rect.centerx)**2 + (self.rect.centery - enemy.rect.centery)**2
            
            if distance_sq <= scaled_range**2:
                currently_in_range.add(enemy)
                if enemy not in self.affected_enemies:
                    enemy.apply_aura_effect(self, self.speed_boost)
        
        # Remove effects from enemies that left range
        enemies_to_remove = self.affected_enemies - currently_in_range
        for enemy in enemies_to_remove:
            enemy.remove_aura_effect(self)
        
        self.affected_enemies = currently_in_range
    
    def kill(self):
        """Clean up aura effects when enemy dies"""
        for enemy in list(self.affected_enemies):
            enemy.remove_aura_effect(self)
        self.affected_enemies.clear()
        super().kill()

class EnemyFactory:
    """Factory class for creating different enemy types"""
    
    @staticmethod
    def create_enemy(enemy_type, path_or_start, end=None, wave_number=1):
        """Create an enemy based on type with health scaling based on wave number"""
        if enemy_type == 'Adframe':
            enemy = AdframeEnemy(path_or_start, end)
        elif enemy_type == 'Wiregeist':
            enemy = WiregeistEnemy(path_or_start, end)
        else:
            enemy = BaseEnemy(path_or_start, end, enemy_type)
        
        # Apply wave health scaling (10% increase per wave)
        health_multiplier = 1.0 + (wave_number - 1) * 0.1
        if wave_number > 1:
            enemy.max_health = int(enemy.max_health * health_multiplier)
            enemy.health = enemy.max_health
        
        # Debug print for enemy health (for all waves)
        print(f"Wave {wave_number}: {enemy_type} - Base Health: {ENEMY_TYPES[enemy_type]['health']}, "
              f"Scaled Health: {enemy.health} (multiplier: {health_multiplier:.1f})")
        
        return enemy
    
    @staticmethod
    def get_wave_composition(wave_number, total_enemies):
        """Generate completely random enemy composition for a wave"""
        composition = {}
        
        # Initialize all enemy types
        enemy_types = list(ENEMY_TYPES.keys())
        for enemy_type in enemy_types:
            composition[enemy_type] = 0
        
        # Randomly distribute all enemies
        for _ in range(total_enemies):
            random_enemy = random.choice(enemy_types)
            composition[random_enemy] += 1
        
        return composition

# Legacy classes for backward compatibility
class Enemy(BaseEnemy):
    """Legacy enemy class - redirects to BaseEnemy"""
    def __init__(self, path_or_start, end=None, enemy_type='Boxshot'):
        super().__init__(path_or_start, end, enemy_type)

class EnemyWithGrid(BaseEnemy):
    """Enemy class that accepts a grid parameter for path calculation"""
    def __init__(self, start, end, grid, enemy_type='Boxshot'):
        self.grid = grid
        path = a_star(start, end, grid)
        if not path:
            raise ValueError("No path found!")
        super().__init__(path, None, enemy_type)

    def calculate_path(self, start, end):
        """Calculate path using the provided grid"""
        return a_star(start, end, self.grid)
