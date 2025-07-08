import flet as ft
from models import SourceRecord
# Import the new generator function
from utils.citation_generator import generate_citation

class SourceCitationDialog(ft.AlertDialog):
    """
    A dialog box that displays a formatted citation and all available metadata
    for a given source record.
    """
    def __init__(self, source: SourceRecord):
        super().__init__()
        self.modal = True
        self.title = ft.Text("Source Details")
        self.source = source
        self.content = self._build_content()
        self.actions = [
            ft.TextButton("Close", on_click=self._close_dialog)
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def _build_content(self) -> ft.Container:
        """Creates the main content of the dialog."""
        
        # --- NEW: Generate the formatted citation first ---
        formatted_citation = generate_citation(self.source)
        
        content_column = ft.Column(spacing=12, tight=True, scroll=ft.ScrollMode.ADAPTIVE)
        
        # --- NEW: Display the formatted citation at the top ---
        content_column.controls.append(
            ft.Text(
                value=formatted_citation, 
                weight=ft.FontWeight.BOLD, 
                italic=True,
                size=14
            )
        )
        content_column.controls.append(ft.Divider())
        content_column.controls.append(ft.Text("Raw Data:", weight=ft.FontWeight.BOLD))

        # Iterate through the raw source model attributes to display them
        for field_name, field_value in vars(self.source).items():
            if field_name.startswith('_') or not field_value:
                continue

            label = field_name.replace('_', ' ').title()
            
            if isinstance(field_value, list):
                value_str = ", ".join(map(str, field_value))
            else:
                value_str = str(field_value)

            content_column.controls.append(
                ft.Row([
                    ft.Text(f"{label}:", weight=ft.FontWeight.BOLD, width=120),
                    ft.Text(value_str, selectable=True, expand=True)
                ])
            )
            
        return ft.Container(
            content=content_column,
            width=500,
            padding=ft.padding.only(top=10)
        )

    def _close_dialog(self, e):
        """Closes the dialog."""
        self.open = False
        e.page.update()