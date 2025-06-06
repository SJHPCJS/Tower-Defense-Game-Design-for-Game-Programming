import pygame
import os
import math
from settings import *
from bullet import BulletFactory

class TowerSprite:
    """Handles tower sprite loading and animation"""
    def __init__(self, tower_name):
        self.tower_name = tower_name
        self.frames = []
        self.attack_frames = []
        self.idle_frames = []
        self.current_frame = 0
        self.animation_timer = 0.0
        self.frame_duration = 0.5  # Half second per frame
        
        # Load sprite sheet
        sprite_path = f"assets/sprite/tower/{tower_name}.png"
        try:
            if os.path.exists(sprite_path):
                self.sprite_sheet = pygame.image.load(sprite_path)
                self.load_frames()
                print(f"Loaded sprite for {tower_name}")
            else:
                raise FileNotFoundError(f"Sprite file not found: {sprite_path}")
        except (pygame.error, FileNotFoundError, OSError) as e:
            print(f"Could not load sprite: {sprite_path}, using fallback - {e}")
            self.sprite_sheet = None
            self.create_fallback_frames()
    
    def load_frames(self):
        """Load frames from sprite sheet (assuming 2x2 grid)"""
        if not self.sprite_sheet:
            return
            
        sheet_width = self.sprite_sheet.get_width()
        sheet_height = self.sprite_sheet.get_height()
        frame_width = sheet_width // 2
        frame_height = sheet_height // 2
        
        # Load all 4 frames
        for row in range(2):
            for col in range(2):
                frame_rect = pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
                frame = self.sprite_sheet.subsurface(frame_rect).copy()
                self.frames.append(frame)
        
        # For Chrono Cactus, use all 4 frames for animation
        if self.tower_name == "Chrono Cactus":
            self.idle_frames = self.frames
            self.attack_frames = self.frames
        else:
            # For attacking towers: top 2 are idle, bottom 2 are attack
            self.idle_frames = [self.frames[0], self.frames[1]]
            self.attack_frames = [self.frames[2], self.frames[3]]
    
    def create_fallback_frames(self):
        """Create simple colored rectangles with text as fallback"""
        # Get tower type from settings for color
        tower_color = (100, 100, 100)  # Default gray
        for tower_type in TOWER_TYPES:
            if tower_type['name'] == self.tower_name:
                tower_color = tower_type['color']
                break
        
        frames = []
        for i in range(4):
            frame = pygame.Surface((64, 64))
            frame.fill(tower_color)
            
            # Add border
            pygame.draw.rect(frame, (255, 255, 255), frame.get_rect(), 2)
            
            # Add text
            font = pygame.font.SysFont('Arial', 12, bold=True)
            text = font.render(self.tower_name[:6], True, (255, 255, 255))
            text_rect = text.get_rect(center=(32, 32))
            frame.blit(text, text_rect)
            
            # Add small animation indicator
            if i % 2 == 1:  # Every other frame is slightly different
                pygame.draw.circle(frame, (255, 255, 255), (56, 8), 3)
            
            frames.append(frame)
        
        self.frames = frames
        
        # For Chrono Cactus, use all 4 frames for animation
        if self.tower_name == "Chrono Cactus":
            self.idle_frames = self.frames
            self.attack_frames = self.frames
        else:
            # For attacking towers: first 2 are idle, last 2 are attack
            self.idle_frames = [self.frames[0], self.frames[1]]
            self.attack_frames = [self.frames[2], self.frames[3]]
    
    def get_current_frame(self, is_attacking=False):
        """Get current animation frame"""
        if self.tower_name == "Chrono Cactus":
            # Always use idle frames (which contains all 4 frames)
            frames = self.idle_frames
        else:
            frames = self.attack_frames if is_attacking else self.idle_frames
        
        if frames:
            return frames[self.current_frame % len(frames)]
        return self.frames[0] if self.frames else pygame.Surface((40, 40))
    
    def update_animation(self, dt):
        """Update animation timer and frame"""
        self.animation_timer += dt
        if self.animation_timer >= self.frame_duration:
            self.animation_timer = 0.0
            # Determine frame count based on tower type
            if self.tower_name == "Chrono Cactus":
                frame_count = 4
            else:
                frame_count = 2
            self.current_frame = (self.current_frame + 1) % frame_count

