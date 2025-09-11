import flet as ft
from typing import Callable, Optional, Dict, Any
from src.models.user_config_models import UserRole

class UserEditorDialog(ft.AlertDialog):
    """A dialog for adding a new user or editing an existing one."""

    def __init__(self, on_save: Callable, user_data: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.on_save = on_save
        self.user_data = user_data
        self.original_name = user_data.get("display_name") if user_data else None

        self.modal = True
        self.title = ft.Text("Edit User" if user_data else "Add New User")

        self.name_field = ft.TextField(
            label="Display Name",
            value=self.original_name or "",
            autofocus=True
        )
        self.role_dropdown = ft.Dropdown(
            label="Role",
            options=[ft.dropdown.Option(role.value, role.name.replace("_", " ").title()) for role in UserRole],
            value=user_data.get("role") if user_data else UserRole.USER.value
        )
        self.active_switch = ft.Switch(
            label="Active",
            value=user_data.get("is_active", True) if user_data else True
        )

        self.content = ft.Column([self.name_field, self.role_dropdown, self.active_switch], tight=True, spacing=15)
        self.actions = [
            ft.TextButton("Cancel", on_click=self._handle_close),
            ft.FilledButton("Save", on_click=self._handle_save)
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def _handle_save(self, e):
        new_name = self.name_field.value.strip()
        if not new_name:
            self.name_field.error_text = "Name cannot be empty."
            self.page.update()
            return
        
        updated_data = {"display_name": new_name, "role": self.role_dropdown.value, "is_active": self.active_switch.value}
        self.on_save(self.original_name, updated_data)
        self.open = False
        self.page.update()

    def _handle_close(self, e):
        self.open = False
        self.page.update()