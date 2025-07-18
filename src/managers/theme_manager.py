"""
ThemeManager

This class centralizes all theme-related logic for the application. It uses
Flet's Material 3 `color_scheme_seed` to automatically generate complete
light and dark mode color palettes from a single seed color. It also provides
a failsafe default ColorScheme.
"""

import flet as ft
from typing import Dict


class ThemeManager:
    """Manages the application's theme using a seed color."""

    # Predefined color seeds for Material 3 color scheme generation.
    COLOR_SEEDS: Dict[str, str] = {
        "blue": ft.colors.BLUE,
        "orange": ft.colors.ORANGE,
        "green": ft.colors.GREEN,
        "yellow": ft.colors.YELLOW,
        "purple": ft.colors.PURPLE,
        "indigo": ft.colors.INDIGO,
        "pink": ft.colors.PINK,
        "teal": ft.colors.TEAL,
        "cyan": ft.colors.CYAN,
        "amber": ft.colors.AMBER,
        "lime": ft.colors.LIME,
    }

    def __init__(self, initial_mode: str = "light", initial_color: str = "blue"):
        """
        Initializes the ThemeManager with a mode and color.
        Args:
            initial_mode (str): The initial theme mode ('light' or 'dark').
            initial_color (str): The initial color seed name.
        """
        self.mode = initial_mode  # 'light' or 'dark'
        # Use the provided color if valid, otherwise default to 'blue'.
        self.color_name = initial_color if initial_color in self.COLOR_SEEDS else "blue"

    def set_theme_mode(self, mode: str):
        """
        Updates the theme mode ('light' or 'dark').
        Args:
            mode (str): The new theme mode.
        """
        if mode in ["light", "dark"]:
            self.mode = mode

    def set_theme_color(self, color_name: str):
        """
        Updates the seed color for the theme.
        Args:
            color_name (str): The name of the new color seed.
        """
        if color_name in self.COLOR_SEEDS:
            self.color_name = color_name

    def get_seed_color(self) -> str:
        """
        Gets the current seed color string.
        Returns:
            str: The color value for the current color seed.
        """
        return self.COLOR_SEEDS.get(self.color_name, self.COLOR_SEEDS["blue"])

    def get_theme_data(self) -> ft.Theme:
        """
        Generates a Flet Theme object based on the current seed color.
        Returns:
            ft.Theme: The Flet Theme object for the current color and mode.
        """
        return ft.Theme(
            color_scheme_seed=self.get_seed_color(),
            font_family="Segoe UI",
            appbar_theme=ft.AppBarTheme(
                color=ft.colors.ON_PRIMARY_CONTAINER,
                bgcolor=ft.colors.PRIMARY_CONTAINER,
            ),
            # Add other theme customizations as needed
        )

    # --- Failsafe Default ColorScheme ---
    @staticmethod
    def get_default_color_scheme() -> ft.ColorScheme:
        """
        Returns a complete, failsafe ColorScheme object.
        This is used as a fallback when the main page theme is not yet available,
        ensuring that UI components always have a valid color source.
        Returns:
            ft.ColorScheme: A default color scheme for safe UI rendering.
        """
        return ft.ColorScheme(
            primary=ft.colors.BLUE_700,
            on_primary=ft.colors.WHITE,
            on_surface_variant=ft.colors.GREY_700,
            surface_variant=ft.colors.with_opacity(0.05, ft.colors.BLACK),
            error=ft.colors.RED_400,
            error_container=ft.colors.with_opacity(0.1, ft.colors.RED),
            # Add any other colors your UI might need by default
            background=ft.colors.WHITE,
            surface=ft.colors.GREY_50,
        )
