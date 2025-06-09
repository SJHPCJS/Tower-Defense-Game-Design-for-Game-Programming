import pygame
import os
import math
from settings import *
from library_data import LIBRARY_DATA, TOWERS, ENEMIES
from audio_manager import audio_manager

class ImageCache:
    """Image cache system to avoid repeated loading"""
    _cache = {}
    
    @classmethod
    def load_image(cls, path, size=None):
        cache_key = f"{path}_{size}"
        if cache_key not in cls._cache:
            try:
                image = pygame.image.load(path)
                if size:
                    image = pygame.transform.scale(image, size)
                cls._cache[cache_key] = image
            except Exception as e:
                print(f"Failed to load image {path}: {e}")
                cls._cache[cache_key] = None
        return cls._cache[cache_key]

class LibraryCard:
    """Character library card class"""
    def __init__(self, character_name, rect, card_type="normal"):
        self.character_name = character_name
        self.rect = rect
        self.card_type = card_type
        self.is_hovered = False
        self.portrait_image = None
        self.load_portrait()
        
    def load_portrait(self):
        """Load character portrait image"""
        data = LIBRARY_DATA.get(self.character_name)
        if data and data.get('portrait_path'):
            # Don't compress image, maintain original proportions
            original_image = ImageCache.load_image(data['portrait_path'])
            if original_image:
                # Calculate maximum size while maintaining aspect ratio
                max_width = self.rect.width - 10
                max_height = self.rect.height - 35
                
                img_width = original_image.get_width()
                img_height = original_image.get_height()
                
                # Calculate scale ratio to maintain original proportions
                scale = min(max_width / img_width, max_height / img_height)
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                
                self.portrait_image = pygame.transform.scale(original_image, (new_width, new_height))
    
    def draw(self, screen, is_selected=False):
        """Draw card with jungle theme, different colors based on faction"""
        # Get character faction information
        data = LIBRARY_DATA.get(self.character_name, {})
        faction = data.get('faction', 'ally')  # Default to ally
        
        # Determine colors based on faction and state
        if self.card_type == "home":
            if is_selected:
                bg_color = GOLD
                border_color = (255, 180, 0)
                text_color = BLACK
            else:
                bg_color = CREAM
                border_color = BROWN
                text_color = DARK_GREEN
        else:
            if faction == "ally":  # Allied forest spirits - green theme
                if is_selected:
                    bg_color = FOREST_GREEN
                    border_color = LIGHT_GREEN
                    text_color = WHITE
                else:
                    bg_color = (240, 255, 240)  # Light green background
                    border_color = FOREST_GREEN
                    text_color = DARK_GREEN
            else:  # Enemy city invaders - red theme
                if is_selected:
                    bg_color = (180, 50, 50)  # Dark red selected
                    border_color = (220, 80, 80)  # Bright red border
                    text_color = WHITE
                else:
                    bg_color = (255, 240, 240)  # Light red background
                    border_color = (180, 80, 80)  # Red border
                    text_color = (120, 40, 40)  # Dark red text
        
        # Hover effects
        if self.is_hovered and not is_selected:
            if faction == "ally":
                bg_color = tuple(min(255, c + 20) for c in bg_color)
            else:
                # Enemy hover effect
                bg_color = (255, 220, 220)  # Brighter light red
        
        # Draw card
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, border_color, self.rect, 3, border_radius=8)
        
        # Draw portrait image maintaining original proportions
        if self.portrait_image:
            image_x = self.rect.x + (self.rect.width - self.portrait_image.get_width()) // 2
            image_y = self.rect.y + 8
            screen.blit(self.portrait_image, (image_x, image_y))
        
        # Display name
        font = pygame.font.SysFont('Arial', 14, bold=True)
        display_name = LIBRARY_DATA.get(self.character_name, {}).get('name', self.character_name)
        text = font.render(display_name, True, text_color)
        text_rect = text.get_rect(centerx=self.rect.centerx, y=self.rect.bottom - 25)
        screen.blit(text, text_rect)
    
    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False

