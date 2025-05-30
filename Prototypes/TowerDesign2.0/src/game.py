import sys
import pygame
import json
from settings import *
from menu import MainMenu, LevelSelector, show_level_creator_message
from level_creator import run_level_creator
from grid import GRID_MAP, update_grid_map
from map_component import MapComponent
from level import Level
from tower import Tower
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
    
    def run_game_loop(self, level_data):
        level = Level()
        # Initialize Level with loaded level data BEFORE calling recalculate_path
        if 'name' in level_data:
            level.name = level_data['name']
        if 'grid' in level_data:
            level.grid = level_data['grid']
        # NOW call recalculate_path with the correct grid data
        level.recalculate_path()
        
        # Initialize MapComponent with the correct grid data
        game_map = MapComponent(grid=level.grid)
        
        # Set spawn and home for map component
        game_map.set_spawn_and_home(level.start, level.end)
        
        towers = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        sel = None
        game_over = False
        game_won = False
        money = STARTING_MONEY
        selected_tower = None
        current_screen_size = screen.get_size()

        # Toolbar settings will be dynamically calculated in draw_enhanced_toolbar
        
        running = True
        while running:
            dt = clock.tick(FPS)/1000.0
            mouse_pos = pygame.mouse.get_pos()
            current_screen_size = screen.get_size()
            
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
                                        towers.add(Tower(gx, gy, sel))
                                        sel = None

            # Update game logic only if the game is not over
            if not game_over and not game_won:
                level.update(dt)
                bullets.update(dt)
                towers.update(dt, level.enemies, bullets)
                
                # Gain money reward
                for enemy in level.enemies:
                    if hasattr(enemy, 'is_dead') and enemy.is_dead and not hasattr(enemy, 'rewarded'):
                        money += KILL_REWARD
                        enemy.rewarded = True
                
                # Check game over condition
                if level.base_hp <= 0:
                    game_over = True

            # Draw background
            current_screen = pygame.display.get_surface()
            current_screen.fill(BG_COLOUR)

            # Draw enhanced toolbar
            self.draw_enhanced_toolbar(current_screen, current_screen_size, sel, selected_tower, money, level.base_hp, level.name)

            # Draw back button
            screen_w, screen_h = current_screen_size
            back_button_rect = pygame.Rect(screen_w - 120, 10, 100, 35)
            pygame.draw.rect(current_screen, UI_DANGER, back_button_rect)
            pygame.draw.rect(current_screen, WHITE, back_button_rect, 2)
            back_text = FONTS['button'].render("Menu", True, WHITE)
            current_screen.blit(back_text, back_text.get_rect(center=back_button_rect.center))

            # Draw game world
            game_map.draw(current_screen)
            level.draw(current_screen)
            
            # Draw towers (using custom draw method)
            for tower in towers:
                tower.draw(current_screen)
                
            bullets.draw(current_screen)
            
            # Draw visual feedback for demolish mode
            if selected_tower == "demolish_mode":
                mx, my = pygame.mouse.get_pos()
                if my >= UI_HEIGHT:
                    gx, gy = px_to_grid(mx, my, screen_w, screen_h)
                    if 0 <= gx < GRID_W and 0 <= gy < GRID_H:
                        # Check if there is a tower at this position
                        for tower in towers:
                            if tower.gx == gx and tower.gy == gy:
                                # Draw red overlay layer to indicate demolition
                                scaled_grid_size = get_scaled_grid_size(screen_w, screen_h)
                                px, py = grid_to_px(gx, gy, screen_w, screen_h)
                                overlay = pygame.Surface((scaled_grid_size, scaled_grid_size), pygame.SRCALPHA)
                                overlay.fill((255, 0, 0, 80))
                                current_screen.blit(overlay, (px, py))
                                break

            # Draw game over screen
            if game_over:
                self.draw_game_over_screen(current_screen, current_screen_size, False)
            elif game_won:
                self.draw_game_over_screen(current_screen, current_screen_size, True)
            
            pygame.display.flip()
        
        return "menu"
    
    def get_toolbar_layout(self, screen_w, screen_h):
        """Get toolbar layout information for current screen size"""
        toolbar_margin = 20
        button_width = 90
        button_height = 70
        button_spacing = 10
        
        # Create tower building buttons
        tower_buttons = []
        for i, tower_type in enumerate(TOWER_TYPES):
            x = toolbar_margin + i * (button_width + button_spacing)
            y = (UI_HEIGHT - button_height) // 2
            button_rect = pygame.Rect(x, y, button_width, button_height)
            tower_buttons.append({
                'rect': button_rect,
                'type': tower_type
            })
        
        # Demolish button
        demolish_x = toolbar_margin + len(TOWER_TYPES) * (button_width + button_spacing) + 30
        demolish_button = {
            'rect': pygame.Rect(demolish_x, (UI_HEIGHT - button_height) // 2, button_width, button_height)
        }
        
        return {
            'tower_buttons': tower_buttons,
            'demolish_button': demolish_button
        }

    def draw_enhanced_toolbar(self, screen, screen_size, selected_type, selected_tower, money, base_hp, level_name):
        """Draw enhanced toolbar"""
        screen_w, screen_h = screen_size
        
        # Toolbar background
        toolbar_rect = pygame.Rect(0, 0, screen_w, UI_HEIGHT)
        pygame.draw.rect(screen, UI_DARK_BG, toolbar_rect)
        pygame.draw.rect(screen, UI_LIGHT_BG, toolbar_rect, 3)
        
        # Get layout information
        layout = self.get_toolbar_layout(screen_w, screen_h)
        
        # Draw tower building buttons
        for button_info in layout['tower_buttons']:
            tower_type = button_info['type']
            rect = button_info['rect']
            
            # Check if selected
            is_selected = selected_type == tower_type
            # Check if can afford
            can_afford = money >= TOWER_COSTS[tower_type['name']]
            # Check hover
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = rect.collidepoint(mouse_pos)
            
            # Button background color
            if is_selected:
                bg_color = UI_ACCENT
            elif not can_afford:
                bg_color = UI_DARK_BG
            elif is_hovered:
                bg_color = UI_LIGHT_BG
            else:
                bg_color = UI_MID_BG
            
            # Draw button
            pygame.draw.rect(screen, bg_color, rect, border_radius=8)
            border_color = tower_type['color'] if can_afford else (100, 100, 100)
            pygame.draw.rect(screen, border_color, rect, 3, border_radius=8)
            
            # Draw tower type icon (using colored circle)
            center_x = rect.centerx
            icon_y = rect.y + 20
            pygame.draw.circle(screen, tower_type['color'], (center_x, icon_y), 12)
            pygame.draw.circle(screen, WHITE, (center_x, icon_y), 12, 2)
            
            # Draw tower name
            name_color = WHITE if can_afford else (120, 120, 120)
            name_text = FONTS['small'].render(tower_type['name'], True, name_color)
            name_rect = name_text.get_rect(center=(center_x, icon_y + 25))
            screen.blit(name_text, name_rect)
            
            # Draw price
            cost_color = UI_SUCCESS if can_afford else UI_DANGER
            cost_text = FONTS['tiny'].render(f"${TOWER_COSTS[tower_type['name']]}", True, cost_color)
            cost_rect = cost_text.get_rect(center=(center_x, icon_y + 40))
            screen.blit(cost_text, cost_rect)
            
            # Draw description (on hover)
            if is_hovered and 'description' in tower_type:
                desc_text = FONTS['tiny'].render(tower_type['description'], True, WHITE)
                desc_y = rect.bottom + 5
                screen.blit(desc_text, (rect.x, desc_y))
        
        # Draw demolish button
        demolish_rect = layout['demolish_button']['rect']
        is_demolish_active = selected_tower == "demolish_mode"
        mouse_pos = pygame.mouse.get_pos()
        is_demolish_hovered = demolish_rect.collidepoint(mouse_pos)
        
        if is_demolish_active:
            bg_color = UI_DANGER
        elif is_demolish_hovered:
            bg_color = UI_LIGHT_BG
        else:
            bg_color = UI_MID_BG
        
        pygame.draw.rect(screen, bg_color, demolish_rect, border_radius=8)
        pygame.draw.rect(screen, UI_DANGER, demolish_rect, 3, border_radius=8)
        
        # Draw demolish icon (hammer icon)
        center_x, center_y = demolish_rect.center
        icon_y = demolish_rect.y + 20
        
        # Simple hammer icon
        pygame.draw.circle(screen, UI_DANGER, (center_x, icon_y), 8)
        pygame.draw.rect(screen, UI_DANGER, (center_x - 2, icon_y, 4, 15))
        
        demolish_text = FONTS['small'].render("Demolish", True, WHITE)
        demolish_text_rect = demolish_text.get_rect(center=(center_x, icon_y + 25))
        screen.blit(demolish_text, demolish_text_rect)
        
        refund_text = FONTS['tiny'].render("50% refund", True, UI_WARNING)
        refund_rect = refund_text.get_rect(center=(center_x, icon_y + 40))
        screen.blit(refund_text, refund_rect)
        
        # Draw game info panel
        info_panel_x = screen_w - 300
        info_panel_w = 280
        info_panel_rect = pygame.Rect(info_panel_x, 10, info_panel_w, UI_HEIGHT - 20)
        pygame.draw.rect(screen, UI_MID_BG, info_panel_rect, border_radius=8)
        pygame.draw.rect(screen, UI_LIGHT_BG, info_panel_rect, 2, border_radius=8)
        
        # Money information
        money_text = FONTS['hud'].render(f"Money: ${money}", True, UI_WARNING)
        screen.blit(money_text, (info_panel_x + 15, 25))
        
        # Base health
        hp_color = UI_SUCCESS if base_hp > 5 else UI_DANGER
        hp_text = FONTS['hud'].render(f"Base HP: {base_hp}", True, hp_color)
        screen.blit(hp_text, (info_panel_x + 15, 50))
        
        # Level name
        level_text = FONTS['hud'].render(f"Level: {level_name}", True, UI_ACCENT)
        screen.blit(level_text, (info_panel_x + 15, 75))
        
        # Draw game title
        title_text = FONTS['hud'].render("Forest Guard", True, FOREST_GREEN)
        screen.blit(title_text, (20, 15))
        
        # Draw control hints (removed fullscreen hint)
        help_text = FONTS['tiny'].render("ESC: Menu", True, (150, 150, 150))
        screen.blit(help_text, (20, UI_HEIGHT - 25))

    def draw_game_over_screen(self, screen, screen_size, victory=False):
        """Draw game over screen"""
        screen_w, screen_h = screen_size
        
        # Semi-transparent background
        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Result panel
        panel_w, panel_h = 400, 200
        panel_x = (screen_w - panel_w) // 2
        panel_y = (screen_h - panel_h) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        
        pygame.draw.rect(screen, UI_DARK_BG, panel_rect, border_radius=15)
        pygame.draw.rect(screen, UI_LIGHT_BG, panel_rect, 3, border_radius=15)
        
        # Title
        if victory:
            title_text = "Victory!"
            title_color = UI_SUCCESS
        else:
            title_text = "Game Over!"
            title_color = UI_DANGER
            
        title = FONTS['title'].render(title_text, True, title_color)
        title_rect = title.get_rect(center=(screen_w // 2, panel_y + 60))
        screen.blit(title, title_rect)
        
        # Instruction text
        instruction = FONTS['button'].render("Press ESC to return to menu", True, WHITE)
        instruction_rect = instruction.get_rect(center=(screen_w // 2, panel_y + 130))
        screen.blit(instruction, instruction_rect)

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
                    self.current_level_file = selected_level
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