"""
Source Editor Dialog (Refactored)

A dialog for editing a master source and its project-specific link data.
"""
import flet as ft
import logging
from typing import Dict, List, Optional, Any, Callable

from config.source_types_config import get_fields_for_source_type
from models.source_models import SourceRecord
from models.project_models import ProjectSourceLink
from utils.validators import create_validated_field

class SourceEditorDialog:
    """A dialog for viewing and editing a master source and its project-specific link data."""

    def __init__(
        self,
        page: ft.Page,
        source: SourceRecord,
        link: ProjectSourceLink,
        on_save: Callable[[str, Dict[str, Any], Dict[str, Any]], None],
    ):
        """
        Initializes the editor dialog.

        Args:
            page: The Flet Page object.
            source: The master source record to edit.
            link: The project-specific source link to edit.
            on_save: Callback to execute with (source_id, master_data, link_data).
        """
        self.page = page
        self.source = source
        self.link = link
        self.on_save = on_save
        self.dialog: Optional[ft.AlertDialog] = None
        self.master_form_fields: Dict[str, ft.Control] = {}
        self.logger = logging.getLogger(__name__)

        # --- UI Components for project-specific data ---
        self.notes_field = ft.TextField(
            label="Usage Notes (for this project)",
            value=self.link.notes or "",
            multiline=True,
            min_lines=3,
        )
        self.declassify_field = ft.TextField(
            label="Declassify Information (for this project)",
            value=self.link.declassify or "",
        )

    def show(self):
        """Builds and displays the dialog on the page."""
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Edit: {self.source.title}", size=20, weight=ft.FontWeight.BOLD),
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

        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()

    def _build_content(self) -> List[ft.Control]:
        """Builds the form content, pre-populated with the source's data."""
        self.logger.debug("Building editor content")
        self.master_form_fields.clear()

        # --- Build fields for the Master Source Record ---
        fields_to_create = get_fields_for_source_type(self.source.source_type.value)
        master_source_controls = []
        for field_config in fields_to_create:
            # Get the current value from the source model
            current_value = getattr(self.source, field_config.name, "")
            if isinstance(current_value, list):
                current_value = ", ".join(map(str, current_value))

            # Adapt config and create the widget using the centralized utility
            compatible_config = _CompatibleFieldConfig(field_config)
            widget = create_validated_field(compatible_config, str(current_value))

            self.master_form_fields[field_config.name] = widget
            master_source_controls.append(widget)

        # --- Combine all controls into a single list ---
        return [
            ft.Text("Master Source Details", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            *master_source_controls,
            ft.Divider(height=20),
            ft.Text("Project-Specific Details", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            self.notes_field,
            self.declassify_field,
        ]

    def _handle_save_clicked(self, e):
        """Gathers updated data and calls the on_save callback."""
        self.logger.info("Save Changes button clicked - collecting data.")

        # Gather data from master source form
        master_data = {
            name: control.value for name, control in self.master_form_fields.items()
        }
        # Gather data from project-specific link form
        link_data = {
            "notes": self.notes_field.value or "",
            "declassify": self.declassify_field.value or "",
        }

        self.logger.debug(f"Master data to save: {master_data}")
        self.logger.debug(f"Link data to save: {link_data}")

        # Execute the callback with all necessary data
        self.on_save(self.source.id, master_data, link_data)
        self._close()

    def _handle_close(self, e):
        self._close()

    def _close(self):
        """Closes the dialog."""
        if self.dialog:
            self.dialog.open = False
            self.page.update()