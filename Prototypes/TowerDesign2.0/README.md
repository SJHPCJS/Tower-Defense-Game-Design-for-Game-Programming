# Forest Guard - Tower Defense Game

A modern tower defense game built with Pygame featuring adaptive UI, level creation tools, and strategic gameplay.

## Features

### Game Features
- **Adaptive UI**: Resizable window with minimum size constraints (800x600)
- **Fullscreen Support**: Toggle with F11 key
- **Economic System**: Starting money ($100), tower costs, and kill rewards
- **Tower Types**: 
  - Fast Tower ($20): High attack speed, low damage
  - Strong Tower ($40): High damage, slow attack speed  
  - Balanced Tower ($30): Moderate damage and speed
- **Demolish System**: Remove towers for 50% refund
- **Dynamic Scaling**: All game elements scale with window size

### Level Creator
- **Visual Editor**: Place and remove path tiles
- **AI Generation**: Automated level creation with path optimization
- **Save/Load**: JSON-based level storage
- **Path Validation**: Ensures valid paths from spawn to home

### Technical Features
- **Pathfinding**: A* algorithm for enemy navigation
- **Sprite Management**: Efficient tower, bullet, and enemy handling
- **Modern UI**: Dark theme with hover effects and visual feedback
- **Encoding Support**: Full UTF-8 support for level names

## How to Run

```bash
cd Prototypes/TowerDesign2.0
python run_game.py
```

## Controls

- **ESC**: Return to menu / Exit
- **F11**: Toggle fullscreen
- **Mouse**: Click to place towers, interact with UI
- **Level Creator**: 
  - Click tools to select
  - Click grid to place/remove paths
  - Enter to save level

## Project Structure

```
TowerDesign2.0/
├── src/                 # Source code
│   ├── game.py         # Main game logic
│   ├── menu.py         # Menu system
│   ├── level_creator.py # Level creation tool
│   ├── level.py        # Level management
│   ├── tower.py        # Tower mechanics
│   ├── enemy.py        # Enemy behavior
│   ├── bullet.py       # Projectile system
│   ├── pathfinding.py  # A* pathfinding
│   ├── grid.py         # Grid management
│   ├── map_component.py # Map rendering
│   └── settings.py     # Game configuration
├── levels/             # Level files (JSON)
├── assets/             # Game assets
└── run_game.py         # Entry point
```

## Game Mechanics

### Economy
- Start with $100
- Towers cost $20-40 depending on type
- Earn $1 per enemy defeated
- Demolish towers for 50% refund

### Tower Placement
- Only on grass tiles (green)
- Cannot place on paths (brown)
- Cannot place on spawn/home points

### Enemy Behavior
- Follow optimal paths using A* pathfinding
- Scale with window size for consistent gameplay
- Deal damage to base when reaching home

### Level Design
- Spawn point: Usually top-left
- Home point: Automatically calculated as farthest path point from spawn
- Path validation ensures playable levels

## Recent Updates

- Removed all backup files for cleaner project structure
- Fixed Chinese comments and encoding issues
- Removed fullscreen hints from UI
- Updated level creator to use proper end point calculation
- Ensured consistent spawn/home positioning across all levels 