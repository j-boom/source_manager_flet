"""
Source Editor Dialog (Refactored)

A dialog for editing a master source and its project-specific link data.
"""
import flet as ft
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field

from src.models.source_models import SourceFieldConfig
from src.models.project_models import FieldConfig, ValidationRule, FieldType
from src.models.source_models import SourceRecord
from src.models.project_models import ProjectSourceLink
from utils.validators import create_validated_field

@dataclass
class _CompatibleFieldConfig:
    name: str
    label: str
    field_type: FieldType
    required: bool = False
    hint_text: str = ""
    validation_rules: Dict[ValidationRule, Any] = field(default_factory=dict)
    width: Optional[int] = None
    show_in_editor: bool = True
    options: Optional[List[str]] = None

    @classmethod
    def from_source_field_config(cls, s_config: SourceFieldConfig):
        return cls(
            name=s_config.name,
            label=s_config.label,
            field_type=FieldType(s_config.field_type), # Convert string to FieldType enum
            required=s_config.required,
            hint_text=s_config.hint_text,
            width=s_config.width,
            validation_rules=s_config.validation_rules,
        )

class SourceEditorDialog:
    """
A dialog for viewing and editing a master source and its project-specific link data.
"""

    def __init__(
        self,
        page: ft.Page,
        source: SourceRecord,
        link: ProjectSourceLink,
        on_save: Callable[[str, Dict[str, Any], Dict[str, Any]], None],
        admin_service: "AdminService",
    ):
        """
        Initializes the editor dialog.

        Args:
            page: The Flet Page object.
            source: The master source record to edit.
            link: The project-specific source link to edit.
            on_save: Callback to execute with (source_id, master_data, link_data).
            admin_service: The admin service instance.
        """
        self.page = page
        self.source = source
        self.link = link
        self.on_save = on_save
        self.dialog: Optional[ft.AlertDialog] = None
        self.admin_service = admin_service
        self.master_form_fields: Dict[str, ft.Control] = {}
        self.link_form_fields: Dict[str, ft.Control] = {}
        self.field_configs: Dict[str, _CompatibleFieldConfig] = {}
        self.logger = logging.getLogger(__name__)

    def show(self):
        """
Builds and displays the dialog on the page.
"""
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Edit: {self.source.get_title()}", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                self._build_content(),
                tight=True,
                width=500,
                height=550,
                scroll=ft.ScrollMode.ADAPTIVE
            ),
            actions=[
                ft.TextButton("Cancel", on_click=self._handle_close),
                ft.FilledButton("Save Changes", on_click=self._handle_save_clicked),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: self._close(),
        )

        if self.dialog not in self.page.overlay:
            self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()

    def _build_content(self) -> List[ft.Control]:
        """
Builds the form content, pre-populated with the source's data.
"""
        self.logger.debug("Building editor content")
        self.master_form_fields.clear()
        self.link_form_fields.clear()
        self.field_configs.clear()

        all_source_types = self.admin_service.get_source_types()
        source_type_config = all_source_types.get(self.source.source_type, {})
        
        # Get all field definitions and filter them based on the 'show_in_editor' flag
        all_fields_data = source_type_config.get("fields", [])
        visible_fields_data = [f for f in all_fields_data if f.get("show_in_editor", True)]
        
        # Separate fields by their storage scope
        core_fields_data = [f for f in visible_fields_data if f.get("storage_scope", "core") == "core"]
        link_fields_data = [f for f in visible_fields_data if f.get("storage_scope") == "link"]

        # Sort each list by the display_order property
        core_fields_data.sort(key=lambda f: f.get("display_order", 0))
        link_fields_data.sort(key=lambda f: f.get("display_order", 0))

        master_source_controls = []
        for field_data in core_fields_data:
            field_config = SourceFieldConfig(**field_data)
            # Get the current value from the source model
            current_value = self.source.get_field_value(field_config.name, "")
            if isinstance(current_value, list):
                current_value = ", ".join(map(str, current_value))

            # Adapt config and create the widget using the centralized utility
            compatible_config = _CompatibleFieldConfig.from_source_field_config(field_config)
            widget = create_validated_field(compatible_config, str(current_value))

            self.master_form_fields[field_config.name] = widget
            self.field_configs[field_config.name] = compatible_config
            master_source_controls.append(widget)
            
        link_source_controls = []
        for field_data in link_fields_data:
            field_config = SourceFieldConfig(**field_data)
            # Get the current value from the link's metadata
            current_value = self.link.metadata.get(field_config.name, "")
            if isinstance(current_value, list):
                current_value = ", ".join(map(str, current_value))
            
            compatible_config = _CompatibleFieldConfig.from_source_field_config(field_config)
            widget = create_validated_field(compatible_config, str(current_value))
            
            self.link_form_fields[field_config.name] = widget
            self.field_configs[field_config.name] = compatible_config # Also store for validation
            link_source_controls.append(widget)

        # --- Combine all controls into a single list ---
        return [
            ft.Text("Master Source Details", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            *master_source_controls,
            ft.Divider(height=20),
            ft.Text("Project-Specific Details", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            *link_source_controls,
        ]

    def _handle_save_clicked(self, e):
        """
Gathers updated data, validates it, and calls the on_save callback.
"""
        self.logger.info("Save Changes button clicked - validating and collecting data.")
        is_valid = True

        # --- Validate dynamic fields ---
        all_form_fields = {**self.master_form_fields, **self.link_form_fields}
        for name, control in all_form_fields.items():
            config = self.field_configs.get(name)
            if config and config.required and not control.value:
                control.error_text = f"{config.label} is required."
                is_valid = False
            else:
                control.error_text = None
            control.update()

        if not is_valid:
            self.page.update() # Update the page to show all error texts
            return

        # Gather data from master source form
        master_data = {
            name: control.value for name, control in self.master_form_fields.items()
        }
        # Gather data from project-specific link form
        link_data = {
            name: control.value for name, control in self.link_form_fields.items()
        }

        self.logger.debug(f"Master data to save: {master_data}")
        self.logger.debug(f"Link data to save: {link_data}")

        # Execute the callback with all necessary data
        self.on_save(self.source.id, master_data, link_data)
        self._close()

    def _handle_close(self, e):
        self._close()

    def _close(self):
        """
Closes the dialog.
"""
        if self.dialog:
            self.dialog.open = False
            self.page.update()