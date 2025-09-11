import flet as ft
from typing import Callable

class DeleteConfirmationDialog(ft.AlertDialog):
    """A reusable dialog to confirm a delete action."""

    def __init__(self, item_name: str, item_type: str, on_confirm: Callable):
        super().__init__()
        self.modal = True
        self.title = ft.Text(f"Confirm Deletion")
        self.content = ft.Text(f"Are you sure you want to delete the {item_type} '{item_name}'?\nThis action cannot be undone.")
        self.on_confirm = on_confirm

        self.actions = [
            ft.TextButton("Cancel", on_click=self._handle_close),
            ft.TextButton("Delete", on_click=self._handle_confirm, style=ft.ButtonStyle(color=ft.colors.ERROR)),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def _handle_confirm(self, e):
        self.on_confirm()
        self.open = False
        self.page.update()

    def _handle_close(self, e):
        self.open = False
        self.page.update()