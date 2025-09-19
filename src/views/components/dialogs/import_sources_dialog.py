import flet as ft
from typing import Callable, List, Tuple
from .base_dialog import BaseDialog

class ImportSourcesDialog(BaseDialog):
    """A dialog to import sources from another project."""

    def __init__(self, page: ft.Page, projects: List[Tuple[str, str]], on_import: Callable[[str], None]):
        self.projects = projects
        self.on_import = on_import
        self.project_dropdown = ft.Dropdown(
            label="Select Project to Import From",
            options=[ft.dropdown.Option(key=path, text=title) for title, path in projects],
            on_change=self._on_project_selected,
        )
        self.import_button = ft.FilledButton("Add to On Deck", on_click=self._handle_import_clicked, disabled=True)

        super().__init__(
            page=page,
            title="Import Sources from Another Project",
            width=500,
            height=250
        )

    def _build_content(self) -> List[ft.Control]:
        return [
            ft.Text("Select a project to add all of its sources to your 'On Deck' list."),
            self.project_dropdown,
        ]

    def _build_actions(self) -> List[ft.Control]:
        return [
            ft.TextButton("Cancel", on_click=self._close_dialog),
            self.import_button,
        ]

    def _on_project_selected(self, e):
        self.import_button.disabled = not e.control.value
        self.import_button.update()

    def _handle_import_clicked(self, e):
        selected_project_path = self.project_dropdown.value
        if selected_project_path:
            self.on_import(selected_project_path)
        self._close_dialog()