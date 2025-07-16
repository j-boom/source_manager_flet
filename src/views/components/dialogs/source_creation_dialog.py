"""
Source Creation Dialog (Refactored)

A dialog component for creating new master source records with a dynamic form.
"""

import flet as ft
import logging
from typing import Dict, List, Optional, Any, Callable

from config.source_types_config import get_fields_for_source_type
from models.source_models import SourceType
from utils.validators import create_validated_field

class SourceCreationDialog:
    """A dialog for creating a new master source record."""

    def __init__(
        self,
        page: ft.Page,
        on_create: Callable[[Dict[str, Any]], None],
        available_countries: List[str],
        target_country: Optional[str] = None,
        from_project_sources_tab: bool = False
    ):
        """
        Initializes the dialog.

        Args:
            page: The Flet Page object.
            on_create: A callback to execute with the validated source data.
            available_countries: A list of countries to populate the region dropdown.
            target_country: The country to pre-select in the region dropdown.
            from_project_sources_tab: Flag to show project-specific fields.
        """
        self.page = page
        self.on_create = on_create
        self.available_countries = available_countries
        self.target_country = target_country
        self.from_project_sources_tab = from_project_sources_tab
        self.dialog: Optional[ft.AlertDialog] = None
        self.form_fields: Dict[str, ft.Control] = {}
        self.logger = logging.getLogger(__name__)

        # --- UI Components ---
        self.source_type_dropdown = self._build_source_type_dropdown()
        self.country_dropdown = self._build_country_dropdown()
        self.dynamic_fields_container = ft.Column(spacing=15, scroll=ft.ScrollMode.ADAPTIVE)

        # Conditionally visible project-specific fields
        self.notes_field = ft.TextField(
            label="Usage Notes (for this project)", multiline=True, min_lines=2,
            visible=self.from_project_sources_tab
        )
        self.declassify_field = ft.TextField(
            label="Declassify Information (for this project)",
            visible=self.from_project_sources_tab
        )

    def show(self):
        """Builds and displays the dialog on the page."""
        # Populate the dynamic fields for the initial selection before showing
        if self.source_type_dropdown.value:
            self._populate_dynamic_fields(self.source_type_dropdown.value)

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Create New Master Source", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                [
                    ft.Row([self.source_type_dropdown, self.country_dropdown], spacing=10),
                    ft.Divider(height=1, thickness=1),
                    self.dynamic_fields_container,
                    self.notes_field,
                    self.declassify_field,
                ],
                tight=True,
                width=500,
                height=450,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=self._handle_close),
                ft.FilledButton("Create Source", on_click=self._handle_create_clicked),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: self._close(),
        )

        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()

    def _build_source_type_dropdown(self) -> ft.Dropdown:
        return ft.Dropdown(
            label="Source Type *",
            options=[ft.dropdown.Option(st.value, st.name.title()) for st in SourceType],
            on_change=self._on_source_type_change,
            autofocus=True,
            expand=True
        )

    def _build_country_dropdown(self) -> ft.Dropdown:
        options = [ft.dropdown.Option(c, c) for c in sorted(self.available_countries)]
        return ft.Dropdown(
            label="Region/Country *",
            options=options,
            value=self.target_country if self.target_country else None,
            expand=True
        )

    def _populate_dynamic_fields(self, source_type_value: str):
        """Clears and rebuilds the form fields based on the selected source type."""
        self.form_fields.clear()
        self.dynamic_fields_container.controls.clear()
        fields_to_create = get_fields_for_source_type(source_type_value)

        for field_config in fields_to_create:
            # Use the centralized field creator for consistency and built-in validation
            widget = create_validated_field(field_config)
            self.form_fields[field_config.name] = widget
            self.dynamic_fields_container.controls.append(widget)

        if self.dialog and self.dialog.open:
            self.page.update()

    def _on_source_type_change(self, e: ft.ControlEvent):
        """Dynamically update the form fields when the source type changes."""
        self.logger.info(f"Source type changed to: {e.control.value}")
        if e.control.value:
            self._populate_dynamic_fields(e.control.value)

    def _handle_create_clicked(self, e: ft.ControlEvent):
        """Gathers data, validates it, and calls the on_create callback."""
        # --- Validation ---
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

        if not is_valid:
            self.country_dropdown.update()
            self.source_type_dropdown.update()
            return

        # --- Data Collection ---
        form_data = {"source_type": self.source_type_dropdown.value, "region": self.country_dropdown.value}
        for name, control in self.form_fields.items():
            if hasattr(control, "value"):
                form_data[name] = control.value

        if self.from_project_sources_tab:
            form_data["usage_notes"] = self.notes_field.value
            form_data["declassify_info"] = self.declassify_field.value

        # --- Execute Callback ---
        self.logger.info("Validation passed. Executing on_create callback.")
        self.on_create(form_data)
        self._close()

    def _handle_close(self, e):
        self._close()

    def _close(self):
        if self.dialog:
            self.dialog.open = False
            self.page.update()