import flet as ft
from typing import Callable, List
from .base_dialog import BaseDialog


class AddConfigTypeDialog(BaseDialog):
    """A reusable dialog for adding a new configuration type (like a source or project type)."""

    def __init__(self, page: ft.Page, title: str, on_create: Callable[[str, str], None]):
        self.on_create = on_create

        self.type_name_field = ft.TextField(
            label="Type Name (e.g., 'Book', 'IC Source')",
            autofocus=True,
            on_submit=self._handle_create_clicked,
        )

        super().__init__(page=page, title=title)

    def _build_content(self) -> List[ft.Control]:
        return [self.type_name_field]

    def _build_actions(self) -> List[ft.Control]:
        return [
            ft.TextButton("Cancel", on_click=self._close_dialog),
            ft.FilledButton("Create", on_click=self._handle_create_clicked),
        ]

    def _handle_create_clicked(self, e):
        """Sanitizes the name and calls the on_create callback."""
        display_name = self.type_name_field.value.strip()
        if not display_name:
            self.type_name_field.error_text = "Name cannot be empty."
            self.type_name_field.update()
            return

        # Generate the internal name for use as a key, while preserving the display name
        internal_name = display_name.lower().replace(" ", "_")

        self.on_create(display_name, internal_name)
        self._close_dialog()