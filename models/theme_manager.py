import flet as ft
from typing import Dict, Any


class ThemeManager:
    """Manages application theme colors and modes"""
    
    def __init__(self):
        self.theme_colors = {
            "blue": {"primary": ft.colors.BLUE_700, "accent": ft.colors.BLUE_50},
            "red": {"primary": ft.colors.RED_700, "accent": ft.colors.RED_50},
            "orange": {"primary": ft.colors.ORANGE_700, "accent": ft.colors.ORANGE_50},
            "green": {"primary": ft.colors.GREEN_700, "accent": ft.colors.GREEN_50},
            "yellow": {"primary": ft.colors.YELLOW_700, "accent": ft.colors.YELLOW_50},
            "purple": {"primary": ft.colors.PURPLE_700, "accent": ft.colors.PURPLE_50},
            "indigo": {"primary": ft.colors.INDIGO_700, "accent": ft.colors.INDIGO_50},
        }
        self.current_color = "blue"
        self.current_mode = "light"
    
    def get_available_colors(self) -> Dict[str, Dict[str, str]]:
        """Get all available theme colors"""
        return self.theme_colors.copy()
    
    def get_color_data(self, color_name: str) -> Dict[str, str]:
        """Get color data for a specific theme color"""
        return self.theme_colors.get(color_name, self.theme_colors["blue"])
    
    def is_valid_color(self, color_name: str) -> bool:
        """Check if a color name is valid"""
        return color_name in self.theme_colors
    
    def is_valid_mode(self, mode: str) -> bool:
        """Check if a theme mode is valid"""
        return mode in ["light", "dark"]
    
    def set_color(self, color_name: str):
        """Set the current theme color"""
        if self.is_valid_color(color_name):
            self.current_color = color_name
    
    def set_mode(self, mode: str):
        """Set the current theme mode"""
        if self.is_valid_mode(mode):
            self.current_mode = mode
    
    def apply_theme_to_page(self, page: ft.Page, mode: str):
        """Apply theme mode to a Flet page"""
        if mode == "dark":
            page.theme_mode = ft.ThemeMode.DARK
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
    
    def get_sidebar_color(self, mode: str) -> str:
        """Get sidebar background color based on theme mode"""
        if mode == "dark":
            return ft.colors.GREY_900
        return ft.colors.GREY_100
    
    def get_content_bg_color(self, mode: str) -> str:
        """Get content area background color based on theme mode"""
        if mode == "dark":
            return ft.colors.GREY_800
        return ft.colors.WHITE
    
    def get_secondary_bg_color(self, mode: str) -> str:
        """Get secondary background color based on theme mode"""
        if mode == "dark":
            return ft.colors.GREY_700
        return ft.colors.GREY_50
    
    def get_card_bg_color(self, mode: str) -> str:
        """Get card background color based on theme mode"""
        if mode == "dark":
            return ft.colors.GREY_700
        return ft.colors.WHITE
    
    def get_card_border_color(self, mode: str) -> str:
        """Get card border color based on theme mode"""
        if mode == "dark":
            return ft.colors.GREY_600
        return ft.colors.GREY_300
