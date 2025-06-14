"""
AI assisted code included in this file, you can see the comments below for details.
"""
import sys
import pygame
import json
import time
import math  # Add math import
import os
from settings import *
from menu import MainMenu, LevelSelector, show_level_creator_message
from level_creator import run_level_creator
from library import CharacterLibrary, ImageCache
from grid import GRID_MAP, update_grid_map
from map_component import MapComponent
from level import Level
from tower import TowerFactory
from bullet import Bullet
from audio_manager import audio_manager
from resource_manager import get_library_path

class TowerImageCache:
    """Cache system for tower images"""
    """This class is inspired and supported by ChatGPT-o4-mini-high. It provides a caching mechanism for tower images to improve performance and reduce loading times."""
    _tower_images = {}
    _tower_images_gray = {}
    
    @classmethod
    def get_tower_image(cls, tower_name, size, grayscale=False):
        cache_key = f"{tower_name}_{size}_{grayscale}"
        
        if cache_key not in cls._tower_images:
            try:
                library_image_path = get_library_path("tower", f"{tower_name}.png")
                image = pygame.image.load(str(library_image_path))
                
                scaled_image = pygame.transform.scale(image, size)
                
                if grayscale:
                    gray_image = pygame.Surface(size, pygame.SRCALPHA)
                    for x in range(size[0]):
                        for y in range(size[1]):
                            color = scaled_image.get_at((x, y))
                            if color[3] > 0:
                                gray = int(0.299 * color.r + 0.587 * color.g + 0.114 * color.b)
                                gray_color = (gray // 3, gray // 3, gray // 3, color.a)
                                gray_image.set_at((x, y), gray_color)
                    cls._tower_images[cache_key] = gray_image
                else:
                    cls._tower_images[cache_key] = scaled_image
                    
            except Exception as e:
                print(f"Failed to load tower image {tower_name}: {e}")
                cls._tower_images[cache_key] = None
        
        return cls._tower_images[cache_key]

class Game:
    def __init__(self):
        self.state = "menu"  # menu, level_select, playing, creator, library
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

            if 'settings' not in level_data:
                level_data['settings'] = {}
            
            level_data['settings']['best_time'] = new_time
            

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
        

        level.load_settings(level_data)

        level.recalculate_path()

        level.start_first_wave()

        game_map = MapComponent(grid=level.grid)

        game_map.set_spawn_and_home(level.start, level.end)
        
        towers = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        sel = None
        game_over = False
        game_won = False
        money = level.initial_money
        selected_tower = None
        current_screen_size = screen.get_size()
        
        # Game timing - initially paused for level start message
        start_time = None  # Will be set after countdown
        current_game_time = 0.0
        is_new_best_time = False
        
        # Level start countdown
        show_level_start = True
        level_start_timer = 3.0
        game_timer_started = False
        
        # Wave completion message display
        wave_message = ""
        wave_message_timer = 0.0
        wave_message_duration = 3.0

        ui_update_timer = 0.0
        ui_update_interval = 0.1
        
        # Kill reward callback function
        def on_enemy_killed(enemy):
            nonlocal money

            reward = getattr(enemy, 'reward', KILL_REWARD)
            money += reward
            print(f"{getattr(enemy, 'enemy_type', 'Enemy')} killed! Reward: +${reward}")

        level.set_kill_callback(on_enemy_killed)
        

        audio_manager.play_game_music()
        audio_manager.update_enemy_count(0)

        
        running = True
        clock = pygame.time.Clock()
        
        while running:
            dt = clock.tick(60)/1000.0
            mouse_pos = pygame.mouse.get_pos()
            current_screen_size = screen.get_size()

            ui_update_timer += dt
            should_update_ui = ui_update_timer >= ui_update_interval
            if should_update_ui:
                ui_update_timer = 0.0
            
            # Handle level start countdown
            if show_level_start:
                level_start_timer -= dt
                if level_start_timer <= 0:
                    show_level_start = False
                    start_time = time.time()
                    game_timer_started = True
            
            # Update game time if game is running and timer has started
            if not game_over and not game_won and game_timer_started and start_time:
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

                    # Check menu button (bottom right corner)
                    menu_button_rect = pygame.Rect(screen_w - 100, screen_h - 60, 80, 40)
                    if menu_button_rect.collidepoint(mx, my):
                        return "menu"

                    # Allow interaction only if the game is not over and level start is complete
                    if not game_over and not game_won and not show_level_start:
                        # Check UI area click
                        if my < UI_HEIGHT:
                            # Get toolbar button info
                            toolbar_info = self.get_toolbar_layout(screen_w, screen_h)

                            for button_info in toolbar_info['tower_buttons']:
                                if button_info['rect'].collidepoint(mx, my):
                                    if money >= TOWER_COSTS[button_info['type']['name']]:
                                        sel = button_info['type']
                                        # Reset demolish mode
                                        selected_tower = None
                                    break
                            
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
                                elif level.grid and level.grid[gy][gx] == 1 and sel:  # 1 = grass, 0 = path
                                    can_build = True
                                    for tower in towers:
                                        if tower.gx == gx and tower.gy == gy:
                                            can_build = False
                                            break
                                    
                                    if can_build and money >= TOWER_COSTS[sel['name']]:
                                        money -= TOWER_COSTS[sel['name']]
                                        towers.add(TowerFactory.create_tower(sel, gx, gy))
                                        sel = None

            # Update game logic only if the game is not over and level start is complete
            if not game_over and not game_won and not show_level_start:
                prev_wave_complete = level.wave_complete
                prev_wave = level.current_wave
                
                # Update map component with enemy status and time
                game_map.update(dt, level.enemies)
                
                level.update(dt)
                bullets.update(dt)
                towers.update(dt, level.enemies, bullets)
                
                # Update audio manager with enemy count for music switching
                enemy_count = len(level.enemies)
                audio_manager.update_enemy_count(enemy_count)
                
                # Check if enemies have reached the end and trigger HOME hit animation
                for e in list(level.enemies):
                    if hasattr(e, 'path_index') and e.path_index >= len(e.path) - 1:
                        game_map.on_home_hit()
                        level.base_hp -= getattr(e, 'damage_to_base', 1)
                        audio_manager.play_home_hit_sound()
                        if hasattr(e, 'cleanup_speed_modifiers'):
                            e.cleanup_speed_modifiers()
                        e.kill()
                        print(f"Enemy reached HOME! Base HP: {level.base_hp}")
                    elif hasattr(e, 'reached_end') and e.reached_end:
                        game_map.on_home_hit()
                        level.base_hp -= getattr(e, 'damage_to_base', 1)
                        audio_manager.play_home_hit_sound()
                        if hasattr(e, 'cleanup_speed_modifiers'):
                            e.cleanup_speed_modifiers()
                        e.kill()
                        print(f"Enemy reached HOME! Base HP: {level.base_hp}")

                if level.wave_complete and not prev_wave_complete:
                    # Wave just completed, give reward immediately
                    money += WAVE_REWARD
                    wave_message = f"Wave {level.current_wave} Complete! Bonus: +${WAVE_REWARD}"
                    wave_message_timer = 0.0
                    print(f"Wave {level.current_wave} completed! Bonus: +${WAVE_REWARD}")
                    # Play wave complete sound
                    audio_manager.play_wave_complete_sound()
                
                # Check game over condition
                if level.base_hp <= 0:
                    game_over = True
                    audio_manager.stop_all_audio()
                    audio_manager.play_game_over_sound()
                
                # Check victory condition - all waves complete
                if level.all_waves_complete:
                    game_won = True
                    final_time = current_game_time
                    audio_manager.play_victory_sound()
                    
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

            """
            This section is inspired and supported by ChatGPT-o4-mini-high.
            """
            # Draw screen elements
            current_screen = pygame.display.get_surface()
            current_screen.fill(BG_COLOUR)
            
            # Draw map
            game_map.draw(current_screen)
            
            # Draw towers
            for tower in towers:
                tower.draw(current_screen)
            
            # Draw bullets
            bullets.draw(current_screen)

            self.draw_enhanced_toolbar(current_screen, current_screen_size, sel, selected_tower, money, level.base_hp, level.name, level)
            
            # Draw wave panel with updated format
            self.draw_wave_panel_with_timing(current_screen, current_screen_size, level, current_game_time)

            level.draw(current_screen)
            
            # Draw wave completion message if active
            if wave_message:
                self.draw_wave_message(current_screen, current_screen_size, wave_message)
            
            # Draw level start message if active
            if show_level_start:
                self.draw_level_start_message(current_screen, current_screen_size, level.initial_money, level_start_timer)
            
            # Draw game over screen if applicable
            if game_over:
                self.draw_game_over_screen(current_screen, current_screen_size, victory=False)
            elif game_won:
                self.draw_victory_screen(current_screen, current_screen_size, current_game_time, level.best_time, is_new_best_time)
            
            pygame.display.flip()
        
        return "menu"
    
    def get_toolbar_layout(self, screen_w, screen_h):
        """Get toolbar layout information for current screen size - enhanced layout"""
        toolbar_margin = 15
        card_width = 120
        card_height = 105
        card_spacing = 15

        tower_buttons = []
        
        # Starting position
        start_x = toolbar_margin
        start_y = toolbar_margin

        max_cards_width = screen_w - 280  # Leave space for info panel
        max_cards = (max_cards_width - start_x) // (card_width + card_spacing)
        
        # Create tower buttons
        for i, tower_type in enumerate(TOWER_TYPES):
            if i >= max_cards:
                break
                
            x = start_x + i * (card_width + card_spacing)
            y = start_y
            
            button_rect = pygame.Rect(x, y, card_width, card_height)
            tower_buttons.append({
                'rect': button_rect,
                'type': tower_type
            })
        
        # Demolish button - place after towers if space allows
        demolish_x = start_x + len(tower_buttons) * (card_width + card_spacing)
        demolish_y = start_y
        
        # If demolish button won't fit, place on second row
        if demolish_x + card_width > screen_w - 280:
            demolish_x = start_x
            demolish_y = start_y + card_height + 12
        
        demolish_button = {
            'rect': pygame.Rect(demolish_x, demolish_y, card_width, card_height)
        }
        
        return {
            'tower_buttons': tower_buttons,
            'demolish_button': demolish_button
        }

    def draw_enhanced_toolbar(self, screen, screen_size, selected_type, selected_tower, money, base_hp, level_name, level):
        """Draw enhanced toolbar with jungle theme like library"""
        """The design is made with ChatGPT-4o"""
        screen_w, screen_h = screen_size

        toolbar_rect = pygame.Rect(0, 0, screen_w, UI_HEIGHT)
        pygame.draw.rect(screen, BROWN, toolbar_rect)
        pygame.draw.rect(screen, DARK_GREEN, toolbar_rect, 4)
        layout = self.get_toolbar_layout(screen_w, screen_h)

        mx, my = pygame.mouse.get_pos()
        
        for button_info in layout['tower_buttons']:
            tower_type = button_info['type']
            rect = button_info['rect']
            
            # Check states
            is_selected = selected_type == tower_type
            can_afford = money >= TOWER_COSTS[tower_type['name']]
            is_hovered = rect.collidepoint(mx, my) and my < UI_HEIGHT

            if is_selected:
                bg_color = FOREST_GREEN
                border_color = LIGHT_GREEN
                text_color = WHITE
            elif not can_afford:
                bg_color = (160, 140, 120)
                border_color = (120, 100, 80)
                text_color = (100, 80, 60)
            elif is_hovered:
                bg_color = LIGHT_GREEN
                border_color = FOREST_GREEN
                text_color = DARK_GREEN
            else:
                bg_color = CREAM
                border_color = BROWN
                text_color = DARK_GREEN

            pygame.draw.rect(screen, bg_color, rect, border_radius=8)
            pygame.draw.rect(screen, border_color, rect, 3, border_radius=8)

            image_area_height = 70
            image_area_width = rect.width - 12

            cache_key = f"{tower_type['name']}_{image_area_width}_{image_area_height}_{can_afford}"
            
            if not hasattr(self, '_image_cache'):
                self._image_cache = {}
            
            if cache_key in self._image_cache:
                tower_image = self._image_cache[cache_key]
                if tower_image:
                    image_x = rect.x + (rect.width - tower_image.get_width()) // 2
                    image_y = rect.y + 8
                    screen.blit(tower_image, (image_x, image_y))
            else:
                original_image_path = get_library_path("tower", f"{tower_type['name']}.png")
                try:
                    original_image = pygame.image.load(str(original_image_path))

                    img_width = original_image.get_width()
                    img_height = original_image.get_height()
                    
                    scale_x = image_area_width / img_width
                    scale_y = image_area_height / img_height
                    scale = min(scale_x, scale_y) * 0.9
                    
                    new_width = int(img_width * scale)
                    new_height = int(img_height * scale)

                    if can_afford:
                        tower_image = pygame.transform.scale(original_image, (new_width, new_height))
                    else:
                        scaled_image = pygame.transform.scale(original_image, (new_width, new_height))
                        tower_image = pygame.Surface((new_width, new_height), pygame.SRCALPHA)
                        tower_image.fill((128, 128, 128, 180))  # Simple gray overlay
                        tower_image.blit(scaled_image, (0, 0), special_flags=pygame.BLEND_MULT)

                    self._image_cache[cache_key] = tower_image

                    image_x = rect.x + (rect.width - new_width) // 2
                    image_y = rect.y + 8
                    screen.blit(tower_image, (image_x, image_y))
                    
                except Exception as e:
                    print(f"Failed to load tower image {tower_type['name']}: {e}")

                    center_x = rect.centerx
                    icon_y = rect.y + 35
                    icon_color = tower_type['color'] if can_afford else (120, 100, 80)
                    pygame.draw.circle(screen, icon_color, (center_x, icon_y), 22)
                    pygame.draw.circle(screen, border_color, (center_x, icon_y), 22, 3)

                    letter = tower_type['name'][0]
                    letter_font = pygame.font.SysFont('Arial', 20, bold=True)
                    letter_text = letter_font.render(letter, True, WHITE if can_afford else (80, 60, 40))
                    letter_rect = letter_text.get_rect(center=(center_x, icon_y))
                    screen.blit(letter_text, letter_rect)
                    
                    # Cache None to avoid repeated failed loads
                    self._image_cache[cache_key] = None
            
            # Tower name
            name_text = FONTS['button'].render(tower_type['name'], True, text_color)
            name_x = rect.centerx - name_text.get_width()//2
            name_y = rect.y + rect.height - 38  # 调整位置
            screen.blit(name_text, (name_x, name_y))
            
            # Price display
            cost_color = FOREST_GREEN if can_afford else (180, 80, 80)
            cost_text = FONTS['small'].render(f"${TOWER_COSTS[tower_type['name']]}", True, cost_color)
            cost_x = rect.centerx - cost_text.get_width()//2
            cost_y = rect.y + rect.height - 18
            screen.blit(cost_text, (cost_x, cost_y))
        
        # Demolish button
        demolish_rect = layout['demolish_button']['rect']
        is_demolish_active = selected_tower == "demolish_mode"
        is_demolish_hovered = demolish_rect.collidepoint(mx, my) and my < UI_HEIGHT
        
        if is_demolish_active:
            bg_color = (200, 80, 80)
            border_color = (160, 60, 60)
            text_color = WHITE
        elif is_demolish_hovered:
            bg_color = (220, 120, 120)
            border_color = (180, 80, 80)
            text_color = DARK_GREEN
        else:
            bg_color = CREAM
            border_color = BROWN
            text_color = DARK_GREEN
        
        # Draw demolish card
        pygame.draw.rect(screen, bg_color, demolish_rect, border_radius=8)
        pygame.draw.rect(screen, border_color, demolish_rect, 3, border_radius=8)
        
        # Demolish icon - X symbol adjusted for larger size
        center_x, center_y = demolish_rect.center
        icon_y = demolish_rect.y + 35
        
        # Draw X symbol
        line_color = text_color if not is_demolish_active else WHITE
        line_width = 4
        offset = 12
        pygame.draw.line(screen, line_color, 
                        (center_x - offset, icon_y - offset), 
                        (center_x + offset, icon_y + offset), line_width)
        pygame.draw.line(screen, line_color, 
                        (center_x + offset, icon_y - offset), 
                        (center_x - offset, icon_y + offset), line_width)
        
        # Demolish text
        demolish_main = FONTS['small'].render("DEMOLISH", True, text_color)
        main_x = demolish_rect.centerx - demolish_main.get_width()//2
        main_y = demolish_rect.centery + 18
        screen.blit(demolish_main, (main_x, main_y))
        
        refund_text = FONTS['tiny'].render("50% Refund", True, text_color)
        refund_x = demolish_rect.centerx - refund_text.get_width()//2
        refund_y = demolish_rect.y + demolish_rect.height - 16
        screen.blit(refund_text, (refund_x, refund_y))
        
        # Enhanced Info panel
        info_panel_x = screen_w - 280
        info_panel_w = 260
        info_panel_h = UI_HEIGHT - 20
        info_panel_rect = pygame.Rect(info_panel_x, 10, info_panel_w, info_panel_h)
        
        # Beautiful info panel background with nature theme
        # Gradient background - darker at top, lighter at bottom
        for i in range(info_panel_h):
            color_progress = i / info_panel_h
            r = int(34 + (144 - 34) * color_progress)    # From dark green to light green
            g = int(100 + (158 - 100) * color_progress)  # From dark green to light green
            b = int(34 + (44 - 34) * color_progress)     # From dark green to light green
            pygame.draw.line(screen, (r, g, b), 
                           (info_panel_x, 10 + i), 
                           (info_panel_x + info_panel_w, 10 + i))
        
        # Elegant border with rounded corners
        pygame.draw.rect(screen, (245, 245, 220, 200), info_panel_rect, border_radius=15)
        pygame.draw.rect(screen, (139, 115, 85), info_panel_rect, 3, border_radius=15)
        
        # Inner glow effect
        inner_rect = pygame.Rect(info_panel_x + 3, 13, info_panel_w - 6, info_panel_h - 6)
        pygame.draw.rect(screen, (255, 255, 255, 60), inner_rect, 2, border_radius=12)
        
        # Status icons and text with better spacing
        def draw_status_item(icon_color, label, value, value_color, y_offset):
            icon_x = info_panel_x + 20
            icon_y = 25 + y_offset
            text_x = info_panel_x + 50
            
            # Draw icon background circle (no text inside)
            pygame.draw.circle(screen, icon_color, (icon_x, icon_y), 12)
            pygame.draw.circle(screen, (255, 255, 255, 100), (icon_x, icon_y), 12, 2)
            
            # Draw label and value with shadow
            shadow_offset = 1
            label_text = f"{label}: {value}"
            
            # Shadow
            shadow_surface = FONTS['button'].render(label_text, True, (0, 0, 0, 120))
            screen.blit(shadow_surface, (text_x + shadow_offset, icon_y - 8 + shadow_offset))
            
            # Main text
            text_surface = FONTS['button'].render(label_text, True, value_color)
            screen.blit(text_surface, (text_x, icon_y - 8))
        
        # Money status
        money_color = (34, 139, 34) if money >= 50 else (184, 134, 11)
        draw_status_item((255, 215, 0), "Gold", f"{money}", money_color, 0)
        
        # Base health status  
        hp_color = (34, 139, 34) if base_hp > 5 else (220, 20, 60)
        draw_status_item((220, 20, 60), "Base HP", f"{base_hp}", hp_color, 30)
        
        # Level name status
        draw_status_item((70, 130, 180), "Level", level_name, (25, 25, 112), 60)
        
        # Menu button - moved to bottom right corner
        menu_button_rect = pygame.Rect(screen_w - 100, screen_h - 60, 80, 40)
        menu_hovered = menu_button_rect.collidepoint(mx, my)
        menu_color = (200, 100, 100) if menu_hovered else BROWN
        
        pygame.draw.rect(screen, menu_color, menu_button_rect, border_radius=8)
        pygame.draw.rect(screen, DARK_GREEN, menu_button_rect, 2, border_radius=8)
        
        menu_text = FONTS['small'].render("MENU", True, WHITE)
        menu_x = menu_button_rect.centerx - menu_text.get_width()//2
        menu_y = menu_button_rect.centery - menu_text.get_height()//2
        screen.blit(menu_text, (menu_x, menu_y))

    def draw_wave_panel(self, screen, screen_size, level):
        """Draw wave information panel on top of everything"""
        screen_w, screen_h = screen_size

        wave_panel_x = 20
        wave_panel_y = screen_h - 80
        wave_panel_w = 300
        wave_panel_h = 60
        wave_panel_rect = pygame.Rect(wave_panel_x, wave_panel_y, wave_panel_w, wave_panel_h)
        pygame.draw.rect(screen, UI_MID_BG, wave_panel_rect, border_radius=8)
        pygame.draw.rect(screen, UI_ACCENT, wave_panel_rect, 2, border_radius=8)
        
        # Wave title
        wave_title = FONTS['button'].render(f"Wave {level.current_wave}", True, UI_ACCENT)
        screen.blit(wave_title, (wave_panel_x + 10, wave_panel_y + 5))
        
        # Wave progress
        if level.in_preparation and not level.first_wave_started:
            time_left = level.preparation_time - level.preparation_timer
            countdown_text = FONTS['small'].render(f"First wave in: {time_left:.1f}s", True, (255, 100, 100))
            screen.blit(countdown_text, (wave_panel_x + 10, wave_panel_y + 30))
        elif level.in_wave_break:
            time_left = level.wave_break_duration - level.wave_break_timer
            countdown_text = FONTS['small'].render(f"Next wave in: {time_left:.1f}s", True, UI_WARNING)
            screen.blit(countdown_text, (wave_panel_x + 10, wave_panel_y + 30))
        else:
            living_enemies = len([e for e in level.enemies if hasattr(e, 'health') and e.health > 0])
            progress_text = FONTS['small'].render(f"Enemies: {level.enemies_spawned_this_wave}/{level.enemies_in_wave} (Alive: {living_enemies})", True, WHITE)
            screen.blit(progress_text, (wave_panel_x + 10, wave_panel_y + 30))

    def draw_wave_message(self, screen, screen_size, message):
        """Draw simplified wave completion message"""
        """Optimized with ChatGPT-4o"""
        screen_w, screen_h = screen_size

        main_text = FONTS['title'].render(message, True, WHITE)
        text_w, text_h = main_text.get_size()

        panel_w = text_w + 100
        panel_h = text_h + 60
        panel_x = (screen_w - panel_w) // 2
        panel_y = (screen_h - panel_h) // 2 - 50

        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((10, 30, 10, 100))
        screen.blit(overlay, (0, 0))

        pygame.draw.rect(screen, (40, 70, 40, 220), (panel_x, panel_y, panel_w, panel_h), border_radius=15)
        pygame.draw.rect(screen, (220, 180, 100), (panel_x, panel_y, panel_w, panel_h), 3, border_radius=15)

        text_x = panel_x + (panel_w - text_w) // 2
        text_y = panel_y + (panel_h - text_h) // 2

        shadow_text = FONTS['title'].render(message, True, (0, 0, 0))
        screen.blit(shadow_text, (text_x + 2, text_y + 2))

        main_text_render = FONTS['title'].render(message, True, (255, 250, 240))
        screen.blit(main_text_render, (text_x, text_y))

    def draw_game_over_screen(self, screen, screen_size, victory=False):
        """Draw game over screen with clear text and dynamic background"""
        """Enhanced with ChatGPT-4o"""
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
        """Draw beautiful wave panel with forest theme"""
        """Enhanced with ChatGPT-4o, but lots of changes made by myself"""
        screen_w, screen_h = screen_size
        
        # Calculate content
        wave_text = f"Wave {level.current_wave}/{level.total_waves}"
        time_text = f"Time: {current_game_time:.1f}s"
        
        # Status text and color determination
        if level.in_preparation and not level.first_wave_started:
            time_left = level.preparation_time - level.preparation_timer
            status_text = f"First wave starts in {time_left:.1f}s"
            status_color = (255, 165, 0)  # Orange for preparation

        elif level.in_wave_break and not level.all_waves_complete:
            time_left = level.wave_break_duration - level.wave_break_timer
            status_text = f"Next wave arrives in {time_left:.1f}s"
            status_color = (255, 215, 0)  # Gold for break

        elif not level.all_waves_complete:
            living_enemies = len([e for e in level.enemies if hasattr(e, 'health') and e.health > 0])
            status_text = f"Enemies: {level.enemies_spawned_this_wave}/{level.enemies_in_wave} | Active: {living_enemies}"
            status_color = (64, 224, 208)  # Turquoise for active combat

        else:
            status_text = "All waves completed!"
            status_color = (50, 205, 50)  # Lime green for completion

        
        # Optimized panel sizing
        panel_w = 380
        panel_h = 100
        panel_x = 25
        panel_y = screen_h - panel_h - 25
        
        # Beautiful gradient background
        panel_surface = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        
        # Multi-layer gradient for depth
        for i in range(panel_h):
            progress = i / panel_h
            r = int(25 + (45 - 25) * progress)
            g = int(60 + (80 - 60) * progress) 
            b = int(25 + (35 - 25) * progress)
            alpha = int(240 - 20 * progress)
            
            color = (r, g, b, alpha)
            pygame.draw.line(panel_surface, color, (0, i), (panel_w, i))
        
        screen.blit(panel_surface, (panel_x, panel_y))
        
        # Elegant frame and inner highlight
        frame_color = (139, 115, 85)  # Woodland brown
        pygame.draw.rect(screen, frame_color, (panel_x, panel_y, panel_w, panel_h), 4, border_radius=15)
        
        # Inner glow
        inner_glow_rect = (panel_x + 3, panel_y + 3, panel_w - 6, panel_h - 6)
        pygame.draw.rect(screen, (255, 255, 255, 80), inner_glow_rect, 2, border_radius=12)
        
        # Enhanced text rendering with shadows and better positioning
        def draw_enhanced_text(text, font, color, x, y, shadow_color=(0, 0, 0), shadow_offset=2):
            # Enhanced shadow
            shadow_surface = font.render(text, True, shadow_color)
            screen.blit(shadow_surface, (x + shadow_offset, y + shadow_offset))
            
            # Main text
            text_surface = font.render(text, True, color)
            screen.blit(text_surface, (x, y))
            return text_surface
        
        # Wave title with large font
        wave_title_x = panel_x + 20
        wave_title_y = panel_y + 15
        draw_enhanced_text(wave_text, FONTS['button'], (255, 255, 240), wave_title_x, wave_title_y)
        
        # Status section with indicator circles (no emoji)
        status_x = panel_x + 20
        status_y = panel_y + 45
        
        # Status indicator circle
        indicator_x = status_x
        indicator_y = status_y + 8
        
        # Draw status indicator based on current state
        if level.in_preparation and not level.first_wave_started:
            # Preparation indicator - pulsing orange circle
            pulse = int(128 + 127 * abs(math.sin(pygame.time.get_ticks() / 300)))
            pygame.draw.circle(screen, (255, pulse, 0), (indicator_x, indicator_y), 6)
        elif level.in_wave_break:
            # Break indicator - steady yellow circle
            pygame.draw.circle(screen, (255, 215, 0), (indicator_x, indicator_y), 6)
        elif not level.all_waves_complete:
            # Combat indicator - pulsing red circle
            pulse = int(128 + 127 * abs(math.sin(pygame.time.get_ticks() / 200)))
            pygame.draw.circle(screen, (pulse, 64, 64), (indicator_x, indicator_y), 6)
        else:
            # Complete indicator - steady green circle
            pygame.draw.circle(screen, (50, 205, 50), (indicator_x, indicator_y), 6)
        
        # White border for indicator
        pygame.draw.circle(screen, (255, 255, 255), (indicator_x, indicator_y), 6, 2)
        
        # Status text
        status_text_x = status_x + 20
        draw_enhanced_text(status_text, FONTS['small'], status_color, status_text_x, status_y)
        
        # Time display
        time_x = panel_x + 20
        time_y = panel_y + 70
        
        # Time indicator circle
        time_indicator_color = (100, 149, 237)  # Cornflower blue
        pygame.draw.circle(screen, time_indicator_color, (time_x, time_y + 8), 6)
        pygame.draw.circle(screen, (255, 255, 255), (time_x, time_y + 8), 6, 2)
        
        # Time text
        time_text_x = time_x + 20
        draw_enhanced_text(time_text, FONTS['small'], (173, 216, 230), time_text_x, time_y)

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
            celebration_text = "NEW RECORD ACHIEVED!"
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

    def draw_level_start_message(self, screen, screen_size, initial_money, countdown_time):
        """Draw level start countdown message"""
        screen_w, screen_h = screen_size
        
        # Message content
        main_text = "Level Starting!"
        countdown_text = f"First wave arrives in 10 seconds"
        money_text = f"Initial Gold: ${initial_money}"
        timer_text = f"Get ready... {countdown_time:.1f}s"
        
        # Calculate panel dimensions
        texts = [main_text, countdown_text, money_text, timer_text]
        text_widths = [FONTS['title'].size(main_text)[0],
                      FONTS['hud'].size(countdown_text)[0],
                      FONTS['hud'].size(money_text)[0],
                      FONTS['button'].size(timer_text)[0]]
        
        max_width = max(text_widths)
        panel_w = max_width + 120
        panel_h = 220
        panel_x = (screen_w - panel_w) // 2
        panel_y = (screen_h - panel_h) // 2 - 50
        
        # Background overlay
        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((10, 50, 10, 120))
        screen.blit(overlay, (0, 0))
        
        # Panel background with forest theme gradient
        panel_surface = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        for i in range(panel_h):
            progress = i / panel_h
            r = int(40 + (70 - 40) * progress)
            g = int(80 + (120 - 80) * progress)
            b = int(40 + (50 - 40) * progress)
            alpha = int(240 - 20 * progress)
            color = (r, g, b, alpha)
            pygame.draw.line(panel_surface, color, (0, i), (panel_w, i))
        
        screen.blit(panel_surface, (panel_x, panel_y))
        
        # Panel border
        pygame.draw.rect(screen, (139, 115, 85), (panel_x, panel_y, panel_w, panel_h), 4, border_radius=20)
        pygame.draw.rect(screen, (255, 255, 255, 100), (panel_x + 3, panel_y + 3, panel_w - 6, panel_h - 6), 2, border_radius=17)
        
        # Enhanced text drawing function
        def draw_message_text(text, font, color, y_pos, center_x=panel_x + panel_w // 2):
            # Shadow
            shadow_text = font.render(text, True, (0, 0, 0))
            shadow_rect = shadow_text.get_rect(center=(center_x + 2, y_pos + 2))
            screen.blit(shadow_text, shadow_rect)
            
            # Main text
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect(center=(center_x, y_pos))
            screen.blit(text_surface, text_rect)
        
        # Draw texts with proper spacing
        draw_message_text(main_text, FONTS['title'], (255, 255, 240), panel_y + 50)
        draw_message_text(countdown_text, FONTS['hud'], (255, 165, 0), panel_y + 100)
        draw_message_text(money_text, FONTS['hud'], (255, 215, 0), panel_y + 130)
        draw_message_text(timer_text, FONTS['button'], (144, 238, 144), panel_y + 170)

    def run(self):
        while True:
            if self.state == "menu":
                main_menu = MainMenu()
                result = main_menu.run()
                
                if result == "start":
                    self.state = "level_select"
                elif result == "library":
                    self.state = "library"
                elif result == "creator":
                    creator_result = run_level_creator()
                    if creator_result == "quit":
                        pygame.quit()
                        sys.exit()
                    self.state = "menu"
                    
            elif self.state == "library":
                character_library = CharacterLibrary()
                result = character_library.run()
                
                if result == "quit":
                    pygame.quit()
                    sys.exit()
                else:
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