class BaseTower(pygame.sprite.Sprite):
    """Base tower class with common functionality"""
    RANGE = 120

    def __init__(self, gx, gy, props):
        super().__init__()
        self.gx = gx  # Grid coordinates
        self.gy = gy
        self.tower_type = props  # Store tower type information
        self.damage = props['damage']
        self.rof = props['rof']
        self.color = props['color']
        self.name = props['name']
        
        # Animation state
        self.is_attacking = False
        self.attack_timer = 0.0
        
        # Load sprite
        self.sprite = TowerSprite(self.name)
        
        # Initial image (will be scaled in the draw method based on screen size)
        self.base_size = GRID_SIZE - 6
        self.image = self.get_scaled_image()
        
        # Initial position (will be updated in update_position method)
        px, py = grid_to_px(gx, gy)
        self.rect = self.image.get_rect(topleft=(px+3, py+3))
        self.cool = 0.0

    def get_scaled_image(self):
        """Get current frame scaled to appropriate size"""
        current_frame = self.sprite.get_current_frame(self.is_attacking)
        screen = pygame.display.get_surface()
        if screen:
            screen_w, screen_h = screen.get_size()
            scaled_grid_size = get_scaled_grid_size(screen_w, screen_h)
            # Increase size by 1.25x and center on grid
            size = max(int(scaled_grid_size * 1.25), 12)  # Minimum size is 12
        else:
            size = int(self.base_size * 1.25)
        
        return pygame.transform.scale(current_frame, (size, size))

    def update_position(self, screen_width, screen_height):
        """Update tower position and size based on screen dimensions"""
        self.image = self.get_scaled_image()
        
        # Update position - center the larger image on the grid cell
        px, py = grid_to_px(self.gx, self.gy, screen_width, screen_height)
        scaled_grid_size = get_scaled_grid_size(screen_width, screen_height)
        
        # Center the 1.25x sized image on the grid cell
        image_size = int(scaled_grid_size * 1.25)
        offset_x = (scaled_grid_size - image_size) // 2
        offset_y = (scaled_grid_size - image_size) // 2
        
        self.rect = self.image.get_rect(topleft=(px + offset_x, py + offset_y))

    def update(self, dt, enemies, bullets):
        """Base update method - to be overridden by specific tower types"""
        # Update animation
        self.sprite.update_animation(dt)
        
        # Update attack timer
        if self.attack_timer > 0:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.is_attacking = False
        
        self.cool -= dt

    def start_attack_animation(self):
        """Start attack animation"""
        self.is_attacking = True
        self.attack_timer = 0.3  # Show attack animation for 0.3 seconds

    def draw(self, screen):
        """Custom draw method to ensure tower is at the correct position and size"""
        screen_w, screen_h = screen.get_size()
        self.update_position(screen_w, screen_h)
        screen.blit(self.image, self.rect)

class AttackingTower(BaseTower):
    """Tower that can attack enemies"""
    
    def update(self, dt, enemies, bullets):
        super().update(dt, enemies, bullets)
        
        if self.cool > 0 or not enemies:
            return
            
        cx, cy = self.rect.center
        
        # Calculate scaled range
        screen = pygame.display.get_surface()
        if screen:
            screen_w, screen_h = screen.get_size()
            scale = get_scaled_grid_size(screen_w, screen_h) / GRID_SIZE
            scaled_range = self.RANGE * scale
        else:
            scaled_range = self.RANGE
        
        nearest = min(enemies,
                      key=lambda e:(cx-e.rect.centerx)**2+(cy-e.rect.centery)**2)
        if (cx-nearest.rect.centerx)**2 + (cy-nearest.rect.centery)**2 <= scaled_range**2:
            bullet = BulletFactory.create_bullet(self.name, self.rect.center, nearest, self.damage, enemies)
            bullets.add(bullet)
            self.cool = self.rof
            self.start_attack_animation()

