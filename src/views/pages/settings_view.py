"""
Settings View (Refactored)

This view provides the UI for changing application settings. It follows the
application's standard architecture, building its UI on demand and delegating
all logic to the controller and its managers.
"""
import flet as ft
from src.views.base_view import BaseView

class SettingsView(BaseView):
    """The UI for the settings page."""

    def __init__(self, page: ft.Page, controller):
        """Initializes the SettingsView."""
        # Call the parent constructor first to ensure self.page and self.controller are set.
        super().__init__(page, controller)
        
        # The SettingsManager is accessed via the controller.
        self.settings_manager = self.controller.settings_manager

    def build(self) -> ft.Control:
        """Builds the settings UI using the safe 'colors' property from BaseView."""
        # Use the safe 'self.colors' property, which is guaranteed to exist.
        colors = self.colors

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Settings", theme_style=ft.TextThemeStyle.HEADLINE_LARGE, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=20),
                    
                    self._build_appearance_section(colors),
                    
                    # You can add other settings sections here following the same pattern.
                ],
                spacing=15,
                scroll=ft.ScrollMode.ADAPTIVE
            ),
            padding=ft.padding.all(30),
            expand=True,
        )

    def _build_appearance_section(self, colors) -> ft.Column:
        """Builds the UI controls for the 'Appearance' settings."""
        return ft.Column(
            [
                ft.Text("Appearance", theme_style=ft.TextThemeStyle.TITLE_LARGE),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.BRIGHTNESS_6, color=colors.primary),
                    title=ft.Text("Dark Mode"),
                    trailing=ft.Switch(
                        value=self.page.theme_mode == ft.ThemeMode.DARK,
                        # The on_change event calls the appropriate manager method.
                        on_change=lambda e: self.settings_manager.toggle_theme_mode()
                    )
                ),
                
                ft.Container(height=20),
                ft.Text("Theme Color", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.Row(self._build_color_buttons(colors), wrap=True, spacing=15),
            ],
            spacing=10
        )

    def _build_color_buttons(self, colors) -> list[ft.Control]:
        """Creates the color selection buttons."""
        buttons = []
        current_color_name = self.settings_manager.theme_manager.color_name
        theme_manager = self.settings_manager.theme_manager

        for color_name, seed_color in theme_manager.COLOR_SEEDS.items():
            is_selected = color_name == current_color_name
            
            buttons.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(
                                width=40, height=40, bgcolor=seed_color, border_radius=20,
                                border=ft.border.all(3, colors.primary if is_selected else ft.colors.TRANSPARENT),
                            ),
                            ft.Text(
                                color_name.title(), size=12,
                                weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL,
                                color=colors.primary if is_selected else colors.on_surface_variant
                            )
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8
                    ),
                    # The on_click event calls the appropriate manager method.
                    on_click=lambda e, c=color_name: self.settings_manager.change_theme_color(c),
                    border_radius=8,
                    ink=True,
                    padding=8
                )
            )
        return buttons

