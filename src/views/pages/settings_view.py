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


    def __init__(self, page: ft.Page, controller):
        """
        Initializes the SettingsView.

        Args:
            page (ft.Page): The Flet page instance.
            controller: The main application controller.
        """
        # Call the parent constructor first to ensure self.page and self.controller are set.
        super().__init__(page, controller)

        # The SettingsManager is accessed via the controller for all settings logic.
        self.settings_manager = self.controller.settings_manager


    def build(self) -> ft.Control:
        """
        Builds the settings UI using the safe 'colors' property from BaseView.

        Returns:
            ft.Control: The root container for the settings page.
        """
        # Use the safe 'self.colors' property, which is guaranteed to exist.
        colors = self.colors

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
                    # You can add other settings sections here following the same pattern.
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
        return ft.Column(
            [
                ft.Text("Appearance", theme_style=ft.TextThemeStyle.TITLE_LARGE),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.BRIGHTNESS_6, color=colors.primary),
                    title=ft.Text("Dark Mode"),
                    trailing=ft.Switch(
                        value=self.page.theme_mode == ft.ThemeMode.DARK,
                        # The on_change event calls the appropriate manager method.
                        on_change=lambda e: self.settings_manager.toggle_theme_mode(),
                    ),
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
        current_name = self.settings_manager.user_config.get_display_name() or ""
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
                self.settings_manager.save_display_name(new_name)
                self.controller.main_view.update_greeting()
                feedback_text.value = "Display name updated successfully."
                feedback_text.color = ft.colors.GREEN
                feedback_text.visible = True
                self.page.update()

        # Save button for display name
        save_button = ft.ElevatedButton(
            text="Save",
            on_click=lambda e: save_display_name(),
            style=ft.ButtonStyle(
                bgcolor=ft.colors.PRIMARY, color=ft.colors.ON_PRIMARY
            ),
        )
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
        current_color_name = self.settings_manager.theme_manager.color_name
        theme_manager = self.settings_manager.theme_manager

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
                    # The on_click event calls the appropriate manager method.
                    on_click=lambda e, c=color_name: self.settings_manager.change_theme_color(
                        c
                    ),
                    border_radius=8,
                    ink=True,
                    padding=8,
                )
            )
        return buttons
