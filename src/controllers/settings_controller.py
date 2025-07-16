import flet as ft
from .base_controller import BaseController


class SettingsController(BaseController):
    def apply_theme(self):
        """
        Applies the current theme settings to the page.
        This method is called to ensure the page reflects the current theme mode and color.
        """
        self.controller.main_view.refresh_theme()

    def get_display_name(self):
        """
        Returns the user's display name, if set.
        Returns:
            str: The display name, or an empty string if not set.
        """
        return self.controller.settings_manager.get_display_name()

    def save_display_name(self, display_name: str):
        """
        Saves the user's display name.
        Args:
            display_name (str): The display name to save.
        """
        self.controller.settings_manager.save_display_name(display_name.strip())
        self.controller.main_view.update_greeting()
        self.controller.navigate_to("settings")

    def toggle_theme_mode(self, e=None):
        """
        Handles the event to toggle the theme mode and update the UI.
        """
        # Persist the mode change
        new_mode = self.controller.settings_manager.toggle_theme_mode()

        # In-memory change
        self.controller.theme_manager.set_theme_mode(new_mode)
        # Apply the new theme to the UI
        self.apply_theme()

        # Force a rebuild to change the icon
        self.controller.navigate_to("settings")

    def change_theme_color(self, color_name: str):
        """
        Changes the theme color and updates the UI.
        Args:
            color_name (str): The name of the color to set.
        """
        # Persist the color change
        self.controller.settings_manager.save_theme_color(color_name)
        # In-memory change
        self.controller.theme_manager.set_theme_color(color_name)
        # Apply the new theme to the UI
        self.apply_theme()

        # Force a rebuild to change the selected color
        self.controller.navigate_to("settings")
