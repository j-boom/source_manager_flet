import flet as ft
from typing import Dict, List
from .base_dialog import BaseDialog
from config import create_field_widget
from config.source_types_config import get_fields_for_source_type
from models.source_models import SourceRecord

class SourceEditorDialog(BaseDialog):
    """A dialog for viewing and editing an existing master source record."""

    def __init__(self, page: ft.Page, controller, source: SourceRecord, on_close: callable):
        self.controller = controller
        self.source = source
        self.form_fields: Dict[str, ft.Control] = {}
        
        # The BaseDialog's __init__ will call _build_content and _build_actions
        super().__init__(page, f"Edit: {source.title}", on_close, width=450, height=400)

    def _build_content(self) -> List[ft.Control]:
        """Builds the form content, pre-populated with the source's data."""
        fields_to_create = get_fields_for_source_type(self.source.source_type.value)
        
        content_controls = []
        for field_config in fields_to_create:
            # Get the existing value from the source object
            current_value = getattr(self.source, field_config.name, "")
            # Handle list values like 'authors' for display
            if isinstance(current_value, list):
                current_value = ", ".join(current_value)

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
        updated_data = {name: control.value for name, control in self.form_fields.items()}
        
        if hasattr(self.controller, "submit_source_update"):
            self.controller.submit_source_update(self.source.id, updated_data)
        
        self._close_dialog(e)
