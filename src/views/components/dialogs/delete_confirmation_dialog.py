import flet as ft
from typing import Callable, List
from .base_dialog import BaseDialog

class DeleteConfirmationDialog(BaseDialog):
    """A reusable dialog to confirm a delete action."""

    def __init__(self, page: ft.Page, item_name: str, item_type: str, on_confirm: Callable):
        self.on_confirm = on_confirm
        self.item_name = item_name
        self.item_type = item_type

        super().__init__(page=page, title=f"Confirm Deletion")

    def _build_content(self) -> List[ft.Control]:
        return [ft.Text(f"Are you sure you want to delete the {self.item_type} '{self.item_name}'?\nThis action cannot be undone.")]

    def _build_actions(self) -> List[ft.Control]:
        return [
            ft.TextButton("Cancel", on_click=self._close_dialog),
            ft.TextButton("Delete", on_click=self._handle_confirm, style=ft.ButtonStyle(color=ft.Colors.ERROR)),
        ]

    def _handle_confirm(self, e):
        self.on_confirm()
        self._close_dialog()