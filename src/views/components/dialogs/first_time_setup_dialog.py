"""
First-time user setup dialog
"""

import flet as ft
from typing import Callable, Optional, List
from .base_dialog import BaseDialog


class FirstTimeSetupDialog(BaseDialog):
    """Dialog for collecting user information on first login"""

    def __init__(self, page: ft.Page, on_complete: Callable[[str], None]):
        self.on_complete = on_complete

        # Form fields
        self.display_name_field = ft.TextField(
            hint_text="What should I call you?",
            width=300,
            autofocus=True,
            on_submit=self._on_continue,
        )

        self.error_text = ft.Text(color=ft.Colors.RED_400, size=14, visible=False)

        super().__init__(
            page=page,
            title=ft.Text("Welcome to Source Manager!", size=24, weight=ft.FontWeight.BOLD),
            width=400
        )

    def _build_content(self) -> List[ft.Control]:
        return [
            ft.Text("Welcome! Let's get you set up with a personalized experience.", size=16, color=ft.Colors.GREY_600),
            ft.Container(height=20),
            self.display_name_field,
            self.error_text,
            ft.Container(height=10),
            ft.Text("This will be used for personalization throughout the app.  You can change it later in settings.", size=12, color=ft.Colors.GREY_500),
        ]

    def _build_actions(self) -> List[ft.Control]:
        return [
            ft.TextButton("Skip for now", on_click=self._on_skip),
            ft.ElevatedButton("Continue", on_click=self._on_continue, style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE_700)),
        ]

    def _on_continue(self, e=None):
        """Handle continue button click"""
        display_name = (self.display_name_field.value or "").strip()

        if not display_name:
            self.error_text.value = "Please enter a display name"
            self.error_text.visible = True
            self.error_text.update()
            return

        if len(display_name) > 50:
            self.error_text.value = "Display name must be 50 characters or less"
            self.error_text.visible = True
            self.error_text.update()
            return

        self._close_dialog()
        self.on_complete(display_name)

    def _on_skip(self, e):
        """Handle skip button click"""
        self._close_dialog()
        self.on_complete("")  # Empty string indicates skipped