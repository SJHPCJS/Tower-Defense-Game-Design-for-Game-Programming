"""
AI assisted code included in this file, you can see the comments below for details.
"""
import pygame
import os
from pathlib import Path
from typing import Optional
from resource_manager import get_music_path, ResourceManager

class AudioManager:
    """Audio manager - handles background music and sound effects"""
    """This class is inspired by the Pygame documentation and examples. Available at: https://www.pygame.org/docs/ref/music.html"""

    
    def __init__(self):
        # initialize pygame audio module
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

        # use the resource manager to get the music directory
        self.music_dir = ResourceManager.get_asset_path("music")

        self.music_files = {
            'menu': 'Fantasy Menu Theme.mp3',
            'game': 'game music.ogg', 
            'battle': 'UrbanTheme.mp3'
        }
        
        # sound effect file mapping
        self.sound_files = {
            'flame': 'flame.ogg',
            'death': 'death.wav',
            'wave_complete': 'vgmenuselect.wav',
            'victory': 'vgmenuselect.wav',
            'game_over': 'GAMEOVER.wav',
            'home_hit': 'lose sound 1_0.wav',
            'banana_detect': 'monkey-1.ogg',
            'wood_sage_detect': 'bear_01.ogg'
        }
        
        # state tracking
        self.current_state = "menu"
        self.enemy_count = 0
        self.current_music = None
        self.music_volume = 0.3
        self.effect_volume = 0.7
        self.music_enabled = True
        self.sound_enabled = True
        

        self.sounds = {}
        self._load_sounds()
        self.in_battle = False
        
        pygame.mixer.music.set_volume(self.music_volume)
        
    def _load_sounds(self):
        """Load all sound effects"""
        for sound_name, filename in self.sound_files.items():
            sound_path = self.music_dir / filename
            try:
                if sound_path.exists():
                    self.sounds[sound_name] = pygame.mixer.Sound(str(sound_path))
                    self.sounds[sound_name].set_volume(self.effect_volume)
                    print(f"Loaded sound: {sound_name}")
                else:
                    print(f"Sound file not found: {sound_path}")
            except pygame.error as e:
                print(f"Failed to load sound {sound_name}: {e}")
    
    def play_music(self, music_key: str, loops: int = -1, fade_in_ms: int = 1000):
        """Play background music"""
        if not self.music_enabled:
            return
            
        if music_key not in self.music_files:
            print(f"Unknown music key: {music_key}")
            return
            
        music_path = self.music_dir / self.music_files[music_key]
        
        if not music_path.exists():
            print(f"Music file not found: {music_path}")
            return
            
        try:
            # avoid reloading the same music if it's already playing
            if self.current_music == music_key and pygame.mixer.music.get_busy():
                return
                
            pygame.mixer.music.load(str(music_path))
            pygame.mixer.music.set_volume(self.music_volume)
            
            if fade_in_ms > 0:
                pygame.mixer.music.play(loops, fade_ms=fade_in_ms)
            else:
                pygame.mixer.music.play(loops)
                
            self.current_music = music_key
            print(f"Playing music: {music_key}")
            
        except pygame.error as e:
            print(f"Failed to play music {music_key}: {e}")
    
    def stop_music(self, fade_out_ms: int = 1000):
        if pygame.mixer.music.get_busy():
            if fade_out_ms > 0:
                pygame.mixer.music.fadeout(fade_out_ms)
            else:
                pygame.mixer.music.stop()
            self.current_music = None
    
    def pause_music(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
    
    def unpause_music(self):
        pygame.mixer.music.unpause()
    
    def play_sound(self, sound_key: str):
        if not self.sound_enabled:
            return
            
        if sound_key not in self.sounds:
            print(f"Unknown sound key: {sound_key}")
            return
            
        try:
            self.sounds[sound_key].play()
            print(f"Playing sound: {sound_key}")
        except pygame.error as e:
            print(f"Failed to play sound {sound_key}: {e}")
    
    def set_music_volume(self, volume: float):
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sound_volume(self, volume: float):
        self.effect_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.effect_volume)
    
    def enable_music(self, enabled: bool):
        self.music_enabled = enabled
        if not enabled:
            self.stop_music()
    
    def enable_sound(self, enabled: bool):
        self.sound_enabled = enabled
    
    def update_enemy_count(self, count: int):
        old_count = self.enemy_count
        self.enemy_count = count

        was_in_battle = self.in_battle
        self.in_battle = count > 0

        # If the battle state changed, play appropriate music
        if self.in_battle and not was_in_battle:
            print(f"Entering battle! Enemy count: {count}")
            self.play_music('battle', fade_in_ms=500)
        elif not self.in_battle and was_in_battle:
            print(f"Leaving battle! Enemy count: {count}")
            self.play_music('game', fade_in_ms=500)
    
    def play_menu_music(self):
        self.play_music('menu')
    
    def play_game_music(self):
        # play the game music only if there are no enemies
        if self.enemy_count == 0:
            self.play_music('game')
    
    def play_battle_music(self):
        # play the battle music only if there are enemies
        if self.enemy_count > 0:
            self.play_music('battle')
    
    def play_flame_sound(self):
        self.play_sound('flame')
    
    def play_death_sound(self):
        self.play_sound('death')
    
    def play_wave_complete_sound(self):
        self.play_sound('wave_complete')
    
    def play_victory_sound(self):
        self.play_sound('victory')
    
    def play_game_over_sound(self):
        self.play_sound('game_over')
    
    def play_home_hit_sound(self):
        self.play_sound('home_hit')
    
    def play_banana_detect_sound(self):
        self.play_sound('banana_detect')
    
    def play_wood_sage_detect_sound(self):
        self.play_sound('wood_sage_detect')
    
    def stop_all_audio(self):
        pygame.mixer.music.stop()
        print("Stopped all music")
        pygame.mixer.stop()
        print("Stopped all sounds")

audio_manager = AudioManager() 