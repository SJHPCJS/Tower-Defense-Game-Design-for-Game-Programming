# Tower Defense Game 2.0

A tower defense game with comprehensive bullet system, special effects, and adaptive UI.

## Key Features

### Adaptive UI System
- **Adaptive Library Toolbar**: Automatically adjusts card spacing and sizes based on screen resolution
  - Optimal spacing on wide screens (1920px+)
  - Compressed spacing on medium screens (1024-1366px)
  - Scaled-down cards on narrow screens (<1024px)
  - Real-time window resize support
  - Maintains visual balance across all screen sizes

### Advanced Bullet System
- **Design Patterns**: Strategy and Factory patterns for bullet behavior
- **Special Effects**: 
  - Emberwing: Burn damage (5 damage/sec for 3 seconds) with red "Fire" text
  - Volt Cow: Electric chain damage (50% to nearby enemies) with yellow "Zap" text
  - Other towers: Normal damage with white "Miss" text
- **Visual Enhancements**: 
  - Bullet rotation animation (360°/second)
  - Large 40x40 bullet sprites with proper scaling
  - Text effects sized at 32px for visibility

### Game Flow Improvements
- **Preparation Time**: 10-second countdown before first wave with Chinese/English text support
- **Unified Forest Guard Theme**: Consistent green/brown color scheme across all interfaces
- **Enhanced Text Effects**: Properly sized and visible damage/miss indicators

### UI Enhancements
- **Level Creator**: Forest Guard themed interface with wood textures and shadows
- **Library System**: Character gallery with adaptive card layout
- **ESC Key Bindings**: Return to menu from library and level creator

## Technical Implementation

### Adaptive Library System
```python
# Automatically calculates optimal card layout based on screen width
def init_cards(self):
    screen_w, screen_h = pygame.display.get_surface().get_size()
    total_cards = 1 + len(TOWERS) + len(ENEMIES)  # 11 cards total
    
    # Adaptive sizing algorithm:
    # 1. Try base size (140x110) with ideal spacing (25px)
    # 2. Reduce spacing to minimum (15px) if needed
    # 3. Scale down cards proportionally if still too wide
    # 4. Center the entire toolbar on screen
```

### Bullet Strategy Pattern
```python
class BulletStrategy:
    def create_bullet(self, start_pos, target_pos, tower_name):
        # Factory method creates appropriate bullet type
        
class FireBulletStrategy(BulletStrategy):
    def apply_damage(self, enemy, enemies_group):
        # Apply burn effect: 5 damage/sec for 3 seconds
        
class ElectricBulletStrategy(BulletStrategy):
    def apply_damage(self, enemy, enemies_group):
        # Chain to nearby enemies within 40px for 50% damage
```

## File Structure

```
Prototypes/TowerDesign2.0/
├── src/
│   ├── bullets.py          # Bullet system with strategy pattern
│   ├── game.py            # Main game with preparation time
│   ├── library.py         # Adaptive character library
│   ├── level_creator.py   # Forest-themed level creator
│   ├── main.py           # Updated main menu
│   └── ...
├── test_adaptive_library.py    # Adaptive UI demonstration
├── test_preparation_time.py    # Preparation time test
├── test_all_improvements.py    # Comprehensive feature test
└── README.md
```

## Testing

### Adaptive Library Test
```bash
python test_adaptive_library.py
```
- Press SPACE to cycle through different screen resolutions
- Drag window edges to test real-time resizing
- Observe automatic card spacing and size adjustments

### Preparation Time Test
```bash
python test_preparation_time.py
```
- Shows 10-second countdown before first wave
- Displays timing in wave panel

### Comprehensive Test
```bash
python test_all_improvements.py
```
- Tests all features: bullets, effects, preparation time, and adaptive UI

## Screen Size Support

| Resolution | Card Size | Spacing | Behavior |
|------------|-----------|---------|-----------|
| 2560x1440+ | 140x110 | 25px | Optimal layout with generous spacing |
| 1920x1080 | 140x110 | 25px | Standard layout |
| 1366x768 | 140x110 | 15px | Compressed spacing |
| 1024x768 | 120x96 | 15px | Scaled down cards |
| 800x600 | 100x80 | 15px | Minimum card size |

The adaptive system ensures the library toolbar remains functional and visually appealing across all supported screen sizes, automatically adjusting layout parameters without requiring manual configuration.

## Running the Game

```bash
python run_game.py
```

Navigate through the menus to access:
- **PLAY**: Start the game with preparation time
- **LIBRARY**: View adaptive character gallery
- **LEVEL CREATOR**: Create custom levels with Forest Guard theme
- **QUIT**: Exit the game

All interfaces support ESC key to return to the main menu. 