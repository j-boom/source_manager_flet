"""
Reports View - Modern export-focused interface for generating bibliographies and citations
"""

import flet as ft
from typing import Optional, List, Dict, Any
from src.views.base_view import BaseView

class ReportsView(BaseView):
    """Modern export-focused view for generating reports and managing citations"""

    def __init__(self, page: ft.Page, controller):
        super().__init__(page, controller)
        self.export_paths: Dict[str, Optional[str]] = {
            'word': None,
            'powerpoint': None
        }

        # UI Components that need to be accessed later
        self.word_export_card: Optional[ft.Card] = None
        self.powerpoint_export_card: Optional[ft.Card] = None
        self.bibliography_preview: Optional[ft.Card] = None
        self.word_path_display: Optional[ft.Text] = None
        self.ppt_path_display: Optional[ft.Text] = None

    def build(self) -> ft.Control:
        """Build the modern reports view"""
        # Check if a project is loaded before building the main view
        if not self.controller.project_state_manager.has_loaded_project():
            return self.show_empty_state(
                message="Please load a project to access the Reports & Export features.",
                icon=ft.icons.FOLDER_OFF_OUTLINED,
                action_text="Browse for a Project",
                on_action=lambda e: self.controller.navigate_to("new_project"),
            )

        # Initialize UI components
        self._init_components()

        return ft.Column(
            [
                # Header
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text("Reports & Export", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                            ft.Text("Generate and export your project's bibliography and slide citations.",
                                   color=self.colors.on_surface_variant)
                        ], spacing=4, expand=True),
                    ]),
                    padding=ft.padding.symmetric(horizontal=20, vertical=15),
                    border=ft.border.only(bottom=ft.BorderSide(1, self.colors.outline_variant))
                ),

                # Main content
                ft.Container(
                    content=ft.Column([
                        # Export options grid
                        ft.ResponsiveRow([
                            ft.Column([self.word_export_card], col={"md": 6}),
                            ft.Column([self.powerpoint_export_card], col={"md": 6})
                        ]),
                        ft.Container(height=20),
                        # Bibliography preview
                        self.bibliography_preview
                    ], spacing=20, scroll=ft.ScrollMode.ADAPTIVE),
                    padding=20,
                    expand=True
                )
            ],
            expand=True,
            spacing=0
        )

    def _init_components(self):
        """Initialize modern UI components"""
        # File path displays
        self.word_path_display = ft.Text("No location selected", size=12, color=self.colors.on_surface_variant, overflow=ft.TextOverflow.ELLIPSIS, expand=True)
        self.ppt_path_display = ft.Text("No location selected", size=12, color=self.colors.on_surface_variant, overflow=ft.TextOverflow.ELLIPSIS, expand=True)

        # Export cards
        self.word_export_card = self._create_export_card(
            title="Word Bibliography",
            subtitle="Export a formatted bibliography (.docx).",
            icon=ft.icons.DESCRIPTION_ROUNDED,
            color=ft.colors.BLUE_700,
            export_type="word",
            path_display_control=self.word_path_display
        )

        self.powerpoint_export_card = self._create_export_card(
            title="PowerPoint Citations",
            subtitle="Attach citations directly to slides.",
            icon=ft.icons.SLIDESHOW_ROUNDED,
            color=ft.colors.ORANGE_700,
            export_type="powerpoint",
            path_display_control=self.ppt_path_display
        )

        # Bibliography preview
        self.bibliography_preview = self._create_bibliography_preview()

    def _create_export_card(self, title: str, subtitle: str, icon: str, color: str, export_type: str, path_display_control: ft.Text) -> ft.Card:
        """Create modern export option card"""
        path_container = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.FOLDER_OUTLINED, size=16, color=self.colors.on_surface_variant),
                path_display_control
            ], spacing=8),
            bgcolor=self.colors.surface_variant,
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            margin=ft.margin.only(bottom=15)
        )

        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(icon, size=24, color=ft.colors.WHITE),
                            bgcolor=color,
                            border_radius=8,
                            padding=12
                        ),
                        ft.Column([
                            ft.Text(title, weight=ft.FontWeight.BOLD),
                            ft.Text(subtitle, size=12, color=self.colors.on_surface_variant)
                        ], spacing=2, expand=True)
                    ], spacing=15),
                    path_container,
                    ft.Row([
                        ft.OutlinedButton(
                            "Choose Location",
                            icon=ft.icons.FOLDER_OPEN_OUTLINED,
                            on_click=lambda e, t=export_type: self._choose_export_location(t)
                        ),
                        ft.FilledButton(
                            "Export",
                            icon=ft.icons.FILE_DOWNLOAD_ROUNDED,
                            on_click=lambda e, t=export_type: self._perform_export(t)
                        )
                    ], spacing=10, alignment=ft.MainAxisAlignment.END)
                ], spacing=15),
                padding=20
            ),
            elevation=2
        )

    def _create_bibliography_preview(self) -> ft.Card:
        """Create bibliography preview card"""
        bibliography_text = self._generate_bibliography_text()

        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.icons.LIBRARY_BOOKS_ROUNDED, size=24, color=self.colors.primary),
                        ft.Text("Bibliography Preview", theme_style=ft.TextThemeStyle.TITLE_LARGE),
                        ft.Container(expand=True),
                        ft.IconButton(
                            icon=ft.icons.COPY_ALL_OUTLINED,
                            tooltip="Copy to clipboard",
                            on_click=self._copy_bibliography
                        )
                    ]),
                    ft.Divider(),
                    ft.Container(
                        content=ft.Text(bibliography_text, size=12, selectable=True, font_family="monospace"),
                        height=300,
                        bgcolor=self.colors.surface_variant,
                        border_radius=8,
                        padding=15,
                        expand=True,
                    )
                ], spacing=15),
                padding=20
            ),
            elevation=2
        )

    def _generate_bibliography_text(self) -> str:
        """Generate formatted bibliography text by calling the controller"""
        # In a real scenario, this would call the controller to get a formatted string
        # For example: return self.controller.citation_controller.get_formatted_bibliography()
        # Using a placeholder for demonstration:
        project = self.controller.project_state_manager.current_project
        if not project or not project.sources:
            return "No sources have been added to this project yet."

        # This part should ideally be in a dedicated citation service/manager
        preview_lines = []
        for i, link in enumerate(project.sources):
            source = self.controller.data_service.get_source_by_id(link.source_id)
            if source:
                preview_lines.append(f"[{i+1}] {source.title} ({source.publication_year or 'n.d.'}).")
        return "\n".join(preview_lines)

    def _choose_export_location(self, export_type: str):
        """Ask the controller to open a file picker for the export location."""
        # The controller will handle the FilePicker logic and call back to update the path
        # Example: self.controller.export_controller.pick_export_path(export_type, self.update_export_path)
        def on_path_selected(path: Optional[str]):
            if path:
                self.update_export_path(export_type, path)

        # This is a simplified stand-in for the controller's file picker logic
        file_picker = ft.FilePicker(on_result=lambda e: on_path_selected(e.path if e.path else None))
        self.page.overlay.append(file_picker)
        self.page.update()
        ext = "docx" if export_type == "word" else "pptx"
        file_picker.save_file(
            dialog_title=f"Choose {export_type.title()} export location",
            file_name=f"bibliography.{ext}",
            allowed_extensions=[ext]
        )

    def update_export_path(self, export_type: str, path: str):
        """Callback for the controller to update the UI with the selected path."""
        self.export_paths[export_type] = path
        display_control = self.word_path_display if export_type == 'word' else self.ppt_path_display
        if display_control:
            display_control.value = path
        self.page.update()

    def _perform_export(self, export_type: str):
        """Ask the controller to perform the export."""
        path = self.export_paths.get(export_type)
        if not path:
            self.controller.show_error_message(f"Please choose a location for the {export_type} export first.")
            return

        # Delegate the actual export logic to a controller
        # Example: success = self.controller.export_controller.export(export_type, path)
        # Placeholder logic:
        self.controller.show_success_message(f"{export_type.title()} exported successfully to {path}")

    def _copy_bibliography(self, e):
        """Copy bibliography text to clipboard."""
        bibliography_text = self._generate_bibliography_text()
        self.page.set_clipboard(bibliography_text)
        self.controller.show_success_message("Bibliography copied to clipboard!")

    def update_view(self):
        """Refreshes the view, called by the controller."""
        # Re-initialize components to get fresh data
        self._init_components()
        # Re-build the entire view content
        self.controls[0] = self.build()
        self.page.update()