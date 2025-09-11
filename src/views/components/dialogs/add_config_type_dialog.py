import flet as ft
from typing import Callable


class AddConfigTypeDialog(ft.AlertDialog):
    """A reusable dialog for adding a new configuration type (like a source or project type)."""

    def __init__(self, title: str, on_create: Callable[[str], None]):
        super().__init__()
        self.modal = True
        self.title = ft.Text(title)
        self.on_create = on_create

        self.type_name_field = ft.TextField(
            label="Type Name (e.g., 'book', 'website')",
            autofocus=True,
            on_submit=self._handle_create_clicked,
        )

        self.content = self.type_name_field
        self.actions = [
            ft.TextButton("Cancel", on_click=self._handle_close),
            ft.FilledButton("Create", on_click=self._handle_create_clicked),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def _handle_create_clicked(self, e):
        """Sanitizes the name and calls the on_create callback."""
        type_name = self.type_name_field.value.strip().lower().replace(" ", "_")
        if not type_name:
            self.type_name_field.error_text = "Name cannot be empty."
            self.page.update()
            return

        self.on_create(type_name)
        self.open = False
        self.page.update()

    def _handle_close(self, e):
        self.open = False
        self.page.update()