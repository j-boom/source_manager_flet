"""
Project Creation Dialog (Refactored)

A dialog component for creating new projects. This component is now a "dumb"
view, responsible only for UI and delegating all logic to the AppController.
"""

import flet as ft
import logging
from pathlib import Path
from typing import Callable, Dict, Any, List

# Configuration for dynamic form generation
from .base_dialog import BaseDialog
from config import get_dialog_fields, get_project_type_display_names, create_field_widget
from config.project_types_config import validate_form_data


class ProjectCreationDialog(BaseDialog):
    """A dialog for collecting new project information dynamically."""

    def __init__(
        self, page: ft.Page, controller, parent_path: Path, on_close: Callable, initial_be_number: str = ""
    ):
        """
        Initializes the dialog.  Delegates most of the work to the Base Dialog
        """
        self.controller = controller
        self.parent_path = parent_path
        self.form_fields: Dict[str, ft.Control] = {}
        self.initial_be_number = initial_be_number  # Optional initial value for 'be_number'
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"ProjectCreationDialog initialized for path: {parent_path}")

        print(f"Initial BE Number: {self.initial_be_number}")
        # --- UI Components ---
        self.project_type_dropdown = self._build_project_type_dropdown()
        self.fields_container = ft.Column(spacing=15)

        super().__init__(
            page=page,
            title="Create New Project",
            on_close=on_close,
            width=600,
            height=500,  # Adjust size as needed
        )

    def _build_content(self) -> List[ft.Control]:
        """Constructs the list of controls for the dialog content."""
        return [
            self.project_type_dropdown,
            ft.Divider(height=1, thickness=1, color=ft.colors.OUTLINE),
            self.fields_container,
        ]

    def _build_actions(self) -> List[ft.Control]:
        return [
            ft.TextButton("Cancel", on_click=self._close_dialog),
            ft.FilledButton("Create Project", on_click=self._on_create_clicked),
        ]

    # --- UI Builder & Update Methods ---

    def _build_project_type_dropdown(self) -> ft.Dropdown:
        """Builds the project type dropdown with dynamic options."""
        project_types = get_project_type_display_names()
        return ft.Dropdown(
            label="Project Type",
            options=[
                ft.dropdown.Option(key=code, text=name)
                for code, name in project_types.items()
            ],
            on_change=self._on_project_type_change,
            autofocus=True,
        )

    def _update_form_fields(self, project_type_code: str):
        """
        Clears and rebuilds the form fields using only the fields
        configured for the 'dialog' collection stage.
        """
        self.form_fields.clear()
        self.fields_container.controls.clear()

        # Get ONLY the fields designated for the dialog stage from the config.
        dialog_fields = get_dialog_fields(project_type_code)

        # Create a widget for each field and add it to the form.
        for field_config in dialog_fields:
            widget = create_field_widget(field_config)
            self.form_fields[field_config.name] = widget
            self.fields_container.controls.append(widget)
            if field_config.name == "be_number":
                # If the field is 'be_number', set its initial value if provided
                widget.value = self.initial_be_number or ""
                widget.read_only = True
        self.page.update()

    # --- Event Handlers ---

    def _on_project_type_change(self, e: ft.ControlEvent):
        """Handles changes to the project type dropdown."""
        if e.control.value:
            self._update_form_fields(e.control.value)

    def _on_create_clicked(self, e: ft.ControlEvent):
        self.logger.info("Create button clicked - collecting form data")
        
        # Collect form data
        form_data = {}
        for name, control in self.form_fields.items():
            if hasattr(control, "value"):
                form_data[name] = control.value

        self.logger.debug(f"Collected form data: {form_data}")

        project_type = self.project_type_dropdown.value
        if not project_type:
            self.logger.warning("Project creation attempted without selecting project type")
            # Show error if no project type selected
            error_dialog = ft.AlertDialog(
                title=ft.Text("Project Type Required"),
                content=ft.Text("Please select a project type before creating the project."),
                actions=[
                    ft.TextButton("OK", on_click=lambda _: self.page.close(error_dialog))
                ],
            )
            self.page.open(error_dialog)
            return

        form_data["project_type"] = project_type
        self.logger.info(f"Project creation requested for type: {project_type}")

        # Validate the form data using the config validation rules
        is_valid, error_messages = validate_form_data(project_type, form_data)
        self.logger.debug(f"Form validation result: valid={is_valid}, errors={error_messages}")
        
        if not is_valid:
            self.logger.warning(f"Form validation failed: {error_messages}")
            # Show validation errors and keep dialog open for corrections
            error_text = "Please fix the following errors and try again:\n\n" + "\n".join(f"• {msg}" for msg in error_messages)
            
            # Create error dialog
            error_dialog = ft.AlertDialog(
                title=ft.Text("Validation Errors", weight=ft.FontWeight.BOLD),
                content=ft.Text(error_text, selectable=True),
                actions=[
                    ft.TextButton(
                        "OK", 
                        on_click=lambda _: self.page.close(error_dialog),
                        style=ft.ButtonStyle(color=ft.colors.PRIMARY)
                    )
                ],
            )
            self.page.open(error_dialog)
            # Dialog stays open - user can fix errors and try again
            return

        self.logger.info("Form validation passed - proceeding with project creation")
        
        # If validation passes, submit the project
        self.logger.debug("Calling controller to submit new project")
        self.controller.project_controller.create_project(
            parent_path=self.parent_path,
            project_type=project_type,
            form_data=form_data
        )
        self.logger.info("Project creation initiated - closing dialog")
        self._close_dialog()
        