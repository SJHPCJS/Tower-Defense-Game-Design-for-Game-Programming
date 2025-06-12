# Forest Guard – Tower-Defense Game Design Project

This repository contains the full development record of **Forest Guard**, a modular tower-defense game created for the *DI32002 - Games Programming ( SEM 2 24/25 ).  You will find the playable source code, early prototypes, AI experiments, and design documentation all in one place.

> Latest stable build: **`Prototypes/TowerDesign2.0`** (codename *Forest Guard v2.0*)

---

## 📁 Repository Layout

```
TowerDesign/
├── Prototypes/            # Playable prototypes
│   ├── TowerTest/         # Earliest proof-of-concept
│   └── TowerDesign2.0/    # Final implementation (v2.0)
│
├── Experiments/           # Stand-alone algorithm experiments
│   ├── Pathfinding/       # BFS, Dijkstra, A*, etc.
│   └── AImap2.0/          # Map-generation benchmarks
│
├── Reference/             # Temporary reference material
└──README.md              # ← you are here
```

Naming conventions
* All run-time source lives in a local **`src/`** folder.
* Build scripts are placed at prototype root (`build_executable.py`, `build_game.bat`).
* Custom levels are JSON files inside a **`levels/`** directory.

---

## 🚀 Quick Start (v2.0)

```bash
# 1 – jump to the latest prototype
cd Prototypes/TowerDesign2.0

# 2 – install runtime dependencies
pip install -r requirements.txt

# 3 – run from source (works on Windows / macOS / Linux)
python run_game.py

# 4 – (make.exe) optional Windows build
python build_executable.py      # or double-click build_game.bat
# resulting file → dist/ForestGuard2.0/ForestGuard2.0.exe
```

---

## 🏗️ Code Architecture (TowerDesign2.0)

| Layer | Key Files | Responsibility |
|-------|-----------|----------------|
| **Core loop** | `main.py`, `game.py`, `run_game.py` | Entry point & high-level state machine (menu / play / library / editor) |
| **Entities**  | `tower.py`, `enemy.py`, `bullet.py`, `map_component.py` | Towers, enemies, bullets, map visuals |
| **Systems**   | `audio_manager.py`, `pathfinding.py`, `level_creator.py`, `level.py` | Audio, path-finding, procedural map generation, wave controller |
| **Resources** | `settings.py`, `resource_manager.py`, `library_data.py` | Global constants, asset lookup, encyclopedia metadata |
| **UI/Tools**  | `menu.py`, `library.py`, `grid.py` | Menus, in-game library, grid utilities |

### Applied Design Patterns
* **Factory** – `TowerFactory`, `EnemyFactory`, `BulletFactory` centralise object creation.
* **Strategy** – interchangeable bullet effects & map-generation algorithms.
* **Observer-like** – `AudioManager` adjusts music based on enemy count without tight coupling.

---

## 🔬 Experiments & Optimisation
* **Path-finding benchmarks** – see `Experiments/Pathfinding`: five algorithms compared on runtime vs. optimality ⇒ A* + stochastic branching selected.
* **Map-generation benchmarks** – see `Experiments/AImap2.0`: three procedural methods evaluated on speed & readability.

---

## 🎮 Feature Highlights (v2.0)
* Combat effect system: burn, chain lightning, slow field, dodge, aura buffs.
* Level editor: drag-to-paint + three AI generators + auto-cleanup/smoothing.
* Adaptive UI: cards & panels scale gracefully on any resolution.
* Modular audio: standalone AudioManager handles BGM/SFX automatically.



Stars ⭐, forks, and feedback are most welcome—help us grow a better tower-defence experience! 😊

## Thanks for ChatGPT for helping with refactoring and README modification!
AI declaration can be found in code comments and report.
