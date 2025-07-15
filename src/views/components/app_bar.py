"""
AppBar Component

A custom AppBar for the application that displays a greeting and action buttons.
"""

import flet as ft
from typing import Callable


class AppBar(ft.AppBar):
    """A custom AppBar that extends ft.AppBar."""

    def __init__(
        self, greeting: str, on_settings_click: Callable, on_help_click: Callable
    ):
        """
        Initializes the AppBar.

        Args:
            greeting: The initial greeting text to display.
            on_settings_click: Callback function for when the settings icon is clicked.
            on_help_click: Callback function for when the help icon is clicked.
        """
        # This text control will hold the greeting message.
        self.title = ft.Text("Source Manager 2.0", size=20, weight=ft.FontWeight.BOLD)
        self.greeting_text = ft.Text(greeting, size=16)

        # Call the parent constructor with all the AppBar properties.
        super().__init__(
            title=self.title,
            center_title=False,
            bgcolor=ft.colors.PRIMARY_CONTAINER,  # A default color to prevent errors on init
            actions=[
                ft.Container(
                    content=self.greeting_text, padding=ft.padding.only(right=16)
                ),  # Left-side greeting
                ft.IconButton(
                    ft.icons.SETTINGS_OUTLINED,
                    on_click=on_settings_click,
                    tooltip="Settings",
                ),
                ft.IconButton(
                    ft.icons.HELP_OUTLINE, on_click=on_help_click, tooltip="Help"
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
