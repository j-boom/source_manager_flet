"""
Folder Creation Dialog (Refactored)

A dialog component for creating new folders. This component is now a "dumb"
view, responsible only for UI and delegating all logic to the AppController.
"""

import flet as ft
from pathlib import Path
from typing import Callable


class FolderCreationDialog:
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

        # The main dialog control
        self.dialog = self._build_dialog()

    def show(self):
        """Opens the dialog on the page."""
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()

    # --- UI Builder Methods ---

    def _build_dialog(self) -> ft.AlertDialog:
        """Constructs the main AlertDialog."""
        return ft.AlertDialog(
            modal=True,
            title=ft.Text("Create New Folder"),
            content=ft.Column(
                [
                    self.folder_name_field,
                    self.description_field,
                ],
                spacing=15,
                tight=True,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=self._on_cancel_clicked),
                ft.FilledButton("Create Folder", on_click=self._on_create_clicked),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    # --- Event Handlers ---

    def _on_create_clicked(self, e):
        """
        Gathers form data and passes it to the controller for processing.
        The dialog itself does not perform validation or file creation.
        """
        folder_name = self.folder_name_field.value
        description = self.description_field.value

        if folder_name:  # Basic check to ensure a name is provided
            # Delegate the actual creation logic to the controller
            self.controller.submit_new_folder(
                parent_path=self.parent_path,
                folder_name=folder_name,
                description=description,
            )
            self._close_dialog()
        else:
            self.folder_name_field.error_text = "Folder name cannot be empty."
            self.page.update()

    def _on_cancel_clicked(self, e):
        """Handles the cancel action."""
        self._close_dialog()

    def _close_dialog(self):
        """Closes the dialog and calls the on_close callback."""
        self.dialog.open = False
        self.page.update()
        if self.on_close:
            self.on_close()
