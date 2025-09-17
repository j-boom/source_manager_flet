import flet as ft
from typing import Callable, List
from .base_dialog import BaseDialog
from src.models.source_models import SourceRecord

class AddBoilerplateSourcesDialog(BaseDialog):
    """A dialog to select and add multiple boilerplate sources to a project."""

    def __init__(self, page: ft.Page, sources: List[SourceRecord], on_add: Callable[[List[str]], None]):
        self.sources = sources
        self.on_add = on_add
        self.checkboxes: List[ft.Checkbox] = []

        super().__init__(
            page=page,
            title="Add Boilerplate Sources",
            width=500,
            height=450
        )

    def _build_content(self) -> List[ft.Control]:
        self.checkboxes = [
            ft.Checkbox(label=source.display_name, data=source.id)
            for source in sorted(self.sources, key=lambda s: s.display_name)
        ]
        
        if not self.checkboxes:
            return [ft.Text("No boilerplate sources are available.")]

        return [ft.ListView(controls=self.checkboxes, expand=True, spacing=5)]

    def _build_actions(self) -> List[ft.Control]:
        add_button = ft.FilledButton("Add Selected", on_click=self._handle_add_clicked)
        if not self.checkboxes:
            add_button.disabled = True

        return [
            ft.TextButton("Cancel", on_click=self._close_dialog),
            add_button,
        ]

    def _handle_add_clicked(self, e):
        selected_ids = [cb.data for cb in self.checkboxes if cb.value]
        if selected_ids:
            self.on_add(selected_ids)
        self._close_dialog()

