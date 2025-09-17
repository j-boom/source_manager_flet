"""
Source Creation Dialog (Refactored)

A dialog component for creating new master source records with a dynamic form.
This version inherits from BaseDialog to ensure consistent behavior like scrolling.
"""

import flet as ft
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field

from .base_dialog import BaseDialog
from utils import create_validated_field, generate_source_title, validate_field_value
from src.models.source_models import SourceFieldConfig
from src.models.project_models import FieldType, ValidationRule

@dataclass
class _CompatibleFieldConfig:
    """An adapter to make SourceFieldConfig compatible with create_validated_field."""
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
            field_type=FieldType(s_config.field_type),
            required=s_config.required,
            hint_text=s_config.hint_text,
            width=s_config.width,
            validation_rules=s_config.validation_rules,
        )

class SourceCreationDialog(BaseDialog):
    """A dialog for creating a new master source record, with scrollable dynamic content."""

    def __init__(
        self,
        page: ft.Page,
        on_create: Callable[[Dict[str, Any]], None],
        dialog_controller: "DialogController",
        source_types: Dict[str, Any] = None,
        available_countries: Optional[List[str]] = None,
        target_country: Optional[str] = None,
        from_project_sources_tab: bool = False,
        is_boilerplate: bool = False,
    ):
        """
        Initializes the dialog.

        Args:
            page: The Flet Page object.
            on_create: A callback to execute with the validated source data.
            dialog_controller: The dialog controller.
            source_types: A dictionary of source types.
            mode: The dialog mode, either "country" or "boilerplate".
            available_countries: A list of countries to populate the country dropdown.
            target_country: The country to pre-select in the country dropdown.
            from_project_sources_tab: Flag to show project-specific fields.
            is_boilerplate: Flag to configure the dialog for boilerplate source creation.
        """
        self.on_create = on_create
        self.dialog_controller = dialog_controller
        self.source_types = source_types
        self.available_countries = available_countries
        self.target_country = target_country
        self.is_boilerplate = is_boilerplate
        self.from_project_sources_tab = from_project_sources_tab
        self.form_fields: Dict[str, ft.Control] = {}
        self.field_configs: Dict[str, _CompatibleFieldConfig] = {}
        self.logger = logging.getLogger(__name__)

        # --- UI Components ---
        self.source_type_dropdown = self._build_source_type_dropdown()
        self.country_dropdown = self._build_country_dropdown()
        
        # This container will hold the dynamically generated form fields.
        # The BaseDialog will make this scrollable.
        self.dynamic_fields_container = ft.Column(spacing=15)

        # Initialize the BaseDialog superclass
        super().__init__(
            page=page,
            title="Create New Master Source",
            width=500,
            height=450  # Giving a fixed height is crucial for scrolling
        )
        
        # Populate initial fields after super().__init__ has run
        if self.source_type_dropdown.value:
            self._populate_dynamic_fields(self.source_type_dropdown.value)

    def _build_content(self) -> List[ft.Control]:
        """
        Builds the main content of the dialog, which will be placed
        inside the scrollable column of the BaseDialog.
        """
        row_controls = [self.source_type_dropdown]
        if not self.is_boilerplate:
            row_controls.append(self.country_dropdown)
        return [
            ft.Row(row_controls, spacing=10),
            ft.Divider(height=1, thickness=1),
            self.dynamic_fields_container,
        ]

    def _build_actions(self) -> List[ft.Control]:
        """Builds the action buttons for the dialog."""
        return [
            ft.TextButton("Cancel", on_click=self._close_dialog),
            ft.FilledButton("Create Source", on_click=self._handle_create_clicked),
        ]

    def _build_source_type_dropdown(self) -> ft.Dropdown:
        return ft.Dropdown(
            label="Source Type *",
            options=[
                ft.dropdown.Option(key=code, text=config.get("display_name", code.title()))
                for code, config in self.source_types.items()
            ],
            on_change=self._on_source_type_change,
            autofocus=True,
            expand=True,
            value=list(self.source_types.keys())[0] if self.source_types else None
        )

    def _build_country_dropdown(self) -> ft.Dropdown:
        options = [ft.dropdown.Option(c, c) for c in sorted(self.available_countries or [])]
        return ft.Dropdown(
            label="Country *",
            options=options,
            value=self.target_country if self.target_country else None,
            expand=True,
            visible=not self.is_boilerplate,
        )

    def _populate_dynamic_fields(self, source_type_value: str):
        """Clears and rebuilds the form fields based on the selected source type."""
        self.form_fields.clear()
        self.field_configs.clear()
        self.dynamic_fields_container.controls.clear()
        fields_to_create = self.dialog_controller.get_source_type_fields(source_type_value)

        # If creating a source outside of a project context (e.g., master library or boilerplate),
        # only show the core fields. Link-specific fields are only relevant when adding to a project.
        if not self.from_project_sources_tab:
            self.logger.info("Not in project context. Filtering for 'core' storage scope fields.")
            fields_to_create = [f for f in fields_to_create if f.get("storage_scope", "core") == "core"]

        # Sort fields based on the display_order property
        fields_to_create.sort(key=lambda f: f.get("display_order", 0))

        for s_config_dict in fields_to_create:
            # Only display fields that are marked to be shown in the editor
            if s_config_dict.get("show_in_editor", True):
                # Convert dict to a proper SourceFieldConfig object
                s_config_obj = SourceFieldConfig(**s_config_dict)
                # Adapt it to be compatible with the validator function
                compatible_config = _CompatibleFieldConfig.from_source_field_config(s_config_obj)

                widget = create_validated_field(compatible_config)
                self.form_fields[compatible_config.name] = widget
                self.field_configs[compatible_config.name] = compatible_config
                self.dynamic_fields_container.controls.append(widget)

        # Update the page if the dialog is already visible
        if self.dialog and self.dialog.open:
            self.page.update()

    def _on_source_type_change(self, e: ft.ControlEvent):
        """Dynamically update the form fields when the source type changes."""
        self.logger.info(f"Source type changed to: {e.control.value}")
        if e.control.value:
            self._populate_dynamic_fields(e.control.value)

    def _handle_create_clicked(self, e: ft.ControlEvent):
        """Gathers data, validates it, and calls the on_create callback."""
        is_valid = True
        if not self.is_boilerplate:
            if not self.country_dropdown.value:
                self.country_dropdown.error_text = "Country is required."
                is_valid = False
            else:
                self.country_dropdown.error_text = None
            self.country_dropdown.update()

        if not self.source_type_dropdown.value:
            self.source_type_dropdown.error_text = "Source type is required."
            is_valid = False
        else:
            self.source_type_dropdown.error_text = None
        self.source_type_dropdown.update()

        # --- Validate dynamic fields ---
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
            return

        # --- Data Collection ---
        form_data = {"source_type": self.source_type_dropdown.value}
        if not self.is_boilerplate:
            form_data["country"] = self.country_dropdown.value
        for name, control in self.form_fields.items():
            if hasattr(control, "value"):
                form_data[name] = control.value

        generated_title = generate_source_title(
            form_data["source_type"], form_data, self.dialog_controller.controller.admin_service
        )
        form_data["display_name"] = generated_title

        self.logger.info("Validation passed. Executing on_create callback.")
        self.on_create(form_data)
        self._close_dialog()
