"""
Admin Login Dialog
"""

import flet as ft
from typing import Callable

from .base_dialog import BaseDialog
from src.services.admin_auth_service import AdminAuthService


class AdminLoginDialog(BaseDialog):
    """A dialog to prompt for the admin password, conforming to BaseDialog."""

    def __init__(
        self,
        page: ft.Page,
        controller,
        on_login_success: Callable,
    ):
        """
        Initializes the AdminLoginDialog.

        Args:
            page: The Flet Page object.
            admin_auth_service: The service responsible for authentication logic.
            on_login_success: A callback to execute after successful authentication.
        """
        self.controller = controller
        self.admin_auth_service = self.controller.admin_auth_service
        self.on_login_success = on_login_success

        # --- UI Components ---
        self.password_field = ft.TextField(
            label="Admin Password",
            password=True,
            can_reveal_password=True,
            autofocus=True,
            on_submit=self._handle_login_clicked,
        )

        # Initialize the BaseDialog superclass
        super().__init__(page=page, title="Admin Access Required")

    def _build_content(self) -> list[ft.Control]:
        """
        Builds the main content for the dialog as required by BaseDialog.
        """
        return [
            ft.Text("Please enter the master admin password to continue."),
            self.password_field,
        ]

    def _build_actions(self) -> list[ft.Control]:
        """
        Builds the action buttons for the dialog as required by BaseDialog.
        """
        return [
            ft.TextButton("Cancel", on_click=self._close_dialog),
            ft.FilledButton("Login", on_click=self._handle_login_clicked),
        ]
    
    def _build_add_commands(self):
        pass

    def _handle_login_clicked(self, e):
        """
        Handles the login button click.
        Validates the password and triggers the success callback if valid.
        """
        password = self.password_field.value

        if self.admin_auth_service.authenticate_admin(password):
            self.on_login_success()
            self._close_dialog(e)  # Use the close method from BaseDialog
        else:
            self.password_field.error_text = "Incorrect password."
            self.password_field.update()
