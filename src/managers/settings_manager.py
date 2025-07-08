"""
Settings Manager

Manages application settings and preferences logic.
This class holds NO UI components.
"""

from typing import Callable, Optional
from .theme_manager import ThemeManager
from .user_config_manager import UserConfigManager


class SettingsManager:
    """Manages application settings logic, decoupled from the UI."""

    def __init__(self, user_config: UserConfigManager, theme_manager: ThemeManager):
        self.user_config = user_config
        self.theme_manager = theme_manager
        self.on_theme_change: Optional[Callable[[], None]] = None
        self.on_display_name_change: Optional[Callable[[], None]] = None

    def set_callbacks(
        self, on_theme_change: Callable, on_display_name_change: Callable
    ):
        """Sets callbacks to notify the controller of changes."""
        self.on_theme_change = on_theme_change
        self.on_display_name_change = on_display_name_change

    def toggle_theme_mode(self):
        """Toggles the theme between light and dark mode."""
        current_mode = self.theme_manager.mode
        new_mode = "light" if current_mode == "dark" else "dark"

        self.theme_manager.set_theme_mode(new_mode)
        self.user_config.save_theme_mode(new_mode)

        if self.on_theme_change:
            self.on_theme_change()

    def change_theme_color(self, color_name: str):
        """Changes the application's primary color theme."""
        if color_name in self.theme_manager.COLOR_SEEDS:
            self.theme_manager.set_theme_color(color_name)
            self.user_config.save_theme_color(color_name)

            if self.on_theme_change:
                self.on_theme_change()

    def save_display_name(self, new_name: str):
        """Saves the user's display name."""
        self.user_config.save_display_name(new_name)
        if self.on_display_name_change:
            self.on_display_name_change()
