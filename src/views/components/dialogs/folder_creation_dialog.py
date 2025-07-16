"""
Folder Creation Dialog (Refactored)

A dialog component for creating new folders with real-time validation.
It follows a self-contained pattern, delegating logic to a callback.
"""

from pathlib import Path
from typing import Callable
import flet as ft

class FolderCreationDialog:
    """A dialog for collecting and validating a new folder's name."""

    def __init__(self, page: ft.Page, parent_path: Path, on_create: Callable[[str, str], None]):
        """
        Initializes the dialog.

        Args:
            page: The Flet Page object.
            parent_path: The directory where the new folder will be created.
            on_create: A callback to execute with (folder_name, description).
        """
        self.page = page
        self.parent_path = parent_path
        self.on_create = on_create
        self.dialog: ft.AlertDialog | None = None

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

    def show(self):
        """Builds and displays the dialog on the page."""
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Create New Folder", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                [
                    self.folder_name_field,
                    self.description_field,
                ],
                spacing=15,
                tight=True,
                width=450
            ),
            actions=[
                ft.TextButton("Cancel", on_click=self._handle_close),
                ft.FilledButton("Create Folder", on_click=self._handle_create_clicked),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: self._close(),
        )

        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()

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
        self._close()

    def _handle_close(self, e):
        """Handler for the cancel button."""
        self._close()

    def _close(self):
        """Closes the dialog."""
        if self.dialog:
            self.dialog.open = False
            self.page.update()