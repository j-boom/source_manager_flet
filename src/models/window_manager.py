import flet as ft
from typing import Optional, Dict, Any
from .user_config import UserConfigManager


class WindowManager:
    """Manages window configuration and state"""
    
    def __init__(self, page: ft.Page, user_config: UserConfigManager):
        self.page = page
        self.user_config = user_config
    
    def apply_saved_window_config(self):
        """Apply saved window configuration to the page"""
        window_config = self.user_config.get_window_config()
        
        # Set window dimensions
        self.page.window_width = window_config["width"]
        self.page.window_height = window_config["height"]
        self.page.window_min_width = 1200
        self.page.window_min_height = 700
        
        # Set window position if saved
        if window_config["x"] is not None and window_config["y"] is not None:
            self.page.window_left = window_config["x"]
            self.page.window_top = window_config["y"]
        
        # Set maximized state
        if window_config["maximized"]:
            self.page.window_maximized = True
    
    def save_current_window_config(self):
        """Save current window configuration"""
        try:
            self.user_config.save_window_config(
                width=int(self.page.window_width or 1600),
                height=int(self.page.window_height or 900),
                x=int(self.page.window_left) if self.page.window_left is not None else None,
                y=int(self.page.window_top) if self.page.window_top is not None else None,
                maximized=self.page.window_maximized or False
            )
        except Exception as e:
            print(f"Error saving window config: {e}")
    
    def setup_window_event_handler(self, callback):
        """Set up window event handler if available"""
        # TODO: Add window event handler when Flet properly supports it
        # For now, we'll save on application exit
        pass
    
    def get_window_info(self) -> Dict[str, Any]:
        """Get current window information"""
        return {
            "width": self.page.window_width,
            "height": self.page.window_height,
            "x": self.page.window_left,
            "y": self.page.window_top,
            "maximized": self.page.window_maximized
        }
