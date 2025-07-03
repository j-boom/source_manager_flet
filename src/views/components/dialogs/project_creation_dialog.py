"""
Project Creation Dialog (Refactored)

A dialog component for creating new projects. This component is now a "dumb"
view, responsible only for UI and delegating all logic to the AppController.
"""

import flet as ft
from pathlib import Path
from typing import Callable, Dict, Any

# Configuration for dynamic form generation
from config.project_types_config import (
    get_project_type_config,
    get_project_type_display_names,
    create_field_widget,
)


class ProjectCreationDialog:
    """A dialog for collecting new project information dynamically."""

    def __init__(
        self, page: ft.Page, controller, parent_path: Path, on_close: Callable
    ):
        """
        Initializes the dialog.

        Args:
            page: The Flet Page object.
            controller: The main AppController instance.
            parent_path: The directory where the new project will be created.
            on_close: A callback function to execute when the dialog is closed.
        """
        self.page = page
        self.controller = controller
        self.parent_path = parent_path
        self.on_close = on_close

        # This will hold the dynamically generated form field controls
        self.form_fields: Dict[str, ft.Control] = {}

        # --- UI Components ---
        self.project_type_dropdown = self._build_project_type_dropdown()
        # This container will be populated with fields dynamically
        self.fields_container = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, spacing=15)

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
            title=ft.Text("Create New Project"),
            content=ft.Container(
                ft.Column(
                    [
                        self.project_type_dropdown,
                        ft.Divider(height=10, thickness=1),
                        self.fields_container,
                    ],
                    spacing=10,
                ),
                width=600,
                height=500,  # Adjust size as needed
            ),
            actions=[
                ft.TextButton("Cancel", on_click=self._on_cancel_clicked),
                ft.FilledButton("Create Project", on_click=self._on_create_clicked),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def _build_project_type_dropdown(self) -> ft.Dropdown:
        """Builds the dropdown for selecting a project type."""
        display_names = get_project_type_display_names()
        return ft.Dropdown(
            label="Project Type",
            hint_text="Select a type to see required fields",
            options=[
                ft.dropdown.Option(key=code, text=name)
                for code, name in display_names.items()
            ],
            on_change=self._on_project_type_change,
            autofocus=True,
        )

    def _update_form_fields(self, project_type_code: str):
        """Clears and rebuilds the form fields based on the selected project type."""
        self.form_fields.clear()
        self.fields_container.controls.clear()

        config = get_project_type_config(project_type_code)
        if not config:
            self.page.update()
            return

        # Use the helper function from the config to create widgets
        for field_config in config.fields:
            widget = create_field_widget(field_config)
            self.form_fields[field_config.name] = widget
            self.fields_container.controls.append(widget)

        self.page.update()

    # --- Event Handlers ---

    def _on_project_type_change(self, e: ft.ControlEvent):
        """Handles changes in the project type dropdown."""
        if e.control.value:
            self._update_form_fields(e.control.value)

    def _on_create_clicked(self, e: ft.ControlEvent):
        """
        Gathers form data and passes it to the controller for processing.
        The dialog itself does not perform validation or file creation.
        """
        form_data = {}
        for name, control in self.form_fields.items():
            if hasattr(control, "value"):
                form_data[name] = control.value

        # Add the selected project type to the data payload
        form_data["project_type"] = self.project_type_dropdown.value

        # Delegate the actual creation logic to the controller
        self.controller.submit_new_project(
            parent_path=self.parent_path, form_data=form_data
        )
        self._close_dialog()

    def _on_cancel_clicked(self, e: ft.ControlEvent):
        """Handles the cancel action."""
        self._close_dialog()

    def _close_dialog(self):
        """Closes the dialog and calls the on_close callback."""
        self.dialog.open = False
        self.page.update()
        if self.on_close:
            self.on_close()
