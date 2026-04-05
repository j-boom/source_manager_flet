"""
Project Metadata Tab (Refactored)

This tab displays and allows editing of project metadata, with a layout
dynamically generated from the project_types_config.
"""
import logging
import flet as ft
from collections import defaultdict
from typing import Dict, Any

from .base_tab import BaseTab
from utils import create_validated_field


class ProjectMetadataTab(BaseTab):
    """A tab for viewing and editing project metadata in a multi-column layout."""

    def __init__(self, controller):
        super().__init__(controller)
        self.is_edit_mode = False
        self.form_fields: Dict[str, ft.Control] = {}
        self.form_container = ft.Container(expand=True)
        self.action_button = ft.ElevatedButton(
            "edit", icon=ft.Icons.EDIT, on_click=self._on_action_button_click
        )
        self.logger = logging.getLogger(__name__)

    def build(self) -> ft.Control:
        """
        Builds the initial content for the metadata tab, including the edit/save 
        button and the form container.

        Returns:
            ft.Control: The root column for the tab.
        """
        self._rebuild_form()

        return ft.Column(
            controls=[
                ft.Row([ft.Container(expand=True), self.action_button]),
                self.form_container,
            ],
            spacing=20,
            expand=True,
        )

    def _rebuild_form(self):
        """
        Reconstructs the metadata form based on the current edit mode and project type.
        Dynamically generates columns and fields, applies editability and visual styles.
        """
        project = self.project_state_manager.current_project
        if not project:
            # No project loaded: show a message
            self.form_container.content = ft.Text("No project loaded.", italic=True)
            if self.page:
                self.page.update()
            return

        project_type_code = project.project_type
        project_data = self._extract_form_data(project)

        # --- Get field definitions from the central configuration ---
        self.logger.info(f"Loading field definitions from global config for type '{project_type_code}'.")
        project_config = self.controller.project_controller.get_project_type_config(project_type_code)
        all_display_fields_list = project_config.get("fields", [])
        
        all_display_fields = {field.get("name"): field for field in all_display_fields_list}

        # Group fields by their column group for layout
        grouped_fields = defaultdict(list)
        for field in all_display_fields.values():
            grouped_fields[field.get("column_group", "Project Metadata")].append(field)

        # Only show the three main columns in this order
        column_order = ["Facility Information", "Team", "Project Info"]
        form_columns = []

        for group_name in column_order:
            if group_name not in grouped_fields:
                continue

            fields_in_group = sorted(grouped_fields[group_name], key=lambda f: f.get("tab_order", 0))

            # Start each column with a header and divider
            column_controls = [
                ft.Text(
                    group_name,
                    weight=ft.FontWeight.BOLD,
                    theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                ),
                ft.Divider(height=5),
            ]

            for field_config in fields_in_group:
                current_value = project_data.get(field_config.get("name"), "")
                # Create the appropriate widget for this field
                widget = create_validated_field(field_config, str(current_value))

                # Determine if the field should be editable in the current mode
                is_dialog_field = field_config.get("collection_stage") == "dialog"
                # Project title is a special case: it's a dialog field but should be editable
                is_editable = self.is_edit_mode and (not is_dialog_field or field_config.get("name") == "project_title")

                # Apply read-only/disabled state based on edit mode
                if isinstance(widget, (ft.Checkbox, ft.Dropdown)):
                    widget.disabled = not is_editable
                elif hasattr(widget, 'read_only'):
                    widget.read_only = not is_editable

                # Apply background color for fields
                if is_editable and hasattr(widget, 'bgcolor'):
                    widget.bgcolor = ft.Colors.TERTIARY_CONTAINER
                    if isinstance(widget, (ft.TextField, ft.Dropdown)):
                        widget.filled=True
                        widget.border_color = ft.Colors.TRANSPARENT
                
                self.form_fields[field_config.get("name")] = widget
                column_controls.append(widget)
                
            form_columns.append(ft.Column(controls=column_controls, spacing=10, expand=True))

        # Update the form container with the new layout
        self.form_container.content = ft.Container(
            content=ft.Row(
                controls=form_columns,
                spacing=20,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            padding=ft.padding.all(20),
        )

        if self.controller.page:
            self.controller.page.update()

    def _extract_form_data(self, project) -> Dict[str, Any]:
        """
        Extracts data from the project's structure into a flat dictionary for form fields.
        Includes both top-level and metadata fields.
        Args:
            project: The current project object.
        Returns:
            Dict[str, Any]: Flat dictionary of all form field values.
        """
        # Start with the dynamic metadata dictionary
        form_data = project.metadata.copy()
        
        # Overlay top-level, authoritative fields to ensure consistency.
        # This prevents stale data in the metadata dict from being shown.
        form_data['project_title'] = project.project_title
        
        return form_data

    def _on_action_button_click(self, e):
        """
        Handles clicks on the 'Edit' or 'Save' button.
        Switches between edit and view mode, and saves data if needed.
        """
        if self.is_edit_mode:
            # Save changes and switch to view mode
            self._save_metadata()
            self.is_edit_mode = False
            self.action_button.text = "Edit"
            self.action_button.icon = ft.Icons.EDIT
        else:
            # Switch to edit mode
            self.is_edit_mode = True
            self.action_button.text = "Save"
            self.action_button.icon = ft.Icons.SAVE

        self._rebuild_form()

    def _save_metadata(self):
        """
        Collects data from form fields and tells the controller to save it.
        Only saves fields that are editable in the current mode.
        """
        updated_data = {}
        for name, control in self.form_fields.items():
            if hasattr(control, 'value'):
                if isinstance(control, ft.Checkbox):
                    updated_data[name] = bool(control.value)
                else:
                    updated_data[name] = control.value
        
        # Delegate the update logic to the project controller
        self.controller.project_controller.update_project_metadata(updated_data)

    def update_project_data(self, project_data: Dict[str, Any], project_path: str):
        """
        Called by the parent view when the project changes.
        Resets the form to view mode and rebuilds the form for the new project.
        Args:
            project_data (Dict[str, Any]): The new project data.
            project_path (str): The path to the new project file.
        """
        self.logger.info(f"Updating project data for path: {project_path}")
        self.is_edit_mode = False
        if hasattr(self, "action_button"):
            self.action_button.text = "Edit"
            self.action_button.icon = ft.Icons.EDIT

        self._rebuild_form()