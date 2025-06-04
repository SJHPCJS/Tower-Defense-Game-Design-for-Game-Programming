import pygame
import json
import os
import time
import random
import heapq
from collections import deque
from typing import List, Tuple, Set
from pathlib import Path
from settings import *
from pathfinding import a_star

class LevelCreator:
    def __init__(self):
        self.grid = [[1 for _ in range(GRID_W)] for _ in range(GRID_H)]  # 1 = grass, 0 = path
        self.spawn = (0, 0)
        # Set spawn as path first
        self.grid[self.spawn[1]][self.spawn[0]] = 0
        # Set a reasonable default home position
        self.home = (GRID_W - 2, GRID_H - 2)  # A bit inward from corner
        self.grid[self.home[1]][self.home[0]] = 0
        
        self.selected_tool = "place_path"
        self.message = ""
        self.message_color = WHITE
        self.message_timer = 0
        
        # Load tile images
        self._load_tile_images()
        
        # UI state
        self.save_dialog_active = False
        self.level_name_input = ""
        self.input_active = False
        
        # Level settings for the new save dialog
        self.level_settings = {
            'name': '',
            'initial_money': 100,
            'wave_count': 5,
            'enemy_speed': 50,
            'best_time': None
        }
        
        # Settings dialog input fields
        self.settings_inputs = {
            'name': '',
            'initial_money': str(self.level_settings['initial_money']),
            'wave_count': str(self.level_settings['wave_count']),
            'enemy_speed': str(self.level_settings['enemy_speed'])
        }
        self.active_input_field = None
        
        # Tools definition with modern UI colors
        self.tools = [
            {'id': 'place_path', 'name': 'Place Path', 'icon': 'PATH', 'color': UI_SUCCESS, 'hover': (60, 200, 120)},
            {'id': 'delete_path', 'name': 'Delete Path', 'icon': 'DEL', 'color': UI_DANGER, 'hover': (240, 80, 90)},
            {'id': 'reset_map', 'name': 'Reset Map', 'icon': 'RESET', 'color': UI_WARNING, 'hover': (255, 210, 30)},
            {'id': 'ai_generate', 'name': 'AI Generate', 'icon': 'AI', 'color': UI_ACCENT, 'hover': (90, 150, 200)},
            {'id': 'save_level', 'name': 'Save Level', 'icon': 'SAVE', 'color': (100, 100, 255), 'hover': (130, 130, 255)}
        ]
        
    def _load_tile_images(self):
        """Load tile images for rendering"""
        try:
            assets_path = Path(__file__).parent.parent / 'assets' / 'tiles'
            self.path_img = pygame.image.load(assets_path / 'path.png')
            self.grass_img = pygame.image.load(assets_path / 'grass.png')
            self.path_img = pygame.transform.scale(self.path_img, (GRID_SIZE, GRID_SIZE))
            self.grass_img = pygame.transform.scale(self.grass_img, (GRID_SIZE, GRID_SIZE))
        except:
            # Fallback to colored rectangles
            self.path_img = None
            self.grass_img = None
    
    def neighbors4(self, x: int, y: int, w: int = GRID_W, h: int = GRID_H):
        """Get 4-directional neighbors within grid bounds"""
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                yield nx, ny
    
    def algo_tower_path_optimized(self, strategy="optimal"):
        """Generate AI path using the optimized tower path algorithm"""
        # Generate original path using tower_path algorithm
        path = {self.spawn}
        x, y = self.spawn
        max_steps = GRID_W * GRID_H * 4
        
        # Generate main path to HOME
        while (x, y) != self.home and len(path) < max_steps:
            dirs = list(self.neighbors4(x, y))
            random.shuffle(dirs)
            dirs.sort(key=lambda p: (abs(p[0]-self.home[0])+abs(p[1]-self.home[1])) + random.randint(-2,2))
            moved = False
            for nx, ny in dirs:
                if (nx, ny) not in path:
                    x, y = nx, ny
                    path.add((x, y))
                    moved = True
                    break
            if not moved:
                if x < self.home[0]: x += 1
                elif x > self.home[0]: x -= 1
                elif y < self.home[1]: y += 1
                elif y > self.home[1]: y -= 1
                path.add((x,y))
        
        path.add(self.home)
        
        # Create initial grid
        temp_grid = [[1]*GRID_W for _ in range(GRID_H)]
        for px, py in path:
            temp_grid[py][px] = 0

        # Add random branches
        for _ in range(random.randint(2,5)):
            bx, by = random.choice(tuple(path))
            length = random.randint(2,4)
            dir = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
            nx, ny = bx, by
            for _ in range(length):
                nx += dir[0]; ny += dir[1]
                if not (0 <= nx < GRID_W and 0 <= ny < GRID_H): break
                temp_grid[ny][nx] = 0
                if random.random() < 0.25:
                    dir = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        
        # Optimize the generated path
        if strategy == "optimal":
            useful_nodes = self.find_all_optimal_path_nodes(temp_grid, self.spawn, self.home)
        else:
            useful_nodes = self.find_all_reasonable_path_nodes(temp_grid, self.spawn, self.home, tolerance=3)
        
        # Clean up useless path tiles
        for y in range(GRID_H):
            for x in range(GRID_W):
                if temp_grid[y][x] == 0 and (x, y) not in useful_nodes:
                    temp_grid[y][x] = 1  # Convert back to grass
        
        return temp_grid
    
    def find_shortest_path_length(self, grid: List[List[int]], start: Tuple[int,int], goal: Tuple[int,int]) -> int:
        """Find the shortest path length using A*"""
        if grid[start[1]][start[0]] != 0 or grid[goal[1]][goal[0]] != 0:
            return -1
        
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        open_set = [(0, start)]
        g_score = {start: 0}
        
        while open_set:
            current_f, current = heapq.heappop(open_set)
            
            if current == goal:
                return g_score[current]
            
            for nx, ny in self.neighbors4(current[0], current[1]):
                if grid[ny][nx] != 0:  # Can only move on path tiles
                    continue
                    
                tentative_g = g_score[current] + 1
                
                if (nx, ny) not in g_score or tentative_g < g_score[(nx, ny)]:
                    g_score[(nx, ny)] = tentative_g
                    f_score = tentative_g + heuristic((nx, ny), goal)
                    heapq.heappush(open_set, (f_score, (nx, ny)))
        
        return -1  # No path found

    def find_all_optimal_path_nodes(self, grid: List[List[int]], start: Tuple[int,int], goal: Tuple[int,int]) -> Set[Tuple[int,int]]:
        """Find all nodes that are part of ANY optimal (shortest) path from start to goal"""
        shortest_length = self.find_shortest_path_length(grid, start, goal)
        if shortest_length == -1:
            return set()
        
        optimal_nodes = set()
        
        # Calculate distances from start
        distances_from_start = {}
        queue = deque([(start, 0)])
        distances_from_start[start] = 0
        
        while queue:
            (x, y), dist = queue.popleft()
            for nx, ny in self.neighbors4(x, y):
                if grid[ny][nx] != 0:
                    continue
                if (nx, ny) not in distances_from_start:
                    distances_from_start[(nx, ny)] = dist + 1
                    queue.append(((nx, ny), dist + 1))
        
        # Calculate distances to goal
        distances_to_goal = {}
        queue = deque([(goal, 0)])
        distances_to_goal[goal] = 0
        
        while queue:
            (x, y), dist = queue.popleft()
            for nx, ny in self.neighbors4(x, y):
                if grid[ny][nx] != 0:
                    continue
                if (nx, ny) not in distances_to_goal:
                    distances_to_goal[(nx, ny)] = dist + 1
                    queue.append(((nx, ny), dist + 1))
        
        # Find nodes on optimal paths
        for y in range(GRID_H):
            for x in range(GRID_W):
                if grid[y][x] == 0:
                    pos = (x, y)
                    if (pos in distances_from_start and 
                        pos in distances_to_goal and
                        distances_from_start[pos] + distances_to_goal[pos] == shortest_length):
                        optimal_nodes.add(pos)
        
        return optimal_nodes

    def find_all_reasonable_path_nodes(self, grid: List[List[int]], start: Tuple[int,int], goal: Tuple[int,int], tolerance: int = 2) -> Set[Tuple[int,int]]:
        """Find all nodes that are part of any reasonably short path (within tolerance of optimal)"""
        shortest_length = self.find_shortest_path_length(grid, start, goal)
        if shortest_length == -1:
            return set()
        
        max_allowed_length = shortest_length + tolerance
        reasonable_nodes = set()
        
        # Calculate distances from start
        distances_from_start = {}
        queue = deque([(start, 0)])
        distances_from_start[start] = 0
        
        while queue:
            (x, y), dist = queue.popleft()
            for nx, ny in self.neighbors4(x, y):
                if grid[ny][nx] != 0:
                    continue
                if (nx, ny) not in distances_from_start:
                    distances_from_start[(nx, ny)] = dist + 1
                    queue.append(((nx, ny), dist + 1))
        
        # Calculate distances to goal
        distances_to_goal = {}
        queue = deque([(goal, 0)])
        distances_to_goal[goal] = 0
        
        while queue:
            (x, y), dist = queue.popleft()
            for nx, ny in self.neighbors4(x, y):
                if grid[ny][nx] != 0:
                    continue
                if (nx, ny) not in distances_to_goal:
                    distances_to_goal[(nx, ny)] = dist + 1
                    queue.append(((nx, ny), dist + 1))
        
        # Find nodes on reasonable paths
        for y in range(GRID_H):
            for x in range(GRID_W):
                if grid[y][x] == 0:
                    pos = (x, y)
                    if (pos in distances_from_start and 
                        pos in distances_to_goal and
                        distances_from_start[pos] + distances_to_goal[pos] <= max_allowed_length):
                        reasonable_nodes.add(pos)
        
        return reasonable_nodes
    
    def has_valid_path(self):
        """Check if there's a valid path from spawn to home"""
        return self.find_shortest_path_length(self.grid, self.spawn, self.home) > 0
    
    def show_message(self, text, color=WHITE, duration=3000):
        """Show a temporary message"""
        self.message = text
        self.message_color = color
        self.message_timer = pygame.time.get_ticks() + duration
    
    def handle_events(self, event):
        if event.type == pygame.QUIT:
            return "quit"
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.save_dialog_active:
                    self.save_dialog_active = False
                    self.input_active = False
                    self.active_input_field = None
                else:
                    return "menu"
            elif self.save_dialog_active and self.active_input_field:
                # Handle input for any active field
                current_text = self.settings_inputs[self.active_input_field]
                if event.key == pygame.K_RETURN or event.key == pygame.K_TAB:
                    self.active_input_field = None
                elif event.key == pygame.K_BACKSPACE:
                    self.settings_inputs[self.active_input_field] = current_text[:-1]
                else:
                    if self.active_input_field == 'name':
                        # Allow text input for name
                        if len(current_text) < 30 and event.unicode.isprintable():
                            self.settings_inputs[self.active_input_field] = current_text + event.unicode
                    else:
                        # Only digits for numeric fields
                        if event.unicode.isdigit() and len(current_text) < 10:
                            self.settings_inputs[self.active_input_field] = current_text + event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            screen = pygame.display.get_surface()
            screen_w, screen_h = screen.get_size()
            
            if self.save_dialog_active:
                result = self.handle_save_dialog_click(mx, my, screen_w, screen_h)
                if result == "menu":
                    return "menu"
            elif my < UI_HEIGHT:
                result = self.handle_toolbar_click(mx, my, screen_w)
                if result:
                    return result
            else:
                self.handle_grid_click(mx, my, screen_w, screen_h)
        elif event.type == pygame.VIDEORESIZE:
            new_width = max(event.w, MIN_SCREEN_W)
            new_height = max(event.h, MIN_SCREEN_H)
            pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE | pygame.DOUBLEBUF)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
        
        return None

    def handle_toolbar_click(self, mx, my, screen_w):
        """Handle toolbar button clicks"""
        button_width = 150
        button_height = 50
        margin = 10
        start_x = margin
        
        for i, tool in enumerate(self.tools):
            x = start_x + i * (button_width + margin)
            y = (UI_HEIGHT - button_height) // 2
            
            if x <= mx <= x + button_width and y <= my <= y + button_height:
                if tool['id'] == 'save_level':
                    if self.has_valid_path():
                        self.save_dialog_active = True
                        # Reset all input fields
                        self.settings_inputs = {
                            'name': '',
                            'initial_money': str(self.level_settings['initial_money']),
                            'wave_count': str(self.level_settings['wave_count']),
                            'enemy_speed': str(self.level_settings['enemy_speed'])
                        }
                        self.active_input_field = 'name'  # Start with name field active
                    else:
                        self.show_message("No valid path found!", UI_DANGER)
                elif tool['id'] == 'reset_map':
                    self.reset_map()
                elif tool['id'] == 'ai_generate':
                    self.ai_generate_map()
                else:
                    self.selected_tool = tool['id']
                break
        
        return None

    def handle_grid_click(self, mx, my, screen_w, screen_h):
        """Handle grid area clicks"""
        gx, gy = px_to_grid(mx, my, screen_w, screen_h)
        if 0 <= gx < GRID_W and 0 <= gy < GRID_H:
            if self.selected_tool == "place_path":
                self.grid[gy][gx] = 0
            elif self.selected_tool == "delete_path":
                self.grid[gy][gx] = 1

    def handle_save_dialog_click(self, mx, my, screen_w, screen_h):
        """Handle save dialog clicks"""
        dialog_w, dialog_h = 600, 500
        dialog_x = (screen_w - dialog_w) // 2
        dialog_y = (screen_h - dialog_h) // 2
        
        # Input fields
        field_configs = [
            ('name', dialog_y + 100),
            ('initial_money', dialog_y + 150),
            ('wave_count', dialog_y + 200),
            ('enemy_speed', dialog_y + 250)
        ]
        
        self.active_input_field = None
        for field_name, y_pos in field_configs:
            field_rect = pygame.Rect(dialog_x + 250, y_pos, 200, 30)
            if field_rect.collidepoint(mx, my):
                self.active_input_field = field_name
                break
        
        # Save button
        save_rect = pygame.Rect(dialog_x + dialog_w - 180, dialog_y + dialog_h - 70, 80, 40)
        if save_rect.collidepoint(mx, my):
            result = self.save_level_with_settings()
            if result:  # If save was successful, return to menu
                return "menu"
        
        # Cancel button
        cancel_rect = pygame.Rect(dialog_x + dialog_w - 90, dialog_y + dialog_h - 70, 80, 40)
        if cancel_rect.collidepoint(mx, my):
            self.save_dialog_active = False
            self.active_input_field = None

    def reset_map(self):
        """Reset the map to all grass"""
        self.grid = [[1 for _ in range(GRID_W)] for _ in range(GRID_H)]
        self.spawn = (0, 0)
        self.home = (GRID_W-1, GRID_H-1)
        self.grid[self.spawn[1]][self.spawn[0]] = 0
        self.grid[self.home[1]][self.home[0]] = 0
        self.show_message("Map reset to grass!", UI_SUCCESS)

    def ai_generate_map(self):
        """Generate a map using AI pathfinding"""
        try:
            # Use the optimized algorithm to generate path
            new_grid = self.algo_tower_path_optimized("optimal")
            self.grid = new_grid
            
            # Update spawn and home
            self.spawn = self.find_best_start_point()
            self.home = self.find_best_end_point()
            
            self.show_message("AI generated path successfully!", UI_SUCCESS)
        except Exception as e:
            self.show_message(f"AI generation failed: {str(e)}", UI_DANGER)
    
    def find_best_start_point(self):
        """Find the best start point in the current grid"""
        # Look for path tiles in the first row or first column
        for x in range(GRID_W):
            if self.grid[0][x] == 0:
                return (x, 0)
        for y in range(GRID_H):
            if self.grid[y][0] == 0:
                return (0, y)
        # Default fallback
        return (0, 0)
    
    def find_best_end_point(self):
        """Find the best end point in the current grid"""
        start = self.find_best_start_point()
        max_distance = -1
        best_end = (GRID_W-1, GRID_H-1)
        
        for y in range(GRID_H):
            for x in range(GRID_W):
                if self.grid[y][x] == 0:  # Is path
                    distance = abs(x - start[0]) + abs(y - start[1])
                    if distance > max_distance:
                        max_distance = distance
                        best_end = (x, y)
        
        return best_end

    def save_level_with_settings(self):
        """Save the level with all settings"""
        try:
            # Validate name
            if not self.settings_inputs['name'].strip():
                self.show_message("Please enter a level name!", UI_DANGER)
                return False
            
            # Parse settings from input fields
            initial_money = int(self.settings_inputs['initial_money'] or 100)
            wave_count = int(self.settings_inputs['wave_count'] or 5)
            enemy_speed = int(self.settings_inputs['enemy_speed'] or 50)
            
            # Validate settings
            if initial_money < 0:
                initial_money = 100
            if wave_count < 1:
                wave_count = 5
            if enemy_speed < 10:
                enemy_speed = 50
                
        except ValueError:
            self.show_message("Invalid numeric values!", UI_DANGER)
            return False
        
        # Update spawn and home
        self.spawn = self.find_best_start_point()
        self.home = self.find_best_end_point()
        
        # Create level data
        level_data = {
            "name": self.settings_inputs['name'].strip(),
            "settings": {
                "initial_money": initial_money,
                "wave_count": wave_count,
                "enemy_speed": enemy_speed,
                "best_time": None
            },
            "grid": self.grid
        }
        
        # Save to file
        levels_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "levels")
        os.makedirs(levels_dir, exist_ok=True)
        
        filename = f"{self.settings_inputs['name'].strip()}.json"
        filepath = os.path.join(levels_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(level_data, f, indent=2, ensure_ascii=False)
            self.show_message(f"Level saved as {filename}!", UI_SUCCESS)
            self.save_dialog_active = False
            return True
        except Exception as e:
            self.show_message(f"Failed to save: {str(e)}", UI_DANGER)
            return False

    def draw(self, screen):
        """Main drawing method"""
        current_screen = pygame.display.get_surface()
        screen_w, screen_h = current_screen.get_size()
        
        # Clear screen
        screen.fill(BG_COLOUR)
        
        # Draw main UI
        self.draw_toolbar(screen, screen_w)
        self.draw_grid(screen, screen_w, screen_h)
        
        # Handle message timer
        if self.message and pygame.time.get_ticks() > self.message_timer:
            self.message = ""
        
        # Draw temporary message
        if self.message:
            self.draw_message(screen, screen_w, screen_h)
        
        # Draw dialogs on top
        if self.save_dialog_active:
            self.draw_complete_save_dialog(screen, screen_w, screen_h)

    def draw_complete_save_dialog(self, screen, screen_w, screen_h):
        """Draw the complete save dialog with all settings"""
        dialog_w, dialog_h = 600, 500
        dialog_x = (screen_w - dialog_w) // 2
        dialog_y = (screen_h - dialog_h) // 2
        
        # Semi-transparent overlay
        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Dialog box
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)
        pygame.draw.rect(screen, UI_DARK_BG, dialog_rect, border_radius=15)
        pygame.draw.rect(screen, UI_ACCENT, dialog_rect, 3, border_radius=15)
        
        # Title
        title_text = FONTS['title'].render("Save Level", True, WHITE)
        title_x = dialog_x + (dialog_w - title_text.get_width()) // 2
        screen.blit(title_text, (title_x, dialog_y + 20))
        
        # Input fields
        field_configs = [
            ('Level Name:', 'name', dialog_y + 100),
            ('Initial Money:', 'initial_money', dialog_y + 150),
            ('Wave Count:', 'wave_count', dialog_y + 200),
            ('Enemy Speed:', 'enemy_speed', dialog_y + 250)
        ]
        
        for label_text, field_name, y_pos in field_configs:
            # Label
            label = FONTS['hud'].render(label_text, True, WHITE)
            screen.blit(label, (dialog_x + 30, y_pos))
            
            # Input field
            field_rect = pygame.Rect(dialog_x + 250, y_pos, 200, 30)
            is_active = self.active_input_field == field_name
            field_color = UI_ACCENT if is_active else UI_MID_BG
            
            pygame.draw.rect(screen, field_color, field_rect, border_radius=5)
            pygame.draw.rect(screen, WHITE, field_rect, 2, border_radius=5)
            
            # Input text
            display_text = self.settings_inputs[field_name]
            input_text = FONTS['hud'].render(display_text, True, WHITE)
            screen.blit(input_text, (field_rect.x + 10, field_rect.y + 5))
            
            # Cursor for active field
            if is_active and pygame.time.get_ticks() % 1000 < 500:
                cursor_x = field_rect.x + 10 + input_text.get_width()
                pygame.draw.line(screen, WHITE, (cursor_x, field_rect.y + 5), (cursor_x, field_rect.y + 25), 2)
        
        # Help text
        help_texts = [
            "Configure your level:",
            "• Level Name: Display name for the level",
            "• Initial Money: Starting money for players",
            "• Wave Count: Total number of enemy waves",
            "• Enemy Speed: Base movement speed of enemies"
        ]
        
        for i, help_text in enumerate(help_texts):
            color = UI_ACCENT if i == 0 else (200, 200, 200)
            text = FONTS['small'].render(help_text, True, color)
            screen.blit(text, (dialog_x + 30, dialog_y + 310 + i * 20))
        
        # Buttons
        # Save button
        save_x = dialog_x + dialog_w - 180
        save_y = dialog_y + dialog_h - 70
        save_rect = pygame.Rect(save_x, save_y, 80, 40)
        
        mx, my = pygame.mouse.get_pos()
        save_hover = save_rect.collidepoint(mx, my)
        save_color = UI_SUCCESS if save_hover else UI_MID_BG
        
        pygame.draw.rect(screen, save_color, save_rect, border_radius=5)
        pygame.draw.rect(screen, UI_SUCCESS, save_rect, 2, border_radius=5)
        save_text = FONTS['button'].render("Save", True, WHITE)
        save_text_x = save_x + (80 - save_text.get_width()) // 2
        save_text_y = save_y + (40 - save_text.get_height()) // 2
        screen.blit(save_text, (save_text_x, save_text_y))
        
        # Cancel button
        cancel_x = dialog_x + dialog_w - 90
        cancel_y = dialog_y + dialog_h - 70
        cancel_rect = pygame.Rect(cancel_x, cancel_y, 80, 40)
        
        cancel_hover = cancel_rect.collidepoint(mx, my)
        cancel_color = UI_DANGER if cancel_hover else UI_MID_BG
        
        pygame.draw.rect(screen, cancel_color, cancel_rect, border_radius=5)
        pygame.draw.rect(screen, UI_DANGER, cancel_rect, 2, border_radius=5)
        cancel_text = FONTS['button'].render("Cancel", True, WHITE)
        cancel_text_x = cancel_x + (80 - cancel_text.get_width()) // 2
        cancel_text_y = cancel_y + (40 - cancel_text.get_height()) // 2
        screen.blit(cancel_text, (cancel_text_x, cancel_text_y))
        
        # Instructions
        instr_text = FONTS['small'].render("Click fields to edit, then press Save", True, (180, 180, 180))
        instr_x = dialog_x + (dialog_w - instr_text.get_width()) // 2
        screen.blit(instr_text, (instr_x, dialog_y + dialog_h - 25))

    def draw_toolbar(self, screen, screen_w):
        """Draw the modern toolbar"""
        # Background
        pygame.draw.rect(screen, UI_DARK_BG, (0, 0, screen_w, UI_HEIGHT))
        pygame.draw.line(screen, UI_MID_BG, (0, UI_HEIGHT-1), (screen_w, UI_HEIGHT-1), 2)
        
        # Tool buttons
        button_width = 150
        button_height = 50
        margin = 10
        start_x = margin
        
        mx, my = pygame.mouse.get_pos()
        
        for i, tool in enumerate(self.tools):
            x = start_x + i * (button_width + margin)
            y = (UI_HEIGHT - button_height) // 2
            
            # Check hover state
            is_hovered = x <= mx <= x + button_width and y <= my <= y + button_height and my < UI_HEIGHT
            is_selected = self.selected_tool == tool['id']
            
            # Button color
            if is_selected:
                button_color = tool['hover']
            elif is_hovered:
                button_color = tuple(min(255, c + 20) for c in tool['color'])
            else:
                button_color = tool['color']
            
            # Draw button with rounded corners
            pygame.draw.rect(screen, button_color, (x, y, button_width, button_height), border_radius=8)
            
            # Button border
            border_color = WHITE if is_selected else UI_MID_BG
            pygame.draw.rect(screen, border_color, (x, y, button_width, button_height), 2, border_radius=8)
            
            # Icon and text
            icon_text = FONTS['button'].render(tool['icon'], True, WHITE)
            name_text = FONTS['small'].render(tool['name'], True, WHITE)
            
            icon_x = x + (button_width - icon_text.get_width()) // 2
            name_x = x + (button_width - name_text.get_width()) // 2
            
            screen.blit(icon_text, (icon_x, y + 8))
            screen.blit(name_text, (name_x, y + 28))
        
        # Title
        title_text = FONTS['subtitle'].render("Level Creator", True, WHITE)
        screen.blit(title_text, (screen_w - title_text.get_width() - 20, 20))
        
        # Instructions
        instr_text = FONTS['small'].render("ESC: Return to Menu", True, (200, 200, 200))
        screen.blit(instr_text, (screen_w - instr_text.get_width() - 20, 50))
    
    def draw_grid(self, screen, screen_w, screen_h):
        """Draw the game grid"""
        for y in range(GRID_H):
            for x in range(GRID_W):
                px, py = grid_to_px(x, y, screen_w, screen_h)
                scaled_size = get_scaled_grid_size(screen_w, screen_h)
                
                # Draw tile
                if self.path_img and self.grass_img:
                    # Use images
                    if self.grid[y][x] == 0:  # Path
                        img = pygame.transform.scale(self.path_img, (scaled_size, scaled_size))
                    else:  # Grass
                        img = pygame.transform.scale(self.grass_img, (scaled_size, scaled_size))
                    screen.blit(img, (px, py))
                else:
                    # Fallback to colors
                    color = (139, 69, 19) if self.grid[y][x] == 0 else (34, 139, 34)  # Brown path, green grass
                    pygame.draw.rect(screen, color, (px, py, scaled_size, scaled_size))
                
                # Draw grid lines
                pygame.draw.rect(screen, (100, 100, 100), (px, py, scaled_size, scaled_size), 1)
                
                # Highlight spawn and home
                if (x, y) == self.spawn:
                    pygame.draw.rect(screen, GREEN, (px+2, py+2, scaled_size-4, scaled_size-4), 3)
                    text = FONTS['small'].render("START", True, WHITE)
                    screen.blit(text, (px + 4, py + 4))
                elif (x, y) == self.home:
                    pygame.draw.rect(screen, RED, (px+2, py+2, scaled_size-4, scaled_size-4), 3)
                    text = FONTS['small'].render("HOME", True, WHITE)
                    screen.blit(text, (px + 4, py + 4))
    
    def draw_message(self, screen, screen_w, screen_h):
        """Draw temporary messages"""
        if self.message:
            text = FONTS['hud'].render(self.message, True, self.message_color)
            bg_rect = pygame.Rect(0, 0, text.get_width() + 20, text.get_height() + 10)
            bg_rect.centerx = screen_w // 2
            bg_rect.y = screen_h - 80
            
            pygame.draw.rect(screen, UI_DARK_BG, bg_rect, border_radius=5)
            pygame.draw.rect(screen, self.message_color, bg_rect, 2, border_radius=5)
            
            text_x = bg_rect.x + 10
            text_y = bg_rect.y + 5
            screen.blit(text, (text_x, text_y))

def run_level_creator():
    """Main function to run the level creator"""
    creator = LevelCreator()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return "quit"
            
            result = creator.handle_events(event)
            if result:
                return result
        
        current_screen = pygame.display.get_surface()
        creator.draw(current_screen)
        pygame.display.flip()
        clock.tick(FPS)
    
    return "menu" 