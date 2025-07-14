import flet as ft
from typing import Callable

class AddSourceToProjectDialog(ft.AlertDialog):
    def __init__(self, on_save: Callable[[str, str], None]):
        super().__init__()
        self.modal = True
        self.title = ft.Text("Add Source to Project")
        self.on_save = on_save

        self.notes_field = ft.TextField(label="Usage Notes", multiline=True, min_lines=3, autofocus=True)
        self.declassify_field = ft.TextField(label="Declassify Information")

        self.content = ft.Column([
            self.notes_field,
            self.declassify_field,
        ], spacing=15, width=400)

        self.actions = [
            ft.TextButton("Cancel", on_click=self._close),
            ft.FilledButton("Save", on_click=self._save),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def _save(self, e):
        notes = self.notes_field.value.strip()
        declassify = self.declassify_field.value.strip()

        if not notes or not declassify:
            if not notes:
                self.notes_field.error_text = "Notes are required."
            if not declassify:
                self.declassify_field.error_text = "Declassify information is required."
            self.page.update()
            return

        self.on_save(notes, declassify)
        self._close(e)

    def _close(self, e):
        self.open = False
        self.page.update()