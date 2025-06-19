#!/usr/bin/env python3
"""
Test script to check Flet window position properties
"""

import flet as ft
import time

def main(page: ft.Page):
    page.title = "Window Position Test"
    page.window_resizable = True
    
    def check_position():
        print("\n=== Checking window properties ===")
        
        # Try new API first
        if hasattr(page, 'window'):
            print("Using new API (page.window):")
            try:
                print(f"  window.left: {page.window.left}")
                print(f"  window.top: {page.window.top}")
                print(f"  window.width: {page.window.width}")
                print(f"  window.height: {page.window.height}")
                print(f"  window.maximized: {page.window.maximized}")
            except Exception as e:
                print(f"  Error with new API: {e}")
        
        # Try old API
        print("Using old API (page.window_*):")
        try:
            print(f"  window_left: {page.window_left}")
            print(f"  window_top: {page.window_top}")
            print(f"  window_width: {page.window_width}")
            print(f"  window_height: {page.window_height}")
            print(f"  window_maximized: {page.window_maximized}")
        except Exception as e:
            print(f"  Error with old API: {e}")
        
        print("===================================\n")
    
    def on_close(e):
        print("Window closing - final position check:")
        check_position()
    
    page.on_close = on_close
    
    page.add(
        ft.Column([
            ft.Text("Move this window and click the button to check position"),
            ft.ElevatedButton("Check Position", on_click=lambda e: check_position()),
            ft.Text("Close the window to see final position")
        ])
    )
    
    # Check initial position
    check_position()

if __name__ == "__main__":
    ft.app(target=main)
