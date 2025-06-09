import pygame
import random
from settings import *
from enemy import EnemyFactory, EnemyWithGrid
from pathfinding import a_star
from grid import GRID_MAP

class Level:
    def __init__(self):
        self.enemies = pygame.sprite.Group()
        self.timer = 0.0
        self.delay = 0.5  # Adjusted from 0.3 to 0.5 for better balance
        self.base_hp = 10
        self.name = "Default Level"
        self.grid = None
        
        # Wave system
        self.current_wave = 1
        self.total_waves = 5  # Default total waves
        self.enemies_in_wave = 10
        self.enemies_spawned_this_wave = 0
        self.enemies_killed_this_wave = 0
        self.wave_complete = False
        self.wave_break_timer = 0.0
        self.wave_break_duration = 8.0  # Increased from 5.0 to 8.0 seconds for more building time
        self.in_wave_break = False
        
        # Preparation time system
        self.preparation_time = 10.0  # 10 seconds preparation time
        self.preparation_timer = 0.0
        self.in_preparation = True  # Start with preparation time
        self.first_wave_started = False
        
        # Enemy wave composition
        self.wave_composition = {}
        self.current_enemy_queue = []
        self.enemy_spawn_index = 0
        
        # Level settings from JSON
        self.initial_money = STARTING_MONEY
        self.enemy_speed = 50  # Base enemy speed
        self.best_time = None
        
        # Game completion state
        self.all_waves_complete = False
        
        # Remove automatic path initialization - will be called manually after grid is set
        # self.recalculate_path()  # Commented out
    
    def load_settings(self, level_data):
        """Load level settings from JSON data"""
        if 'settings' in level_data:
            settings = level_data['settings']
            self.initial_money = settings.get('initial_money', STARTING_MONEY)
            self.total_waves = settings.get('wave_count', 5)
            self.enemy_speed = settings.get('enemy_speed', 50)
            self.base_hp = settings.get('base_hp', 10)  # load custom base_hp
            self.best_time = settings.get('best_time', None)
            print(f"Level settings: Money=${self.initial_money}, Waves={self.total_waves}, Speed={self.enemy_speed}, Base HP={self.base_hp}")
        else:
            # Default settings for backward compatibility
            self.initial_money = STARTING_MONEY
            self.total_waves = 5
            self.enemy_speed = 50
            self.base_hp = 10  # default base_hp
            self.best_time = None
    
    def recalculate_path(self):
        """Recalculate path, called when the level changes"""
        # Use level-specific grid data
        grid_to_use = self.grid if self.grid is not None else GRID_MAP
        
        # Automatically find start and end points
        self.start = self.find_start_point(grid_to_use)
        self.end = self.find_end_point(grid_to_use)
        
        print(f"Level: Start point {self.start}, End point {self.end}")  # Debug info
        
        # Calculate path
        self.path = a_star(self.start, self.end, grid_to_use)
        if not self.path:
            # If pathfinding fails, create a simple straight path
            self.path = [self.start, self.end]
            print(f"Level: Pathfinding failed, using simple path")
        else:
            print(f"Level: Pathfinding successful, path length {len(self.path)}")
    
    def find_start_point(self, grid):
        """Find start point (path tile) from the first row"""
        for x in range(GRID_W):
            if grid[0][x] == 0:  # 0 indicates path
                return (x, 0)
        
        # If no path in the first row, search from the left
        for y in range(GRID_H):
            if grid[y][0] == 0:
                return (0, y)
        
        # Default start point
        return (0, 0)
    
    def find_end_point(self, grid):
        """Find end point (path tile)"""
        # Find the path point farthest from the start in the grid
        start = self.find_start_point(grid)
        max_distance = -1
        best_end = None
        
        for y in range(GRID_H):
            for x in range(GRID_W):
                if grid[y][x] == 0:  # Is path
                    # Calculate Manhattan distance
                    distance = abs(x - start[0]) + abs(y - start[1])
                    if distance > max_distance:
                        max_distance = distance
                        best_end = (x, y)
        
        if best_end:
            return best_end
        
        # If no path point found, return start point
        return start

    def prepare_wave_composition(self):
        """Prepare the enemy composition for the current wave"""
        self.wave_composition = EnemyFactory.get_wave_composition(self.current_wave, self.enemies_in_wave)
        
        # Create enemy spawn queue
        self.current_enemy_queue = []
        for enemy_type, count in self.wave_composition.items():
            for _ in range(count):
                self.current_enemy_queue.append(enemy_type)
        
        # Shuffle the queue for random spawn order
        random.shuffle(self.current_enemy_queue)
        self.enemy_spawn_index = 0
        
        print(f"Wave {self.current_wave} composition: {self.wave_composition}")

    def update(self, dt):
        # Update enemies
        self.enemies.update(dt)
        
        # Handle preparation time before first wave
        if self.in_preparation and not self.first_wave_started:
            self.preparation_timer += dt
            if self.preparation_timer >= self.preparation_time:
                self.in_preparation = False
                self.first_wave_started = True
                print(f"Preparation time complete! Wave {self.current_wave} starting!")
        
        # Count living enemies (not dead or reached end)
        living_enemies = [e for e in self.enemies if hasattr(e, 'health') and e.health > 0]
        
        # Check if current wave is complete
        if (not self.wave_complete and 
            self.enemies_spawned_this_wave >= self.enemies_in_wave and 
            len(living_enemies) == 0):
            self.wave_complete = True
            self.in_wave_break = True
            self.wave_break_timer = 0.0
            print(f"Wave {self.current_wave} completed! All {self.enemies_in_wave} enemies defeated!")
        
        # Check if all waves are complete
        if self.wave_complete and self.current_wave >= self.total_waves:
            self.all_waves_complete = True
        
        # Handle wave break
        if self.in_wave_break and not self.all_waves_complete:
            self.wave_break_timer += dt
            if self.wave_break_timer >= self.wave_break_duration:
                # Start next wave
                self.current_wave += 1
                self.enemies_in_wave = int(20 + (self.current_wave - 1) * 8)  # Increased from 10 + 5 to 20 + 8
                self.delay = max(0.3, 0.5 - (self.current_wave - 1) * 0.03)  # Slightly slower progression
                self.enemies_spawned_this_wave = 0
                self.enemies_killed_this_wave = 0
                self.wave_complete = False
                self.in_wave_break = False
                self.timer = 0.0
                
                # Prepare new wave composition
                self.prepare_wave_composition()
                
                print(f"Wave {self.current_wave} starting! {self.enemies_in_wave} enemies, {self.delay:.2f}s delay")
        
        # Spawn enemies if not in wave break, not in preparation, and haven't spawned all enemies for this wave
        if (not self.in_wave_break and not self.in_preparation and 
            self.enemies_spawned_this_wave < self.enemies_in_wave and not self.all_waves_complete):
            self.timer += dt
            if self.timer >= self.delay:
                self.timer -= self.delay
                
                # Spawn enemy from the queue
                if self.enemy_spawn_index < len(self.current_enemy_queue):
                    enemy_type = self.current_enemy_queue[self.enemy_spawn_index]
                    self.enemy_spawn_index += 1
                    
                    # Create enemy with start and end points
                    if self.start and self.end:
                        # Use factory to create the appropriate enemy type
                        if hasattr(self, 'grid') and self.grid is not None:
                            # Calculate path for this specific enemy
                            path = a_star(self.start, self.end, self.grid)
                            if path:
                                enemy = EnemyFactory.create_enemy(enemy_type, path, None, self.current_wave)
                            else:
                                print(f"Failed to create path for {enemy_type}, skipping")
                                return
                        else:
                            # Use global grid
                            enemy = EnemyFactory.create_enemy(enemy_type, self.start, self.end, self.current_wave)
                        
                        # Apply level-specific enemy speed scaling (if different from default)
                        if self.enemy_speed != 50:  # Only apply if different from default base speed
                            speed_scale = self.enemy_speed / 50.0
                            enemy.speed = int(enemy.original_speed * speed_scale)
                            enemy.original_speed = enemy.speed
                        
                        # Set kill callback if available
                        if hasattr(self, 'kill_callback') and self.kill_callback:
                            enemy.kill_callback = self.kill_callback
                        
                        self.enemies.add(enemy)
                        self.enemies_spawned_this_wave += 1
                        print(f"Spawned {enemy_type} {self.enemies_spawned_this_wave}/{self.enemies_in_wave}")
        
        # Note: Enemy end-reached logic moved to game.py for HOME animation integration

    def start_first_wave(self):
        """Initialize the first wave composition"""
        if not hasattr(self, 'wave_composition') or not self.wave_composition:
            self.prepare_wave_composition()

    def draw(self, surf):
        for e in self.enemies:
            # Use new version enemy's draw method
            if hasattr(e, 'draw'):
                e.draw(surf)
            else:
                # Compatibility with old version enemy's draw
                surf.blit(e.image, e.rect)
                
                # Draw health bar
                if hasattr(e, 'hp') and hasattr(e, 'max_hp'):
                    hb_w = getattr(e, 'size', GRID_SIZE-8)
                    x, y = e.rect.x, e.rect.y-6
                    back = pygame.Rect(x, y, hb_w, 4)
                    front = pygame.Rect(x, y, int(hb_w * e.hp / e.max_hp), 4)
                    pygame.draw.rect(surf, RED, back)
                    pygame.draw.rect(surf, GREEN, front)
                elif hasattr(e, 'health') and hasattr(e, 'max_health'):
                    hb_w = GRID_SIZE-8
                    x, y = e.rect.x, e.rect.y-6
                    back = pygame.Rect(x, y, hb_w, 4)
                    front = pygame.Rect(x, y, int(hb_w * e.health / e.max_health), 4)
                    pygame.draw.rect(surf, RED, back)
                    pygame.draw.rect(surf, GREEN, front)
                
                # Flash effect
                if hasattr(e, 'hit_flash') and e.hit_flash > 0:
                    overlay = pygame.Surface((e.rect.w, e.rect.h), pygame.SRCALPHA)
                    overlay.fill((255, 255, 255, 120))
                    surf.blit(overlay, e.rect.topleft)
                elif hasattr(e, 'flash_time') and e.flash_time > 0:
                    overlay = pygame.Surface((e.rect.w, e.rect.h), pygame.SRCALPHA)
                    overlay.fill((255, 255, 255, 120))
                    surf.blit(overlay, e.rect.topleft)

    def set_kill_callback(self, callback):
        """Set the kill reward callback function"""
        self.kill_callback = callback
