import flet as ft
from typing import Dict, List
from .base_dialog import BaseDialog
from config.source_types_config import get_fields_for_source_type, SourceFieldConfig
from config.project_types_config import create_field_widget, FieldType
from models.source_models import SourceType

class _CompatibleFieldConfig:
    """A helper class to adapt SourceFieldConfig to what create_field_widget expects."""
    def __init__(self, source_field: SourceFieldConfig):
        self.name = source_field.name
        self.label = source_field.label
        self.field_type = FieldType[source_field.field_type.name]
        self.required = source_field.required
        self.hint_text = source_field.hint_text
        self.options = None
        self.width = 400

class SourceCreationDialog(BaseDialog):
    """A dialog for creating a new master source record."""
    
    def __init__(self, page: ft.Page, controller, on_close, target_country = None):
        self.controller = controller
        self.target_country = target_country  # If specified, create source for this country
        self.form_fields: Dict[str, ft.Control] = {}
        self.dynamic_fields_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
        self.source_type_dropdown = ft.Dropdown(
            label="Source Type",
            options=[ft.dropdown.Option(key=st.value, text=st.name.title()) for st in SourceType],
            on_change=self._on_source_type_change,
            autofocus=True,
        )
        
        super().__init__(
            page=page,
            title="Create New Master Source",
            on_close=on_close,
            width=450,
            height=400
        )

    def _build_content(self) -> List[ft.Control]:
        """Builds the content for the dialog, returning it as a list of controls."""
        self._populate_dynamic_fields(SourceType.BOOK.value)

        # --- FIX: Return a list containing the column to satisfy the BaseDialog ---
        return [
            self.source_type_dropdown,
            ft.Divider(),
            self.dynamic_fields_container
        ]

    def _build_actions(self) -> list:
        return [
            ft.TextButton("Cancel", on_click=self._close_dialog),
            ft.ElevatedButton("Create Source", on_click=self._on_submit),
        ]

    def _on_source_type_change(self, e):
        """Dynamically update the form fields when the source type changes."""
        self._populate_dynamic_fields(e.control.value)
        self.page.update()

    def _populate_dynamic_fields(self, source_type_value: str):
        """Clears and rebuilds the form fields based on the selected source type."""
        self.dynamic_fields_container.controls.clear()
        self.form_fields.clear()
        
        fields_to_create = get_fields_for_source_type(source_type_value)
        
        for field_config in fields_to_create:
            widget = create_field_widget(_CompatibleFieldConfig(field_config), "")
            self.form_fields[field_config.name] = widget
            self.dynamic_fields_container.controls.append(widget)

    def _on_submit(self, e):
        """Gathers data and passes it to the controller."""
        form_data = {name: getattr(control, 'value', '') for name, control in self.form_fields.items()}
        form_data["source_type"] = self.source_type_dropdown.value
        
        title_field = self.form_fields.get("title")
        if not form_data.get("title") and title_field:
            if hasattr(title_field, 'error_text'):
                title_field.error_text = "Title is required"
            self.page.update()
            return
        
        # Use target_country if specified, otherwise use project-based submission
        if self.target_country:
            self.controller.submit_new_source_for_country(self.target_country, form_data)
        else:
            self.controller.submit_new_source(form_data)
        
        self._close_dialog(e)

