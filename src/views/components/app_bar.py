"""
AppBar Component

A custom AppBar for the application that displays a greeting and action buttons.
"""

import flet as ft
from typing import Callable


class AppBar(ft.AppBar):
    """A custom AppBar that extends ft.AppBar."""

    def __init__(
        self,
        greeting: str,
        on_settings_click: Callable,
        on_help_click: Callable,
        on_admin_click: Callable,
    ):
        """
        Initializes the AppBar.

        Args:
            greeting: The initial greeting text to display.
            on_settings_click: Callback function for when the settings icon is clicked.
            on_help_click: Callback function for when the help icon is clicked.
            on_admin_click: Callback function for when the admin access item is clicked
        """
        # This text control will hold the greeting message.
        self.title = ft.Text("Source Manager 2.0", size=20, weight=ft.FontWeight.BOLD)
        self.greeting_text = ft.Text(greeting, size=16)

        self.user_profile_button = ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(
                    text="Settings",
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    on_click=on_settings_click,
                ),
                ft.PopupMenuItem(),  # Divider
                ft.PopupMenuItem(
                    text="Admin Access",
                    icon=ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED,
                    on_click=on_admin_click,
                ),
            ],
            # Use a more descriptive icon for the user profile
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.PERSON_OUTLINE),
                    self.greeting_text,
                ],
                spacing=5,
            ),
        )

        # Call the parent constructor with all the AppBar properties.
        super().__init__(
            title=self.title,
            center_title=False,
            bgcolor=ft.Colors.PRIMARY_CONTAINER,  # A default color to prevent errors on init
            actions=[
                self.user_profile_button,
                ft.IconButton(
                    ft.Icons.HELP_OUTLINE, on_click=on_help_click, tooltip="Help"
                ),
                ft.Container(width=10),  # Right-side padding
            ],
        )

    def update_greeting(self, new_greeting: str):
        """Updates the greeting text displayed in the AppBar."""
        self.greeting_text.value = new_greeting
        # The .page attribute is automatically available when the control is added to a page.
        if self.page:
            self.page.update()
