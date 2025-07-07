"""
Project View with Tabs (Refactored)

This view serves as the main container for the tabbed interface that appears
when a project is opened. It initializes and manages the individual tab views.
"""

import flet as ft
from views import BaseView

# Import the refactored tab classes
from .tabs.project_metadata import ProjectMetadataTab
from .tabs.project_sources import ProjectSourcesTab
from .tabs.cite_sources import CiteSourcesTab
from config.project_types_config import get_project_type_config

class ProjectView(BaseView):
    """Project view with a tabbed interface for different project aspects."""
    
    def __init__(self, page: ft.Page, controller):
        super().__init__(page, controller)
        self.project_state_manager = self.controller.project_state_manager
        
        # Initialize all tab view classes, passing the controller to each
        self.metadata_tab = ProjectMetadataTab(controller=self.controller)
        self.sources_tab = ProjectSourcesTab(controller=self.controller)
        # self.cite_sources_tab = CiteSourcesTab(controller=self.controller)

    def build(self) -> ft.Control:
        """
        Builds the entire project view UI. This method is called by the 
        navigation logic in the AppController.
        """
        project = self.project_state_manager.current_project
        
        if not project:
            return self.show_error("No project is currently loaded.")

        self.metadata_tab.update_project_data(project.metadata, str(project.file_path))
        self.sources_tab.update_project_data(project.metadata, str(project.file_path))
        # self.cite_sources_tab.update_project_data(project.metadata, str(project.file_path))

        project_info = f"Project: {project.title}"
        
        # --- FIX: Add project type to the header ---
        project_type_config = get_project_type_config(project.project_type.value)
        project_type_display = f"({project_type_config.display_name})" if project_type_config else ""
        # --- END FIX ---

        return ft.Column([
            ft.Container(
                content=ft.Row([
                    # This group will stay on the left
                    ft.Row([
                        ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            on_click=lambda e: self.controller.navigate_to("new_project"),
                            tooltip="Back to Project Browser"
                        ),
                        ft.Text(project_info, size=20, weight=ft.FontWeight.BOLD),
                    ]),
                    # This spacer will push the next item to the right
                    ft.Container(expand=True),
                    # This will be on the right
                    ft.Text(project_type_display, size=20, color=ft.colors.ON_SURFACE_VARIANT),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.all(20),
                border=ft.border.only(bottom=ft.BorderSide(1, ft.colors.OUTLINE))
            ),
            ft.Container(
                content=self._build_tabs(),
                expand=True,
                padding=ft.padding.symmetric(horizontal=20, vertical=10)
            )
        ], expand=True, spacing=0)

    def _build_tabs(self) -> ft.Tabs:
        """Constructs the Flet Tabs control with the built content from each tab class."""
        return ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Project Metadata",
                    icon=ft.icons.INFO_OUTLINE,
                    content=self.metadata_tab.build() 
                ),
                ft.Tab(
                    text="Manage Sources",
                    icon=ft.icons.SOURCE,
                    content=self.sources_tab.build()
                ),
                # ft.Tab(
                #     text="Cite Slides",
                #     icon=ft.icons.COMPARE_ARROWS,
                #     content=self.cite_sources_tab.build()
                # ),
            ],
            expand=True
        )

    def update_view(self):
        """
        Refreshes the entire view.
        """
        self.page.update()
