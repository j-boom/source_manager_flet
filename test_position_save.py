#!/usr/bin/env python3
"""
Test window position saving in our actual app
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import flet as ft
from src.models.user_config import UserConfigManager
from src.models.window_manager import WindowManager

def main(page: ft.Page):
    page.title = "Window Position Save Test"
    
    # Initialize managers
    user_config = UserConfigManager()
    window_manager = WindowManager(page, user_config)
    
    # Apply saved config
    window_manager.apply_saved_window_config()
    
    def save_position_now():
        print("\n=== Manual save triggered ===")
        window_manager.save_current_window_config()
        print("=== Save complete ===\n")
    
    def check_config():
        config = user_config.get_window_config()
        print(f"\n=== Current saved config ===")
        print(f"Config: {config}")
        print("=== End config ===\n")
    
    page.add(
        ft.Column([
            ft.Text("Move window and test saving"),
            ft.ElevatedButton("Save Position Now", on_click=lambda e: save_position_now()),
            ft.ElevatedButton("Check Saved Config", on_click=lambda e: check_config()),
            ft.Text("Close window to test automatic save")
        ])
    )
    
    # Set up close handler
    def on_close(e):
        print("\n=== Window closing - auto save ===")
        window_manager.save_current_window_config()
        print("=== Auto save complete ===\n")
    
    page.on_close = on_close

if __name__ == "__main__":
    ft.app(target=main)
