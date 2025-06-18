"""
Refactored Project View - Main project management interface with three tabs
Uses modular tab components for better separation of concerns
"""

import flet as ft
from views.base_view import BaseView
from .tabs import MetadataTab, SourcesTab, SlideAssignmentsTab
from typing import Optional, Callable


class ProjectViewRefactored(BaseView):
    """Project management view with three tabs using modular components"""
    
    def __init__(self, page: ft.Page, theme_manager=None, database_manager=None, project_state_manager=None, on_navigate=None):
        super().__init__(page)
        self.theme_manager = theme_manager
        self.database_manager = database_manager
        self.project_state_manager = project_state_manager
        self.on_navigate = on_navigate
        
        # Tab index
        self.current_tab_index = 0
        
        # UI components
        self.header_container = None
        self.tabs_container = None
        self.content_container = None
        
        # Initialize tab components
        self.metadata_tab = MetadataTab(page, theme_manager, database_manager, project_state_manager)
        self.sources_tab = SourcesTab(page, theme_manager, database_manager, project_state_manager)
        self.slide_assignments_tab = SlideAssignmentsTab(page, theme_manager, database_manager, project_state_manager)
        
    def build(self) -> ft.Control:
        """Build the project view with tabs"""
        return ft.Column([
            self._build_header(),
            self._build_tabs(),
            self._build_content()
        ], expand=True, spacing=0)
    
    def _build_header(self) -> ft.Control:
        """Build header with project title and back button"""
        # Get project info if available
        project_title = "No Project Loaded"
        if self.project_state_manager and self.project_state_manager.has_loaded_project():
            project_title = self.project_state_manager.get_project_title()
        
        # Theme-aware colors
        if self.page.theme_mode == ft.ThemeMode.DARK:
            header_bg = ft.colors.GREY_800
            border_color = ft.colors.GREY_600
        else:
            header_bg = ft.colors.WHITE
            border_color = ft.colors.GREY_300
        
        self.subtitle_text = ft.Text(project_title, size=14, color=ft.colors.GREY_700)
        
        self.header_container = ft.Container(
            content=ft.Row([
                ft.IconButton(
                    icon=ft.icons.ARROW_BACK,
                    on_click=lambda e: self._go_back(),
                    icon_size=20
                ),
                ft.Column([
                    ft.Text("Project View", size=20, weight=ft.FontWeight.BOLD),
                    self.subtitle_text
                ], spacing=2, tight=True),
                ft.Container(expand=True),
            ], spacing=10, alignment=ft.MainAxisAlignment.START),
            bgcolor=header_bg,
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
            border=ft.border.only(bottom=ft.BorderSide(1, border_color))
        )
        
        return self.header_container
    
    def _build_tabs(self) -> ft.Control:
        """Build tab navigation"""
        if self.page.theme_mode == ft.ThemeMode.DARK:
            tab_bg = ft.colors.GREY_800
            border_color = ft.colors.GREY_600
        else:
            tab_bg = ft.colors.WHITE
            border_color = ft.colors.GREY_300
        
        # Tab buttons
        tab_buttons = [
            self._create_tab_button("Metadata", 0),
            self._create_tab_button("Sources", 1),
            self._create_tab_button("Slide Assignments", 2)
        ]
        
        self.tabs_container = ft.Container(
            content=ft.Row(tab_buttons, spacing=0),
            bgcolor=tab_bg,
            padding=ft.padding.symmetric(horizontal=20, vertical=0),
            border=ft.border.only(bottom=ft.BorderSide(1, border_color))
        )
        
        return self.tabs_container
    
    def _create_tab_button(self, text: str, index: int) -> ft.Control:
        """Create a tab button"""
        is_active = index == self.current_tab_index
        
        if is_active:
            bgcolor = self._get_theme_color()
            text_color = ft.colors.WHITE
        else:
            bgcolor = ft.colors.TRANSPARENT
            text_color = ft.colors.GREY_600
        
        return ft.Container(
            content=ft.Text(text, color=text_color, weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL),
            bgcolor=bgcolor,
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
            border_radius=ft.border_radius.only(top_left=5, top_right=5),
            on_click=lambda e, idx=index: self._switch_tab(idx)
        )
    
    def _build_content(self) -> ft.Control:
        """Build content area"""
        self.content_container = ft.Container(
            content=self._get_tab_content(self.current_tab_index),
            padding=ft.padding.all(20),
            expand=True
        )
        
        return self.content_container
    
    def _get_tab_content(self, tab_index: int) -> ft.Control:
        """Get content for the specified tab"""
        if tab_index == 0:
            return self.metadata_tab.build()
        elif tab_index == 1:
            return self.sources_tab.build()
        elif tab_index == 2:
            return self.slide_assignments_tab.build()
        else:
            return ft.Text("Invalid tab")
    
    def _switch_tab(self, tab_index: int):
        """Switch to the specified tab"""
        self.current_tab_index = tab_index
        
        # Update tab buttons
        if self.tabs_container:
            self.tabs_container.content = ft.Row([
                self._create_tab_button("Metadata", 0),
                self._create_tab_button("Sources", 1),
                self._create_tab_button("Slide Assignments", 2)
            ], spacing=0)
        
        # Update content
        if self.content_container:
            self.content_container.content = self._get_tab_content(tab_index)
        
        self.page.update()
    
    def _go_back(self):
        """Handle back button click"""
        if self.on_navigate:
            self.on_navigate("recent_projects")
    
    def _get_theme_color(self) -> str:
        """Get current theme color"""
        if self.theme_manager:
            return self.theme_manager.get_current_color()
        return ft.colors.BLUE_600
    
    def refresh_project_data(self):
        """Refresh the view when project data changes"""
        # Update header
        if self.project_state_manager and self.project_state_manager.has_loaded_project():
            project_title = self.project_state_manager.get_project_title()
            if hasattr(self, 'subtitle_text') and self.subtitle_text:
                self.subtitle_text.value = project_title
        
        # Refresh current tab
        if self.content_container:
            self.content_container.content = self._get_tab_content(self.current_tab_index)
            
        self.page.update()
