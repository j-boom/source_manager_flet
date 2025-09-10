"""
Source Creation Dialog (Refactored)

A dialog component for creating new master source records with a dynamic form.
This version inherits from BaseDialog to ensure consistent behavior like scrolling.
"""

import flet as ft
import logging
from typing import Dict, List, Optional, Any, Callable

from .base_dialog import BaseDialog
from utils import create_validated_field, generate_source_title

class SourceCreationDialog(BaseDialog):
    """A dialog for creating a new master source record, with scrollable dynamic content."""

    def __init__(
        self,
        page: ft.Page,
        on_create: Callable[[Dict[str, Any]], None],
        available_countries: List[str],
        dialog_controller: "DialogController",
        source_types: Dict[str, Any] = None,
        target_country: Optional[str] = None,
        from_project_sources_tab: bool = False
    ):
        """
        Initializes the dialog.

        Args:
            page: The Flet Page object.
            on_create: A callback to execute with the validated source data.
            available_countries: A list of countries to populate the country dropdown.
            dialog_controller: The dialog controller.
            source_types: A dictionary of source types.
            target_country: The country to pre-select in the country dropdown.
            from_project_sources_tab: Flag to show project-specific fields.
        """
        self.on_create = on_create
        self.available_countries = available_countries
        self.dialog_controller = dialog_controller
        self.source_types = source_types
        self.target_country = target_country
        self.from_project_sources_tab = from_project_sources_tab
        self.form_fields: Dict[str, ft.Control] = {}
        self.logger = logging.getLogger(__name__)

        # --- UI Components ---
        self.source_type_dropdown = self._build_source_type_dropdown()
        self.country_dropdown = self._build_country_dropdown()
        
        # This container will hold the dynamically generated form fields.
        # The BaseDialog will make this scrollable.
        self.dynamic_fields_container = ft.Column(spacing=15)

        # Conditionally visible project-specific fields
        self.notes_field = ft.TextField(
            label="Usage Notes (for this project)", multiline=True, min_lines=2,
            visible=self.from_project_sources_tab
        )
        self.declassify_field = ft.TextField(
            label="Declassify Information (for this project)",
            visible=self.from_project_sources_tab
        )

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
        return [
            ft.Row([self.source_type_dropdown, self.country_dropdown], spacing=10),
            ft.Divider(height=1, thickness=1),
            self.dynamic_fields_container,
            self.notes_field,
            self.declassify_field,
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
            options=[ft.dropdown.Option(st, st.title()) for st in self.source_types.keys()],
            on_change=self._on_source_type_change,
            autofocus=True,
            expand=True,
            value=list(self.source_types.keys())[0] if self.source_types else None
        )

    def _build_country_dropdown(self) -> ft.Dropdown:
        options = [ft.dropdown.Option(c, c) for c in sorted(self.available_countries)]
        return ft.Dropdown(
            label="Country *",
            options=options,
            value=self.target_country if self.target_country else None,
            expand=True
        )

    def _populate_dynamic_fields(self, source_type_value: str):
        """Clears and rebuilds the form fields based on the selected source type."""
        self.form_fields.clear()
        self.dynamic_fields_container.controls.clear()
        fields_to_create = self.dialog_controller.get_source_type_fields(source_type_value)

        for s_config in fields_to_create:
            widget = create_validated_field(s_config)
            self.form_fields[s_config.get("name")] = widget
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
        if not self.country_dropdown.value:
            self.country_dropdown.error_text = "Country is required."
            is_valid = False
        else:
            self.country_dropdown.error_text = None

        if not self.source_type_dropdown.value:
            self.source_type_dropdown.error_text = "Source type is required."
            is_valid = False
        else:
            self.source_type_dropdown.error_text = None

        # Update UI to show/hide error messages
        self.country_dropdown.update()
        self.source_type_dropdown.update()

        if not is_valid:
            return

        # --- Data Collection ---
        form_data = {"source_type": self.source_type_dropdown.value, "country": self.country_dropdown.value}
        for name, control in self.form_fields.items():
            if hasattr(control, "value"):
                form_data[name] = control.value

        if self.from_project_sources_tab:
            form_data["usage_notes"] = self.notes_field.value
            form_data["declassify_info"] = self.declassify_field.value

        generated_title = generate_source_title(form_data["source_type"], form_data)
        form_data["title"] = generated_title

        self.logger.info("Validation passed. Executing on_create callback.")
        self.on_create(form_data)
        self._close_dialog()
