import flet as ft
from models import SourceRecord
# Import the new generator function
from utils.citation_generator import generate_citation
from .base_dialog import BaseDialog
from typing import List

class SourceCitationDialog(BaseDialog):
    """
    A dialog box that displays a formatted citation and all available metadata
    for a given source record.
    """
    def __init__(self, page: ft.Page, source: SourceRecord, controller):
        self.source = source
        self.controller = controller

        super().__init__(page=page, title="Source Details", width=500)

    def _build_content(self) -> List[ft.Control]:
        """Creates the main content of the dialog."""
        
        # --- Generate the formatted citation first ---
        formatted_citation = generate_citation(self.source, self.controller)
        
        content_column = ft.Column(spacing=12, tight=True, scroll=ft.ScrollMode.ADAPTIVE)
        
        # --- Display the formatted citation at the top ---
        content_column.controls.append(
            ft.Text(
                value=formatted_citation, 
                weight=ft.FontWeight.BOLD, 
                italic=True,
                size=14,
                selectable=True
            )
        )
        content_column.controls.append(ft.Divider())
        content_column.controls.append(ft.Text("Raw Data:", weight=ft.FontWeight.BOLD))

        # --- Create a two-column layout for raw data ---
        # Sort fields by label for consistent order
        for field in sorted(self.source.fields, key=lambda f: f.label or f.name):
            if not field.value:
                continue

            label = field.label or field.name.replace('_', ' ').title()

            if isinstance(field.value, list):
                value_str = ", ".join(map(str, field.value))
            else:
                value_str = str(field.value)
            # Create a row for each field: [Label] [Value]
            field_row = ft.Row(
                controls=[
                    ft.Text(f"{label}:", weight=ft.FontWeight.BOLD, width=150),
                    ft.Text(value_str, selectable=True, expand=True),
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
            content_column.controls.append(field_row)
            
        return [content_column]

    def _build_actions(self) -> List[ft.Control]:
        return [
            ft.TextButton("Close", on_click=self._close_dialog)
        ]