"""
Project Metadata Tab (Refactored)

This tab displays and allows editing of project metadata, with a layout
dynamically generated from the project_types_config.
"""

import flet as ft
from collections import defaultdict
from typing import Dict, Any

from .base_tab import BaseTab
from config.project_types_config import get_metadata_fields, get_dialog_fields, create_field_widget, CollectionStage

class ProjectMetadataTab(BaseTab):
    """A tab for viewing and editing project metadata in a multi-column layout."""

    def __init__(self, controller):
        super().__init__(controller)
        self.is_edit_mode = False
        self.form_fields: Dict[str, ft.Control] = {}
        self.form_container = ft.Container(expand=True)

    def build(self) -> ft.Control:
        """Builds the initial content for the metadata tab."""
        self.action_button = ft.ElevatedButton(
            "Edit",
            icon=ft.icons.EDIT,
            on_click=self._on_action_button_click,
        )
        
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
        """Reconstructs the metadata form based on the current edit mode."""
        project = self.project_state_manager.current_project
        if not project:
            self.form_container.content = ft.Text("No project loaded.", italic=True)
            if self.page:
                self.page.update()
            return

        project_type_code = project.project_type.value
        
        # Extract data from the project's metadata structure
        # This creates a flat dictionary for form field access
        project_data = self._extract_form_data(project)

        metadata_fields = get_metadata_fields(project_type_code)
        dialog_fields = get_dialog_fields(project_type_code)
        
        # Show ALL fields except document_title which should remain hidden
        all_display_fields = {field.name: field for field in metadata_fields}
        for field in dialog_fields:
            if field.name != "document_title":  # Keep document_title hidden
                all_display_fields[field.name] = field
        
        grouped_fields = defaultdict(list)
        for field in all_display_fields.values():
            grouped_fields[field.column_group or "Project Metadata"].append(field)

        column_order = ["Facility Information", "Team", "Project Info"]
        
        form_columns = []
        
        # Filter out "Details" column and only show the three main columns
        sorted_group_names = [group for group in column_order if group in grouped_fields]

        for group_name in sorted_group_names:
            fields_in_group = grouped_fields[group_name]
            fields_in_group.sort(key=lambda f: (f.collection_stage.value, f.tab_order))

            column_controls = [
                ft.Text(group_name, weight=ft.FontWeight.BOLD, theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.Divider(height=5),
            ]
            
            for field_config in fields_in_group:
                current_value = project_data.get(field_config.name, "")
                widget = create_field_widget(field_config, str(current_value))
                
                # --- START OF CHANGES ---
                # Determine if the field should be editable based on your existing logic
                is_editable_field = (
                    field_config.name == "project_title" or 
                    field_config.collection_stage != CollectionStage.DIALOG
                )

                # Apply visual styles based on edit mode
                is_currently_editable = self.is_edit_mode and is_editable_field

                # Set disabled/read_only state
                if isinstance(widget, (ft.Checkbox, ft.Dropdown)):
                    widget.disabled = not is_currently_editable
                elif hasattr(widget, 'read_only'):
                    widget.read_only = not is_currently_editable

                # Set background color for editable fields
                if hasattr(widget, 'bgcolor'):
                    # Ensure the widget is styled to show the background color correctly
                    if isinstance(widget, (ft.TextField, ft.Dropdown)):
                        widget.filled = True
                        widget.border_color = "transparent"
                    
                    widget.bgcolor = ft.colors.TERTIARY_CONTAINER if is_currently_editable else None
                # --- END OF CHANGES ---

                # --- FIX: Handle different widget properties based on type ---
                # Special handling for project_title - should be editable in edit mode
                if field_config.name == "project_title":
                    if isinstance(widget, ft.Checkbox):
                        widget.disabled = not self.is_edit_mode
                    elif isinstance(widget, ft.Dropdown):
                        widget.disabled = not self.is_edit_mode
                    elif hasattr(widget, 'read_only'):
                        widget.read_only = not self.is_edit_mode
                elif field_config.collection_stage == CollectionStage.DIALOG:
                    # Other DIALOG fields remain read-only (be_number, facility_name, osuffix)
                    if isinstance(widget, ft.Checkbox):
                        widget.disabled = True
                    elif isinstance(widget, ft.Dropdown):
                        widget.disabled = True
                    elif hasattr(widget, 'read_only'):
                        widget.read_only = True
                else:
                    # Regular metadata fields follow edit mode
                    if isinstance(widget, ft.Checkbox):
                        widget.disabled = not self.is_edit_mode
                    elif isinstance(widget, ft.Dropdown):
                        widget.disabled = not self.is_edit_mode
                    elif hasattr(widget, 'read_only'):
                        widget.read_only = not self.is_edit_mode
                # --- END FIX ---

                self.form_fields[field_config.name] = widget
                column_controls.append(widget)

            form_columns.append(ft.Column(controls=column_controls, spacing=10, expand=True))

        self.form_container.content = ft.Container(
            content=ft.Row(
                controls=form_columns,
                vertical_alignment=ft.CrossAxisAlignment.START,
                spacing=20,
            ),
            padding=ft.padding.all(20),
        )
        if self.page:
            self.page.update()
                
    def _extract_form_data(self, project) -> Dict[str, Any]:
        """Extracts data from the project's new structure into a flat dictionary for form fields."""
        # Start with metadata dictionary which contains most fields
        form_data = project.metadata.copy() if project.metadata else {}
        
        # Add main project fields that are stored at the top level
        form_data["project_title"] = project.project_title
        form_data["project_type"] = project.project_type.value
        form_data["project_id"] = project.project_id
        
        return form_data
        
    def _on_action_button_click(self, e):
        """Handles clicks on the 'Edit' or 'Save' button."""
        if self.is_edit_mode:
            self._save_metadata()
            self.is_edit_mode = False
            self.action_button.text = "Edit"
            self.action_button.icon = ft.icons.EDIT
        else:
            self.is_edit_mode = True
            self.action_button.text = "Save"
            self.action_button.icon = ft.icons.SAVE
        
        self._rebuild_form()

    def _save_metadata(self):
        """Collects data from form fields and tells the controller to save it."""
        updated_data = {}
        for name, control in self.form_fields.items():
            # --- FIX: Check for 'disabled' on Checkbox and 'read_only' on other controls ---
            is_savable = False
            if isinstance(control, ft.Checkbox):
                # A checkbox is savable if it's not disabled.
                if not control.disabled:
                    is_savable = True
            elif hasattr(control, 'read_only'):
                # Other controls are savable if they are not read-only.
                if not control.read_only:
                    is_savable = True
            else:
                # If a control has neither property, assume it's savable.
                is_savable = True

            if is_savable and hasattr(control, "value"):
                if isinstance(control, ft.Checkbox):
                    updated_data[name] = bool(control.value)
                else:
                    updated_data[name] = control.value
        # --- END FIX ---
        
        if hasattr(self.controller, 'update_project_metadata'):
             self.controller.update_project_metadata(updated_data)
        
        self.page.snack_bar = ft.SnackBar(ft.Text("Project metadata saved!"), open=True)
        self.page.update()

    def update_project_data(self, project_data: Dict[str, Any], project_path: str):
        """Called by the parent view when the project changes."""
        self.is_edit_mode = False
        if hasattr(self, 'action_button'):
            self.action_button.text = "Edit"
            self.action_button.icon = ft.icons.EDIT

        self._rebuild_form()
