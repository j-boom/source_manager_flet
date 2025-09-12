import flet as ft
import logging
from typing import Dict, Any, Callable, List, Optional

from utils import create_validated_field, validate_field_value
from src.models.source_models import SourceFieldConfig
from .base_dialog import BaseDialog
from .source_creation_dialog import _CompatibleFieldConfig


class AddSourceToProjectDialog(BaseDialog):
    """A dialog to collect project-specific link data when adding an existing source to a project."""

    def __init__(
        self,
        page: ft.Page,
        source_type: str,
        dialog_controller: "DialogController",
        on_save: Callable[[Dict[str, Any]], None],
    ):
        self.source_type = source_type
        self.dialog_controller = dialog_controller
        self.on_save = on_save
        self.form_fields: Dict[str, ft.Control] = {}
        self.field_configs: Dict[str, _CompatibleFieldConfig] = {}

        self.fields_container = ft.Column(spacing=15, scroll=ft.ScrollMode.ADAPTIVE)

        super().__init__(page=page, title="Add Source to Project", width=500, height=400)

    def _build_content(self) -> List[ft.Control]:
        """Builds the form content with only project-specific fields."""
        self.form_fields.clear()
        self.field_configs.clear()
        self.fields_container.controls.clear()

        # This is now handled by the BaseDialog's scrollable column
        return self._get_link_fields()

    def _build_actions(self) -> List[ft.Control]:
        return [
            ft.TextButton("Cancel", on_click=self._close_dialog),
            ft.FilledButton("Add to Project", on_click=self._handle_save_clicked),
        ]

    def _get_link_fields(self) -> List[ft.Control]:
        all_fields = self.dialog_controller.get_source_type_fields(self.source_type)

        # Filter for link-specific fields only
        link_fields = [f for f in all_fields if f.get("storage_scope") == "link"]
        link_fields.sort(key=lambda f: f.get("display_order", 0))

        if not link_fields:
            return [ft.Text("This source type has no project-specific fields to configure.")]

        for field_data in link_fields:
            if field_data.get("show_in_editor", True):
                s_config_obj = SourceFieldConfig(**field_data)
                compatible_config = _CompatibleFieldConfig.from_source_field_config(s_config_obj)

                widget = create_validated_field(compatible_config)
                self.form_fields[compatible_config.name] = widget
                self.field_configs[compatible_config.name] = compatible_config
                self.fields_container.controls.append(widget)

        return self.fields_container.controls

    def _handle_save_clicked(self, e: ft.ControlEvent):
        """Gathers data, validates it, and calls the on_save callback."""
        is_valid = True
        for name, control in self.form_fields.items():
            field_config = self.field_configs.get(name)
            if field_config:
                is_valid_field, error_message = validate_field_value(field_config, control.value)
                if not is_valid_field:
                    control.error_text = error_message
                    is_valid = False
                else:
                    control.error_text = None
                control.update()

        if not is_valid:
            self.page.update()
            return

        link_data = {name: control.value for name, control in self.form_fields.items() if hasattr(control, "value")}

        self.logger.info("Validation passed. Executing on_save callback for AddSourceToProjectDialog.")
        self.on_save(link_data)
        self._close_dialog()