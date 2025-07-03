"""
Window Manager

Manages window configuration and state by interacting with the UserConfigManager
and the Flet Page object.
"""
import flet as ft
from typing import Optional

# Import the specific managers to make dependencies clear
from . import UserConfigManager

class WindowManager:
    """Manages window configuration and state."""
    
    def __init__(self, page: ft.Page, user_config: UserConfigManager):
        self.page = page
        self.user_config = user_config
    
    def apply_saved_window_config(self):
        """
        Applies the saved window configuration from the UserConfig dataclass
        to the Flet page.
        """
        # This now returns a WindowConfig object, not a dictionary.
        window_config = self.user_config.get_window_config()
        
        # --- CORRECTED: Use dot notation for dataclass attribute access ---
        self.page.window.width = window_config.width
        self.page.window.height = window_config.height
        
        # Set window position if saved
        if window_config.x is not None and window_config.y is not None:
            self.page.window.left = window_config.x
            self.page.window.top = window_config.y
        
        # Set maximized state
        if window_config.maximized:
            self.page.window.maximized = True
    
    def save_current_window_config(self):
        """
        Saves the current window's size, position, and state to the
        user configuration file via the UserConfigManager.
        """
        try:
            # This call is correct as save_window_config expects individual values.
            self.user_config.save_window_config(
                width=int(self.page.window.width or 1600),
                height=int(self.page.window.height or 900),
                x=int(self.page.window.left) if self.page.window.left is not None else None,
                y=int(self.page.window.top) if self.page.window.top is not None else None,
                maximized=self.page.window.maximized or False
            )
        except Exception as e:
            # In a real app, we'd use self.logger, but for a manager, print is okay.
            print(f"Error saving window config: {e}")

