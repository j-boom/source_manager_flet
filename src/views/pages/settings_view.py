"""
Settings View (Refactored)

This view provides the UI for changing application settings. It follows the
application's standard architecture, building its UI on demand and delegating
all logic to the controller and its managers.
"""

import flet as ft
from src.views.base_view import BaseView


class SettingsView(BaseView):
    """
    The UI for the settings page.

    This view provides controls for changing user preferences such as display name,
    appearance, and theme color. All business logic is delegated to the controller
    and its managers, keeping the view focused on UI construction.
    """

    def build(self) -> ft.Control:
        """
        Builds the settings UI using the safe 'colors' property from BaseView.
        Returns:
            ft.Control: The root container for the settings page.
        """
        # Use the safe 'self.colors' property, which is guaranteed to exist.
        colors = self.colors

        # Build the main settings page layout
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Settings",
                        theme_style=ft.TextThemeStyle.HEADLINE_LARGE,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Divider(height=20),
                    self._build_display_name_section(),
                    self._build_appearance_section(colors),
                    # Future settings sections...
                ],
                spacing=15,
                scroll=ft.ScrollMode.ADAPTIVE,
            ),
            padding=ft.padding.all(30),
            expand=True,
        )

    def _build_appearance_section(self, colors) -> ft.Column:
        """
        Builds the UI controls for the 'Appearance' settings, including theme mode and color.
        Args:
            colors: The color palette from BaseView for consistent theming.
        Returns:
            ft.Column: The column containing appearance controls.
        """
        # Determine the current mode and icon for the theme toggle
        theme_mode = self.controller.theme_manager.mode
        mode_icon = self._get_mode_icon()
        mode_label = "Dark Mode" if theme_mode == "dark" else "Light Mode"

        def on_icon_click(e):
            # Toggle the theme mode via the controller
            self.controller.settings_controller.toggle_theme_mode(e)

        # Make the icon button large to match the color buttons (40x40)
        large_icon_button = ft.Container(
            content=ft.IconButton(
                icon=mode_icon,
                icon_color=colors.primary,
                tooltip=f"Switch to {'Light' if theme_mode == 'dark' else 'Dark'} Mode",
                on_click=on_icon_click,
                icon_size=32,  # Make the icon itself larger
            ),
            width=40,
            height=40,
            alignment=ft.alignment.center,
        )

        # Build the appearance section column
        return ft.Column(
            [
                ft.Text("Appearance", theme_style=ft.TextThemeStyle.TITLE_LARGE),
                ft.ListTile(
                    leading=large_icon_button,
                    title=ft.Text(mode_label),
                ),
                ft.Container(height=20),
                ft.Text("Theme Color", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.Row(self._build_color_buttons(colors), wrap=True, spacing=15),
            ],
            spacing=10,
        )

    def _build_display_name_section(self) -> ft.Control:
        """
        Builds the UI controls for changing the user's display name.
        Returns:
            ft.Control: A column containing the display name field, save button, and feedback.
        """
        current_name = self.controller.settings_controller.get_display_name()
        # TextField for entering the display name
        display_name_field = ft.TextField(
            label="Display Name",
            value=current_name,
            width=300,
            max_length=50,
            autofocus=False,
            on_submit=lambda e: save_display_name(),
            bgcolor=ft.colors.SURFACE_VARIANT,
            focused_bgcolor=ft.colors.SURFACE,
            color=ft.colors.ON_SURFACE_VARIANT,
        )
        # Feedback text for validation and success messages
        feedback_text = ft.Text("", color=ft.colors.GREEN, visible=False)

        def save_display_name():
            """
            Validates and saves the new display name, updating the UI with feedback.
            """
            new_name = display_name_field.value
            if not new_name:
                feedback_text.value = "Display name cannot be empty."
                feedback_text.color = ft.colors.ERROR
                feedback_text.visible = True
            elif len(new_name) > 50:
                feedback_text.value = "Display name cannot exceed 50 characters."
                feedback_text.color = ft.colors.ERROR
                feedback_text.visible = True
            else:
                new_name = new_name.strip()
                self.controller.settings_controller.save_display_name(new_name)
                feedback_text.value = "Display name updated successfully."
                feedback_text.color = ft.colors.GREEN
                feedback_text.visible = True
                self.page.update()

        # Save button for display name
        save_button = ft.ElevatedButton(
            text="Save",
            on_click=lambda e: save_display_name(),
            style=ft.ButtonStyle(bgcolor=ft.colors.PRIMARY, color=ft.colors.ON_PRIMARY),
        )
        # Build the display name section column
        return ft.Column(
            [
                ft.Text(
                    "Change Display Name", theme_style=ft.TextThemeStyle.TITLE_LARGE
                ),
                ft.Row(
                    [display_name_field, save_button],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=10,
                ),
                feedback_text,
                ft.Divider(height=20),
            ]
        )

    def _build_color_buttons(self, colors) -> list[ft.Control]:
        """
        Creates the color selection buttons for theme color selection.
        Args:
            colors: The color palette from BaseView for consistent theming.
        Returns:
            list[ft.Control]: A list of color button controls.
        """
        buttons = []
        current_color_name = self.controller.theme_manager.color_name
        theme_manager = self.controller.theme_manager

        for color_name, seed_color in theme_manager.COLOR_SEEDS.items():
            is_selected = color_name == current_color_name

            # Each color button is a container with a colored circle and label
            buttons.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(
                                width=40,
                                height=40,
                                bgcolor=seed_color,
                                border_radius=20,
                                border=ft.border.all(
                                    3,
                                    (
                                        colors.primary
                                        if is_selected
                                        else ft.colors.TRANSPARENT
                                    ),
                                ),
                            ),
                            ft.Text(
                                color_name.title(),
                                size=12,
                                weight=(
                                    ft.FontWeight.BOLD
                                    if is_selected
                                    else ft.FontWeight.NORMAL
                                ),
                                color=(
                                    colors.primary
                                    if is_selected
                                    else colors.on_surface_variant
                                ),
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    # The on_click event calls the controller to change the theme color.
                    on_click=(
                        lambda e, c=color_name: self.controller.settings_controller.change_theme_color(
                            c
                        )
                    ),
                    border_radius=8,
                    ink=True,
                    padding=8,
                )
            )
        return buttons

    def _get_mode_icon(self):
        """
        Returns the appropriate icon for the current theme mode.
        Returns:
            str: The icon name for the current theme mode.
        """
        theme_mode = self.controller.theme_manager.mode
        return ft.icons.DARK_MODE if theme_mode == "dark" else ft.icons.LIGHT_MODE
