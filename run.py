#!/usr/bin/env python3
"""
Source Manager Application Launcher
"""
import sys
from pathlib import Path

# Add the src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Import and run the main application
from main import main
import flet as ft

if __name__ == "__main__":
    ft.app(target=main)
