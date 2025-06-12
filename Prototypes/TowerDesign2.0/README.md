# Forest Guard 2.0 – Project Overview & Quick Start
## Market-Ready Tower Defence Game
> 🧩 [Download Forest Guard 2.0 Release (.exe)](https://github.com/SJHPCJS/Tower-Defense-Game-Design-for-Game-Programming/releases/latest) – No install needed, just double-click!


> “Nature will fight back… and it’s counting on you!”

Forest Guard is a playful tower-defence experiment built with **Python + Pygame**.  Version 2.0 refactors the original prototype into a cleaner, fairer and much more modular code-base.

---

## 🚀 What’s New in 2.0

| Area | 1.x Prototype | 2.0 Implementation |
|------|--------------|--------------------|
| **Path-finding** | Dynamic auto-rerouting around towers (hard to predict & unbalanced) | Pure A* with *controlled* random branching at junctions → fair & readable |
| **Combat system** | Towers/enemies only differed by HP & speed | Full **effect system** (burn, chain-lightning, slow-field, dodge, aura-boost…) |
| **Level creator** | Manual grid editor, single path | 3 procedural generators (Tower-Path / Maze-Loops / Prim-Loops) + drag-to-paint + auto-cleanup |
| **Character library** | ─ | In-game card gallery with lore & stats |
| **Audio** | ─ | Stand-alone **AudioManager** module, automatically switches BGM & key SFX |
| **Code base** | Monolith | Modular architecture, factories & strategies everywhere |

---

## 🏗️ Code Architecture

```
src/
├── main.py / game.py / run_game.py   # entry point & state machine (menu / play / library / editor)
│
├── tower.py        # Tower hierarchy  +  TowerFactory
├── enemy.py        # Enemy hierarchy  +  EnemyFactory
├── bullet.py       # Bullet & visual-effect strategies  +  BulletFactory
│
├── level.py        # Wave manager  +  A* routing hooks
├── level_creator.py# Manual + AI map designer (strategy pattern)
├── map_component.py# Drawable grid + home animation
├── pathfinding.py  # A* with random branching
│
├── audio_manager.py    # Centralised BGM / SFX hub
├── resource_manager.py # Locate assets both in-dev & in packaged exe
│
├── settings.py     # Global constants
├── library.py      # In-game character encyclopedia
└── library_data.py # JSON-like dict containing lore & stats
```

### Design Patterns Inside
* Factory Pattern – `TowerFactory`, `EnemyFactory`, `BulletFactory`
* Strategy Pattern – bullet effects & procedural map generation
* Observer-lite – `AudioManager` reacts to enemy count without tight coupling

---

## 🧠 AI Highlights
* **A* Path-finding + random branching** – keeps routes fresh yet predictable enough for planning.
* **State-driven game loop** – lightweight FSM toggling between *menu / gameplay / library / editor*.

---

## 🛠️ Building & Running

1. Install dependencies

```bash
pip install -r requirements.txt
```

2. Launch the game (source version)

```bash
python run_game.py
```

3. Create a portable **.exe** (Windows)

```bash
python build_executable.py   # or just double-click build_game.bat
```

The compiled executable will land here:

```
dist/ForestGuard2.0/ForestGuard2.0.exe
```

Send that single folder to a friend – no Python required!

> **Tip**   Assets are bundled automatically.

---

## 👂 Play-Testing & Iteration
* Removed auto-reroute → fairness ++
* Adjusted tower costs
* Added Library after players asked “what can it do?”
* Integrated drag-paint in editor to spare everyone’s wrists

Iterate → Refactor → Test → Repeat – that’s how we got here.

---

## 📁 License & Assets
Open-source.  Sprites & sounds are either CC0, permissive licences, or AI-generated – see `/assets/README_assets.txt` for a all links.

Happy modding, and may the forest be with you 🌲🛡️ 

## Thanks for ChatGPT for helping with refactoring and README modification!
AI declaration can be found in code comments and report.
