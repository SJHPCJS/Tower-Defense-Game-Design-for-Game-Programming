import pygame
import random
from pathlib import Path
from settings import *
from grid import GRID_MAP

class StartSprite:
    """START sprite sheet 动画类，支持4种状态随机切换"""
    
    def __init__(self):
        self.load_sprite_sheet()
        self.current_state = 0  # 当前状态索引 (0-3)
        self.state_timer = 0.0
        self.state_interval = 30.0  # 30秒切换一次状态
        
        # 4个状态帧索引（2x2 sprite sheet）
        self.states = [0, 1, 2, 3]  # 左上、右上、左下、右下
        
        # 随机选择初始状态
        self.current_state = random.randint(0, 3)
        
        print(f"START sprite initialized with state {self.current_state}")
    
    def load_sprite_sheet(self):
        """加载 START sprite sheet 并切割成帧"""
        try:
            assets_path = Path(__file__).parent.parent / 'assets' / 'sprite'
            sheet = pygame.image.load(assets_path / 'START.png').convert_alpha()
            
            # 假设 sprite sheet 是 2x2 格式，每帧大小相等
            sheet_w, sheet_h = sheet.get_size()
            frame_w = sheet_w // 2
            frame_h = sheet_h // 2
            
            # 切割帧：[左上, 右上, 左下, 右下]
            self.sprite_frames = []
            positions = [(0, 0), (frame_w, 0), (0, frame_h), (frame_w, frame_h)]
            
            for x, y in positions:
                rect = pygame.Rect(x, y, frame_w, frame_h)
                frame = sheet.subsurface(rect).copy()
                self.sprite_frames.append(frame)
                
            print(f"START sprite loaded: {len(self.sprite_frames)} frames, {frame_w}x{frame_h} each")
            
        except Exception as e:
            print(f"Failed to load START sprite: {e}")
            # 创建默认方块作为备用
            self.sprite_frames = []
            for color in [(0, 255, 0), (0, 200, 255), (255, 0, 255), (255, 255, 0)]:
                surf = pygame.Surface((GRID_SIZE, GRID_SIZE))
                surf.fill(color)
                self.sprite_frames.append(surf)
    
    def update(self, dt):
        """更新状态切换"""
        self.state_timer += dt
        
        if self.state_timer >= self.state_interval:
            # 随机选择新状态（确保与当前状态不同）
            available_states = [s for s in self.states if s != self.current_state]
            self.current_state = random.choice(available_states)
            self.state_timer = 0.0
            print(f"START状态切换到: {self.current_state}")
    
    def get_current_sprite(self, size):
        """获取当前帧的sprite，按指定大小缩放"""
        sprite = self.sprite_frames[self.current_state]
        
        if size != sprite.get_size():
            return pygame.transform.scale(sprite, size)
        return sprite