class SpriteAnimator:
    """精灵动画播放器 - 2x2布局"""
    def __init__(self, sprite_path, animation_speed=0.5):
        self.frames = []
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = animation_speed
        
        if sprite_path:
            self.load_sprite_sheet(sprite_path)
    
    def load_sprite_sheet(self, sprite_path):
        """加载精灵表 - 2x2布局，像主游戏一样"""
        try:
            sprite_sheet = pygame.image.load(sprite_path)
            sheet_width = sprite_sheet.get_width()
            sheet_height = sprite_sheet.get_height()
            
            # 使用2x2布局，像主游戏tower.py一样
            frame_width = sheet_width // 2
            frame_height = sheet_height // 2
            
            self.frames = []
            # 按2x2顺序加载：左上、右上、左下、右下
            for row in range(2):
                for col in range(2):
                    frame_rect = pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
                    frame = sprite_sheet.subsurface(frame_rect).copy()
                    self.frames.append(frame)
                    
        except Exception as e:
            print(f"Error loading sprite sheet {sprite_path}: {e}")
            self.frames = []
    
    def update(self, dt):
        """更新动画"""
        if len(self.frames) > 1:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames)
    
    def draw(self, screen, rect):
        """绘制当前动画帧，不压缩图片"""
        if self.frames:
            current_frame = self.frames[self.current_frame]
            
            # 保持原始比例，不压缩
            frame_width = current_frame.get_width()
            frame_height = current_frame.get_height()
            
            # 计算保持比例的缩放
            scale = min(rect.width / frame_width, rect.height / frame_height) * 0.8
            new_width = int(frame_width * scale)
            new_height = int(frame_height * scale)
            
            scaled_frame = pygame.transform.scale(current_frame, (new_width, new_height))
            
            # 居中显示当前帧
            display_x = rect.x + (rect.width - new_width) // 2
            display_y = rect.y + (rect.height - new_height) // 2
            screen.blit(scaled_frame, (display_x, display_y))

