import flet as ft
from models import SourceRecord
# Import the new generator function
from utils.citation_generator import generate_citation

class SourceCitationDialog(ft.AlertDialog):
    """
    A dialog box that displays a formatted citation and all available metadata
    for a given source record.
    """
    def __init__(self, source: SourceRecord, controller):
        super().__init__()
        self.modal = True
        self.title = ft.Text("Source Details")
        self.source = source
        self.controller = controller
        self.content = self._build_content()
        self.actions = [
            ft.TextButton("Close", on_click=self._close_dialog)
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def _build_content(self) -> ft.Container:
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
            
        return ft.Container(
            content=content_column,
            width=500,
            padding=ft.padding.only(top=10)
        )

    def _close_dialog(self, e):
        """Closes the dialog."""
        self.open = False
        self.page.update()