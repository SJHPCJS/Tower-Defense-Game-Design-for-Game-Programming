import pygame
import json
import time
from settings import *
from grid import GRID_MAP
from map_component import MapComponent

class LevelCreator:
    def __init__(self):
        self.game_map = MapComponent()
        self.selected_tool = None
        self.grid = [[0 for _ in range(GRID_W)] for _ in range(GRID_H)]  # 0 = grass, 1 = path
        self.start_pos = None
        self.end_pos = None
        
        # Create toolbar buttons
        self.tools = [
            {'name': 'Grass', 'color': GRASS_COLOR},
            {'name': 'Path', 'color': PATH_COLOR},
            {'name': 'Start', 'color': GREEN},
            {'name': 'End', 'color': RED},
            {'name': 'Save', 'color': BLUE}
        ]
        
        self.buttons = []
        card_w, card_h, margin = 60, UI_HEIGHT - 20, 10
        for i, tool in enumerate(self.tools):
            x = margin + i * (card_w + margin)
            y = (UI_HEIGHT - card_h) // 2
            self.buttons.append((pygame.Rect(x, y, card_w, card_h), tool))
        
        self.back_button = pygame.Rect(SCREEN_W - 100, 20, 80, 30)
        self.save_dialog_active = False
        self.save_text = ""
        self.text_input_active = False
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                
                if my < UI_HEIGHT:
                    # Toolbar interaction
                    for rect, tool in self.buttons:
                        if rect.collidepoint(mx, my):
                            self.selected_tool = tool
                            if tool['name'] == 'Save':
                                self.save_dialog_active = True
                                self.text_input_active = True
                            break
                else:
                    # Grid interaction
                    gx = mx // GRID_SIZE
                    gy = (my - UI_HEIGHT) // GRID_SIZE
                    if 0 <= gx < GRID_W and 0 <= gy < GRID_H:
                        if self.selected_tool:
                            if self.selected_tool['name'] == 'Grass':
                                self.grid[gy][gx] = 0
                            elif self.selected_tool['name'] == 'Path':
                                self.grid[gy][gx] = 1
                            elif self.selected_tool['name'] == 'Start':
                                self.start_pos = (gx, gy)
                            elif self.selected_tool['name'] == 'End':
                                self.end_pos = (gx, gy)
                
                if self.save_dialog_active:
                    if self.back_button.collidepoint(mx, my):
                        self.save_dialog_active = False
                        self.text_input_active = False
                        self.save_text = ""
            
            if event.type == pygame.KEYDOWN and self.text_input_active:
                if event.key == pygame.K_RETURN:
                    if self.save_text:
                        self.save_level()
                        self.save_dialog_active = False
                        self.text_input_active = False
                        self.save_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.save_text = self.save_text[:-1]
                else:
                    self.save_text += event.unicode
        
        return True
    
    def save_level(self):
        if not self.start_pos or not self.end_pos:
            return
            
        level_data = {
            'grid': self.grid,
            'start': self.start_pos,
            'end': self.end_pos
        }
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"../levels/{self.save_text}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(level_data, f)
    
    def draw(self):
        screen.fill(BG_COLOR)
        
        # Draw toolbar
        pygame.draw.rect(screen, BLACK, (0, 0, SCREEN_W, UI_HEIGHT))
        
        for rect, tool in self.buttons:
            pygame.draw.rect(screen, tool['color'], rect)
            border = WHITE if self.selected_tool is tool else BLACK
            pygame.draw.rect(screen, border, rect, 2)
            text = FONT.render(tool['name'], True, BLACK)
            screen.blit(text, text.get_rect(center=rect.center))
        
        # Draw grid
        for y in range(GRID_H):
            for x in range(GRID_W):
                rect = pygame.Rect(x * GRID_SIZE, UI_HEIGHT + y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                color = PATH_COLOR if self.grid[y][x] == 1 else GRASS_COLOR
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)
        
        # Draw start and end positions
        if self.start_pos:
            x, y = self.start_pos
            rect = pygame.Rect(x * GRID_SIZE, UI_HEIGHT + y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, GREEN, rect)
        
        if self.end_pos:
            x, y = self.end_pos
            rect = pygame.Rect(x * GRID_SIZE, UI_HEIGHT + y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, RED, rect)
        
        # Draw save dialog
        if self.save_dialog_active:
            dialog_rect = pygame.Rect(SCREEN_W//2 - 150, SCREEN_H//2 - 50, 300, 100)
            pygame.draw.rect(screen, WHITE, dialog_rect)
            pygame.draw.rect(screen, BLACK, dialog_rect, 2)
            
            text = FONT.render("Enter level name:", True, BLACK)
            screen.blit(text, (dialog_rect.x + 10, dialog_rect.y + 10))
            
            input_rect = pygame.Rect(dialog_rect.x + 10, dialog_rect.y + 40, 280, 30)
            pygame.draw.rect(screen, (200, 200, 200), input_rect)
            pygame.draw.rect(screen, BLACK, input_rect, 1)
            
            text = FONT.render(self.save_text, True, BLACK)
            screen.blit(text, (input_rect.x + 5, input_rect.y + 5))
            
            pygame.draw.rect(screen, (100, 100, 100), self.back_button)
            text = FONT.render("Cancel", True, WHITE)
            screen.blit(text, (self.back_button.x + 20, self.back_button.y + 5))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            clock.tick(FPS) 