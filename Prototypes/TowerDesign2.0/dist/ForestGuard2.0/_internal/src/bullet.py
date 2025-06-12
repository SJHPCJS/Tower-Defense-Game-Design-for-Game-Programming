"""
AI assisted code included in this file, you can see the comments below for details.
"""
import pygame
import math
from abc import ABC, abstractmethod
from settings import *
from audio_manager import audio_manager
from resource_manager import get_bullet_path


class DamageEffect(ABC):
    """Abstract base class for damage effects"""
    
    @abstractmethod
    def apply(self, enemy, damage, position):
        pass


class NormalDamageEffect(DamageEffect):
    """Normal damage with no special effects"""
    
    def apply(self, enemy, damage, position):
        if hasattr(enemy, 'hit') and callable(enemy.hit):
            return enemy.hit(damage)
        return True


class BurnDamageEffect(DamageEffect):
    """Burn damage that applies damage over time"""
    
    def apply(self, enemy, damage, position):
        result = True
        if hasattr(enemy, 'hit') and callable(enemy.hit):
            result = enemy.hit(damage)

        if result is not False:  # If not dodged
            self._add_burn_effect(enemy)
        
        return result
    
    def _add_burn_effect(self, enemy):
        if not hasattr(enemy, 'burn_effects'):
            enemy.burn_effects = []
        burn_effect = BurnEffect(enemy.rect.center)
        enemy.burn_effects.append(burn_effect)
        audio_manager.play_flame_sound()


class ElectricDamageEffect(DamageEffect):
    """Electric damage that affects nearby enemies"""
    """This class is fixed by ChatGPT-o4-mini-high, the code is directly copied from the generated code"""
    
    def __init__(self, aoe_range=40):
        self.aoe_range = aoe_range
        self.enemies_group = None
    
    def set_enemies_group(self, enemies_group):
        """Set the enemies group for chain damage"""
        self.enemies_group = enemies_group
    
    def apply(self, enemy, damage, position):
        result = True
        if hasattr(enemy, 'hit') and callable(enemy.hit):
            result = enemy.hit(damage)

        if result is not False:  # If not dodged
            self._add_electric_effect(enemy)
            if self.enemies_group:
                self._apply_chain_damage(enemy, damage * 0.5, position)
        
        return result
    
    def _add_electric_effect(self, enemy):
        if not hasattr(enemy, 'electric_effects'):
            enemy.electric_effects = []
        
        electric_effect = ElectricEffect(enemy.rect.center)
        enemy.electric_effects.append(electric_effect)
        
        # Play death (lightning) sound effect
        audio_manager.play_death_sound()
    
    def _apply_chain_damage(self, primary_enemy, chain_damage, position):
        """Apply chain damage to nearby enemies"""
        if not self.enemies_group:
            return
            
        # Find nearby enemies
        for enemy in self.enemies_group:
            if (hasattr(enemy, 'enemy_type') and 
                enemy != primary_enemy and 
                hasattr(enemy, 'rect')):
                
                distance = math.sqrt((enemy.rect.centerx - position[0])**2 + 
                                   (enemy.rect.centery - position[1])**2)
                
                if distance <= self.aoe_range:
                    # Apply chain damage
                    if hasattr(enemy, 'hit') and callable(enemy.hit):
                        enemy.hit(chain_damage)
                    
                    # Add electric effect
                    if not hasattr(enemy, 'electric_effects'):
                        enemy.electric_effects = []
                    
                    electric_effect = ElectricEffect(enemy.rect.center)
                    enemy.electric_effects.append(electric_effect)
                    
                    # Play death sound for chain damage too
                    audio_manager.play_death_sound()


