import flet as ft
import logging
from typing import Dict, List
from .base_dialog import BaseDialog
from config import create_field_widget
from config.source_types_config import get_fields_for_source_type
from models.source_models import SourceRecord

class SourceEditorDialog(BaseDialog):
    """A dialog for viewing and editing an existing master source record."""

    def __init__(self, page: ft.Page, controller, source: SourceRecord, on_close):
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing SourceEditorDialog for source: {source.title}")
        
        self.controller = controller
        self.source = source
        self.form_fields: Dict[str, ft.Control] = {}
        
        self.logger.debug(f"Source type: {source.source_type}")
        
        # The BaseDialog's __init__ will call _build_content and _build_actions
        super().__init__(page, f"Edit: {source.title}", on_close, width=450, height=400)

    def _build_content(self) -> List[ft.Control]:
        """Builds the form content, pre-populated with the source's data."""
        self.logger.debug("Building editor content")
        
        fields_to_create = get_fields_for_source_type(self.source.source_type.value)
        self.logger.debug(f"Fields to create: {[field.name for field in fields_to_create]}")
        
        content_controls = []
        for field_config in fields_to_create:
            # Get the existing value from the source object
            current_value = getattr(self.source, field_config.name, "")
            # Handle list values like 'authors' for display
            if isinstance(current_value, list):
                current_value = ", ".join(current_value)

            self.logger.debug(f"Creating field widget for {field_config.name} with value: {current_value}")
            widget = create_field_widget(field_config, str(current_value))
            self.form_fields[field_config.name] = widget
            content_controls.append(widget)
            
        return content_controls

    def _build_actions(self) -> list:
        return [
            ft.TextButton("Cancel", on_click=self._close_dialog),
            ft.ElevatedButton("Save Changes", on_click=self._on_submit),
        ]

    def _on_submit(self, e):
        """Gathers updated data and passes it to the controller."""
        self.logger.info("Save Changes button clicked - collecting updated data")
        
        updated_data = {name: control.value for name, control in self.form_fields.items()}
        self.logger.debug(f"Collected updated data: {updated_data}")
        
        if hasattr(self.controller, "submit_source_update"):
            self.logger.info(f"Submitting source update for source ID: {self.source.id}")
            self.controller.submit_source_update(self.source.id, updated_data)
        else:
            self.logger.error("Controller does not have submit_source_update method")
        
        self.logger.info("Source update initiated - closing dialog")
        self._close_dialog()
