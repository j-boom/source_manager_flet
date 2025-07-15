import flet as ft
from dataclasses import dataclass
import logging
from typing import Dict, List, Optional, Any
from .base_dialog import BaseDialog
from config.source_types_config import get_fields_for_source_type, SourceFieldConfig
from config.project_types_config import create_field_widget, FieldType
from models.source_models import SourceType

@dataclass
class _CompatibleFieldConfig:
    """A helper class to adapt SourceFieldConfig to what create_field_widget expects."""
    field_name: str
    label: str
    field_type: FieldType
    required: bool = False
    options: Optional[List[str]] = None
    tooltip: Optional[str] = None
    validation_rules: Optional[Dict[str, Any]] = None
    def __init__(self, source_field: SourceFieldConfig):
        self.name = source_field.name
        self.label = source_field.label
        self.field_type = FieldType[source_field.field_type.name]
        self.required = source_field.required
        self.hint_text = source_field.hint_text
        self.options = None
        self.width = 400
        self.validation_rules: Optional[Dict[str, Any]] = None

class SourceCreationDialog(BaseDialog):
    """A dialog for creating a new master source record."""
    
    def __init__(self, page: ft.Page, controller, on_close, target_country=None, from_project_sources_tab: bool = False):
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing SourceCreationDialog")
        
        self.controller = controller
        self.target_country = target_country
        self.from_project_sources_tab = from_project_sources_tab
        self.logger.debug(f"Target country: {target_country}")
        
        self.form_fields: Dict[str, ft.Control] = {}
        self.dynamic_fields_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
        self.source_type_dropdown = ft.Dropdown(
            label="Source Type",
            options=[ft.dropdown.Option(key=st.value, text=st.name.title()) for st in SourceType],
            on_change=self._on_source_type_change,
            autofocus=True,
        )

        # Conditionally visible fields for when creating a source and adding it directly to a project
        self.notes_field = ft.TextField(label="Usage Notes", multiline=True, min_lines=3, visible=self.from_project_sources_tab)
        self.declassify_field = ft.TextField(label="Declassify Information", visible=self.from_project_sources_tab)
        
        self.logger.debug("SourceCreationDialog components initialized")
        
        super().__init__(
            page=page,
            title="Create New Master Source",
            on_close=on_close,
            width=450,
            height=500  # Increased height to accommodate new fields
        )

    def _build_content(self) -> List[ft.Control]:
        """Builds the content for the dialog, returning it as a list of controls."""
        self.logger.debug("Building dialog content")
        # Populate the default fields for the initial source type
        self._populate_dynamic_fields(SourceType.BOOK.value)

        # The content is a list of all controls for the dialog
        return [
            self.source_type_dropdown,
            ft.Divider(),
            self.dynamic_fields_container,
            # Add the notes and declassify fields which will be visible or not based on the flag
            self.notes_field,
            self.declassify_field,
        ]

    def _build_actions(self) -> list:
        """Builds the action buttons for the dialog."""
        return [
            ft.TextButton("Cancel", on_click=self._close_dialog),
            ft.ElevatedButton("Create Source", on_click=self._on_submit),
        ]

    def _on_source_type_change(self, e):
        """Dynamically update the form fields when the source type changes."""
        self.logger.info(f"Source type changed to: {e.control.value}")
        self._populate_dynamic_fields(e.control.value)
        self.page.update()

    def _populate_dynamic_fields(self, source_type_value: str):
        """Clears and rebuilds the form fields based on the selected source type."""
        self.logger.debug(f"Populating dynamic fields for source type: {source_type_value}")
        self.dynamic_fields_container.controls.clear()
        self.form_fields.clear()
        
        fields_to_create = get_fields_for_source_type(source_type_value)
        self.logger.debug(f"Fields to create: {[field.name for field in fields_to_create]}")
        
        for field_config in fields_to_create:
            widget = create_field_widget(_CompatibleFieldConfig(field_config), "")
            self.form_fields[field_config.name] = widget
            self.dynamic_fields_container.controls.append(widget)
            self.logger.debug(f"Added field widget to form: {field_config.name}")

    def _on_submit(self, e):
        """
        Gathers data from the dynamically generated form fields, passes it to the
        SourceController as a raw dictionary, and closes the dialog.
        """
        # --- 1. Gather Master SourceRecord Data from Dynamic Fields ---
        # We iterate through the controls dictionary created by the DynamicFormGenerator
        # to handle the dynamic nature of the form.
        
        source_data = {}
        for field_name, control in self.form_fields.items():
            # The key is the field name (e.g., 'title'), and the value is the Flet control
            source_data[field_name] = control.value

        # --- 2. Gather ProjectSourceLink Data (if applicable) ---
        # These fields are part of the dialog's static layout.
        link_data = None
        if self.from_project_sources_tab:
            # If adding to a project, the link data is required.
            if not self.notes_field.value or not self.declassify_field.value:
                self.controller.show_error_message("Usage Notes and Declassify Info are required when adding a source to a project.")
                return # Stop the submission if required fields are missing

            link_data = {
                "notes": self.notes_field.value,
                "declassify_info": self.declassify_field.value,
            }

        # --- 3. Call the Controller Method with the Raw Dictionaries ---
        self.controller.source.create_new_source(source_data, link_data)

        # --- 4. Close the Dialog ---
        self.close_dialog(e)