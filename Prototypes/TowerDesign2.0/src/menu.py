import pygame
import sys
from settings import *

class Button:
    def __init__(self, x, y, width, height, text, color=(100, 100, 100), hover_color=(150, 150, 150)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        text_surface = FONT.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class Menu:
    def __init__(self):
        self.start_button = Button(SCREEN_W//2 - 100, SCREEN_H//2 - 50, 200, 50, "Start Game")
        self.creator_button = Button(SCREEN_W//2 - 100, SCREEN_H//2 + 50, 200, 50, "Level Creator")
        
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if self.start_button.handle_event(event):
                    return "start"
                if self.creator_button.handle_event(event):
                    return "creator"
                
            screen.fill(BG_COLOR)
            
            # Draw title
            title = pygame.font.SysFont(None, 72).render("Forest Guard", True, BLACK)
            title_rect = title.get_rect(center=(SCREEN_W//2, SCREEN_H//4))
            screen.blit(title, title_rect)
            
            self.start_button.draw(screen)
            self.creator_button.draw(screen)
            
            pygame.display.flip()
            clock.tick(FPS)

class LevelSelector:
    def __init__(self):
        self.buttons = []
        self.back_button = Button(20, 20, 100, 40, "Back")
        self.load_levels()
        
    def load_levels(self):
        import os
        import json
        
        # Load predefined levels
        level_files = [f for f in os.listdir("../levels") if f.endswith(".json")]
        for i, level_file in enumerate(level_files):
            x = SCREEN_W//2 - 100
            y = 100 + i * 60
            self.buttons.append(Button(x, y, 200, 50, level_file.replace(".json", "")))
    
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if self.back_button.handle_event(event):
                    return None
                
                for i, button in enumerate(self.buttons):
                    if button.handle_event(event):
                        return f"../levels/{button.text}.json"
            
            screen.fill(BG_COLOR)
            
            # Draw title
            title = pygame.font.SysFont(None, 48).render("Select Level", True, BLACK)
            title_rect = title.get_rect(center=(SCREEN_W//2, 50))
            screen.blit(title, title_rect)
            
            self.back_button.draw(screen)
            for button in self.buttons:
                button.draw(screen)
            
            pygame.display.flip()
            clock.tick(FPS) 