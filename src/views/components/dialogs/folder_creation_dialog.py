"""
Folder Creation Dialog (Refactored)

A dialog component for creating new folders. This component is now a "dumb"
view, responsible only for UI and delegating all logic to the AppController.
"""

from pathlib import Path
from typing import Callable, List
import flet as ft

from .base_dialog import BaseDialog


class FolderCreationDialog(BaseDialog):
    """A dialog for collecting a new folder's name and description."""

    def __init__(
        self, page: ft.Page, controller, parent_path: Path, on_close: Callable
    ):
        """
        Initializes the dialog.

        Args:
            page: The Flet Page object.
            controller: The main AppController instance.
            parent_path: The directory where the new folder will be created.
            on_close: A callback function to execute when the dialog is closed.
        """
        self.page = page
        self.controller = controller
        self.parent_path = parent_path
        self.on_close = on_close

        # --- UI Components ---
        self.folder_name_field = ft.TextField(
            label="Folder Name",
            hint_text="e.g., 1001234567 or a descriptive name",
            autofocus=True,
            on_submit=self._on_create_clicked,  # Allow creation on Enter key
        )
        self.description_field = ft.TextField(
            label="Folder Description (optional)", hint_text="e.g., Project Description"
        )

        super().__init__(
            page=page, title="Create New Folder", on_close=on_close, width=400
        )

    def _build_content(self) -> List[ft.Control]:
        """Builds the content of the dialog."""
        return [
            self.folder_name_field,
            self.description_field,
        ]

    def _build_actions(self) -> List[ft.Control]:
        """Builds the action buttons for the dialog."""
        return [
            ft.TextButton("Cancel", on_click=self._close_dialog),
            ft.FilledButton("Create Folder", on_click=self._on_create_clicked),
        ]

    def _on_create_clicked(self, e):
        """Gathers form data and passes it to the controller."""
        folder_name = self.folder_name_field.value
        description = self.description_field.value

        if folder_name:
            self.controller.submit_new_folder(
                parent_path=self.parent_path,
                folder_name=folder_name,
                description=description,
            )
            self._close_dialog()
        else:
            self.folder_name_field.error_text = "Folder name cannot be empty."
            self.page.update()
