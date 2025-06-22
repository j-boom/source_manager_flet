"""
Project View with Tabs
"""

import flet as ft
from views.base_view import BaseView
from .tabs.project_metadata import ProjectMetadataTab


class ProjectView(BaseView):
    """Project view with tabbed interface for different project aspects"""
    
    def __init__(self, page: ft.Page, theme_manager=None, database_manager=None, 
                 project_state_manager=None, on_navigate=None):
        super().__init__(page)
        self.theme_manager = theme_manager
        self.database_manager = database_manager
        self.project_state_manager = project_state_manager
        self.on_navigate = on_navigate
        self.loaded_project_path = None
        self.loaded_project_name = None
        self.loaded_project_data = None
        
        # If we have a project state manager, get the project info
        if self.project_state_manager and hasattr(self.project_state_manager, 'loaded_project_path'):
            self.loaded_project_path = self.project_state_manager.loaded_project_path
            if hasattr(self.project_state_manager, 'project_data') and self.project_state_manager.project_data:
                self.loaded_project_data = self.project_state_manager.project_data
                self.loaded_project_name = self.loaded_project_data.get('name', 'Unknown Project')
        
        # Initialize tabs
        self.metadata_tab = ProjectMetadataTab(
            page=page,
            database_manager=database_manager,
            project_data=self.loaded_project_data,
            project_path=self.loaded_project_path
        )
        
        # Track previous tab for navigation restrictions
        self._previous_tab = 0  # Start on metadata tab
        
        # Create the tabs control
        self.tabs = ft.Tabs(
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
                    content=self._build_placeholder_tab("Sources", "Manage project source documents")
                ),
                ft.Tab(
                    text="Cite Slides",
                    icon=ft.icons.COMPARE_ARROWS,
                    content=self._build_placeholder_tab("Cite Slides", "Add references to project slides")
                ),
            ],
            on_change=self._on_tab_change
        )
    
    def build(self) -> ft.Control:
        """Build the tabbed project view"""
        project_info = "No project loaded"
        if self.loaded_project_path:
            project_info = f"Project: {self.loaded_project_name or 'Unknown'}"
        
        return ft.Column([
            # Header
            ft.Container(
                content=ft.Row([
                    ft.IconButton(
                        icon=ft.icons.ARROW_BACK,
                        on_click=lambda e: self._go_back(),
                        icon_size=20,
                        tooltip="Back to Project List"
                    ),
                    ft.Column([
                        ft.Text("Project View", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(project_info, size=12, color=ft.colors.GREY_600)
                    ], spacing=2),
                ], spacing=10),
                padding=ft.padding.all(20),
                bgcolor=ft.colors.GREY_100 if self.page.theme_mode != ft.ThemeMode.DARK else ft.colors.GREY_800,
                border=ft.border.only(bottom=ft.BorderSide(1, ft.colors.GREY_300))
            ),
            # Tabbed Content
            ft.Container(
                content=self.tabs,
                expand=True
                # Temporarily removed padding to test focus issue
                # padding=ft.padding.all(10)
            )
        ], expand=True, spacing=0)
    
    def _build_placeholder_tab(self, title: str, description: str) -> ft.Control:
        """Build a placeholder tab content"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.CONSTRUCTION, size=64, color=ft.colors.GREY_400),
                ft.Text(title, size=24, weight=ft.FontWeight.BOLD),
                ft.Text(description, size=14, color=ft.colors.GREY_600, text_align=ft.TextAlign.CENTER),
                ft.Text("Coming soon...", size=12, color=ft.colors.GREY_500, text_align=ft.TextAlign.CENTER)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
            alignment=ft.alignment.center,
            expand=True,
            padding=ft.padding.all(40)
        )
    
    def _on_tab_change(self, e):
        """Handle tab change events with navigation restrictions"""
        selected_tab = e.control.selected_index
        current_tab = e.control.selected_index
        
        # If trying to navigate away from metadata tab (index 0), check if allowed
        if hasattr(self, '_previous_tab') and self._previous_tab == 0 and selected_tab != 0:
            if hasattr(self.metadata_tab, 'can_navigate_away'):
                if not self.metadata_tab.can_navigate_away():
                    # Prevent navigation by reverting to metadata tab
                    e.control.selected_index = 0
                    self.page.update()
                    return
        
        # Store the previous tab index
        self._previous_tab = selected_tab
        
        print(f"Switched to tab: {selected_tab}")
        
        # Refresh the active tab content if needed
        if selected_tab == 0:  # Metadata tab
            self.metadata_tab.refresh_data()
    
    def _go_back(self):
        """Handle back button click"""
        if self.on_navigate:
            self.on_navigate("new_project")
    
    def refresh_project_data(self):
        """Refresh project data and update all tabs"""
        # Update project info if project state manager has new data
        if self.project_state_manager and hasattr(self.project_state_manager, 'loaded_project_path'):
            self.loaded_project_path = self.project_state_manager.loaded_project_path
            if hasattr(self.project_state_manager, 'project_data') and self.project_state_manager.project_data:
                self.loaded_project_data = self.project_state_manager.project_data
                self.loaded_project_name = self.loaded_project_data.get('name', 'Unknown Project')
        
        # Update metadata tab with new data
        if hasattr(self, 'metadata_tab'):
            self.metadata_tab.update_project_data(
                self.loaded_project_data or {}, 
                self.loaded_project_path or ""
            )
        
        # Rebuild the view
        if hasattr(self, 'page'):
            self.page.update()