class HomeSprite:
    """HOME sprite sheet 动画类，支持多种状态"""
    
    def __init__(self):
        self.load_sprite_sheet()
        self.current_frame = 0
        self.frame_timer = 0.0
        self.frame_interval = 0.3  # 动画帧间隔（秒）- 稍微快一点
        
        # 状态系统
        self.state = "idle"  # idle(正常), active(有敌人), hit(受到攻击)
        self.hit_timer = 0.0
        self.hit_duration = 1.2  # 受击状态持续时间（稍微长一点）
        
        # 帧索引定义（2x2 sprite sheet）
        self.frames = {
            "idle": [1],        # 右上角：正常状态
            "active": [0, 2],   # 左上、左下：有敌人时交替
            "hit": [3],         # 右下角：受到攻击
            "checking": [1]     # 检查状态：暂时显示正常状态
        }
    
    def load_sprite_sheet(self):
        """加载 HOME sprite sheet 并切割成帧"""
        try:
            assets_path = Path(__file__).parent.parent / 'assets' / 'sprite'
            sheet = pygame.image.load(assets_path / 'HOME.png').convert_alpha()
            
            # 假设 sprite sheet 是 2x2 格式，每帧大小相等
            sheet_w, sheet_h = sheet.get_size()
            frame_w = sheet_w // 2
            frame_h = sheet_h // 2
            
            # 切割帧：[左上, 右上, 左下, 右下]
            self.sprite_frames = []
            positions = [(0, 0), (frame_w, 0), (0, frame_h), (frame_w, frame_h)]
            
            for x, y in positions:
                rect = pygame.Rect(x, y, frame_w, frame_h)
                frame = sheet.subsurface(rect).copy()
                self.sprite_frames.append(frame)
                
            print(f"HOME sprite loaded: {len(self.sprite_frames)} frames, {frame_w}x{frame_h} each")
            
        except Exception as e:
            print(f"Failed to load HOME sprite: {e}")
            # 创建默认方块作为备用
            self.sprite_frames = []
            for color in [(0, 255, 0), (255, 255, 0), (255, 165, 0), (255, 0, 0)]:
                surf = pygame.Surface((GRID_SIZE, GRID_SIZE))
                surf.fill(color)
                self.sprite_frames.append(surf)
    
    def set_state(self, new_state):
        """设置HOME状态"""
        if new_state != self.state:
            self.state = new_state
            self.current_frame = 0
            self.frame_timer = 0.0
            
            if new_state == "hit":
                self.hit_timer = 0.0
    
    def on_enemy_near(self):
        """当有敌人接近时调用"""
        if self.state != "hit":
            self.set_state("active")
    
    def on_no_enemies(self):
        """当没有敌人时调用"""
        if self.state != "hit":
            self.set_state("idle")
    
    def on_hit(self):
        """当受到攻击时调用"""
        self.set_state("hit")
    
    def update(self, dt):
        """更新动画状态"""
        # 更新受击状态计时器
        if self.state == "hit":
            self.hit_timer += dt
            if self.hit_timer >= self.hit_duration:
                # 受击状态结束，需要重新检查周围敌人状态
                # 不能直接设为idle，应该让MapComponent重新检查
                self.hit_timer = 0.0
                self.state = "checking"  # 临时状态，等待MapComponent检查
                return
        
        # 更新动画帧
        current_frames = self.frames[self.state]
        if len(current_frames) > 1:  # 多帧动画才需要切换
            self.frame_timer += dt
            if self.frame_timer >= self.frame_interval:
                self.frame_timer = 0.0
                self.current_frame = (self.current_frame + 1) % len(current_frames)
    
    def get_current_sprite(self, size):
        """获取当前帧的sprite，按指定大小缩放"""
        current_frames = self.frames[self.state]
        frame_index = current_frames[self.current_frame]
        sprite = self.sprite_frames[frame_index]
        
        if size != sprite.get_size():
            return pygame.transform.scale(sprite, size)
        return sprite

