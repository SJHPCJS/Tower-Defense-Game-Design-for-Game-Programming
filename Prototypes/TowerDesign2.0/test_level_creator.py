#!/usr/bin/env python3
"""
Test script for Level Creator
"""

import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

from src.level_creator import run_level_creator

if __name__ == "__main__":
    print("Testing Level Creator...")
    result = run_level_creator()
    print(f"Level Creator returned: {result}") 