class BurnEffect:
    """This class is fixed by ChatGPT-o4-mini-high, the font size is increased to 32 for better visibility, no more code changes by ChatGPT"""
    def __init__(self, pos):
        self.pos = pos
        self.timer = 3.0
        self.damage_timer = 1.0
        self.font = pygame.font.SysFont('Arial', 32, bold=True)  # 2x larger (16 -> 32)
        self.text = self.font.render("Fire", True, (255, 0, 0))
        self.offset_y = 0
        self.damage_per_tick = 5
    
    def update(self, dt, enemy):
        self.timer -= dt
        self.damage_timer -= dt
        self.offset_y += 10 * dt

        if self.damage_timer <= 0:
            if hasattr(enemy, 'hit') and callable(enemy.hit):
                enemy.hit(self.damage_per_tick)
            self.damage_timer = 1.0
        
        return self.timer > 0
    
    def draw(self, screen):

        if self.timer > 0:
            alpha = min(255, int(self.timer * 85))  # Fade out over 3 seconds
            text_surface = self.text.copy()
            text_surface.set_alpha(alpha)
            # Adjust position for larger text
            text_rect = text_surface.get_rect()
            pos = (self.pos[0] - text_rect.width//2, self.pos[1] - 30 - self.offset_y)
            screen.blit(text_surface, pos)


class ElectricEffect:
    """Visual effect for electric attacks"""
    """This class is fixed by ChatGPT-o4-mini-high, the font size is increased to 32 for better visibility, no more code changes by ChatGPT"""
    def __init__(self, pos):
        self.pos = pos
        self.timer = 0.5  # Show for 0.5 seconds
        self.font = pygame.font.SysFont('Arial', 32, bold=True)  # 2x larger (16 -> 32)
        self.text = self.font.render("Zap", True, (255, 255, 0))
        self.offset_y = 0
    
    def update(self, dt):
        self.timer -= dt
        self.offset_y += 30 * dt  # Float upward quickly
        return self.timer > 0
    
    def draw(self, screen):
        if self.timer > 0:
            alpha = min(255, int(self.timer * 510))  # Fade out quickly
            text_surface = self.text.copy()
            text_surface.set_alpha(alpha)
            # Adjust position for larger text
            text_rect = text_surface.get_rect()
            pos = (self.pos[0] - text_rect.width//2, self.pos[1] - 30 - self.offset_y)
            screen.blit(text_surface, pos)


class BulletStrategy(ABC):
    """Abstract strategy for bullet behavior"""
    
    @abstractmethod
    def create_image(self, bullet_type):
        pass
    
    @abstractmethod
    def get_damage_effect(self):
        pass


class NormalBulletStrategy(BulletStrategy):
    """Strategy for normal bullets"""
    
    def __init__(self, bullet_image_path):
        self.bullet_image_path = bullet_image_path
    
    def create_image(self, bullet_type):
        """Create normal bullet image"""
        try:
            image = pygame.image.load(self.bullet_image_path)
            image = pygame.transform.scale(image, (40, 40))
            return image
        except (pygame.error, FileNotFoundError):
            """This error handling is fixed by ChatGPT-o4-mini-high, the fallback image is now a simple colored circle"""
            # Fallback to simple colored circle
            image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(image, (100, 100, 100), (15, 15), 15)
            return image
    
    def get_damage_effect(self):
        return NormalDamageEffect()


class FireBulletStrategy(BulletStrategy):
    """Strategy for fire bullets (Emberwing)"""
    
    def __init__(self, bullet_image_path):
        self.bullet_image_path = bullet_image_path
    
    def create_image(self, bullet_type):
        try:
            image = pygame.image.load(self.bullet_image_path)
            image = pygame.transform.scale(image, (40, 40))
            return image
        except (pygame.error, FileNotFoundError):
            """This error handling is fixed by ChatGPT-o4-mini-high, the fallback image is now a simple colored circle"""
            # Fallback to fire-colored circle
            image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(image, (255, 100, 0), (15, 15), 15)
            return image
    
    def get_damage_effect(self):
        return BurnDamageEffect()


class ElectricBulletStrategy(BulletStrategy):
    """Strategy for electric bullets (Volt Cow)"""
    
    def __init__(self, bullet_image_path):
        self.bullet_image_path = bullet_image_path
    
    def create_image(self, bullet_type):
        try:
            image = pygame.image.load(self.bullet_image_path)
            # Scale to appropriate size (2.5x larger)
            image = pygame.transform.scale(image, (40, 40))
            return image
        except (pygame.error, FileNotFoundError):
            """This error handling is fixed by ChatGPT-o4-mini-high, the fallback image is now a simple colored circle"""
            # Fallback to electric-colored circle
            image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(image, (255, 255, 100), (15, 15), 15)
            return image
    
    def get_damage_effect(self):
        return ElectricDamageEffect()


class BulletFactory:
    """Factory for creating different bullet types"""
    
    _strategies = {
        'Emberwing': FireBulletStrategy(str(get_bullet_path('Emberwing.png'))),
        'Volt Cow': ElectricBulletStrategy(str(get_bullet_path('Volt Cow.png'))),
        'Banana Blaster': NormalBulletStrategy(str(get_bullet_path('Banana Blaster.png'))),
        'Wood Sage': NormalBulletStrategy(str(get_bullet_path('Wood Sage.png'))),
    }
    
    @classmethod
    def create_bullet(cls, tower_name, start_pos, target, damage, enemies_group=None):
        strategy = cls._strategies.get(tower_name, NormalBulletStrategy(''))
        bullet = Bullet(start_pos, target, damage, strategy, tower_name)

        if tower_name == 'Volt Cow' and hasattr(bullet.damage_effect, 'set_enemies_group'):
            bullet.damage_effect.set_enemies_group(enemies_group)
        
        return bullet


class Bullet(pygame.sprite.Sprite):
    """Enhanced bullet class with rotation and special effects"""
    
    def __init__(self, start_pos, target, damage, strategy, bullet_type):
        super().__init__()
        self.strategy = strategy
        self.bullet_type = bullet_type

        self.base_image = strategy.create_image(bullet_type)
        self.image = self.base_image.copy()

        self.rect = self.image.get_rect(center=start_pos)
        self.pos = pygame.Vector2(self.rect.center)
        self.target = target
        self.speed = 300
        self.damage = damage

        vec = pygame.Vector2(target.rect.center) - pygame.Vector2(start_pos)
        self.dir = vec.normalize() if vec.length() else pygame.Vector2()

        self.rotation = 0
        self.rotation_speed = 360

        self.damage_effect = strategy.get_damage_effect()
    
    def update(self, dt):
        """Update bullet position and rotation"""
        self.pos += self.dir * self.speed * dt
        self.rect.center = self.pos

        self.rotation += self.rotation_speed * dt
        self.rotation %= 360

        self.image = pygame.transform.rotate(self.base_image, self.rotation)
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center

        if self.rect.colliderect(self.target.rect):
            hit_result = self.damage_effect.apply(self.target, self.damage, self.rect.center)

            self.kill()
