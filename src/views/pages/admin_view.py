"""
Admin View

The user interface for managing dynamic application configurations like
project types and source types.
"""
import flet as ft
from src.views.base_view import BaseView

class AdminView(BaseView):
    """The UI for the administrator settings page."""

    def build(self) -> ft.Control:
        """Builds the UI for the admin view."""
        
        project_types_section = self._build_config_section(
            "Project Types",
            "Define the types of projects users can create, including their fields, validation, and naming patterns."
        )
        
        source_types_section = self._build_config_section(
            "Source Types",
            "Manage the templates for different kinds of sources, such as books, articles, or websites."
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Administrator Settings",
                        theme_style=ft.TextThemeStyle.HEADLINE_LARGE,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        "Modify the application's core configurations. Changes may require a restart to take full effect.",
                        italic=True,
                        color=ft.colors.ON_SURFACE_VARIANT
                    ),
                    ft.Divider(height=20),
                    project_types_section,
                    source_types_section,
                ],
                spacing=15,
                scroll=ft.ScrollMode.ADAPTIVE,
            ),
            padding=ft.padding.all(30),
            expand=True,
        )

    def _build_config_section(self, title: str, description: str) -> ft.Control:
        """Helper to create a consistent section for each configuration type."""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(title, theme_style=ft.TextThemeStyle.TITLE_LARGE),
                    ft.Text(description, color=ft.colors.ON_SURFACE_VARIANT),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                f"Manage {title}", 
                                icon=ft.icons.EDIT_NOTE,
                                on_click=lambda e, t=title: self._on_manage_click(t)
                            )
                        ],
                        alignment=ft.MainAxisAlignment.END
                    )
                ]),
                padding=20
            )
        )

    def _on_manage_click(self, config_type: str):
        """Placeholder for opening a detailed editor for a config type."""
        # In the next step, this will open a more detailed editing view or dialog.
        self.page.snack_bar = ft.SnackBar(
            ft.Text(f"Managing {config_type}... (Editor UI to be built)"),
            open=True
        )
        self.page.update()
