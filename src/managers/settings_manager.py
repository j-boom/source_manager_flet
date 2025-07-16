from typing import Callable, Optional
from .theme_manager import ThemeManager
from .user_config_manager import UserConfigManager


class SettingsManager:
    """
    Manages application settings logic, decoupled from the UI.

    This class acts as a bridge between the UI and the underlying configuration/theme managers.
    It exposes methods for changing user preferences and notifies the controller via callbacks.
    """

    def __init__(self, user_config: UserConfigManager, theme_manager: ThemeManager):
        """
        Initializes the SettingsManager.

        Args:
            user_config (UserConfigManager): The user configuration manager instance.
            theme_manager (ThemeManager): The theme manager instance.
        """
        self.user_config = user_config
        self.theme_manager = theme_manager
        # Optional callbacks to notify the controller/UI of changes
        self.on_theme_change: Optional[Callable[[], None]] = None
        self.on_display_name_change: Optional[Callable[[], None]] = None

    def set_callbacks(
        self, on_theme_change: Callable, on_display_name_change: Callable
    ):
        """
        Sets callbacks to notify the controller/UI when settings change.

        Args:
            on_theme_change (Callable): Called when the theme changes.
            on_display_name_change (Callable): Called when the display name changes.
        """
        self.on_theme_change = on_theme_change
        self.on_display_name_change = on_display_name_change

    def toggle_theme_mode(self):
        """
        Toggles the theme between light and dark mode.
        Updates both the theme manager and user config, and notifies the UI if needed.
        """
        current_mode = self.theme_manager.mode
        new_mode = "light" if current_mode == "dark" else "dark"

        self.theme_manager.set_theme_mode(new_mode)
        self.user_config.save_theme_mode(new_mode)

        # Notify the UI/controller if a callback is set
        if self.on_theme_change:
            self.on_theme_change()

    def change_theme_color(self, color_name: str):
        """
        Changes the application's primary color theme.
        Updates both the theme manager and user config, and notifies the UI if needed.

        Args:
            color_name (str): The name of the color theme to apply.
        """
        if color_name in self.theme_manager.COLOR_SEEDS:
            self.theme_manager.set_theme_color(color_name)
            self.user_config.save_theme_color(color_name)

            # Notify the UI/controller if a callback is set
            if self.on_theme_change:
                self.on_theme_change()

    def save_display_name(self, new_name: str):
        """
        Saves the user's display name and notifies the UI/controller if needed.

        Args:
            new_name (str): The new display name to save.
        """
        self.user_config.save_display_name(new_name)
        if self.on_display_name_change:
            self.on_display_name_change()
