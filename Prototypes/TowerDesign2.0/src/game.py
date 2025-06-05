import sys
import pygame
import json
import time
import math  # Add math import
import os
from settings import *
from menu import MainMenu, LevelSelector, show_level_creator_message
from level_creator import run_level_creator
from grid import GRID_MAP, update_grid_map
from map_component import MapComponent
from level import Level
from tower import TowerFactory
from bullet import Bullet

class Game:
    def __init__(self):
        self.state = "menu"  # menu, level_select, playing, creator
        self.current_level_file = None
        
    def load_level_from_file(self, level_file):
        try:
            with open(level_file, 'r', encoding='utf-8') as f:
                level_data = json.load(f)
        except UnicodeDecodeError:
            try:
                with open(level_file, 'r', encoding='utf-8-sig') as f:
                    level_data = json.load(f)
            except Exception as e:
                print(f"Error loading level {level_file}: {e}")
                return None
        except Exception as e:
            print(f"Error loading level {level_file}: {e}")
            return None
                
        # Check if level data is valid
        if 'grid' not in level_data:
            print(f"Game: Warning - Level file {level_file} has no grid data")
            return None
            
        # Check if grid size is correct
        grid = level_data['grid']
        if len(grid) != GRID_H or any(len(row) != GRID_W for row in grid):
            print(f"Game: Error - Level file {level_file} has incorrect grid size")
            return None
            
        # Update global grid map
        update_grid_map(grid)
        print(f"Game: Loaded level '{level_data.get('name', level_file)}'")
        print(f"Game: Grid size {len(grid[0])} x {len(grid)}")
                        
        return level_data
    
    def save_best_time(self, level_file, new_time):
        """Save a new best time to the level file"""
        try:
            with open(level_file, 'r', encoding='utf-8') as f:
                level_data = json.load(f)
            
            # Update best time
            if 'settings' not in level_data:
                level_data['settings'] = {}
            
            level_data['settings']['best_time'] = new_time
            
            # Save back to file
            with open(level_file, 'w', encoding='utf-8') as f:
                json.dump(level_data, f, indent=2, ensure_ascii=False)
            
            print(f"New best time saved: {new_time:.2f}s")
            return True
        except Exception as e:
            print(f"Error saving best time: {e}")
            return False
    
    def run_game_loop(self, level_data):
        level = Level()
        # Initialize Level with loaded level data BEFORE calling recalculate_path
        if 'name' in level_data:
            level.name = level_data['name']
        if 'grid' in level_data:
            level.grid = level_data['grid']
        
        # Load level settings
        level.load_settings(level_data)
        
        # NOW call recalculate_path with the correct grid data
        level.recalculate_path()
        
        # Initialize first wave composition
        level.start_first_wave()
        
        # Initialize MapComponent with the correct grid data
        game_map = MapComponent(grid=level.grid)
        
        # Set spawn and home for map component
        game_map.set_spawn_and_home(level.start, level.end)
        
        towers = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        sel = None
        game_over = False
        game_won = False
        money = level.initial_money  # Use level-specific initial money
        selected_tower = None
        current_screen_size = screen.get_size()
        
        # Game timing
        start_time = time.time()
        current_game_time = 0.0
        is_new_best_time = False
        
        # Wave completion message display
        wave_message = ""
        wave_message_timer = 0.0
        wave_message_duration = 3.0  # Show for 3 seconds
        
        # Kill reward callback function
        def on_enemy_killed(enemy):
            nonlocal money
            # Use enemy-specific reward if available, otherwise use default KILL_REWARD
            reward = getattr(enemy, 'reward', KILL_REWARD)
            money += reward
            print(f"{getattr(enemy, 'enemy_type', 'Enemy')} killed! Reward: +${reward}")
        
        # Set kill callback for level
        level.set_kill_callback(on_enemy_killed)
        
        # Toolbar settings will be dynamically calculated in draw_enhanced_toolbar
        
        running = True
        while running:
            dt = clock.tick(FPS)/1000.0
            mouse_pos = pygame.mouse.get_pos()
            current_screen_size = screen.get_size()
            
            # Update game time if game is running
            if not game_over and not game_won:
                current_game_time = time.time() - start_time
            
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return "quit"
                elif ev.type == pygame.VIDEORESIZE:
                    # Handle window resizing
                    new_width = max(ev.w, MIN_SCREEN_W)
                    new_height = max(ev.h, MIN_SCREEN_H)
                    pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE | pygame.DOUBLEBUF)
                    current_screen_size = (new_width, new_height)
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        return "menu"
                    elif ev.key == pygame.K_F11:
                        # Toggle fullscreen
                        pygame.display.toggle_fullscreen()
                elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    mx, my = ev.pos
                    screen_w, screen_h = current_screen_size

                    # Check back button (top right corner)
                    back_button_rect = pygame.Rect(screen_w - 120, 10, 100, 35)
                    if back_button_rect.collidepoint(mx, my):
                        return "menu"

                    # Allow interaction only if the game is not over
                    if not game_over and not game_won:
                        # Check UI area click
                        if my < UI_HEIGHT:
                            # Get toolbar button info
                            toolbar_info = self.get_toolbar_layout(screen_w, screen_h)
                            
                            # Check tower build buttons - FIXED: break is now inside the if condition
                            for button_info in toolbar_info['tower_buttons']:
                                if button_info['rect'].collidepoint(mx, my):
                                    if money >= TOWER_COSTS[button_info['type']['name']]:
                                        sel = button_info['type']
                                        # Reset demolish mode
                                        selected_tower = None
                                    break  # Only break when a button is actually clicked
                            
                            # Check demolish button
                            if toolbar_info['demolish_button']['rect'].collidepoint(mx, my):
                                if selected_tower is None:
                                    selected_tower = "demolish_mode"
                                else:
                                    selected_tower = None
                                sel = None
                        else:
                            # Game area click
                            gx, gy = px_to_grid(mx, my, screen_w, screen_h)
                            if 0 <= gx < GRID_W and 0 <= gy < GRID_H:
                                # Demolish mode
                                if selected_tower == "demolish_mode":
                                    # Find tower at this position
                                    for tower in towers:
                                        if tower.gx == gx and tower.gy == gy:
                                            # Demolish tower and refund some money
                                            refund = TOWER_COSTS[tower.tower_type['name']] // 2
                                            money += refund
                                            tower.kill()
                                            selected_tower = None
                                            break
                                # Build mode - USE LEVEL GRID DATA INSTEAD OF GRID_MAP
                                elif level.grid and level.grid[gy][gx] == 1 and sel:  # 1 = grass, 0 = path
                                    # Check if there is already a tower at this position
                                    can_build = True
                                    for tower in towers:
                                        if tower.gx == gx and tower.gy == gy:
                                            can_build = False
                                            break
                                    
                                    if can_build and money >= TOWER_COSTS[sel['name']]:
                                        money -= TOWER_COSTS[sel['name']]
                                        towers.add(TowerFactory.create_tower(sel, gx, gy))
                                        sel = None

            # Update game logic only if the game is not over
            if not game_over and not game_won:
                # Store previous wave state to detect completion
                prev_wave_complete = level.wave_complete
                prev_wave = level.current_wave
                
                # Update map component with enemy status and time
                game_map.update(dt, level.enemies)
                
                level.update(dt)
                bullets.update(dt)
                towers.update(dt, level.enemies, bullets)
                
                # Check if enemies have reached the end and trigger HOME hit animation
                for e in list(level.enemies):
                    # Check new version enemy's end reached logic
                    if hasattr(e, 'path_index') and e.path_index >= len(e.path) - 1:
                        # Trigger HOME hit animation before removing enemy
                        game_map.on_home_hit()
                        level.base_hp -= 1
                        # Clean up speed modifiers
                        if hasattr(e, 'cleanup_speed_modifiers'):
                            e.cleanup_speed_modifiers()
                        e.kill()
                        print(f"Enemy reached HOME! Base HP: {level.base_hp}")
                    # Compatibility with old version enemy
                    elif hasattr(e, 'reached_end') and e.reached_end:
                        # Trigger HOME hit animation before removing enemy
                        game_map.on_home_hit()
                        level.base_hp -= getattr(e, 'damage_to_base', 1)
                        # Clean up speed modifiers
                        if hasattr(e, 'cleanup_speed_modifiers'):
                            e.cleanup_speed_modifiers()
                        e.kill()
                        print(f"Enemy reached HOME! Base HP: {level.base_hp}")
                
                # Check for wave completion reward - trigger when wave becomes complete
                if level.wave_complete and not prev_wave_complete:
                    # Wave just completed, give reward immediately
                    money += WAVE_REWARD
                    wave_message = f"Wave {level.current_wave} Complete! Bonus: +${WAVE_REWARD}"
                    wave_message_timer = 0.0
                    print(f"Wave {level.current_wave} completed! Bonus: +${WAVE_REWARD}")
                
                # Check game over condition
                if level.base_hp <= 0:
                    game_over = True
                
                # Check victory condition - all waves complete
                if level.all_waves_complete:
                    game_won = True
                    final_time = current_game_time
                    
                    # Check if this is a new best time
                    if level.best_time is None or final_time < level.best_time:
                        is_new_best_time = True
                        if self.current_level_file:
                            self.save_best_time(self.current_level_file, final_time)
                    else:
                        is_new_best_time = False
            
            # Update wave message timer
            if wave_message:
                wave_message_timer += dt
                if wave_message_timer >= wave_message_duration:
                    wave_message = ""

            # Draw screen elements
            current_screen = pygame.display.get_surface()
            current_screen.fill(BG_COLOUR)
            
            # Draw map
            game_map.draw(current_screen)
            
            # Draw level
            level.draw(current_screen)
            
            # Draw towers
            for tower in towers:
                tower.draw(current_screen)
            
            # Draw bullets
            bullets.draw(current_screen)
            
            # Draw UI
            self.draw_enhanced_toolbar(current_screen, current_screen_size, sel, selected_tower, money, level.base_hp, level.name, level)
            
            # Draw wave panel with updated format
            self.draw_wave_panel_with_timing(current_screen, current_screen_size, level, current_game_time)
            
            # Draw wave completion message if active
            if wave_message:
                self.draw_wave_message(current_screen, current_screen_size, wave_message)
            
            # Draw game over screen if applicable
            if game_over:
                self.draw_game_over_screen(current_screen, current_screen_size, victory=False)
            elif game_won:
                self.draw_victory_screen(current_screen, current_screen_size, current_game_time, level.best_time, is_new_best_time)
            
            pygame.display.flip()
        
        return "menu"
    
    def get_toolbar_layout(self, screen_w, screen_h):
        """Get toolbar layout information for current screen size - vertical card style"""
        toolbar_margin = 15
        card_width = 120
        card_height = 90
        card_spacing = 10
        
        # Calculate how many cards fit horizontally
        available_width = screen_w - 350  # Leave space for info panel
        cards_per_row = max(1, available_width // (card_width + card_spacing))
        
        # Create tower building buttons in card grid
        tower_buttons = []
        for i, tower_type in enumerate(TOWER_TYPES):
            row = i // cards_per_row
            col = i % cards_per_row
            
            x = toolbar_margin + col * (card_width + card_spacing)
            y = toolbar_margin + row * (card_height + card_spacing)
            
            # Make sure cards fit within UI_HEIGHT
            if y + card_height <= UI_HEIGHT - toolbar_margin:
                button_rect = pygame.Rect(x, y, card_width, card_height)
                tower_buttons.append({
                    'rect': button_rect,
                    'type': tower_type
                })
        
        # Demolish button - positioned at the end
        last_tower_row = (len(TOWER_TYPES) - 1) // cards_per_row
        last_tower_col = (len(TOWER_TYPES) - 1) % cards_per_row
        
        demolish_x = toolbar_margin + (last_tower_col + 1) * (card_width + card_spacing)
        demolish_y = toolbar_margin + last_tower_row * (card_height + card_spacing)
        
        # If demolish button would go off screen, put it on next row
        if demolish_x + card_width > available_width:
            demolish_x = toolbar_margin
            demolish_y += card_height + card_spacing
        
        demolish_button = {
            'rect': pygame.Rect(demolish_x, demolish_y, card_width, card_height)
        }
        
        return {
            'tower_buttons': tower_buttons,
            'demolish_button': demolish_button
        }

    def draw_enhanced_toolbar(self, screen, screen_size, selected_type, selected_tower, money, base_hp, level_name, level):
        """Draw enhanced toolbar with improved readability and aesthetics"""
        screen_w, screen_h = screen_size
        
        # Dynamic timing for animations
        time_factor = pygame.time.get_ticks() / 1000.0
        
        # Sophisticated toolbar background
        toolbar_rect = pygame.Rect(0, 0, screen_w, UI_HEIGHT)
        
        # Create elegant gradient background
        toolbar_surface = pygame.Surface((screen_w, UI_HEIGHT), pygame.SRCALPHA)
        for i in range(UI_HEIGHT):
            progress = i / UI_HEIGHT
            alpha = 240 - progress * 20
            bg_color = (25, 35, 45, int(alpha))  # Rich dark blue
            pygame.draw.line(toolbar_surface, bg_color, (0, i), (screen_w, i))
        
        screen.blit(toolbar_surface, (0, 0))
        
        # Elegant border
        border_pulse = 0.8 + 0.2 * math.sin(time_factor * 2)
        border_alpha = int(120 * border_pulse)
        pygame.draw.line(screen, (100, 150, 200, border_alpha), (0, UI_HEIGHT-2), (screen_w, UI_HEIGHT-2), 3)
        
        # Get layout information
        layout = self.get_toolbar_layout(screen_w, screen_h)
        
        # Enhanced tower building buttons - Card Style
        mx, my = pygame.mouse.get_pos()
        
        for button_info in layout['tower_buttons']:
            tower_type = button_info['type']
            rect = button_info['rect']
            
            # Check states
            is_selected = selected_type == tower_type
            can_afford = money >= TOWER_COSTS[tower_type['name']]
            is_hovered = rect.collidepoint(mx, my) and my < UI_HEIGHT
            
            # Enhanced card appearance
            if is_selected:
                bg_color = (80, 120, 160, 220)  # Rich blue selection
                glow_color = (120, 180, 255, 120)
                border_color = (150, 200, 255)
            elif not can_afford:
                bg_color = (40, 40, 50, 180)    # Dark disabled
                glow_color = None
                border_color = (80, 80, 90)
            elif is_hovered:
                bg_color = (60, 90, 120, 200)   # Medium blue hover
                glow_color = (100, 150, 200, 100)
                border_color = (120, 170, 220)
            else:
                bg_color = (45, 60, 75, 180)    # Default blue-gray
                glow_color = None
                border_color = (90, 120, 150)
            
            # Card glow effect
            if glow_color:
                for i in range(8, 0, -1):
                    glow_alpha = glow_color[3] * (i / 8) // 4
                    glow_rect = pygame.Rect(rect.x - i, rect.y - i, rect.width + i*2, rect.height + i*2)
                    glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                    glow_surface.fill((*glow_color[:3], glow_alpha))
                    screen.blit(glow_surface, (glow_rect.x, glow_rect.y))
            
            # Draw enhanced card with rounded corners
            card_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            
            # Create rounded rectangle effect
            for i in range(rect.height):
                progress = i / rect.height
                alpha = bg_color[3] + int(20 * math.sin(progress * math.pi))
                alpha = min(255, max(0, alpha))
                line_color = (*bg_color[:3], alpha)
                pygame.draw.line(card_surface, line_color, (5, i), (rect.width - 5, i))
            
            screen.blit(card_surface, (rect.x, rect.y))
            
            # Enhanced border with rounded corners
            pygame.draw.rect(screen, border_color, rect, 3, border_radius=12)
            
            # Tower icon with enhanced effects
            center_x = rect.centerx
            icon_y = rect.y + 25
            
            # Icon background circle
            icon_bg_color = tower_type['color'] if can_afford else (80, 80, 90)
            if is_selected or is_hovered:
                for radius in range(18, 14, -1):
                    glow_alpha = 40 if is_selected else 25
                    pygame.draw.circle(screen, (*icon_bg_color, glow_alpha), (center_x, icon_y), radius)
            
            # Main icon circle
            pygame.draw.circle(screen, icon_bg_color, (center_x, icon_y), 14)
            pygame.draw.circle(screen, WHITE if can_afford else (120, 120, 130), (center_x, icon_y), 14, 2)
            
            # Tower name with enhanced styling
            name_color = WHITE if can_afford else (120, 120, 130)
            name_text = FONTS['small'].render(tower_type['name'], True, (0, 0, 0))
            screen.blit(name_text, (center_x - name_text.get_width()//2 + 1, icon_y + 22))
            name_text = FONTS['small'].render(tower_type['name'], True, name_color)
            screen.blit(name_text, (center_x - name_text.get_width()//2, icon_y + 21))
            
            # Enhanced price display
            cost_color = (100, 255, 150) if can_afford else (255, 120, 120)
            cost_text = FONTS['small'].render(f"${TOWER_COSTS[tower_type['name']]}", True, (0, 0, 0))
            screen.blit(cost_text, (center_x - cost_text.get_width()//2 + 1, icon_y + 38))
            cost_text = FONTS['small'].render(f"${TOWER_COSTS[tower_type['name']]}", True, cost_color)
            screen.blit(cost_text, (center_x - cost_text.get_width()//2, icon_y + 37))
            
            # Tower description (smaller text)
            desc_color = (200, 200, 210) if can_afford else (100, 100, 110)
            desc_text = tower_type.get('description', '')
            if len(desc_text) > 15:  # Truncate long descriptions
                desc_text = desc_text[:12] + "..."
            desc_surface = FONTS['tiny'].render(desc_text, True, desc_color)
            desc_x = center_x - desc_surface.get_width() // 2
            desc_y = rect.y + rect.height - 15
            screen.blit(desc_surface, (desc_x, desc_y))
        
        # Enhanced demolish button - Card Style
        demolish_rect = layout['demolish_button']['rect']
        is_demolish_active = selected_tower == "demolish_mode"
        is_demolish_hovered = demolish_rect.collidepoint(mx, my) and my < UI_HEIGHT
        
        if is_demolish_active:
            bg_color = (160, 80, 80, 220)   # Red active
            glow_color = (255, 120, 120, 120)
            border_color = (255, 150, 150)
        elif is_demolish_hovered:
            bg_color = (120, 60, 60, 200)   # Dark red hover
            glow_color = (200, 100, 100, 100)
            border_color = (200, 120, 120)
        else:
            bg_color = (80, 45, 45, 180)    # Dark red default
            glow_color = None
            border_color = (120, 80, 80)
        
        # Demolish card glow
        if glow_color:
            for i in range(8, 0, -1):
                glow_alpha = glow_color[3] * (i / 8) // 4
                glow_rect = pygame.Rect(demolish_rect.x - i, demolish_rect.y - i, 
                                      demolish_rect.width + i*2, demolish_rect.height + i*2)
                glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                glow_surface.fill((*glow_color[:3], glow_alpha))
                screen.blit(glow_surface, (glow_rect.x, glow_rect.y))
        
        # Draw demolish card
        demolish_surface = pygame.Surface((demolish_rect.width, demolish_rect.height), pygame.SRCALPHA)
        for i in range(demolish_rect.height):
            progress = i / demolish_rect.height
            alpha = bg_color[3] + int(20 * math.sin(progress * math.pi))
            alpha = min(255, max(0, alpha))
            line_color = (*bg_color[:3], alpha)
            pygame.draw.line(demolish_surface, line_color, (5, i), (demolish_rect.width - 5, i))
        
        screen.blit(demolish_surface, (demolish_rect.x, demolish_rect.y))
        pygame.draw.rect(screen, border_color, demolish_rect, 3, border_radius=12)
        
        # Enhanced demolish icon
        center_x, center_y = demolish_rect.center
        icon_y = demolish_rect.y + 25
        
        # Hammer icon with glow
        if is_demolish_active:
            pygame.draw.circle(screen, (255, 150, 150, 50), (center_x, icon_y), 17)
        
        pygame.draw.circle(screen, (220, 100, 100), (center_x, icon_y), 10)
        pygame.draw.rect(screen, (180, 80, 80), (center_x - 2, icon_y, 4, 20))
        
        # Enhanced demolish text
        demolish_text = FONTS['small'].render("Demolish", True, (0, 0, 0))
        screen.blit(demolish_text, (center_x - demolish_text.get_width()//2 + 1, icon_y + 22))
        demolish_text = FONTS['small'].render("Demolish", True, WHITE)
        screen.blit(demolish_text, (center_x - demolish_text.get_width()//2, icon_y + 21))
        
        refund_text = FONTS['tiny'].render("50% refund", True, (0, 0, 0))
        screen.blit(refund_text, (center_x - refund_text.get_width()//2 + 1, demolish_rect.y + demolish_rect.height - 14))
        refund_text = FONTS['tiny'].render("50% refund", True, (255, 200, 120))
        screen.blit(refund_text, (center_x - refund_text.get_width()//2, demolish_rect.y + demolish_rect.height - 15))
        
        # Enhanced game info panel
        info_panel_x = screen_w - 320
        info_panel_w = 300
        info_panel_rect = pygame.Rect(info_panel_x, 10, info_panel_w, UI_HEIGHT - 20)
        
        # Info panel background
        info_surface = pygame.Surface((info_panel_w, UI_HEIGHT - 20), pygame.SRCALPHA)
        for i in range(UI_HEIGHT - 20):
            progress = i / (UI_HEIGHT - 20)
            alpha = 200 - progress * 30
            bg_color = (30, 45, 60, int(alpha))
            pygame.draw.line(info_surface, bg_color, (0, i), (info_panel_w, i))
        
        screen.blit(info_surface, (info_panel_x, 10))
        pygame.draw.rect(screen, (80, 120, 160, 150), info_panel_rect, 2, border_radius=10)
        
        # Enhanced info text with shadows
        def draw_info_text(text, color, x, y):
            shadow_text = FONTS['hud'].render(text, True, (0, 0, 0))
            screen.blit(shadow_text, (x + 1, y + 1))
            main_text = FONTS['hud'].render(text, True, color)
            screen.blit(main_text, (x, y))
        
        # Money with dynamic color
        money_color = (150, 255, 150) if money >= 50 else (255, 200, 100) if money >= 20 else (255, 150, 150)
        draw_info_text(f"Money: ${money}", money_color, info_panel_x + 15, 30)
        
        # Base health with warning colors
        hp_color = (150, 255, 150) if base_hp > 7 else (255, 200, 100) if base_hp > 3 else (255, 120, 120)
        draw_info_text(f"Base HP: {base_hp}", hp_color, info_panel_x + 15, 55)
        
        # Level name
        draw_info_text(f"Level: {level_name}", (180, 220, 255), info_panel_x + 15, 80)
        
        # Enhanced game title
        title_shadow = FONTS['hud'].render("Forest Guard", True, (0, 0, 0))
        screen.blit(title_shadow, (21, 21))
        title_text = FONTS['hud'].render("Forest Guard", True, (100, 200, 150))
        screen.blit(title_text, (20, 20))
        
        # Enhanced control hints
        help_shadow = FONTS['tiny'].render("ESC: Menu", True, (0, 0, 0))
        screen.blit(help_shadow, (21, UI_HEIGHT - 24))
        help_text = FONTS['tiny'].render("ESC: Menu", True, (180, 180, 200))
        screen.blit(help_text, (20, UI_HEIGHT - 25))

    def draw_wave_panel(self, screen, screen_size, level):
        """Draw wave information panel on top of everything"""
        screen_w, screen_h = screen_size
        
        # Wave information panel (bottom-left area)
        wave_panel_x = 20
        wave_panel_y = screen_h - 80  # Position near bottom of screen
        wave_panel_w = 300
        wave_panel_h = 60
        wave_panel_rect = pygame.Rect(wave_panel_x, wave_panel_y, wave_panel_w, wave_panel_h)
        pygame.draw.rect(screen, UI_MID_BG, wave_panel_rect, border_radius=8)
        pygame.draw.rect(screen, UI_ACCENT, wave_panel_rect, 2, border_radius=8)
        
        # Wave title
        wave_title = FONTS['button'].render(f"Wave {level.current_wave}", True, UI_ACCENT)
        screen.blit(wave_title, (wave_panel_x + 10, wave_panel_y + 5))
        
        # Wave progress
        if level.in_wave_break:
            # Show countdown during wave break
            time_left = level.wave_break_duration - level.wave_break_timer
            countdown_text = FONTS['small'].render(f"Next wave in: {time_left:.1f}s", True, UI_WARNING)
            screen.blit(countdown_text, (wave_panel_x + 10, wave_panel_y + 30))
        else:
            # Show enemy progress during wave
            living_enemies = len([e for e in level.enemies if hasattr(e, 'health') and e.health > 0])
            progress_text = FONTS['small'].render(f"Enemies: {level.enemies_spawned_this_wave}/{level.enemies_in_wave} (Alive: {living_enemies})", True, WHITE)
            screen.blit(progress_text, (wave_panel_x + 10, wave_panel_y + 30))

    def draw_wave_message(self, screen, screen_size, message):
        """Draw elegant wave completion message with sophisticated effects"""
        screen_w, screen_h = screen_size
        
        # Dynamic timing for smooth animations
        time_factor = pygame.time.get_ticks() / 1000.0
        
        # Calculate text dimensions
        main_text = FONTS['title'].render(message, True, WHITE)
        text_w, text_h = main_text.get_size()
        
        # Elegant scaling animation - starts small and grows
        scale_factor = min(1.0, (time_factor * 2) % 3.0)  # Reset every 3 seconds
        if scale_factor < 0.3:
            scale_progress = scale_factor / 0.3
            panel_scale = 0.3 + 0.7 * (1 - math.cos(scale_progress * math.pi)) / 2
        else:
            panel_scale = 1.0
        
        # Panel dimensions with elegant proportions
        base_padding = 50
        panel_w = int((text_w + base_padding * 2) * panel_scale)
        panel_h = int((text_h + base_padding * 2) * panel_scale)
        panel_x = (screen_w - panel_w) // 2
        panel_y = (screen_h - panel_h) // 2 - 50  # Slightly above center
        
        # Subtle background overlay - much more gentle
        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay_alpha = int(40 + 15 * math.sin(time_factor * 2))
        overlay.fill((10, 30, 10, overlay_alpha))  # Very dark green tint
        screen.blit(overlay, (0, 0))
        
        # Elegant gradient panel with gold/white theme
        panel_surface = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        
        # Create sophisticated gradient
        for i in range(panel_h):
            progress = i / panel_h
            # Elegant white to light gold gradient
            alpha = int(220 - progress * 40)
            gold_intensity = int(40 + progress * 30)
            bg_color = (40 + gold_intensity, 40 + gold_intensity, 40, alpha)
            pygame.draw.line(panel_surface, bg_color, (0, i), (panel_w, i))
        
        screen.blit(panel_surface, (panel_x, panel_y))
        
        # Elegant animated border with soft gold
        border_pulse = 0.7 + 0.3 * math.sin(time_factor * 3)
        border_alpha = int(180 * border_pulse)
        border_color = (220, 180, 100, border_alpha)  # Soft gold
        
        # Multiple border layers for depth
        for thickness in [4, 2, 1]:
            border_alpha_layer = int(border_alpha * (thickness / 4))
            border_color_layer = (220, 180, 100, border_alpha_layer)
            pygame.draw.rect(screen, border_color_layer, 
                           (panel_x - thickness, panel_y - thickness, 
                            panel_w + thickness*2, panel_h + thickness*2), 
                           thickness, border_radius=15 + thickness)
        
        # Soft glow effect around panel
        glow_intensity = 0.3 + 0.2 * math.sin(time_factor * 2.5)
        for i in range(12, 0, -1):
            glow_alpha = int(15 * glow_intensity * (i / 12))
            glow_rect = pygame.Rect(panel_x - i*2, panel_y - i*2, panel_w + i*4, panel_h + i*4)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            glow_surface.fill((255, 220, 150, glow_alpha))  # Warm golden glow
            screen.blit(glow_surface, (glow_rect.x, glow_rect.y))
        
        # Text with elegant shadow and outline
        text_x = panel_x + (panel_w - text_w) // 2
        text_y = panel_y + (panel_h - text_h) // 2
        
        # Soft shadow layers
        for offset in range(3, 0, -1):
            shadow_alpha = 120 - offset * 30
            shadow_text = FONTS['title'].render(message, True, (0, 0, 0, shadow_alpha))
            screen.blit(shadow_text, (text_x + offset, text_y + offset))
        
        # Elegant outline - much subtler
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    outline_text = FONTS['title'].render(message, True, (50, 50, 50, 180))
                    screen.blit(outline_text, (text_x + dx, text_y + dy))
        
        # Main text with soft golden tint
        text_color = (255, 250, 240)  # Warm white
        main_text_render = FONTS['title'].render(message, True, text_color)
        screen.blit(main_text_render, (text_x, text_y))
        
        # Elegant sparkle effects around the text
        sparkle_count = 8
        for i in range(sparkle_count):
            angle = (time_factor * 2 + i * math.pi * 2 / sparkle_count) % (math.pi * 2)
            radius = 80 + 20 * math.sin(time_factor * 3 + i)
            sparkle_x = panel_x + panel_w // 2 + radius * math.cos(angle)
            sparkle_y = panel_y + panel_h // 2 + radius * math.sin(angle)
            
            sparkle_alpha = int(100 + 80 * math.sin(time_factor * 4 + i))
            sparkle_size = 2 + int(2 * math.sin(time_factor * 5 + i))
            
            # Draw elegant star-like sparkles
            if sparkle_alpha > 50:
                sparkle_color = (255, 220, 100, sparkle_alpha)
                # Create a cross pattern for sparkle
                pygame.draw.circle(screen, sparkle_color, (int(sparkle_x), int(sparkle_y)), sparkle_size)
                # Add sparkle lines
                line_length = sparkle_size * 2
                pygame.draw.line(screen, sparkle_color, 
                               (sparkle_x - line_length, sparkle_y), 
                               (sparkle_x + line_length, sparkle_y), 1)
                pygame.draw.line(screen, sparkle_color, 
                               (sparkle_x, sparkle_y - line_length), 
                               (sparkle_x, sparkle_y + line_length), 1)

    def draw_game_over_screen(self, screen, screen_size, victory=False):
        """Draw game over screen with clear text and dynamic background"""
        screen_w, screen_h = screen_size
        
        # Dynamic timing
        time_factor = pygame.time.get_ticks() / 1000.0
        
        # Strong overlay for background contrast
        overlay_alpha = int(150 + 30 * math.sin(time_factor * 2))
        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        if victory:
            overlay.fill((0, 50, 0, overlay_alpha))  # Green tint for victory
        else:
            overlay.fill((50, 0, 0, overlay_alpha))  # Red tint for defeat
        screen.blit(overlay, (0, 0))
        
        # Content setup
        if victory:
            title_text = "VICTORY!"
            title_color = (100, 255, 100)  # Bright green
            subtitle = "Mission Accomplished"
            bg_color = (0, 80, 0)
        else:
            title_text = "GAME OVER"
            title_color = (255, 100, 100)  # Bright red
            subtitle = "Base Destroyed"
            bg_color = (80, 0, 0)
        
        # Dynamic panel sizing
        title_size = FONTS['title'].size(title_text)
        subtitle_size = FONTS['hud'].size(subtitle)
        instruction_size = FONTS['button'].size("Press ESC to return to menu")
        
        max_width = max(title_size[0], subtitle_size[0], instruction_size[0])
        panel_w = max_width + 120
        panel_h = 250
        
        # Breathing effect for panel
        breath = 1.0 + 0.05 * math.sin(time_factor * 3)
        panel_w = int(panel_w * breath)
        panel_h = int(panel_h * breath)
        
        panel_x = (screen_w - panel_w) // 2
        panel_y = (screen_h - panel_h) // 2
        
        # Multi-layer background panel
        
        # Background panel with strong contrast
        panel_surface = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        for i in range(panel_h):
            alpha = 220 - (i / panel_h) * 30
            color = (*bg_color, int(alpha))
            pygame.draw.line(panel_surface, color, (0, i), (panel_w, i))
        
        screen.blit(panel_surface, (panel_x, panel_y))
        
        # Animated border
        border_intensity = int(150 + 50 * math.sin(time_factor * 4))
        border_color = (*title_color[:2], border_intensity) if len(title_color) == 3 else title_color
        pygame.draw.rect(screen, border_color, (panel_x, panel_y, panel_w, panel_h), 5, border_radius=20)
        
        # Inner glow
        pygame.draw.rect(screen, (255, 255, 255, 80), (panel_x + 3, panel_y + 3, panel_w - 6, panel_h - 6), 3, border_radius=17)
        
        # Title with strong outline and shadow
        title_y = panel_y + 50
        
        # Shadow
        shadow_text = FONTS['title'].render(title_text, True, (0, 0, 0))
        screen.blit(shadow_text, (screen_w // 2 - title_size[0] // 2 + 3, title_y + 3))
        
        # Outline
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                if dx != 0 or dy != 0:
                    outline_text = FONTS['title'].render(title_text, True, (0, 0, 0))
                    screen.blit(outline_text, (screen_w // 2 - title_size[0] // 2 + dx, title_y + dy))
        
        # Main title
        title = FONTS['title'].render(title_text, True, title_color)
        screen.blit(title, (screen_w // 2 - title_size[0] // 2, title_y))
        
        # Subtitle
        subtitle_y = title_y + 60
        subtitle_surface = FONTS['hud'].render(subtitle, True, (0, 0, 0))
        screen.blit(subtitle_surface, (screen_w // 2 - subtitle_size[0] // 2 + 2, subtitle_y + 2))
        subtitle_surface = FONTS['hud'].render(subtitle, True, (220, 220, 220))
        screen.blit(subtitle_surface, (screen_w // 2 - subtitle_size[0] // 2, subtitle_y))
        
        # Instructions
        instruction_y = title_y + 120
        instruction_alpha = int(200 + 55 * math.sin(time_factor * 3))
        instruction_text = "Press ESC to return to menu"
        
        # Shadow
        instruction_shadow = FONTS['button'].render(instruction_text, True, (0, 0, 0))
        screen.blit(instruction_shadow, (screen_w // 2 - instruction_size[0] // 2 + 2, instruction_y + 2))
        
        # Main text
        instruction = FONTS['button'].render(instruction_text, True, (255, 255, 255))
        screen.blit(instruction, (screen_w // 2 - instruction_size[0] // 2, instruction_y))

    def draw_wave_panel_with_timing(self, screen, screen_size, level, current_game_time):
        """Draw elegant wave panel with excellent readability"""
        screen_w, screen_h = screen_size
        
        # Dynamic timing for smooth animations
        time_factor = pygame.time.get_ticks() / 1000.0
        
        # Calculate content
        wave_text = f"Wave {level.current_wave}/{level.total_waves}"
        time_text = f"Time: {current_game_time:.1f}s"
        
        # Status text with better colors
        if level.in_wave_break and not level.all_waves_complete:
            time_left = level.wave_break_duration - level.wave_break_timer
            status_text = f"Next wave in: {time_left:.1f}s"
            status_color = (255, 220, 100)  # Warm yellow
        elif not level.all_waves_complete:
            living_enemies = len([e for e in level.enemies if hasattr(e, 'health') and e.health > 0])
            status_text = f"Enemies: {level.enemies_spawned_this_wave}/{level.enemies_in_wave} (Active: {living_enemies})"
            status_color = (180, 220, 255)  # Soft blue
        else:
            status_text = "All waves complete!"
            status_color = (150, 255, 150)  # Soft green
        
        # Calculate panel size with proper padding
        texts = [wave_text, status_text, time_text]
        max_width = max(FONTS['button'].size(wave_text)[0], 
                       FONTS['small'].size(status_text)[0], 
                       FONTS['small'].size(time_text)[0])
        
        panel_padding = 25
        panel_w = max_width + panel_padding * 2
        panel_h = 110
        panel_x = 20
        panel_y = screen_h - panel_h - 20
        
        # Elegant breathing effect
        breath = 1.0 + 0.02 * math.sin(time_factor * 2)
        panel_w = int(panel_w * breath)
        
        # Sophisticated background with multiple layers
        panel_surface = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        
        # Create elegant gradient background
        for i in range(panel_h):
            progress = i / panel_h
            # Rich dark blue to navy gradient for excellent contrast
            alpha = 240 - (progress * 20)
            blue_intensity = int(25 + progress * 15)
            bg_color = (15, 25, blue_intensity + 25, int(alpha))
            pygame.draw.line(panel_surface, bg_color, (0, i), (panel_w, i))
        
        screen.blit(panel_surface, (panel_x, panel_y))
        
        # Multi-layer elegant border
        border_pulse = 0.8 + 0.2 * math.sin(time_factor * 3)
        
        # Outer glow effect
        glow_intensity = 0.4 + 0.3 * math.sin(time_factor * 2)
        for i in range(8, 0, -1):
            glow_alpha = int(25 * glow_intensity * (i / 8))
            glow_rect = pygame.Rect(panel_x - i*2, panel_y - i*2, panel_w + i*4, panel_h + i*4)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            glow_surface.fill((100, 180, 255, glow_alpha))  # Soft blue glow
            screen.blit(glow_surface, (glow_rect.x, glow_rect.y))
        
        # Main border layers
        for thickness in [3, 2, 1]:
            border_alpha = int(180 * border_pulse * (thickness / 3))
            border_color = (120, 200, 255, border_alpha)  # Elegant blue
            pygame.draw.rect(screen, border_color, 
                           (panel_x - thickness//2, panel_y - thickness//2, 
                            panel_w + thickness, panel_h + thickness), 
                           thickness, border_radius=12 + thickness)
        
        # Inner highlight for depth
        highlight_alpha = int(60 * border_pulse)
        pygame.draw.rect(screen, (255, 255, 255, highlight_alpha), 
                        (panel_x + 2, panel_y + 2, panel_w - 4, panel_h - 4), 
                        1, border_radius=10)
        
        # Text with enhanced readability
        text_x = panel_x + panel_padding
        
        # Helper function for high-contrast text
        def draw_enhanced_text(text, font, color, x, y):
            # Strong shadow for depth
            shadow_text = font.render(text, True, (0, 0, 0))
            screen.blit(shadow_text, (x + 2, y + 2))
            
            # Subtle outline for clarity
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        outline_text = font.render(text, True, (20, 20, 40))
                        screen.blit(outline_text, (x + dx, y + dy))
            
            # Main text
            main_text = font.render(text, True, color)
            screen.blit(main_text, (x, y))
        
        # Wave title with enhanced visibility
        wave_y = panel_y + 15
        draw_enhanced_text(wave_text, FONTS['button'], (180, 220, 255), text_x, wave_y)
        
        # Status text with dynamic colors
        status_y = panel_y + 45
        draw_enhanced_text(status_text, FONTS['small'], status_color, text_x, status_y)
        
        # Time text with warm golden color
        time_y = panel_y + 75
        draw_enhanced_text(time_text, FONTS['small'], (255, 220, 120), text_x, time_y)

    def draw_victory_screen(self, screen, screen_size, current_game_time, best_time, is_new_best_time):
        """Draw elegant victory screen with sophisticated golden effects"""
        screen_w, screen_h = screen_size
        
        # Dynamic timing for animations
        time_factor = pygame.time.get_ticks() / 1000.0
        
        # Elegant celebration overlay layers
        overlay_alpha_base = int(60 + 20 * math.sin(time_factor * 1.5))
        
        if is_new_best_time:
            # Rich golden celebration for new record
            overlay_colors = [
                (80, 60, 20, overlay_alpha_base),     # Deep golden base
                (100, 80, 30, overlay_alpha_base + 20), # Brighter gold
                (120, 100, 40, overlay_alpha_base + 30) # Bright gold highlight
            ]
            primary_color = (255, 215, 0)      # Pure gold
            secondary_color = (255, 240, 150)  # Light gold
            celebration_text = "★ NEW RECORD ACHIEVED! ★"
            panel_base_color = (60, 45, 15)    # Dark golden base
        else:
            # Elegant golden victory theme
            overlay_colors = [
                (60, 50, 20, overlay_alpha_base),     # Warm golden base
                (80, 70, 30, overlay_alpha_base + 15), # Medium gold
                (100, 85, 40, overlay_alpha_base + 25) # Bright gold
            ]
            primary_color = (255, 200, 100)    # Warm gold
            secondary_color = (255, 220, 150)  # Light warm gold
            celebration_text = ""
            panel_base_color = (50, 40, 15)    # Dark warm base
        
        # Multi-layer animated overlay
        for i, color in enumerate(overlay_colors):
            wave_offset = math.sin(time_factor * (2 + i * 0.5)) * 20
            alpha_mod = int(wave_offset)
            adjusted_color = (color[0], color[1], color[2], max(20, color[3] + alpha_mod))
            overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
            overlay.fill(adjusted_color)
            screen.blit(overlay, (0, 0))
        
        # Calculate content dimensions
        title_text = "VICTORY!"
        if is_new_best_time:
            subtitle = "NEW BEST TIME!"
        else:
            subtitle = "Mission Complete"
        
        your_time_text = f"Your Time: {current_game_time:.2f}s"
        
        if is_new_best_time:
            if best_time is None:
                best_info = "First completion!"
            else:
                best_info = f"Previous best: {best_time:.2f}s"
        else:
            if best_time is not None:
                best_info = f"Best Time: {best_time:.2f}s"
            else:
                best_info = "No previous best time"
        
        instruction_text = "Press ESC to return to menu"
        
        # Dynamic panel sizing with elegant proportions
        texts = [title_text, subtitle, your_time_text, best_info, celebration_text, instruction_text]
        max_width = max(FONTS['title'].size(title_text)[0],
                       FONTS['hud'].size(subtitle)[0],
                       FONTS['hud'].size(your_time_text)[0],
                       FONTS['hud'].size(best_info)[0],
                       FONTS['button'].size(celebration_text)[0] if celebration_text else 0,
                       FONTS['button'].size(instruction_text)[0])
        
        panel_w = max_width + 160
        panel_h = 420 if celebration_text else 380
        
        # Elegant pulsing effect for celebration
        if is_new_best_time:
            pulse = 1.0 + 0.06 * math.sin(time_factor * 4)
            panel_w = int(panel_w * pulse)
            panel_h = int(panel_h * pulse)
        
        panel_x = (screen_w - panel_w) // 2
        panel_y = (screen_h - panel_h) // 2
        
        # Sophisticated background panel with rich gradient
        panel_surface = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        
        # Create luxurious gradient
        for i in range(panel_h):
            progress = i / panel_h
            alpha = 245 - (progress * 25)
            gold_r = panel_base_color[0] + int(30 + progress * 20)
            gold_g = panel_base_color[1] + int(25 + progress * 15)
            gold_b = panel_base_color[2] + int(10 + progress * 5)
            bg_color = (gold_r, gold_g, gold_b, int(alpha))
            pygame.draw.line(panel_surface, bg_color, (0, i), (panel_w, i))
        
        screen.blit(panel_surface, (panel_x, panel_y))
        
        # Spectacular multi-layer glow system
        glow_intensity = 0.8 + 0.4 * math.sin(time_factor * 3)
        
        # Outer spectacular glow
        for i in range(15, 0, -1):
            glow_alpha = int(20 * glow_intensity * (i / 15))
            glow_rect = pygame.Rect(panel_x - i*2, panel_y - i*2, panel_w + i*4, panel_h + i*4)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            glow_surface.fill((*primary_color[:3], glow_alpha))
            screen.blit(glow_surface, (glow_rect.x, glow_rect.y))
        
        # Elegant border system
        border_pulse = 0.9 + 0.3 * math.sin(time_factor * 4)
        for thickness in [5, 3, 2, 1]:
            border_alpha = int(200 * border_pulse * (thickness / 5))
            border_color = (*primary_color[:3], border_alpha)
            pygame.draw.rect(screen, border_color, 
                           (panel_x - thickness, panel_y - thickness, 
                            panel_w + thickness*2, panel_h + thickness*2), 
                           thickness, border_radius=25 + thickness)
        
        # Inner luxury highlight
        highlight_alpha = int(80 * border_pulse)
        pygame.draw.rect(screen, (255, 255, 255, highlight_alpha), 
                        (panel_x + 3, panel_y + 3, panel_w - 6, panel_h - 6), 
                        2, border_radius=22)
        
        # Content positioning
        content_y = panel_y + 50
        line_spacing = 55
        
        # Enhanced text rendering function
        def draw_luxury_text(text, font, color, x, y, center=True):
            # Calculate position
            text_surface = font.render(text, True, color)
            if center:
                text_x = x - text_surface.get_width() // 2
            else:
                text_x = x
            
            # Multiple shadow layers for depth
            for offset in range(4, 0, -1):
                shadow_alpha = 150 - offset * 30
                shadow_text = font.render(text, True, (0, 0, 0, shadow_alpha))
                screen.blit(shadow_text, (text_x + offset, y + offset))
            
            # Elegant outline for definition
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        outline_text = font.render(text, True, (20, 15, 5))
                        screen.blit(outline_text, (text_x + dx, y + dy))
            
            # Main text with luxury appearance
            screen.blit(text_surface, (text_x, y))
        
        # Render all content with enhanced effects
        draw_luxury_text(title_text, FONTS['title'], primary_color, screen_w // 2, content_y)
        content_y += line_spacing + 15
        
        draw_luxury_text(subtitle, FONTS['hud'], secondary_color, screen_w // 2, content_y)
        content_y += line_spacing
        
        draw_luxury_text(your_time_text, FONTS['hud'], (255, 255, 240), screen_w // 2, content_y)
        content_y += line_spacing - 10
        
        best_color = (255, 215, 0) if is_new_best_time else (220, 200, 150)
        draw_luxury_text(best_info, FONTS['hud'], best_color, screen_w // 2, content_y)
        content_y += line_spacing
        
        # Spectacular celebration text for new records
        if celebration_text:
            celebration_pulse = 0.9 + 0.3 * math.sin(time_factor * 6)
            celebration_color = (*primary_color[:3], int(255 * celebration_pulse))
            draw_luxury_text(celebration_text, FONTS['button'], primary_color, screen_w // 2, content_y)
            
            # Add sparkle effects around celebration text
            sparkle_count = 12
            for i in range(sparkle_count):
                angle = (time_factor * 3 + i * math.pi * 2 / sparkle_count) % (math.pi * 2)
                radius = 120 + 30 * math.sin(time_factor * 4 + i)
                sparkle_x = screen_w // 2 + radius * math.cos(angle)
                sparkle_y = content_y + 15 + radius * 0.3 * math.sin(angle)
                
                sparkle_alpha = int(120 + 100 * math.sin(time_factor * 5 + i))
                sparkle_size = 3 + int(2 * math.sin(time_factor * 6 + i))
                
                if sparkle_alpha > 70:
                    sparkle_color = (*primary_color[:3], sparkle_alpha)
                    # Enhanced star pattern
                    pygame.draw.circle(screen, sparkle_color, (int(sparkle_x), int(sparkle_y)), sparkle_size)
                    line_length = sparkle_size * 3
                    # Create 4-point star
                    for angle_offset in [0, math.pi/2, math.pi, 3*math.pi/2]:
                        end_x = sparkle_x + line_length * math.cos(angle_offset)
                        end_y = sparkle_y + line_length * math.sin(angle_offset)
                        pygame.draw.line(screen, sparkle_color, 
                                       (sparkle_x, sparkle_y), (end_x, end_y), 2)
            
            content_y += line_spacing
        
        # Instructions with elegant fade
        instruction_alpha = int(220 + 35 * math.sin(time_factor * 2))
        draw_luxury_text(instruction_text, FONTS['button'], (255, 245, 220), screen_w // 2, content_y)

    def run(self):
        while True:
            if self.state == "menu":
                main_menu = MainMenu()
                result = main_menu.run()
                
                if result == "start":
                    self.state = "level_select"
                elif result == "creator":
                    creator_result = run_level_creator()
                    if creator_result == "quit":
                        pygame.quit()
                        sys.exit()
                    self.state = "menu"
                    
            elif self.state == "level_select":
                level_selector = LevelSelector()
                selected_level = level_selector.run()
                
                if selected_level is None:
                    self.state = "menu"
                else:
                    self.current_level_file = selected_level  # Store level file path
                    level_data = self.load_level_from_file(selected_level)
                    if level_data:
                        result = self.run_game_loop(level_data)
                        if result == "quit":
                            pygame.quit()
                            sys.exit()
                        else:
                            self.state = "menu"
                    else:
                        self.state = "level_select"

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main() 