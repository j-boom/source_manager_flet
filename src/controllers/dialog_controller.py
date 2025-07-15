import flet as ft
from typing import Callable, Optional, Dict, Any, TYPE_CHECKING
from .base_controller import BaseController
from src.views.components.dialogs import (
    ProjectCreationDialog,
    AddSourceToProjectDialog,
    SourceCreationDialog,
    SourceEditorDialog
)

if TYPE_CHECKING:
    from src.models.source_models import SourceRecord

class DialogController(BaseController):
    """
    Controller for handling the opening of all dialogs.
    """
    def open_dialog(self, dialog: ft.AlertDialog):
        """
        Helper method to open a dialog by adding it to the page overlay.
        """
        self.controller.page.overlay.append(dialog)
        dialog.open = True
        self.controller.page.update()

    def open_new_project_dialog(self, e):
        """Opens the new project creation dialog."""
        dialog = ProjectCreationDialog(controller=self.controller)
        self.open_dialog(dialog)

    def open_add_source_to_project_dialog(self, e):
        """Opens the dialog to add an existing source to the current project."""
        dialog = AddSourceToProjectDialog(controller=self.controller)
        self.open_dialog(dialog)

    def open_new_source_dialog(self, e, add_to_project: bool = False, initial_data: Optional[Dict[str, Any]] = None):
        """
        Opens the new source creation dialog, optionally pre-filling some data.
        """
        dialog = SourceCreationDialog(
            controller=self.controller, 
            add_to_project=add_to_project,
            initial_data=initial_data
        )
        self.open_dialog(dialog)

    def open_source_editor_dialog(self, source: "SourceRecord", on_close: Optional[Callable] = None):
        """
        Opens the source editor dialog for a given source.
        """
        dialog = SourceEditorDialog(
            controller=self.controller, 
            source=source, 
            on_close=on_close
        )
        self.open_dialog(dialog)
