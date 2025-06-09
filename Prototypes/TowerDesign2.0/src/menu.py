import pygame
import sys
import os
import json
import math
import random
from settings import *
from audio_manager import audio_manager

class Button:
    def __init__(self, x, y, width, height, text, color=FOREST_GREEN, hover_color=LIGHT_GREEN, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.font = pygame.font.SysFont('Arial', 24, bold=True)
        
        # Add animation effects
        self.hover_scale = 1.0
        self.shadow_offset = 2

    def draw(self, screen):
        # Update hover animation
        target_scale = 1.05 if self.is_hovered else 1.0
        self.hover_scale += (target_scale - self.hover_scale) * 0.1
        
        # Calculate scaled rectangle
        original_center = self.rect.center
        scaled_width = int(self.rect.width * self.hover_scale)
        scaled_height = int(self.rect.height * self.hover_scale)
        scaled_rect = pygame.Rect(0, 0, scaled_width, scaled_height)
        scaled_rect.center = original_center
        
        color = self.hover_color if self.is_hovered else self.color
        shadow_offset = self.shadow_offset + (2 if self.is_hovered else 0)
        
        # Draw shadow (enhanced effect)
        shadow_rect = pygame.Rect(scaled_rect.x + shadow_offset, scaled_rect.y + shadow_offset, 
                                scaled_rect.width, scaled_rect.height)
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=8)
        
        # Draw button body
        pygame.draw.rect(screen, color, scaled_rect, border_radius=8)
        pygame.draw.rect(screen, DARK_GREEN, scaled_rect, 3, border_radius=8)
        
        # Add inner border highlight effect
        if self.is_hovered:
            highlight_rect = pygame.Rect(scaled_rect.x + 2, scaled_rect.y + 2, 
                                       scaled_rect.width - 4, scaled_rect.height - 4)
            pygame.draw.rect(screen, (255, 255, 255, 50), highlight_rect, 2, border_radius=6)
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=scaled_rect.center)
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
        
        # Add natural element animation
        self.title_wave = 0.0
        self.init_natural_effects()
        
        # Play menu music
        audio_manager.play_menu_music()
        
        # Buttons with enhanced styling
        button_width, button_height = 250, 60
        button_x = DEFAULT_SCREEN_W // 2 - button_width // 2
        
        self.start_button = Button(button_x, DEFAULT_SCREEN_H // 2 - 70, button_width, button_height, "Start Game")
        self.library_button = Button(button_x, DEFAULT_SCREEN_H // 2 - 10, button_width, button_height, "Character Library", color=UI_ACCENT, hover_color=(100, 150, 200))
        self.create_button = Button(button_x, DEFAULT_SCREEN_H // 2 + 50, button_width, button_height, "Create a Level")
        self.quit_button = Button(button_x, DEFAULT_SCREEN_H // 2 + 110, button_width, button_height, "Quit", color=BROWN, hover_color=RED)
        
    def init_natural_effects(self):
        """Initialize natural effect elements"""
        # Pixel style clouds
        self.clouds = []
        for i in range(4):  # Reduce cloud count for better performance
            self.clouds.append({
                'x': random.randint(-200, DEFAULT_SCREEN_W),
                'y': random.randint(30, 250),
                'speed': random.uniform(0.3, 1.0),
                'size': random.randint(60, 120),
                'offset': random.uniform(0, 2 * math.pi),
                'type': random.choice(['normal', 'large'])  # Different cloud types
            })
        
        # Falling leaves
        self.leaves = []
        for i in range(12):  # Slightly reduce leaf count
            self.leaves.append({
                'x': random.randint(0, DEFAULT_SCREEN_W),
                'y': random.randint(-100, DEFAULT_SCREEN_H),
                'speed_x': random.uniform(-0.3, 0.3),
                'speed_y': random.uniform(0.8, 2.5),
                'rotation': random.uniform(0, 360),
                'rotation_speed': random.uniform(-1.5, 1.5),
                'color': random.choice([
                    (34, 139, 34), (107, 142, 35), (85, 107, 47), 
                    (154, 205, 50), (50, 205, 50), (46, 125, 50)
                ]),
                'size': random.randint(6, 14),
                'wobble': random.uniform(0, 2 * math.pi)  # Wobble phase
            })
        
        # Firefly effect
        self.fireflies = []
        for i in range(6):  # Reduce firefly count
            self.fireflies.append({
                'x': random.randint(100, DEFAULT_SCREEN_W - 100),
                'y': random.randint(300, DEFAULT_SCREEN_H - 100),
                'target_x': random.randint(100, DEFAULT_SCREEN_W - 100),
                'target_y': random.randint(300, DEFAULT_SCREEN_H - 100),
                'glow': random.uniform(0, 2 * math.pi),
                'glow_speed': random.uniform(0.03, 0.08),
                'move_timer': random.randint(60, 180)  # Movement timer
            })

    def draw_pixel_clouds(self, screen, screen_w, screen_h):
        """Draw pixel style clouds"""
        for cloud in self.clouds:
            # Update cloud position
            cloud['x'] += cloud['speed']
            if cloud['x'] > screen_w + cloud['size']:
                cloud['x'] = -cloud['size']
                cloud['y'] = random.randint(30, 250)  # Randomly reset height
            
            # Add slight vertical floating
            float_y = cloud['y'] + math.sin(pygame.time.get_ticks() * 0.0008 + cloud['offset']) * 6
            
            # Draw pixelated clouds
            base_x, base_y = int(cloud['x']), int(float_y)
            size = cloud['size']
            block_size = max(6, size // 10)  # Adjust pixel block size
            
            # Choose different shapes based on cloud type
            if cloud['type'] == 'large':
                cloud_pattern = [
                    "      ████████████      ",
                    "    ████████████████    ",
                    "  ████████████████████  ",
                    "████████████████████████",
                    "████████████████████████",
                    " ██████████████████████ ",
                    "  ████████████████████  "
                ]
            else:
                cloud_pattern = [
                    "    ████████    ",
                    "  ████████████  ",
                    "████████████████",
                    "████████████████",
                    " ██████████████ ",
                    "  ████████████  "
                ]
            
            # Draw cloud pixel blocks
            for row, pattern in enumerate(cloud_pattern):
                for col, pixel in enumerate(pattern):
                    if pixel == '█':
                        pixel_x = base_x + (col - len(pattern[0])//2) * block_size
                        pixel_y = base_y + row * block_size
                        
                        # Ensure within screen bounds
                        if 0 <= pixel_x < screen_w and 0 <= pixel_y < screen_h:
                            # Cloud color gradient
                            distance_from_center = abs(col - len(pattern[0])//2)
                            alpha = max(180, 240 - distance_from_center * 8)
                            cloud_color = (255, 255, 255)
                            
                            # Draw pixel block
                            pygame.draw.rect(screen, cloud_color, 
                                           (pixel_x, pixel_y, block_size, block_size))

    def draw_falling_leaves(self, screen, screen_w, screen_h):
        """Draw falling leaves"""
        for leaf in self.leaves:
            # Update leaf position
            leaf['wobble'] += 0.05
            leaf['x'] += leaf['speed_x'] + math.sin(leaf['wobble']) * 0.8  # Enhanced wobble effect
            leaf['y'] += leaf['speed_y']
            leaf['rotation'] += leaf['rotation_speed']
            
            # Reset leaves that go off screen
            if leaf['y'] > screen_h + 30:
                leaf['y'] = -30
                leaf['x'] = random.randint(-30, screen_w + 30)
                leaf['wobble'] = random.uniform(0, 2 * math.pi)
            
            if leaf['x'] < -100:
                leaf['x'] = screen_w + 100
            elif leaf['x'] > screen_w + 100:
                leaf['x'] = -100
            
            # Only draw if within visible range
            if -50 <= leaf['x'] <= screen_w + 50 and -50 <= leaf['y'] <= screen_h + 50:
                # Create leaf surface
                leaf_size = leaf['size']
                leaf_surface = pygame.Surface((leaf_size * 2, leaf_size * 2), pygame.SRCALPHA)
                
                # Draw more realistic leaf shape
                points = []
                for i in range(8):
                    angle = i * math.pi / 4
                    if i % 2 == 0:
                        radius = leaf_size * 0.8
                    else:
                        radius = leaf_size * 0.4
                    x = leaf_size + radius * math.cos(angle)
                    y = leaf_size + radius * math.sin(angle) * 1.2  # Elongate leaf
                    points.append((x, y))
                
                pygame.draw.polygon(leaf_surface, leaf['color'], points)
                
                # Rotate and draw leaf
                rotated_leaf = pygame.transform.rotate(leaf_surface, leaf['rotation'])
                leaf_rect = rotated_leaf.get_rect(center=(leaf['x'], leaf['y']))
                screen.blit(rotated_leaf, leaf_rect)

    def draw_fireflies(self, screen, screen_w, screen_h):
        """Draw firefly effect"""
        for firefly in self.fireflies:
            firefly['move_timer'] -= 1
            
            # Update firefly position (move towards target)
            dx = firefly['target_x'] - firefly['x']
            dy = firefly['target_y'] - firefly['y']
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < 10 or firefly['move_timer'] <= 0:
                # Choose new target
                firefly['target_x'] = random.randint(100, screen_w - 100)
                firefly['target_y'] = random.randint(300, screen_h - 100)
                firefly['move_timer'] = random.randint(120, 300)
            else:
                # Slowly move towards target
                speed = 0.008
                firefly['x'] += dx * speed
                firefly['y'] += dy * speed
            
            # Add random drift
            firefly['x'] += random.uniform(-0.5, 0.5)
            firefly['y'] += random.uniform(-0.5, 0.5)
            
            # Keep within screen bounds
            firefly['x'] = max(50, min(screen_w - 50, firefly['x']))
            firefly['y'] = max(250, min(screen_h - 50, firefly['y']))
            
            # Update glow effect
            firefly['glow'] += firefly['glow_speed']
            glow_intensity = (math.sin(firefly['glow']) + 1) * 0.5
            
            # Draw firefly (performance optimized)
            if glow_intensity > 0.3:  # Only draw when bright enough
                glow_size = int(6 + glow_intensity * 3)
                
                # Simplified glow effect
                for i in range(2, 0, -1):
                    alpha = int(40 * glow_intensity / i)
                    color = (255, 255, 100 + int(50 * glow_intensity))
                    pygame.draw.circle(screen, color, 
                                     (int(firefly['x']), int(firefly['y'])), 
                                     glow_size + i * 3)
                
                # Core light point
                pygame.draw.circle(screen, (255, 255, 200), 
                                 (int(firefly['x']), int(firefly['y'])), 2)

    def draw_background(self, screen):
        screen_w, screen_h = screen.get_size()
        
        # Enhanced gradient background (sky to horizon)
        for y in range(screen_h):
            color_ratio = y / screen_h
            # From sky blue gradient to warmer horizon color
            r = int(135 + (200 - 135) * color_ratio)
            g = int(206 + (220 - 206) * color_ratio)
            b = int(235 + (200 - 235) * color_ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (screen_w, y))
        
        # Draw natural effects
        self.draw_pixel_clouds(screen, screen_w, screen_h)
        self.draw_falling_leaves(screen, screen_w, screen_h)
        self.draw_fireflies(screen, screen_w, screen_h)
        
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    # Handle window resizing
                    new_width = max(event.w, MIN_SCREEN_W)
                    new_height = max(event.h, MIN_SCREEN_H)
                    pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE | pygame.DOUBLEBUF)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        # Toggle fullscreen
                        pygame.display.toggle_fullscreen()
                
                if self.start_button.handle_event(event):
                    return "start"
                if self.library_button.handle_event(event):
                    return "library"
                if self.create_button.handle_event(event):
                    return "creator"
                if self.quit_button.handle_event(event):
                    pygame.quit()
                    sys.exit()
                
            current_screen = pygame.display.get_surface()
            screen_w, screen_h = current_screen.get_size()
            
            # Dynamically adjust button positions
            button_width, button_height = 250, 60
            button_x = screen_w // 2 - button_width // 2
            center_y = screen_h // 2
            
            self.start_button.rect = pygame.Rect(button_x, center_y - 70, button_width, button_height)
            self.library_button.rect = pygame.Rect(button_x, center_y - 10, button_width, button_height)
            self.create_button.rect = pygame.Rect(button_x, center_y + 50, button_width, button_height)
            self.quit_button.rect = pygame.Rect(button_x, center_y + 110, button_width, button_height)
            
            self.draw_background(current_screen)
            
            # Update title animation
            self.title_wave += 0.03
            wave_offset = math.sin(self.title_wave) * 8
            
            # Draw enhanced title (without shadows)
            title_y = screen_h // 4 + int(wave_offset)
            
            # Main title only (no shadow effects)
            title = self.title_font.render("Forest Guard", True, DARK_GREEN)
            title_rect = title.get_rect(center=(screen_w // 2, title_y))
            current_screen.blit(title, title_rect)
            
            # Enhanced subtitle
            subtitle_y = title_y + 80
            subtitle = self.subtitle_font.render("Defend the Forest from Invaders!", True, FOREST_GREEN)
            subtitle_rect = subtitle.get_rect(center=(screen_w // 2, subtitle_y))
            
            # Subtitle shadow (minimal)
            subtitle_shadow = self.subtitle_font.render("Defend the Forest from Invaders!", True, (0, 50, 0))
            shadow_rect = subtitle_shadow.get_rect(center=(screen_w // 2 + 1, subtitle_y + 1))
            current_screen.blit(subtitle_shadow, shadow_rect)
            current_screen.blit(subtitle, subtitle_rect)
            
            # Draw enhanced buttons
            self.start_button.draw(current_screen)
            self.library_button.draw(current_screen)
            self.create_button.draw(current_screen)
            self.quit_button.draw(current_screen)
            
            # Add version info
            version_font = pygame.font.SysFont('Arial', 16)
            version_text = version_font.render("Forest Guard v2.0", True, (100, 100, 100))
            version_rect = version_text.get_rect(bottomright=(screen_w - 10, screen_h - 10))
            current_screen.blit(version_text, version_rect)
            
            pygame.display.flip()
            clock.tick(FPS)

class LevelSelector:
    def __init__(self):
        self.buttons = []
        self.back_button = Button(30, 30, 120, 50, "← Back", color=BROWN, hover_color=RED)
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        
        # Delete functionality
        self.delete_mode = False
        self.delete_button = None
        self.confirm_delete_dialog = False
        self.level_to_delete = None
        
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
        start_x = DEFAULT_SCREEN_W // 2 - (cols * button_width + (cols - 1) * 20) // 2
        start_y = 150
        
        self.buttons.clear()
        
        for i, level_file in enumerate(level_files):
            col = i % cols
            row = i // cols
            x = start_x + col * (button_width + 20)
            y = start_y + row * (button_height + 20)
            
            # Use filename as button text, do not preload level data
            level_name = level_file.replace('.json', '')
            button = Button(x, y, button_width, button_height, level_name)
            button.level_file = level_file  # Store the filename
            self.buttons.append(button)
        
        # Create delete button (bottom-right corner)
        screen = pygame.display.get_surface()
        if screen:
            screen_w, screen_h = screen.get_size()
            delete_x = screen_w - 140
            delete_y = screen_h - 80
            self.delete_button = Button(delete_x, delete_y, 120, 50, "Delete Level", color=UI_DANGER, hover_color=RED)
    
    def draw_background(self, screen):
        screen_w, screen_h = screen.get_size()
        # Same gradient background as main menu
        for y in range(screen_h):
            color_ratio = y / screen_h
            r = int(135 + (173 - 135) * color_ratio)
            g = int(206 + (216 - 206) * color_ratio)
            b = int(235 + (230 - 235) * color_ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (screen_w, y))

    def draw_confirm_delete_dialog(self, screen, screen_w, screen_h):
        """Draw the delete confirmation dialog"""
        if not self.level_to_delete:
            return
        
        dialog_w, dialog_h = 400, 200
        dialog_x = (screen_w - dialog_w) // 2
        dialog_y = (screen_h - dialog_h) // 2
        
        # Semi-transparent overlay
        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Dialog box
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)
        pygame.draw.rect(screen, UI_DARK_BG, dialog_rect, border_radius=15)
        pygame.draw.rect(screen, UI_DANGER, dialog_rect, 3, border_radius=15)
        
        # Title
        title_text = FONTS['title'].render("Confirm Delete", True, UI_DANGER)
        title_rect = title_text.get_rect(center=(screen_w // 2, dialog_y + 50))
        screen.blit(title_text, title_rect)
        
        # Warning message
        level_name = self.level_to_delete.replace('.json', '')
        warning_text = FONTS['hud'].render(f"Delete level '{level_name}'?", True, WHITE)
        warning_rect = warning_text.get_rect(center=(screen_w // 2, dialog_y + 90))
        screen.blit(warning_text, warning_rect)
        
        warning2_text = FONTS['small'].render("This action cannot be undone!", True, UI_WARNING)
        warning2_rect = warning2_text.get_rect(center=(screen_w // 2, dialog_y + 115))
        screen.blit(warning2_text, warning2_rect)
        
        # Buttons
        # Confirm button
        confirm_x = dialog_x + dialog_w // 2 - 90
        confirm_y = dialog_y + dialog_h - 60
        confirm_rect = pygame.Rect(confirm_x, confirm_y, 80, 40)
        
        mx, my = pygame.mouse.get_pos()
        confirm_hover = confirm_rect.collidepoint(mx, my)
        confirm_color = RED if confirm_hover else UI_DANGER
        
        pygame.draw.rect(screen, confirm_color, confirm_rect, border_radius=5)
        confirm_text = FONTS['button'].render("Delete", True, WHITE)
        confirm_text_rect = confirm_text.get_rect(center=confirm_rect.center)
        screen.blit(confirm_text, confirm_text_rect)
        
        # Cancel button
        cancel_x = dialog_x + dialog_w // 2 + 10
        cancel_y = dialog_y + dialog_h - 60
        cancel_rect = pygame.Rect(cancel_x, cancel_y, 80, 40)
        
        cancel_hover = cancel_rect.collidepoint(mx, my)
        cancel_color = UI_LIGHT_BG if cancel_hover else UI_MID_BG
        
        pygame.draw.rect(screen, cancel_color, cancel_rect, border_radius=5)
        cancel_text = FONTS['button'].render("Cancel", True, WHITE)
        cancel_text_rect = cancel_text.get_rect(center=cancel_rect.center)
        screen.blit(cancel_text, cancel_text_rect)
        
        return confirm_rect, cancel_rect

    def delete_level_file(self, level_file):
        """Delete a level file"""
        try:
            levels_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "levels")
            filepath = os.path.join(levels_dir, level_file)
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"Deleted level: {level_file}")
                return True
            else:
                print(f"Level file not found: {level_file}")
                return False
        except Exception as e:
            print(f"Error deleting level: {e}")
            return False
    
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    # Handle window resizing
                    new_width = max(event.w, MIN_SCREEN_W)
                    new_height = max(event.h, MIN_SCREEN_H)
                    pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE | pygame.DOUBLEBUF)
                    # Recreate delete button with new position
                    screen_w, screen_h = new_width, new_height
                    delete_x = screen_w - 140
                    delete_y = screen_h - 80
                    self.delete_button = Button(delete_x, delete_y, 120, 50, "Delete Level", color=UI_DANGER, hover_color=RED)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        # Toggle fullscreen
                        pygame.display.toggle_fullscreen()
                    elif event.key == pygame.K_ESCAPE:
                        if self.confirm_delete_dialog:
                            self.confirm_delete_dialog = False
                            self.level_to_delete = None
                        elif self.delete_mode:
                            self.delete_mode = False
                        else:
                            return None
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    current_screen = pygame.display.get_surface()
                    screen_w, screen_h = current_screen.get_size()
                    
                    if self.confirm_delete_dialog:
                        # Handle delete confirmation dialog
                        confirm_rect, cancel_rect = self.draw_confirm_delete_dialog(current_screen, screen_w, screen_h)
                        
                        if confirm_rect and confirm_rect.collidepoint(mx, my):
                            # Confirm delete
                            if self.delete_level_file(self.level_to_delete):
                                self.load_levels()  # Reload level list
                            self.confirm_delete_dialog = False
                            self.level_to_delete = None
                            self.delete_mode = False
                        elif cancel_rect and cancel_rect.collidepoint(mx, my):
                            # Cancel delete
                            self.confirm_delete_dialog = False
                            self.level_to_delete = None
                    else:
                        # Normal button handling
                        if self.back_button.handle_event(event):
                            return None
                        
                        if self.delete_button and self.delete_button.handle_event(event):
                            self.delete_mode = not self.delete_mode
                        
                        for button in self.buttons:
                            if button.handle_event(event):
                                if self.delete_mode:
                                    # Show delete confirmation
                                    self.level_to_delete = button.level_file
                                    self.confirm_delete_dialog = True
                                else:
                                    # Normal level selection
                                    levels_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "levels")
                                    return os.path.join(levels_dir, button.level_file)
                
                # Handle button hover states
                if not self.confirm_delete_dialog:
                    self.back_button.handle_event(event)
                    if self.delete_button:
                        self.delete_button.handle_event(event)
                    for button in self.buttons:
                        button.handle_event(event)
            
            current_screen = pygame.display.get_surface()
            screen_w, screen_h = current_screen.get_size()
            
            # Dynamically adjust button positions
            cols = 3
            button_width, button_height = 200, 80
            start_x = screen_w // 2 - (cols * button_width + (cols - 1) * 20) // 2
            start_y = 150
            
            for i, button in enumerate(self.buttons):
                col = i % cols
                row = i // cols
                x = start_x + col * (button_width + 20)
                y = start_y + row * (button_height + 20)
                button.rect = pygame.Rect(x, y, button_width, button_height)
            
            self.draw_background(current_screen)
            
            # Draw title
            title = self.title_font.render("Select Level", True, DARK_GREEN)
            title_rect = title.get_rect(center=(screen_w // 2, 80))
            # Title shadow
            title_shadow = self.title_font.render("Select Level", True, BLACK)
            shadow_rect = title_shadow.get_rect(center=(screen_w // 2 + 2, 82))
            current_screen.blit(title_shadow, shadow_rect)
            current_screen.blit(title, title_rect)
            
            # Draw level buttons
            for button in self.buttons:
                # Highlight buttons in delete mode
                if self.delete_mode:
                    button.color = UI_DANGER
                    button.hover_color = RED
                else:
                    button.color = FOREST_GREEN
                    button.hover_color = LIGHT_GREEN
                button.draw(current_screen)
            
            # Draw back button
            self.back_button.draw(current_screen)
            
            # Draw delete button
            if self.delete_button:
                # Change appearance based on delete mode
                if self.delete_mode:
                    self.delete_button.color = RED
                    self.delete_button.text = "Cancel Delete"
                else:
                    self.delete_button.color = UI_DANGER
                    self.delete_button.text = "Delete Level"
                self.delete_button.draw(current_screen)
            
            # Draw mode indicator
            if self.delete_mode:
                mode_text = FONTS['hud'].render("DELETE MODE: Click a level to delete it", True, RED)
                mode_rect = mode_text.get_rect(center=(screen_w // 2, screen_h - 120))
                current_screen.blit(mode_text, mode_rect)
            
            # Draw confirmation dialog if active
            if self.confirm_delete_dialog:
                self.draw_confirm_delete_dialog(current_screen, screen_w, screen_h)
            
            pygame.display.flip()
            clock.tick(FPS)

def show_level_creator_message():
    """Show level creator placeholder message"""
    font = pygame.font.SysFont('Arial', 48, bold=True)
    message_font = pygame.font.SysFont('Arial', 24)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resizing
                new_width = max(event.w, MIN_SCREEN_W)
                new_height = max(event.h, MIN_SCREEN_H)
                pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE | pygame.DOUBLEBUF)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    # Toggle fullscreen
                    pygame.display.toggle_fullscreen()
                else:
                    return  # Return to main menu
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return  # Return to main menu
        
        current_screen = pygame.display.get_surface()
        screen_w, screen_h = current_screen.get_size()
        
        # Gradient background
        for y in range(screen_h):
            color_ratio = y / screen_h
            r = int(135 + (173 - 135) * color_ratio)
            g = int(206 + (216 - 206) * color_ratio)
            b = int(235 + (230 - 235) * color_ratio)
            pygame.draw.line(current_screen, (r, g, b), (0, y), (screen_w, y))
        
        # Title
        title = font.render("Level Creator", True, DARK_GREEN)
        title_rect = title.get_rect(center=(screen_w // 2, screen_h // 3))
        current_screen.blit(title, title_rect)
        
        # Message
        message = message_font.render("Coming Soon!", True, FOREST_GREEN)
        message_rect = message.get_rect(center=(screen_w // 2, screen_h // 2))
        current_screen.blit(message, message_rect)
        
        # Instructions
        instruction = message_font.render("Press any key or click to return to main menu", True, BROWN)
        instruction_rect = instruction.get_rect(center=(screen_w // 2, screen_h // 2 + 50))
        current_screen.blit(instruction, instruction_rect)
        
        pygame.display.flip()
        clock.tick(FPS) 