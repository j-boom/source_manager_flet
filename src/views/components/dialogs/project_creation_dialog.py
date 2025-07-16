"""
Project Creation Dialog (Refactored)

A dialog component for creating new projects. This component is now a "dumb"
view, responsible only for UI and delegating all logic to the AppController.
"""

import flet as ft
import logging
from pathlib import Path
from typing import Callable, Dict, Any, List, Optional

from config import get_dialog_fields, get_project_type_display_names
from utils.validators import create_validated_field, validate_form_data

class ProjectCreationDialog:
    """A dialog for collecting new project information dynamically."""

    def __init__(
        self,
        page: ft.Page,
        on_create: Callable[[Dict[str, Any]], None],
        initial_be_number: str = ""
    ):
        """
        Initializes the dialog.

        Args:
            page: The Flet Page object.
            on_create: A callback to execute with the validated form_data dictionary.
            initial_be_number: An optional initial value for the 'be_number' field.
        """
        self.page = page
        self.on_create = on_create
        self.initial_be_number = initial_be_number
        self.dialog: Optional[ft.AlertDialog] = None
        self.form_fields: Dict[str, ft.Control] = {}
        self.logger = logging.getLogger(__name__)

        # --- UI Components ---
        self.project_type_dropdown = self._build_project_type_dropdown()
        self.fields_container = ft.Column(spacing=15, scroll=ft.ScrollMode.ADAPTIVE)

    def show(self):
        """Builds and displays the dialog on the page."""
        # Update form with initial fields before showing
        if self.project_type_dropdown.value:
            self._update_form_fields(self.project_type_dropdown.value)

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Create New Project", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                [
                    self.project_type_dropdown,
                    ft.Divider(height=1, thickness=1),
                    self.fields_container,
                ],
                tight=True,
                width=600,
                height=450,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=self._handle_close),
                ft.FilledButton("Create Project", on_click=self._handle_create_clicked),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: self._close(),
        )

        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()

    def _build_project_type_dropdown(self) -> ft.Dropdown:
        """Builds the project type dropdown."""
        project_types = get_project_type_display_names()
        return ft.Dropdown(
            label="Project Type *",
            options=[
                ft.dropdown.Option(key=code, text=name)
                for code, name in project_types.items()
            ],
            on_change=self._on_project_type_change,
            autofocus=True,
        )

    def _update_form_fields(self, project_type_code: str):
        """Clears and rebuilds the dynamic form fields."""
        self.form_fields.clear()
        self.fields_container.controls.clear()
        dialog_fields = get_dialog_fields(project_type_code)

        for field_config in dialog_fields:
            initial_val = self.initial_be_number if field_config.name == "be_number" else ""
            widget = create_validated_field(field_config, initial_value=initial_val)

            if field_config.name == "be_number" and self.initial_be_number:
                widget.read_only = True # Make BE number read-only if pre-filled

            self.form_fields[field_config.name] = widget
            self.fields_container.controls.append(widget)

        if self.dialog and self.dialog.open:
            self.page.update()

    def _on_project_type_change(self, e: ft.ControlEvent):
        """Handles changes to the project type dropdown."""
        if e.control.value:
            self._update_form_fields(e.control.value)

    def _handle_create_clicked(self, e: ft.ControlEvent):
        """Validates the form and calls the on_create callback if successful."""
        self.logger.info("Create button clicked - collecting form data.")

        project_type = self.project_type_dropdown.value
        if not project_type:
            self.project_type_dropdown.error_text = "Please select a project type."
            self.project_type_dropdown.update()
            return
        else:
             self.project_type_dropdown.error_text = None
             self.project_type_dropdown.update()


        form_data = {"project_type": project_type}
        for name, control in self.form_fields.items():
            if hasattr(control, "value"):
                form_data[name] = control.value

        is_valid, errors = validate_form_data(project_type, form_data)
        if not is_valid:
            self.logger.warning(f"Form validation failed: {errors}")
            error_dialog = ft.AlertDialog(
                title=ft.Text("Validation Errors"),
                content=ft.Text("\n".join(errors)),
                actions=[ft.TextButton("OK", on_click=lambda _: self.page.close(error_dialog))]
            )
            self.page.open(error_dialog)
            return

        self.logger.info("Validation passed. Executing on_create callback.")
        self.on_create(form_data)
        self._close()

    def _handle_close(self, e):
        self._close()

    def _close(self):
        """Closes the dialog."""
        if self.dialog:
            self.dialog.open = False
            self.page.update()