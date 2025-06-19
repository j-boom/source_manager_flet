"""
Simple Project View
"""

import flet as ft
from views.base_view import BaseView


class ProjectView(BaseView):
    """Simple project view to display selected projects"""
    
    def __init__(self, page: ft.Page, theme_manager=None, database_manager=None, project_state_manager=None, on_navigate=None):
        super().__init__(page)
        self.theme_manager = theme_manager
        self.database_manager = database_manager
        self.project_state_manager = project_state_manager
        self.on_navigate = on_navigate
        self.loaded_project_path = None
        self.loaded_project_name = None
        
        # If we have a project state manager, get the project info
        if self.project_state_manager and hasattr(self.project_state_manager, 'loaded_project_path'):
            self.loaded_project_path = self.project_state_manager.loaded_project_path
            if hasattr(self.project_state_manager, 'project_data') and self.project_state_manager.project_data:
                self.loaded_project_name = self.project_state_manager.project_data.get('name', 'Unknown Project')
    
    def build(self) -> ft.Control:
        """Build the simple project view"""
        project_info = "No project loaded"
        if self.loaded_project_path:
            project_info = f"Project: {self.loaded_project_name or 'Unknown'}\nPath: {self.loaded_project_path}"
        
        return ft.Column([
            # Header
            ft.Container(
                content=ft.Row([
                    ft.IconButton(
                        icon=ft.icons.ARROW_BACK,
                        on_click=lambda e: self._go_back(),
                        icon_size=20
                    ),
                    ft.Text("Project View", size=20, weight=ft.FontWeight.BOLD),
                ], spacing=10),
                padding=ft.padding.all(20),
                bgcolor=ft.colors.GREY_100 if self.page.theme_mode != ft.ThemeMode.DARK else ft.colors.GREY_800,
                border=ft.border.only(bottom=ft.BorderSide(1, ft.colors.GREY_300))
            ),
            # Content
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.FOLDER_OPEN, size=64, color=ft.colors.BLUE_400),
                    ft.Text("Project View", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(project_info, size=14, color=ft.colors.GREY_600, text_align=ft.TextAlign.CENTER),
                    ft.Text("✅ Navigation is working! JSON card click successful.", 
                           size=16, color=ft.colors.GREEN_600, text_align=ft.TextAlign.CENTER)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
                alignment=ft.alignment.center,
                expand=True,
                padding=ft.padding.all(40)
            )
        ], expand=True, spacing=0)
    
    def _go_back(self):
        """Handle back button click"""
        if self.on_navigate:
            self.on_navigate("new_project")
    
    def refresh_project_data(self):
        """Refresh project data"""
        # Update project info if project state manager has new data
        if self.project_state_manager and hasattr(self.project_state_manager, 'loaded_project_path'):
            self.loaded_project_path = self.project_state_manager.loaded_project_path
            if hasattr(self.project_state_manager, 'project_data') and self.project_state_manager.project_data:
                self.loaded_project_name = self.project_state_manager.project_data.get('name', 'Unknown Project')
        
        # Rebuild the view
        if hasattr(self, 'page'):
            self.page.update()
