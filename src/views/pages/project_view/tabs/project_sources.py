"""
Project Sources Tab - Manage sources for the current project
"""

import flet as ft
from typing import Optional, Dict, Any, List


class ProjectSourcesTab:
    """Tab for managing project sources with drag-and-drop functionality"""
    
    def __init__(self, page: ft.Page, database_manager=None, project_data=None, project_path=None):
        self.page = page
        self.database_manager = database_manager
        self.project_data = project_data or {}
        self.project_path = project_path
        
        # Sample data for testing (will be replaced with real data later)
        self.on_deck_sources = []
        self.project_sources = []
        
        # Create the main containers
        self._init_containers()
    
    def _init_containers(self):
        """Initialize the main containers for the tab"""
        # On Deck Circle - smaller left column
        self.on_deck_list = ft.Column(
            controls=[],  # Will be populated with sources
            spacing=10,
            scroll=ft.ScrollMode.AUTO
        )
        
        self.on_deck_container = ft.Container(
            content=ft.Column([
                ft.Text(
                    "On Deck Circle",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.BLUE_700
                ),
                ft.Container(height=10),
                ft.Container(
                    content=self.on_deck_list,
                    expand=True,
                    bgcolor=ft.colors.GREY_50,
                    border_radius=8,
                    border=ft.border.all(1, ft.colors.GREY_300),
                    padding=ft.padding.all(15)
                )
            ], spacing=0),
            width=300,
            expand=False,
            padding=ft.padding.only(right=15)
        )
        
        # Main Sources - larger right column with drag/drop
        self.sources_list = ft.Column(
            controls=[],  # Will be populated with sources
            spacing=10
        )
        
        self.sources_container = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Project Sources",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.BLUE_700
                ),
                ft.Container(height=10),
                ft.Container(
                    content=self.sources_list,
                    expand=True,
                    bgcolor=ft.colors.WHITE,
                    border_radius=8,
                    border=ft.border.all(1, ft.colors.BLUE_200),
                    padding=ft.padding.all(20)
                )
            ], spacing=0),
            expand=True
        )
        
        # Add some placeholder content for testing
        self._add_placeholder_content()
    
    def _add_placeholder_content(self):
        """Add some placeholder content to test the layout"""
        # Placeholder for On Deck Circle
        self.on_deck_list.controls.extend([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Source 1", weight=ft.FontWeight.BOLD, size=14),
                        ft.Text("Sample reference on deck", size=12, color=ft.colors.GREY_600)
                    ], spacing=5),
                    padding=ft.padding.all(10)
                ),
                elevation=2
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Source 2", weight=ft.FontWeight.BOLD, size=14),
                        ft.Text("Another potential source", size=12, color=ft.colors.GREY_600)
                    ], spacing=5),
                    padding=ft.padding.all(10)
                ),
                elevation=2
            )
        ])
        
        # Placeholder for Project Sources
        self.sources_list.controls.extend([
            ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.DRAG_INDICATOR, color=ft.colors.GREY_400),
                        ft.Column([
                            ft.Text("Active Source 1", weight=ft.FontWeight.BOLD, size=14),
                            ft.Text("Main project reference with usage notes", size=12, color=ft.colors.GREY_600),
                            ft.Text("Usage: Primary design reference", size=11, color=ft.colors.BLUE_600, italic=True)
                        ], spacing=3, expand=True)
                    ], spacing=10),
                    padding=ft.padding.all(15)
                ),
                elevation=3
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.DRAG_INDICATOR, color=ft.colors.GREY_400),
                        ft.Column([
                            ft.Text("Active Source 2", weight=ft.FontWeight.BOLD, size=14),
                            ft.Text("Secondary reference document", size=12, color=ft.colors.GREY_600),
                            ft.Text("Usage: Code compliance verification", size=11, color=ft.colors.BLUE_600, italic=True)
                        ], spacing=3, expand=True)
                    ], spacing=10),
                    padding=ft.padding.all(15)
                ),
                elevation=3
            )
        ])
    
    def build(self) -> ft.Control:
        """Build the sources tab content with two-column layout"""
        return ft.Container(
            content=ft.Row([
                self.on_deck_container,
                self.sources_container
            ], 
            spacing=0,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START
            ),
            padding=ft.padding.all(20),
            expand=True
        )
    
    def can_navigate_away(self) -> bool:
        """Check if user can navigate away from this tab"""
        # For now, always allow navigation
        return True
    
    def update_project_data(self, project_data: Dict[str, Any], project_path: str):
        """Update the tab with new project data"""
        self.project_data = project_data or {}
        self.project_path = project_path
        # TODO: Load project-specific sources from database
    
    def refresh_data(self):
        """Refresh the tab data"""
        # TODO: Reload sources from database
        if hasattr(self, 'page'):
            self.page.update()