class CharacterLibrary:
    """角色图鉴主类 - 丛林主题"""
    def __init__(self):
        self.selected_character = "HOME"
        self.cards = []
        self.animator = None
        
        # 字体
        self.title_font = pygame.font.SysFont('Arial', 32, bold=True)
        self.story_font = pygame.font.SysFont('Arial', 16)
        self.stats_font = pygame.font.SysFont('Arial', 18, bold=True)
        self.label_font = pygame.font.SysFont('Arial', 22, bold=True)
        
        # 播放菜单音乐
        audio_manager.play_menu_music()
        
        self.init_cards()
        self.load_character_animator()
    
    def init_cards(self):
        """初始化卡片 - 自适应界面尺寸"""
        self.cards = []
        
        # 获取当前屏幕尺寸
        screen_w, screen_h = pygame.display.get_surface().get_size()
        
        # 计算总卡片数量：1个HOME + 5个防御塔 + 5个敌人 = 11个卡片
        total_cards = 1 + len(TOWERS) + len(ENEMIES)
        
        # 自适应卡片尺寸和间距
        toolbar_margin = 100  # 工具栏左右边距
        available_width = screen_w - toolbar_margin * 2
        
        # 基础卡片尺寸
        base_card_width = 140
        base_card_height = 110
        min_card_width = 100
        min_card_height = 80
        
        # 计算每个卡片组之间的分组间距
        group_spacing = 50  # HOME和塔之间，塔和敌人之间的额外间距
        
        # 计算理想的卡片宽度和间距
        # 总需要宽度 = 卡片宽度 * 卡片数量 + 普通间距 * (卡片数量-1) + 分组间距 * 2
        ideal_card_spacing = 25
        
        # 尝试使用基础尺寸
        total_width_needed = (base_card_width * total_cards + 
                            ideal_card_spacing * (total_cards - 1) + 
                            group_spacing * 2)
        
        if total_width_needed <= available_width:
            # 屏幕足够宽，使用基础尺寸
            card_width = base_card_width
            card_height = base_card_height
            card_spacing = ideal_card_spacing
        else:
            # 屏幕较窄，需要调整尺寸
            # 首先尝试缩小间距
            min_spacing = 15
            total_width_with_min_spacing = (base_card_width * total_cards + 
                                          min_spacing * (total_cards - 1) + 
                                          group_spacing * 2)
            
            if total_width_with_min_spacing <= available_width:
                # 缩小间距后能装下
                card_width = base_card_width
                card_height = base_card_height
                card_spacing = min_spacing
            else:
                # 需要缩小卡片尺寸
                card_spacing = min_spacing
                remaining_width = available_width - (card_spacing * (total_cards - 1) + group_spacing * 2)
                card_width = max(min_card_width, remaining_width // total_cards)
                card_height = max(min_card_height, int(card_width * base_card_height / base_card_width))
        
        # 计算起始位置（居中）
        actual_total_width = (card_width * total_cards + 
                            card_spacing * (total_cards - 1) + 
                            group_spacing * 2)
        start_x = (screen_w - actual_total_width) // 2
        start_y = 30  # 工具栏位置
        
        current_x = start_x
        
        # HOME卡片
        home_rect = pygame.Rect(current_x, start_y, card_width, card_height)
        self.cards.append(LibraryCard("HOME", home_rect, "home"))
        current_x += card_width + card_spacing + group_spacing
        
        # 防御塔卡片
        for i, tower_name in enumerate(TOWERS):
            rect = pygame.Rect(current_x, start_y, card_width, card_height)
            self.cards.append(LibraryCard(tower_name, rect))
            current_x += card_width + card_spacing
        
        # 敌人卡片前添加分组间距
        current_x += group_spacing - card_spacing
        
        # 敌人卡片
        for i, enemy_name in enumerate(ENEMIES):
            rect = pygame.Rect(current_x, start_y, card_width, card_height)
            self.cards.append(LibraryCard(enemy_name, rect))
            current_x += card_width + card_spacing
    
    def load_character_animator(self):
        """加载角色动画"""
        data = LIBRARY_DATA.get(self.selected_character)
        if data and data.get('sprite_path'):
            self.animator = SpriteAnimator(data['sprite_path'], animation_speed=0.5)
        else:
            self.animator = None
    
    def handle_event(self, event):
        """处理事件"""
        screen_w, screen_h = pygame.display.get_surface().get_size()
        
        # 返回按钮在右下角
        back_button_rect = pygame.Rect(screen_w - 150, screen_h - 80, 120, 50)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if back_button_rect.collidepoint(event.pos):
                return "back"
        
        # 卡片点击
        for card in self.cards:
            if card.handle_event(event):
                if self.selected_character != card.character_name:
                    self.selected_character = card.character_name
                    self.load_character_animator()
                break
        
        return None
    
    def update(self, dt):
        """更新"""
        if self.animator:
            self.animator.update(dt)
    
    def draw(self, screen):
        """绘制整个图鉴界面 - 丛林主题"""
        screen_w, screen_h = screen.get_size()
        
        # 丛林主题渐变背景
        for y in range(screen_h):
            ratio = y / screen_h
            # 从浅绿色渐变到深绿色
            r = int(144 + (34 - 144) * ratio)
            g = int(238 + (139 - 238) * ratio)  
            b = int(144 + (34 - 144) * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (screen_w, y))
        
        # 顶部工具栏区域 - 木质背景
        toolbar_height = 170
        toolbar_rect = pygame.Rect(0, 0, screen_w, toolbar_height)
        pygame.draw.rect(screen, BROWN, toolbar_rect)
        pygame.draw.rect(screen, DARK_GREEN, toolbar_rect, 4)
        
        # 绘制卡片
        for card in self.cards:
            is_selected = (card.character_name == self.selected_character)
            card.draw(screen, is_selected)
        
        # 主内容区域
        content_y = toolbar_height + 20
        data = LIBRARY_DATA.get(self.selected_character)
        
        if data:
            # 左侧信息面板 - 丛林主题
            left_panel = pygame.Rect(40, content_y, screen_w // 2 - 60, screen_h - content_y - 60)
            pygame.draw.rect(screen, CREAM, left_panel, border_radius=15)
            pygame.draw.rect(screen, BROWN, left_panel, 4, border_radius=15)
            
            # 右侧图像面板 - 丛林主题
            right_panel = pygame.Rect(screen_w // 2 + 20, content_y, screen_w // 2 - 60, screen_h - content_y - 60)
            pygame.draw.rect(screen, CREAM, right_panel, border_radius=15)
            pygame.draw.rect(screen, BROWN, right_panel, 4, border_radius=15)
            
            # 绘制内容
            self.draw_character_content(screen, left_panel, right_panel, data)
        
        # 返回按钮在右下角 - 丛林主题
        back_button_rect = pygame.Rect(screen_w - 150, screen_h - 80, 120, 50)
        pygame.draw.rect(screen, FOREST_GREEN, back_button_rect, border_radius=10)
        pygame.draw.rect(screen, DARK_GREEN, back_button_rect, 3, border_radius=10)
        
        button_font = pygame.font.SysFont('Arial', 20, bold=True)
        text = button_font.render("← BACK", True, WHITE)
        text_rect = text.get_rect(center=back_button_rect.center)
        screen.blit(text, text_rect)
    
    def draw_character_content(self, screen, left_panel, right_panel, data):
        """绘制角色详细信息 - 丛林主题"""
        # 左侧：角色名称 + 描述 + 属性
        y_offset = left_panel.y + 25
        
        # 角色名称 - 丛林主题
        title = self.title_font.render(data['name'], True, FOREST_GREEN)
        title_rect = title.get_rect(centerx=left_panel.centerx, y=y_offset)
        screen.blit(title, title_rect)
        y_offset += 60
        
        # 描述区域 - 丛林主题
        story_rect = pygame.Rect(left_panel.x + 20, y_offset, left_panel.width - 40, left_panel.height // 2 - 50)
        pygame.draw.rect(screen, (250, 248, 240), story_rect, border_radius=8)
        pygame.draw.rect(screen, BROWN, story_rect, 2, border_radius=8)
        
        # 描述标题
        story_label = self.label_font.render("DESCRIPTION", True, FOREST_GREEN)
        screen.blit(story_label, (story_rect.x + 15, story_rect.y + 15))
        
        # 描述文本
        story_y = story_rect.y + 50
        lines = data['story'].split('\n')
        for line in lines:
            if line.strip() and story_y < story_rect.bottom - 25:
                # 文本自动换行
                words = line.strip().split(' ')
                current_line = ""
                for word in words:
                    test_line = current_line + word + " "
                    test_surface = self.story_font.render(test_line, True, BLACK)
                    if test_surface.get_width() <= story_rect.width - 30:
                        current_line = test_line
                    else:
                        if current_line:
                            text_surface = self.story_font.render(current_line.strip(), True, BLACK)
                            screen.blit(text_surface, (story_rect.x + 15, story_y))
                            story_y += 22
                        current_line = word + " "
                
                if current_line:
                    text_surface = self.story_font.render(current_line.strip(), True, BLACK)
                    screen.blit(text_surface, (story_rect.x + 15, story_y))
                    story_y += 22
            elif not line.strip():
                story_y += 12
        
        # 属性区域 - 丛林主题
        stats_y = left_panel.y + left_panel.height // 2 + 30
        stats_rect = pygame.Rect(left_panel.x + 20, stats_y, left_panel.width - 40, left_panel.height // 2 - 50)
        pygame.draw.rect(screen, (240, 248, 240), stats_rect, border_radius=8)
        pygame.draw.rect(screen, FOREST_GREEN, stats_rect, 2, border_radius=8)
        
        # 属性标题
        stats_label = self.label_font.render("ATTRIBUTES", True, FOREST_GREEN)
        screen.blit(stats_label, (stats_rect.x + 15, stats_rect.y + 15))
        
        # 属性列表
        stats_y_pos = stats_rect.y + 50
        stats = data.get('stats', {})
        for key, value in stats.items():
            if stats_y_pos < stats_rect.bottom - 25:
                stat_text = f"• {key}: {value}"
                text_surface = self.stats_font.render(stat_text, True, DARK_GREEN)
                screen.blit(text_surface, (stats_rect.x + 15, stats_y_pos))
                stats_y_pos += 30
        
        # 右侧：大图像和动画
        # 肖像区域（上半部分）
        portrait_rect = pygame.Rect(right_panel.x + 20, right_panel.y + 20, 
                                   right_panel.width - 40, right_panel.height // 2 - 20)
        
        # 肖像标题
        portrait_label = self.label_font.render("PORTRAIT", True, FOREST_GREEN)
        screen.blit(portrait_label, (portrait_rect.x, portrait_rect.y))
        
        portrait_display_rect = pygame.Rect(portrait_rect.x, portrait_rect.y + 35,
                                          portrait_rect.width, portrait_rect.height - 35)
        
        if data.get('portrait_path'):
            portrait_image = ImageCache.load_image(data['portrait_path'])
            if portrait_image:
                # 保持比例缩放，不压缩
                img_rect = portrait_image.get_rect()
                scale = min(portrait_display_rect.width / img_rect.width, 
                           portrait_display_rect.height / img_rect.height) * 0.9
                
                new_size = (int(img_rect.width * scale), int(img_rect.height * scale))
                scaled_portrait = pygame.transform.scale(portrait_image, new_size)
                
                # 居中显示
                img_pos = (portrait_display_rect.centerx - new_size[0] // 2,
                          portrait_display_rect.centery - new_size[1] // 2)
                screen.blit(scaled_portrait, img_pos)
        
        # 动画区域（下半部分）
        anim_rect = pygame.Rect(right_panel.x + 20, right_panel.y + right_panel.height // 2 + 10,
                               right_panel.width - 40, right_panel.height // 2 - 30)
        pygame.draw.rect(screen, (240, 248, 240), anim_rect, border_radius=8)
        pygame.draw.rect(screen, FOREST_GREEN, anim_rect, 2, border_radius=8)
        
        # 动画标题
        anim_label = self.label_font.render("SPRITE ANIMATION", True, FOREST_GREEN)
        screen.blit(anim_label, (anim_rect.x + 15, anim_rect.y + 15))
        
        # 动画显示区域
        anim_display_rect = pygame.Rect(anim_rect.x + 15, anim_rect.y + 50,
                                       anim_rect.width - 30, anim_rect.height - 65)
        
        if self.animator and self.animator.frames:
            self.animator.draw(screen, anim_display_rect)
        else:
            # 无动画提示
            no_anim_text = self.story_font.render("No animation available", True, (100, 100, 100))
            text_rect = no_anim_text.get_rect(center=anim_display_rect.center)
            screen.blit(no_anim_text, text_rect)
    
    def run(self):
        """运行图鉴"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            dt = clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "menu"
                elif event.type == pygame.VIDEORESIZE:
                    new_width = max(event.w, MIN_SCREEN_W)
                    new_height = max(event.h, MIN_SCREEN_H)
                    pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE | pygame.DOUBLEBUF)
                    self.init_cards()
                
                result = self.handle_event(event)
                if result == "back":
                    return "menu"
            
            self.update(dt)
            
            current_screen = pygame.display.get_surface()
            self.draw(current_screen)
            pygame.display.flip()
        
        return "menu" 