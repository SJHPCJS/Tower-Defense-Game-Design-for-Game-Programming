#!/usr/bin/env python3
"""
Forest Guard - Tower Defense Game
"""

import sys
import os

src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

from src.game import main

if __name__ == "__main__":
    print("Starting Forest Guard...")
    print("Defend the Forest from Invaders!")
    print("-" * 40)
    main()