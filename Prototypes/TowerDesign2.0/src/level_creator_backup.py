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

class LevelCreator:
    def __init__(self):
        self.grid = [[1 for _ in range(GRID_W)] for _ in range(GRID_H)]  # 1 = grass, 0 = path
        self.spawn = (0, 0)
        self.home = (GRID_W - 1, GRID_H - 1)
        
        # Set spawn and home as path tiles
        self.grid[self.spawn[1]][self.spawn[0]] = 0
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
        
        # Tools definition with modern UI colors
        self.tools = [
            {'id': 'place_path', 'name': 'Place Path', 'icon': '🛤️', 'color': UI_SUCCESS, 'hover': (60, 200, 120)},
            {'id': 'delete_path', 'name': 'Delete Path', 'icon': '🗑️', 'color': UI_DANGER, 'hover': (240, 80, 90)},
            {'id': 'reset_map', 'name': 'Reset Map', 'icon': '🔄', 'color': UI_WARNING, 'hover': (255, 210, 30)},
            {'id': 'ai_generate', 'name': 'AI Generate', 'icon': '🧠', 'color': UI_ACCENT, 'hover': (90, 150, 200)},
            {'id': 'save_level', 'name': 'Save Level', 'icon': '💾', 'color': (100, 100, 255), 'hover': (130, 130, 255)}
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
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.save_dialog_active:
                    self.save_dialog_active = False
                    self.input_active = False
                    self.level_name_input = ""
                else:
                    return "main_menu"
            
            if self.input_active:
                if event.key == pygame.K_RETURN:
                    if self.level_name_input.strip():
                        self.save_level()
                    self.save_dialog_active = False
                    self.input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.level_name_input = self.level_name_input[:-1]
                else:
                    if len(self.level_name_input) < 30:
                        self.level_name_input += event.unicode
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mx, my = event.pos
                current_screen = pygame.display.get_surface()
                screen_w, screen_h = current_screen.get_size()
                
                if my < UI_HEIGHT:
                    # Toolbar interaction
                    self.handle_toolbar_click(mx, my, screen_w)
                else:
                    # Grid interaction
                    if not self.save_dialog_active:
                        self.handle_grid_click(mx, my, screen_w, screen_h)
                
                # Save dialog interaction
                if self.save_dialog_active:
                    self.handle_save_dialog_click(mx, my, screen_w, screen_h)
        
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
                        self.input_active = True
                        self.level_name_input = ""
                    else:
                        self.show_message("⚠️ No valid path found! Please create a path from spawn to home.", UI_DANGER)
                elif tool['id'] == 'reset_map':
                    self.reset_map()
                elif tool['id'] == 'ai_generate':
                    self.ai_generate_map()
                else:
                    self.selected_tool = tool['id']
                break
    
    def handle_grid_click(self, mx, my, screen_w, screen_h):
        """Handle grid tile clicks"""
        gx, gy = px_to_grid(mx, my, screen_w, screen_h)
        
        if 0 <= gx < GRID_W and 0 <= gy < GRID_H:
            # Don't allow modifying spawn and home
            if (gx, gy) == self.spawn or (gx, gy) == self.home:
                self.show_message("⚠️ Cannot modify spawn or home positions!", UI_WARNING)
                return
            
            if self.selected_tool == 'place_path':
                self.grid[gy][gx] = 0
            elif self.selected_tool == 'delete_path':
                self.grid[gy][gx] = 1
    
    def handle_save_dialog_click(self, mx, my, screen_w, screen_h):
        """Handle save dialog clicks"""
        dialog_w, dialog_h = 400, 200
        dialog_x = (screen_w - dialog_w) // 2
        dialog_y = (screen_h - dialog_h) // 2
        
        # Cancel button
        cancel_x = dialog_x + dialog_w - 90
        cancel_y = dialog_y + dialog_h - 50
        
        if cancel_x <= mx <= cancel_x + 80 and cancel_y <= my <= cancel_y + 40:
            self.save_dialog_active = False
            self.input_active = False
            self.level_name_input = ""
    
    def reset_map(self):
        """Reset the map to all grass except spawn and home"""
        self.grid = [[1 for _ in range(GRID_W)] for _ in range(GRID_H)]
        self.grid[self.spawn[1]][self.spawn[0]] = 0
        self.grid[self.home[1]][self.home[0]] = 0
        self.show_message("✅ Map reset successfully!", UI_SUCCESS)
    
    def ai_generate_map(self):
        """Generate map using AI algorithm"""
        try:
            new_grid = self.algo_tower_path_optimized("optimal")
            self.grid = new_grid
            path_count = sum(1 for row in self.grid for cell in row if cell == 0)
            self.show_message(f"🧠 AI generated map with {path_count} path tiles!", UI_SUCCESS)
        except Exception as e:
            self.show_message(f"❌ AI generation failed: {str(e)}", UI_DANGER)
    
    def save_level(self):
        """Save the current level"""
        if not self.level_name_input.strip():
            self.show_message("⚠️ Please enter a level name!", UI_WARNING)
            return
        
        # Check for existing files
        levels_dir = Path(__file__).parent.parent / 'levels'
        level_filename = f"{self.level_name_input.strip()}.json"
        level_path = levels_dir / level_filename
        
        if level_path.exists():
            self.show_message(f"⚠️ Level '{self.level_name_input}' already exists!", UI_WARNING)
            return
        
        # Create level data
        level_data = {
            'name': self.level_name_input.strip(),
            'grid': self.grid
        }
        
        try:
            # Ensure levels directory exists
            levels_dir.mkdir(exist_ok=True)
            
            # Save the level
            with open(level_path, 'w', encoding='utf-8') as f:
                json.dump(level_data, f, indent=2)
            
            self.show_message(f"✅ Level '{self.level_name_input}' saved successfully! Press ESC to return to main menu.", UI_SUCCESS, 5000)
            self.level_name_input = ""
            
        except Exception as e:
            self.show_message(f"❌ Failed to save level: {str(e)}", UI_DANGER)
    
    def draw(self, screen):
        """Draw the level creator interface"""
        screen_w, screen_h = screen.get_size()
        
        # Clear screen
        screen.fill(BG_COLOR)
        
        # Draw toolbar
        self.draw_toolbar(screen, screen_w)
        
        # Draw grid
        self.draw_grid(screen, screen_w, screen_h)
        
        # Draw message
        if pygame.time.get_ticks() < self.message_timer:
            self.draw_message(screen, screen_w, screen_h)
        
        # Draw save dialog
        if self.save_dialog_active:
            self.draw_save_dialog(screen, screen_w, screen_h)
    
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
    
    def draw_save_dialog(self, screen, screen_w, screen_h):
        """Draw the save level dialog"""
        dialog_w, dialog_h = 400, 200
        dialog_x = (screen_w - dialog_w) // 2
        dialog_y = (screen_h - dialog_h) // 2
        
        # Semi-transparent overlay
        overlay = pygame.Surface((screen_w, screen_h))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Dialog box
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)
        pygame.draw.rect(screen, UI_DARK_BG, dialog_rect, border_radius=10)
        pygame.draw.rect(screen, UI_ACCENT, dialog_rect, 3, border_radius=10)
        
        # Title
        title_text = FONTS['button'].render("Save Level", True, WHITE)
        title_x = dialog_x + (dialog_w - title_text.get_width()) // 2
        screen.blit(title_text, (title_x, dialog_y + 20))
        
        # Input label
        label_text = FONTS['hud'].render("Level Name:", True, WHITE)
        screen.blit(label_text, (dialog_x + 20, dialog_y + 60))
        
        # Input box
        input_rect = pygame.Rect(dialog_x + 20, dialog_y + 90, dialog_w - 40, 30)
        input_color = UI_ACCENT if self.input_active else UI_MID_BG
        pygame.draw.rect(screen, input_color, input_rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, input_rect, 2, border_radius=5)
        
        # Input text
        input_text = FONTS['hud'].render(self.level_name_input, True, WHITE)
        screen.blit(input_text, (input_rect.x + 10, input_rect.y + 5))
        
        # Cursor
        if self.input_active and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = input_rect.x + 10 + input_text.get_width()
            pygame.draw.line(screen, WHITE, (cursor_x, input_rect.y + 5), (cursor_x, input_rect.y + 25), 2)
        
        # Cancel button
        cancel_x = dialog_x + dialog_w - 90
        cancel_y = dialog_y + dialog_h - 50
        cancel_rect = pygame.Rect(cancel_x, cancel_y, 80, 40)
        
        mx, my = pygame.mouse.get_pos()
        cancel_hover = cancel_rect.collidepoint(mx, my)
        cancel_color = UI_DANGER if cancel_hover else UI_MID_BG
        
        pygame.draw.rect(screen, cancel_color, cancel_rect, border_radius=5)
        cancel_text = FONTS['small'].render("Cancel", True, WHITE)
        cancel_text_x = cancel_x + (80 - cancel_text.get_width()) // 2
        cancel_text_y = cancel_y + (40 - cancel_text.get_height()) // 2
        screen.blit(cancel_text, (cancel_text_x, cancel_text_y))
        
        # Instructions
        instr_text = FONTS['small'].render("Press ENTER to save, ESC to cancel", True, (200, 200, 200))
        instr_x = dialog_x + (dialog_w - instr_text.get_width()) // 2
        screen.blit(instr_text, (instr_x, dialog_y + dialog_h - 20))

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
    
    return "quit" 