class ChronoCactusTower(BaseTower):
    """Chrono Cactus tower that slows nearby enemies"""
    
    def __init__(self, gx, gy, props):
        super().__init__(gx, gy, props)
        self.slow_range = props.get('slow_range', 5) * GRID_SIZE  # Convert grid units to pixels
        self.slow_effect = props.get('slow_effect', 0.25)  # 25% speed reduction
        self.affected_enemies = set()  # Track which enemies are affected
    
    def update(self, dt, enemies, bullets):
        super().update(dt, enemies, bullets)
        
        cx, cy = self.rect.center
        
        # Calculate scaled range
        screen = pygame.display.get_surface()
        if screen:
            screen_w, screen_h = screen.get_size()
            scale = get_scaled_grid_size(screen_w, screen_h) / GRID_SIZE
            scaled_range = self.slow_range * scale
        else:
            scaled_range = self.slow_range
        
        # Track enemies currently in range
        currently_in_range = set()
        
        # Check each enemy
        for enemy in enemies:
            distance_sq = (cx - enemy.rect.centerx)**2 + (cy - enemy.rect.centery)**2
            
            if distance_sq <= scaled_range**2:
                # Enemy is in range
                currently_in_range.add(enemy)
                
                # Only apply slow effect if enemy is not already slowed by any tower
                if not hasattr(enemy, 'is_slowed') or not enemy.is_slowed:
                    if not hasattr(enemy, 'original_speed'):
                        enemy.original_speed = enemy.speed
                    
                    # Apply slow effect (no stacking)
                    enemy.speed = enemy.original_speed * (1 - self.slow_effect)
                    enemy.is_slowed = True
                    enemy.slowing_tower = self
                    self.affected_enemies.add(enemy)
                elif hasattr(enemy, 'slowing_tower') and enemy.slowing_tower == self:
                    # This tower is already affecting this enemy, keep it in the list
                    self.affected_enemies.add(enemy)
        
        # Remove slow effect from enemies that left range (only if this tower was affecting them)
        enemies_to_remove = self.affected_enemies - currently_in_range
        for enemy in enemies_to_remove:
            if hasattr(enemy, 'slowing_tower') and enemy.slowing_tower == self:
                # Restore original speed
                enemy.speed = enemy.original_speed
                enemy.is_slowed = False
                enemy.slowing_tower = None
        
        # Update affected enemies list
        self.affected_enemies = currently_in_range
    
    def kill(self):
        """Override kill to clean up all affected enemies when tower is destroyed"""
        self.cleanup_all_effects()
        super().kill()
    
    def cleanup_all_effects(self):
        """Clean up all slow effects when tower is destroyed"""
        for enemy in list(self.affected_enemies):
            if hasattr(enemy, 'slowing_tower') and enemy.slowing_tower == self:
                # Restore original speed
                enemy.speed = enemy.original_speed
                enemy.is_slowed = False
                enemy.slowing_tower = None
        
        self.affected_enemies.clear()

class TowerFactory:
    """Factory class for creating different tower types"""
    
    @staticmethod
    def create_tower(tower_type, gx, gy):
        """Create a tower based on type"""
        if tower_type['name'] == 'Chrono Cactus':
            return ChronoCactusTower(gx, gy, tower_type)
        else:
            return AttackingTower(gx, gy, tower_type)

# Legacy Tower class for backward compatibility
class Tower(AttackingTower):
    """Legacy tower class - redirects to AttackingTower"""
    pass
