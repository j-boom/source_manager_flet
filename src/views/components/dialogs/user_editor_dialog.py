import flet as ft
from typing import Callable, Optional, Dict, Any, List
from src.models.user_config_models import UserRole
from .base_dialog import BaseDialog

class UserEditorDialog(BaseDialog):
    """A dialog for adding a new user or editing an existing one."""

    def __init__(self, page: ft.Page, on_save: Callable, user_data: Optional[Dict[str, Any]] = None):
        self.on_save = on_save
        self.user_data = user_data
        self.original_name = user_data.get("display_name") if user_data else None

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

        super().__init__(page=page, title="Edit User" if user_data else "Add New User")

    def _build_content(self) -> List[ft.Control]:
        return [self.name_field, self.role_dropdown, self.active_switch]

    def _build_actions(self) -> List[ft.Control]:
        return [
            ft.TextButton("Cancel", on_click=self._close_dialog),
            ft.FilledButton("Save", on_click=self._handle_save)
        ]

    def _handle_save(self, e):
        new_name = self.name_field.value.strip()
        if not new_name:
            self.name_field.error_text = "Name cannot be empty."
            self.name_field.update()
            return
        
        updated_data = {"display_name": new_name, "role": self.role_dropdown.value, "is_active": self.active_switch.value}
        self.on_save(self.original_name, updated_data)
        self._close_dialog()