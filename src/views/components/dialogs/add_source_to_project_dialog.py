import flet as ft
from typing import Callable
from .base_dialog import BaseDialog

class AddSourceToProjectDialog(BaseDialog):
    def __init__(self, page: ft.Page, on_save: Callable[[str, str], None]):
        self.on_save_callback = on_save
        self.notes_field = ft.TextField(label="Usage Notes", multiline=True, min_lines=3, autofocus=True)
        self.declassify_field = ft.TextField(label="Declassify Information")
        super().__init__(page=page, title="Add Source to Project", width=400)

    def _build_content(self) -> list[ft.Control]:
        return [
            self.notes_field,
            self.declassify_field,
        ]

    def _build_actions(self) -> list[ft.Control]:
        return [
            ft.TextButton("Cancel", on_click=self._close_dialog),
            ft.FilledButton("Save", on_click=self._save),
        ]

    def _save(self, e):
        notes = self.notes_field.value.strip()
        declassify = self.declassify_field.value.strip()

        self.on_save_callback(notes, declassify)
        self._close_dialog(e)