class MapComponent:
    def __init__(self, grid=None, spawn=(0,0), home=(GRID_W-2, GRID_H-2)):
        self.grid  = grid if grid is not None else GRID_MAP
        self.spawn = spawn
        self.home  = home
        self._load_imgs()
        
        # 创建START和HOME动画精灵
        self.start_sprite = StartSprite()
        self.home_sprite = HomeSprite()
        
        # 敌人检测相关
        self.enemies_near_home = False
        
    def _load_imgs(self):
        assets = Path(__file__).parent.parent / 'assets' / 'tiles'
        self.base_imgs = {
            0: pygame.image.load(assets/'path.png'),
            1: pygame.image.load(assets/'grass.png'),
        }

    def set_spawn_and_home(self, spawn, home):
        """Set the spawn and home positions"""
        self.spawn = spawn
        self.home = home

    def update_enemy_status(self, enemies):
        """更新敌人状态，影响HOME动画"""
        # 检查是否有敌人接近HOME（距离阈值可调整）
        enemies_near = False
        home_x, home_y = self.home
        
        for enemy in enemies:
            if hasattr(enemy, 'gx') and hasattr(enemy, 'gy'):
                # 计算敌人与HOME的距离
                distance = abs(enemy.gx - home_x) + abs(enemy.gy - home_y)
                if distance <= 5:  # 5格以内算接近（增加检测范围）
                    enemies_near = True
                    break
            elif hasattr(enemy, 'path') and hasattr(enemy, 'step'):
                # 对于使用路径系统的敌人，检查路径位置
                if enemy.step < len(enemy.path):
                    gx, gy = enemy.path[enemy.step]
                    distance = abs(gx - home_x) + abs(gy - home_y)
                    if distance <= 5:  # 5格以内算接近
                        enemies_near = True
                        break
        
        # 处理HOME状态切换
        current_state = self.home_sprite.state
        
        # 如果HOME处于checking状态，重新确定正确状态
        if current_state == "checking":
            if enemies_near:
                self.home_sprite.set_state("active")
                self.enemies_near_home = True
                print(f"HOME状态: 受击后检查，发现敌人，切换到活跃状态")
            else:
                self.home_sprite.set_state("idle")
                self.enemies_near_home = False
                print(f"HOME状态: 受击后检查，无敌人，切换到空闲状态")
        # 正常状态检查逻辑
        elif current_state != "hit":  # 受击状态不会被打断
            if enemies_near and not self.enemies_near_home:
                self.home_sprite.on_enemy_near()
                self.enemies_near_home = True
                print(f"HOME状态: 敌人接近，切换到活跃状态")
            elif not enemies_near and self.enemies_near_home:
                self.home_sprite.on_no_enemies()
                self.enemies_near_home = False
                print(f"HOME状态: 敌人远离，切换到空闲状态")
    
    def on_home_hit(self):
        """当HOME受到攻击时调用"""
        self.home_sprite.on_hit()
    
    def update(self, dt, enemies=None):
        """更新地图组件"""
        if enemies:
            self.update_enemy_status(enemies)
        
        # 更新START和HOME动画
        self.start_sprite.update(dt)
        self.home_sprite.update(dt)

    def _draw(self, screen_w, screen_h):
        # Calculate scaling
        scaled_grid_size = get_scaled_grid_size(screen_w, screen_h)
        
        # Create scaled images
        scaled_imgs = {}
        for key, img in self.base_imgs.items():
            scaled_imgs[key] = pygame.transform.scale(img, (scaled_grid_size, scaled_grid_size))
        
        # Calculate the position and size of the game area
        game_area_height = screen_h - UI_HEIGHT
        scale_x = screen_w / (GRID_W * GRID_SIZE)
        scale_y = game_area_height / (GRID_H * GRID_SIZE)
        scale = min(scale_x, scale_y)
        
        scaled_width = GRID_W * GRID_SIZE * scale
        scaled_height = GRID_H * GRID_SIZE * scale
        offset_x = (screen_w - scaled_width) // 2
        offset_y = UI_HEIGHT + (game_area_height - scaled_height) // 2
        
        # Create game area surface
        game_surface = pygame.Surface((int(scaled_width), int(scaled_height)))
        
        # Draw tiles
        for y, row in enumerate(self.grid):
            for x, t in enumerate(row):
                pos_x = x * scaled_grid_size
                pos_y = y * scaled_grid_size
                game_surface.blit(scaled_imgs[t], (pos_x, pos_y))
        
        # Draw markers
        sx, sy = self.spawn
        hx, hy = self.home
        
        # START marker - 使用sprite动画
        start_sprite = self.start_sprite.get_current_sprite((scaled_grid_size, scaled_grid_size))
        start_pos = (sx * scaled_grid_size, sy * scaled_grid_size)
        game_surface.blit(start_sprite, start_pos)
        
        # HOME marker - 使用sprite动画
        home_sprite = self.home_sprite.get_current_sprite((scaled_grid_size, scaled_grid_size))
        home_pos = (hx * scaled_grid_size, hy * scaled_grid_size)
        game_surface.blit(home_sprite, home_pos)
        
        # 添加HOME边框
        home_rect = pygame.Rect(hx * scaled_grid_size, hy * scaled_grid_size, scaled_grid_size, scaled_grid_size)
        home_state = self.home_sprite.state
        if home_state == "idle" or home_state == "checking":
            border_color = (0, 255,  0) 
        elif home_state == "active":
            border_color = (255, 255, 0)    # 黄色：有敌人
        else:  # hit状态
            border_color = (255, 0, 0)      # 红色：受击
        pygame.draw.rect(game_surface, border_color, home_rect, 3)
        
        return game_surface, (int(offset_x), int(offset_y))

    def set_grid(self, new_grid):
        self.grid = new_grid

    def draw(self, target):
        screen_w, screen_h = target.get_size()
        game_surface, offset = self._draw(screen_w, screen_h)
        target.blit(game_surface, offset)
