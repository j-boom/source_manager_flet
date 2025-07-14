import flet as ft
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from .base_dialog import BaseDialog
from config import create_field_widget
from config.source_types_config import get_fields_for_source_type, SourceFieldConfig
from config.project_types_config import FieldType
from models.source_models import SourceRecord
from models.project_models import ProjectSourceLink # Import the link model

# Helper dataclass to make SourceFieldConfig compatible with create_field_widget
@dataclass
class _CompatibleFieldConfig:
    """A helper class to adapt SourceFieldConfig to what create_field_widget expects."""
    name: str
    label: str
    field_type: FieldType
    required: bool = False
    hint_text: str = ""
    options: Optional[List[str]] = None
    width: int = 400
    validation_rules: Optional[Dict[str, Any]] = None
    
    def __init__(self, source_field: SourceFieldConfig):
        self.name = source_field.name
        self.label = source_field.label
        self.field_type = FieldType[source_field.field_type.name]
        self.required = source_field.required
        self.hint_text = source_field.hint_text
        self.options = None
        self.width = 400
        self.validation_rules = None

class SourceEditorDialog(BaseDialog):
    """A dialog for viewing and editing a master source and its project-specific link data."""

    def __init__(self, page: ft.Page, controller, source: SourceRecord, link: ProjectSourceLink, on_close):
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing SourceEditorDialog for source: {source.title}")
        
        self.controller = controller
        self.source = source
        self.link = link  # Store the project-specific link object
        self.form_fields: Dict[str, ft.Control] = {}
        
        # --- Project-specific fields ---
        self.notes_field = ft.TextField(
            label="Usage Notes (for this project)",
            value=self.link.notes,
            multiline=True,
            min_lines=3
        )
        self.declassify_field = ft.TextField(
            label="Declassify Information (for this project)",
            value=self.link.declassify
        )
        
        # The BaseDialog's __init__ will call _build_content and _build_actions
        super().__init__(page, f"Edit: {source.title}", on_close, width=450, height=550) # Increased height

    def _build_content(self) -> List[ft.Control]:
        """Builds the form content, pre-populated with the source's data."""
        self.logger.debug("Building editor content")
        
        # --- Build fields for the Master Source Record ---
        fields_to_create = get_fields_for_source_type(self.source.source_type.value)
        master_source_controls = []
        for field_config in fields_to_create:
            current_value = getattr(self.source, field_config.name, "")
            if isinstance(current_value, list):
                current_value = ", ".join(current_value)
            
            compatible_config = _CompatibleFieldConfig(field_config)
            widget = create_field_widget(compatible_config, str(current_value))
            
            self.form_fields[field_config.name] = widget
            master_source_controls.append(widget)

        # --- Combine all controls ---
        content_controls = [
            ft.Text("Master Source Details", style=ft.TextThemeStyle.TITLE_MEDIUM),
            *master_source_controls,
            ft.Divider(height=20),
            ft.Text("Project-Specific Details", style=ft.TextThemeStyle.TITLE_MEDIUM),
            self.notes_field,
            self.declassify_field
        ]
            
        return content_controls

    def _build_actions(self) -> list:
        return [
            ft.TextButton("Cancel", on_click=self._close_dialog),
            ft.ElevatedButton("Save Changes", on_click=self._on_submit),
        ]

    def _on_submit(self, e):
        """Gathers updated data and passes it to the controller for both master and link."""
        self.logger.info("Save Changes button clicked - collecting updated data")
        
        # --- Separate the data for master source vs. project link ---
        master_source_data = {name: control.value for name, control in self.form_fields.items()}
        project_link_data = {
            "notes": self.notes_field.value,
            "declassify": self.declassify_field.value,
        }
        
        self.logger.debug(f"Master source data to update: {master_source_data}")
        self.logger.debug(f"Project link data to update: {project_link_data}")
        
        # --- Call controller methods to save both sets of data ---
        # 1. Update the master source record
        if hasattr(self.controller, "submit_source_update"):
            self.controller.submit_source_update(self.source.id, master_source_data)
        else:
            self.logger.error("Controller does not have submit_source_update method")

        # 2. Update the project-specific source link
        if hasattr(self.controller, "submit_project_source_link_update"):
            self.controller.submit_project_source_link_update(self.source.id, project_link_data)
        else:
            self.logger.error("Controller does not have submit_project_source_link_update method")

        self.logger.info("Source update initiated - closing dialog")
        self._close_dialog()
