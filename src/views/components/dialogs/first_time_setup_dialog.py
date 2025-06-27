"""
First-time user setup dialog
"""

import flet as ft
from typing import Callable, Optional


class FirstTimeSetupDialog:
    """Dialog for collecting user information on first login"""

    def __init__(self, page: ft.Page, on_complete: Callable[[str], None]):
        self.page = page
        self.on_complete = on_complete
        self.dialog = None

        # Form fields
        self.display_name_field = ft.TextField(
            hint_text="What should I call you?",
            width=300,
            autofocus=True,
            on_submit=self._on_continue,
        )

        self.error_text = ft.Text(color=ft.colors.RED_400, size=14, visible=False)

    def show(self):
        """Show the setup dialog"""
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Welcome to Source Manager!", size=24, weight=ft.FontWeight.BOLD
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Welcome! Let's get you set up with a personalized experience.",
                            size=16,
                            color=ft.colors.GREY_600,
                        ),
                        ft.Container(height=20),
                        self.display_name_field,
                        self.error_text,
                        ft.Container(height=10),
                        ft.Text(
                            "This will be used for personalization throughout the app.  You can change it later in settings.",
                            size=12,
                            color=ft.colors.GREY_500,
                        ),
                    ],
                    tight=True,
                ),
                width=400,
                padding=20,
            ),
            actions=[
                ft.TextButton("Skip for now", on_click=self._on_skip),
                ft.ElevatedButton(
                    "Continue",
                    on_click=self._on_continue,
                    style=ft.ButtonStyle(
                        color=ft.colors.WHITE, bgcolor=ft.colors.BLUE_700
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()

    def _on_continue(self, e=None):
        """Handle continue button click"""
        display_name = (self.display_name_field.value or "").strip()

        if not display_name:
            self.error_text.value = "Please enter a display name"
            self.error_text.visible = True
            self.page.update()
            return

        if len(display_name) > 50:
            self.error_text.value = "Display name must be 50 characters or less"
            self.error_text.visible = True
            self.page.update()
            return

        self._close_dialog()
        self.on_complete(display_name)

    def _on_skip(self, e):
        """Handle skip button click"""
        self._close_dialog()
        self.on_complete("")  # Empty string indicates skipped

    def _close_dialog(self):
        """Close the dialog"""
        if self.dialog:
            self.dialog.open = False
            self.page.update()
