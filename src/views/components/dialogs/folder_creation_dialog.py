"""
Folder Creation Dialog (Refactored)

A dialog component for creating new folders with real-time validation.
It follows a self-contained pattern, delegating logic to a callback.
"""

from pathlib import Path
from typing import Callable, List
import flet as ft
from .base_dialog import BaseDialog

class FolderCreationDialog(BaseDialog):
    """A dialog for collecting and validating a new folder's name."""

    def __init__(self, page: ft.Page, parent_path: Path, on_create: Callable[[str, str], None]):
        """
        Initializes the dialog.
        Args:
            page: The Flet Page object.
            parent_path: The directory where the new folder will be created.
            on_create: A callback to execute with (folder_name, description).
        """
        self.parent_path = parent_path
        self.on_create = on_create

        # --- UI Components with Validation ---
        self.folder_name_field = ft.TextField(
            label="Folder Name",
            hint_text="e.g., 1001234567 or a descriptive name",
            autofocus=True,
            on_submit=self._handle_create_clicked,
            on_change=self._validate_folder_name,
            width=400,
        )
        self.description_field = ft.TextField(
            label="Folder Description (optional)",
            hint_text="e.g., Project Description",
            width=400,
        )

        super().__init__(page=page, title="Create New Folder", width=450)

    def _build_content(self) -> List[ft.Control]:
        return [
            self.folder_name_field,
            self.description_field,
        ]

    def _build_actions(self) -> List[ft.Control]:
        return [
            ft.TextButton("Cancel", on_click=self._close_dialog),
            ft.FilledButton("Create Folder", on_click=self._handle_create_clicked),
        ]

    def _validate_folder_name(self, e: ft.ControlEvent):
        """Real-time validation for the folder name field."""
        name = e.control.value
        if not name or not name.strip():
            e.control.error_text = "Folder name cannot be empty."
        else:
            e.control.error_text = None
        e.control.update()

    def _handle_create_clicked(self, e):
        """Gathers form data, validates it, and calls the on_create callback."""
        folder_name = self.folder_name_field.value
        
        # Final validation check on submission
        if not folder_name or not folder_name.strip():
            self.folder_name_field.error_text = "Folder name cannot be empty."
            self.folder_name_field.update()
            return

        description = self.description_field.value or ""
        self.on_create(folder_name.strip(), description.strip())
        self._close_dialog()