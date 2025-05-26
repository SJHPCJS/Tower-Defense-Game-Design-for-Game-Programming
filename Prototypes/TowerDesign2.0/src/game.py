import sys
import pygame
import json
from settings import *
from menu import MainMenu, LevelSelector, show_level_creator_message
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
                
        # 更新全局网格地图
        if 'grid' in level_data:
            update_grid_map(level_data['grid'])
                        
        return level_data
    
    def run_game_loop(self, level_data):
        game_map = MapComponent()
        level = Level()
        towers = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        sel = None

        card_w, card_h, margin = 60, UI_HEIGHT-20, 10
        cards = []
        for i, p in enumerate(TOWER_TYPES):
            x = margin + i*(card_w+margin)
            y = (UI_HEIGHT-card_h)//2
            cards.append((pygame.Rect(x,y,card_w,card_h), p))

        back_button_rect = pygame.Rect(SCREEN_W - 100, 10, 80, 30)
        
        running = True
        while running:
            dt = clock.tick(FPS)/1000.0
            
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return "quit"
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        return "menu"
                elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    mx, my = ev.pos

                    if back_button_rect.collidepoint(mx, my):
                        return "menu"

                    if my < UI_HEIGHT:
                        for r, p in cards:
                            if r.collidepoint(mx, my):
                                sel = p
                                break
                    else:
                        gx = mx // GRID_SIZE
                        gy = (my - UI_HEIGHT) // GRID_SIZE
                        if 0 <= gx < GRID_W and 0 <= gy < GRID_H and GRID_MAP[gy][gx] == 1 and sel:
                            towers.add(Tower(gx, gy, sel))
                            sel = None

            level.update(dt)
            bullets.update(dt)
            towers.update(dt, level.enemies, bullets)
            

            screen.fill(BG_COLOUR)

            pygame.draw.rect(screen, BLACK, (0, 0, SCREEN_W, UI_HEIGHT))

            for r, p in cards:
                pygame.draw.rect(screen, p['color'], r)
                border = WHITE if sel is p else BLACK
                pygame.draw.rect(screen, border, r, 2)
                t = FONT.render(p['name'], True, BLACK)
                screen.blit(t, t.get_rect(center=r.center))

            hp = FONT.render(f"Base: {level.base_hp}", True, WHITE)
            screen.blit(hp, (SCREEN_W-200, UI_HEIGHT//2-hp.get_height()//2))

            pygame.draw.rect(screen, FOREST_GREEN, back_button_rect)
            pygame.draw.rect(screen, WHITE, back_button_rect, 2)
            back_text = FONT.render("Menu", True, WHITE)
            screen.blit(back_text, back_text.get_rect(center=back_button_rect.center))

            game_map.draw(screen)
            level.draw(screen)
            towers.draw(screen)
            bullets.draw(screen)

            if level.base_hp <= 0:
                font = pygame.font.SysFont('Arial', 48, bold=True)
                game_over_text = font.render("Game Over!", True, RED)
                text_rect = game_over_text.get_rect(center=(SCREEN_W//2, SCREEN_H//2))
                screen.blit(game_over_text, text_rect)
                
                restart_text = FONT.render("Press ESC to return to menu", True, WHITE)
                restart_rect = restart_text.get_rect(center=(SCREEN_W//2, SCREEN_H//2 + 50))
                screen.blit(restart_text, restart_rect)
            
            pygame.display.flip()
        
        return "menu"
    
    def run(self):
        while True:
            if self.state == "menu":
                main_menu = MainMenu()
                result = main_menu.run()
                
                if result == "start":
                    self.state = "level_select"
                elif result == "creator":
                    show_level_creator_message()
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