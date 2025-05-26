import pygame
import sys
import os
import json
from settings import *

class Button:
    def __init__(self, x, y, width, height, text, color=FOREST_GREEN, hover_color=LIGHT_GREEN, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.font = pygame.font.SysFont('Arial', 24, bold=True)

    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        # Draw button with rounded corners effect
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, DARK_GREEN, self.rect, 3)
        
        # Add shadow effect
        shadow_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, self.rect.width, self.rect.height)
        pygame.draw.rect(screen, (0, 0, 0, 50), shadow_rect)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, DARK_GREEN, self.rect, 3)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False

class MainMenu:
    def __init__(self):
        # Title font
        self.title_font = pygame.font.SysFont('Arial', 72, bold=True)
        self.subtitle_font = pygame.font.SysFont('Arial', 24)
        
        # Buttons
        button_width, button_height = 250, 60
        button_x = SCREEN_W // 2 - button_width // 2
        
        self.start_button = Button(button_x, SCREEN_H // 2 - 30, button_width, button_height, "Start Game")
        self.create_button = Button(button_x, SCREEN_H // 2 + 50, button_width, button_height, "Create a Level")
        self.quit_button = Button(button_x, SCREEN_H // 2 + 130, button_width, button_height, "Quit", color=BROWN, hover_color=RED)
        
    def draw_background(self, screen):
        # Gradient background
        for y in range(SCREEN_H):
            color_ratio = y / SCREEN_H
            r = int(135 + (173 - 135) * color_ratio)
            g = int(206 + (216 - 206) * color_ratio)
            b = int(235 + (230 - 235) * color_ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_W, y))
        
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if self.start_button.handle_event(event):
                    return "start"
                if self.create_button.handle_event(event):
                    return "creator"
                if self.quit_button.handle_event(event):
                    pygame.quit()
                    sys.exit()
                
            self.draw_background(screen)
            
            # Draw title
            title = self.title_font.render("Forest Guard", True, DARK_GREEN)
            title_rect = title.get_rect(center=(SCREEN_W // 2, SCREEN_H // 4))
            # Title shadow
            title_shadow = self.title_font.render("Forest Guard", True, BLACK)
            shadow_rect = title_shadow.get_rect(center=(SCREEN_W // 2 + 3, SCREEN_H // 4 + 3))
            screen.blit(title_shadow, shadow_rect)
            screen.blit(title, title_rect)
            
            # Subtitle
            subtitle = self.subtitle_font.render("Defend the Forest from Invaders!", True, FOREST_GREEN)
            subtitle_rect = subtitle.get_rect(center=(SCREEN_W // 2, SCREEN_H // 4 + 80))
            screen.blit(subtitle, subtitle_rect)
            
            # Draw buttons
            self.start_button.draw(screen)
            self.create_button.draw(screen)
            self.quit_button.draw(screen)
            
            pygame.display.flip()
            clock.tick(FPS)

class LevelSelector:
    def __init__(self):
        self.buttons = []
        self.back_button = Button(30, 30, 120, 50, "← Back", color=BROWN, hover_color=RED)
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.load_levels()
        
    def load_levels(self):
        # Get the levels directory path
        levels_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "levels")
        
        if not os.path.exists(levels_dir):
            print(f"Levels directory not found: {levels_dir}")
            return
            
        # Load all JSON level files
        level_files = [f for f in os.listdir(levels_dir) if f.endswith(".json")]
        level_files.sort()  # Sort for consistent ordering
        
        # Create buttons in a grid layout
        cols = 3
        button_width, button_height = 200, 80
        start_x = SCREEN_W // 2 - (cols * button_width + (cols - 1) * 20) // 2
        start_y = 150
        
        for i, level_file in enumerate(level_files):
            col = i % cols
            row = i // cols
            x = start_x + col * (button_width + 20)
            y = start_y + row * (button_height + 20)
            
            # Load level data to get the name
            level_path = os.path.join(levels_dir, level_file)
            try:
                with open(level_path, 'r', encoding='utf-8') as f:
                    level_data = json.load(f)
                    level_name = level_data.get('name', level_file.replace('.json', ''))
            except (UnicodeDecodeError, json.JSONDecodeError):
                try:
                    with open(level_path, 'r', encoding='utf-8-sig') as f:
                        level_data = json.load(f)
                        level_name = level_data.get('name', level_file.replace('.json', ''))
                except:
                    level_name = level_file.replace('.json', '')
            except:
                level_name = level_file.replace('.json', '')
            
            button = Button(x, y, button_width, button_height, level_name)
            button.level_file = level_file  # Store the filename
            self.buttons.append(button)
    
    def draw_background(self, screen):
        # Same gradient background as main menu
        for y in range(SCREEN_H):
            color_ratio = y / SCREEN_H
            r = int(135 + (173 - 135) * color_ratio)
            g = int(206 + (216 - 206) * color_ratio)
            b = int(235 + (230 - 235) * color_ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_W, y))
    
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if self.back_button.handle_event(event):
                    return None
                
                for button in self.buttons:
                    if button.handle_event(event):
                        levels_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "levels")
                        return os.path.join(levels_dir, button.level_file)
            
            self.draw_background(screen)
            
            # Draw title
            title = self.title_font.render("Select Level", True, DARK_GREEN)
            title_rect = title.get_rect(center=(SCREEN_W // 2, 80))
            # Title shadow
            title_shadow = self.title_font.render("Select Level", True, BLACK)
            shadow_rect = title_shadow.get_rect(center=(SCREEN_W // 2 + 2, 82))
            screen.blit(title_shadow, shadow_rect)
            screen.blit(title, title_rect)
            
            # Draw back button
            self.back_button.draw(screen)
            
            # Draw level buttons
            for button in self.buttons:
                button.draw(screen)
            
            # If no levels found, show message
            if not self.buttons:
                no_levels_text = pygame.font.SysFont('Arial', 32).render("No levels found!", True, RED)
                text_rect = no_levels_text.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2))
                screen.blit(no_levels_text, text_rect)
            
            pygame.display.flip()
            clock.tick(FPS)

def show_level_creator_message():
    """显示关卡创建器的占位符消息"""
    font = pygame.font.SysFont('Arial', 48, bold=True)
    message_font = pygame.font.SysFont('Arial', 24)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # Return to main menu
        
        # Gradient background
        for y in range(SCREEN_H):
            color_ratio = y / SCREEN_H
            r = int(135 + (173 - 135) * color_ratio)
            g = int(206 + (216 - 206) * color_ratio)
            b = int(235 + (230 - 235) * color_ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_W, y))
        
        # Title
        title = font.render("Level Creator", True, DARK_GREEN)
        title_rect = title.get_rect(center=(SCREEN_W // 2, SCREEN_H // 3))
        screen.blit(title, title_rect)
        
        # Message
        message = message_font.render("Coming Soon!", True, FOREST_GREEN)
        message_rect = message.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2))
        screen.blit(message, message_rect)
        
        # Instructions
        instruction = message_font.render("Press any key or click to return to main menu", True, BROWN)
        instruction_rect = instruction.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 50))
        screen.blit(instruction, instruction_rect)
        
        pygame.display.flip()
        clock.tick(FPS) 