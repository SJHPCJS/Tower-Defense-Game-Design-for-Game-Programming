import sys, pygame
from settings import *
from grid import GRID_MAP
from map_component import MapComponent
from level import Level
from tower import TowerFactory
from bullet import Bullet

def main():
    game_map = MapComponent()
    level    = Level()
    towers   = pygame.sprite.Group()
    bullets  = pygame.sprite.Group()
    sel      = None

    # toolbar cards
    card_w, card_h, margin = 60, UI_HEIGHT-20, 10
    cards=[]
    for i,p in enumerate(TOWER_TYPES):
        x = margin + i*(card_w+margin)
        y = (UI_HEIGHT-card_h)//2
        cards.append((pygame.Rect(x,y,card_w,card_h),p))

    running=True
    while running:
        dt = clock.tick(FPS)/1000.0
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: running=False
            elif ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                mx,my=ev.pos
                if my<UI_HEIGHT:
                    for r,p in cards:
                        if r.collidepoint(mx,my):
                            sel=p;break
                else:
                    gx=mx//GRID_SIZE
                    gy=(my-UI_HEIGHT)//GRID_SIZE
                    if 0<=gx<GRID_W and 0<=gy<GRID_H and GRID_MAP[gy][gx]==1 and sel:
                        towers.add(TowerFactory.create_tower(sel, gx, gy)); sel=None

        level.update(dt)
        bullets.update(dt)
        towers.update(dt, level.enemies, bullets)

        screen.fill(BG_COLOUR)
        pygame.draw.rect(screen, BLACK, (0,0,SCREEN_W,UI_HEIGHT))
        for r,p in cards:
            pygame.draw.rect(screen,p['color'],r)
            border=WHITE if sel is p else BLACK
            pygame.draw.rect(screen,border,r,2)
            t=FONT.render(p['name'],True,BLACK)
            screen.blit(t,t.get_rect(center=r.center))
        hp=FONT.render(f"Base: {level.base_hp}",True,WHITE)
        screen.blit(hp,(SCREEN_W-120,UI_HEIGHT//2-hp.get_height()//2))

        game_map.draw(screen)
        for tower in towers:
            tower.draw(screen)
        bullets.draw(screen)
        # Draw enemies last to appear on top of everything (including toolbar)
        level.draw(screen)
        pygame.display.flip()

    pygame.quit(); sys.exit()

if __name__=="__main__":
    main()
