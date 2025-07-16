"""
Project View with Tabs (Refactored)

This view serves as the main container for the tabbed interface that appears
when a project is opened. It initializes and manages the individual tab views.
"""

import flet as ft
import logging
from ...base_view import BaseView

# Import the refactored tab classes
from .tabs.project_metadata import ProjectMetadataTab
from .tabs.project_sources import ProjectSourcesTab
from .tabs.cite_sources import CiteSourcesTab
from config.project_types_config import get_project_type_config

class ProjectView(BaseView):
    """Project view with a tabbed interface for different project aspects."""
    
    def __init__(self, page: ft.Page, controller):
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing ProjectView")
        
        super().__init__(page, controller)
        self.project_state_manager = self.controller.project_state_manager
        
        self.logger.debug("Creating tab instances")
        
        # Initialize all tab view classes, passing the controller to each
        try:
            self.metadata_tab = ProjectMetadataTab(controller=self.controller)
            self.logger.debug("✅ MetadataTab initialized")
        except Exception as e:
            self.logger.error(f"❌ MetadataTab initialization failed: {e}")
            
        try:
            self.sources_tab = ProjectSourcesTab(controller=self.controller)
            self.logger.debug("✅ SourcesTab initialized")
        except Exception as e:
            self.logger.error(f"❌ SourcesTab initialization failed: {e}")
            
        try:
            self.cite_sources_tab = CiteSourcesTab(controller=self.controller)
            self.logger.debug("✅ CiteSourcesTab initialized")
        except Exception as e:
            self.logger.error(f"❌ CiteSourcesTab initialization failed: {e}")
            
        self.logger.info("ProjectView initialization complete")

    def build(self) -> ft.Control:
        """
        Builds the entire project view UI. This method is called by the 
        navigation logic in the AppController.
        """
        self.logger.info("Building ProjectView content")
        
        project = self.project_state_manager.current_project
        
        if not project:
            self.logger.warning("No project loaded - showing error message")
            return self.show_error("No project is currently loaded.")

        self.logger.info(f"Building view for project: {project.project_title}")
        
        # Go to the right page
        nav_manager = self.controller.navigation_manager
        start_tab_index = 0

        if nav_manager.get_previous_page() == "sources":
            start_tab_index = 1

        # Update the tabs with the latest project data
        try:
            self.logger.debug("Updating tab views with project data")
            self.update_view()
            self.logger.debug("✅ Tab views updated successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to update tab views: {e}")
            return self.show_error(f"Error loading project data: {e}")

        project_info = f"Project: {project.project_title}"
        project_type_config = get_project_type_config(project.project_type.value)
        project_type_display = f"({project_type_config.display_name})" if project_type_config else ""

        self.logger.debug("Building tab structure")
        
        try:
            tabs_content = ft.Tabs([
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
                ft.Tab(
                    text="Cite Slides",
                    icon=ft.icons.COMPARE_ARROWS,
                    content=self.cite_sources_tab.build()
                ),
            ],
            expand=True
            )
            
            self.logger.debug("✅ Tabs created successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create tabs: {e}")
            return self.show_error(f"Error creating project tabs: {e}")

        result = ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Row([
                        ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            on_click=lambda e: self.controller.navigate_to("new_project"),
                            tooltip="Back to Project Browser"
                        ),
                        ft.Text(project_info, size=20, weight=ft.FontWeight.BOLD),
                    ]),
                    ft.Container(expand=True),
                    ft.Text(project_type_display, size=20, color=ft.colors.ON_SURFACE_VARIANT),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.all(20),
                border=ft.border.only(bottom=ft.BorderSide(1, ft.colors.OUTLINE))
            ),
            tabs_content
        ])
        
        self.logger.info("✅ ProjectView build complete")
        return result

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
                ft.Tab(
                    text="Cite Slides",
                    icon=ft.icons.COMPARE_ARROWS,
                    content=self.cite_sources_tab.build()
                ),
            ],
            expand=True
        )

    def update_view(self):
        """
        This method is called by the controller's refresh_current_view.
        It ensures all child tabs have their data refreshed before redrawing the page.
        """
        project = self.project_state_manager.current_project
        if not project:
            return

        # Call the update method on the child tabs that need refreshing
        if hasattr(self, 'metadata_tab') and hasattr(self.metadata_tab, 'update_project_data'):
            self.metadata_tab.update_project_data(project.metadata, str(project.file_path))
        
        if hasattr(self, 'sources_tab') and hasattr(self.sources_tab, 'update_project_data'):
            self.sources_tab.update_project_data(project.metadata, str(project.file_path))
        
        # Update the cite sources tab as well
        if hasattr(self, 'cite_sources_tab') and hasattr(self.cite_sources_tab, 'update_view'):
            self.cite_sources_tab.update_view()
