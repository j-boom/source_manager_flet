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

        project_type_code = project.metadata.get("project_type")
        project_data = project.metadata

        metadata_fields = get_metadata_fields(project_type_code)
        dialog_fields = get_dialog_fields(project_type_code)
        
        all_display_fields = {field.name: field for field in metadata_fields}
        for field in dialog_fields:
            field.column_group = "Facility Information"
            all_display_fields[field.name] = field
        
        grouped_fields = defaultdict(list)
        for field in all_display_fields.values():
            grouped_fields[field.column_group or "Details"].append(field)

        column_order = ["Facility Information", "Team", "Project Request", "Details"]
        
        form_columns = []
        
        sorted_group_names = sorted(grouped_fields.keys(), key=lambda g: column_order.index(g) if g in column_order else len(column_order))

        for group_name in sorted_group_names:
            fields_in_group = grouped_fields[group_name]
            fields_in_group.sort(key=lambda f: (f.collection_stage.value, f.tab_order))

            column_controls = [
                ft.Text(group_name, weight=ft.FontWeight.BOLD, style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.Divider(height=5),
            ]
            
            for field_config in fields_in_group:
                current_value = project_data.get(field_config.name, "")
                
                widget = create_field_widget(field_config, str(current_value))
                
                # --- FIX: Handle Checkbox's 'disabled' property separately ---
                if field_config.collection_stage == CollectionStage.DIALOG:
                    if hasattr(widget, 'read_only'):
                        widget.read_only = True
                    elif isinstance(widget, ft.Checkbox):
                        widget.disabled = True
                elif isinstance(widget, ft.Checkbox):
                    widget.disabled = not self.is_edit_mode
                elif hasattr(widget, 'read_only'):
                    widget.read_only = not self.is_edit_mode
                # --- END FIX ---

                self.form_fields[field_config.name] = widget
                column_controls.append(widget)

            form_columns.append(ft.Column(controls=column_controls, spacing=10, expand=True))

        self.form_container.content = ft.Row(
            controls=form_columns,
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=20,
        )
        if self.page:
            self.page.update()

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
