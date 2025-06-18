"""New Project View - Main implementation"""

import flet as ft
from views.base_view import BaseView
from typing import List, Dict, Any, Optional
from services import DirectoryService, ProjectCreationService
from views.components.dialogs.project_creation_dialog import ProjectCreationDialog
from views.components.dialogs.folder_creation_dialog import FolderCreationDialog
from models.database_manager import DatabaseManager
from .tabs.base_tab import TabManager
from .tabs.folder_browsing_tab import FolderBrowsingTab


class NewProjectView(BaseView):
    """New project view with better separation of concerns"""
    
    def __init__(self, page: ft.Page, theme_manager=None, user_config=None, on_back=None, on_project_selected=None, project_state_manager=None, on_navigate=None):
        super().__init__(page)
        self.theme_manager = theme_manager
        self.user_config = user_config
        self.on_back = on_back
        self.on_project_selected = on_project_selected
        self.project_state_manager = project_state_manager
        self.on_navigate = on_navigate
        
        # Services
        self.directory_service = DirectoryService()
        self.project_service = ProjectCreationService(user_config)
        self.db_manager = DatabaseManager()  # Initialize database manager
        
        # Dialog components
        self.project_dialog = ProjectCreationDialog(
            page, self.project_service, self.db_manager,  # Pass database manager
            on_success=self._on_project_created,
            on_cancel=self._on_dialog_cancelled
        )
        self.folder_dialog = FolderCreationDialog(
            page, self.directory_service,
            on_success=self._on_folder_created,
            on_cancel=self._on_dialog_cancelled
        )
        
        # Tab manager
        self.tab_manager = TabManager(page, theme_manager)
        self._setup_tabs()
        
        # UI components
        self.header_container = None
    
    def _setup_tabs(self):
        """Set up the tabs for the new project view"""
        # Folder browsing tab
        folder_tab = FolderBrowsingTab(
            self.page,
            theme_manager=self.theme_manager,
            directory_service=self.directory_service,
            on_add_project_clicked=self._on_add_project_clicked,
            on_create_folder_clicked=self._on_create_folder_clicked
        )
        self.tab_manager.add_tab(folder_tab)

    def build(self) -> ft.Control:
        """Build the view with tabs"""
        if not self.directory_service.directory_source_citations_path:
            return self._build_error_view("Directory_Source_Citations not found")

        return ft.Column([
            self._build_header(),
            self.tab_manager.build_tabs(),
            self.tab_manager.build_content()
        ], expand=True, spacing=0)

    def _build_error_view(self, message: str) -> ft.Control:
        """Build error view"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.ERROR_OUTLINE, size=48, color=ft.colors.RED_400),
                ft.Text(message, size=16, color=ft.colors.RED_400, text_align=ft.TextAlign.CENTER),
                ft.ElevatedButton(
                    "Go Back",
                    on_click=lambda e: self._on_back_clicked(),
                    style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_700, color=ft.colors.WHITE)
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
            alignment=ft.alignment.center,
            expand=True
        )

    def _build_header(self) -> ft.Control:
        """Build header section"""
        # Theme-aware header colors
        if self.page.theme_mode == ft.ThemeMode.DARK:
            header_bg = ft.colors.GREY_800
            border_color = ft.colors.GREY_600
        else:
            header_bg = ft.colors.WHITE
            border_color = ft.colors.GREY_300
        
        # Get theme color for button
        theme_color = self._get_theme_color()
        
        self.header_container = ft.Container(
            content=ft.Row([
                ft.ElevatedButton(
                    "Back",
                    icon=ft.icons.ARROW_BACK,
                    on_click=lambda e: self._on_back_clicked(),
                    style=ft.ButtonStyle(
                        bgcolor=theme_color,
                        color=ft.colors.WHITE
                    )
                ),
                ft.Container(expand=True),
                ft.Text("New Project", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Recent Projects",
                    icon=ft.icons.HISTORY,
                    on_click=lambda e: self._on_recent_projects_clicked(),
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.BLUE_600,
                        color=ft.colors.WHITE
                    )
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.all(20),
            bgcolor=header_bg,
            border=ft.border.only(bottom=ft.BorderSide(1, border_color))
        )
        
        return self.header_container

    def _get_theme_color(self) -> str:
        """Get the theme accent color"""
        if self.theme_manager:
            return self.theme_manager.get_accent_color()
        return ft.colors.BLUE_600

    # Event handlers
    def _on_back_clicked(self):
        """Handle back button click"""
        if self.on_back:
            self.on_back()

    def _on_recent_projects_clicked(self):
        """Handle recent projects button click"""
        if self.on_navigate:
            self.on_navigate("recent_projects")

    def _on_add_project_clicked(self, e):
        """Handle add project button click"""
        # Get the current tab and check if it's a folder browsing tab
        current_tab = self.tab_manager.get_current_tab()
        if isinstance(current_tab, FolderBrowsingTab):
            if not current_tab.directory_service.is_ten_digit_folder(current_tab.current_breadcrumb):
                self._show_error_dialog("Cannot Create Project", 
                                      "Please navigate to a ten-digit folder first to create a project.")
                return
            
            folder_path = current_tab.directory_service.get_folder_path_from_breadcrumb(current_tab.current_breadcrumb)
            ten_digit_number = current_tab.directory_service.extract_ten_digit_number(current_tab.current_breadcrumb[-1])
            
            if ten_digit_number:
                self.project_dialog.show(ten_digit_number, folder_path)

    def _on_create_folder_clicked(self, e):
        """Handle create new ten-digit folder button click"""
        # Get the current tab and check if it's a folder browsing tab
        current_tab = self.tab_manager.get_current_tab()
        if isinstance(current_tab, FolderBrowsingTab):
            if not current_tab.directory_service.is_four_digit_folder(current_tab.current_breadcrumb):
                self._show_error_dialog("Cannot Create Folder", 
                                      "Please navigate to a four-digit folder first to create a ten-digit folder.")
                return
            
            folder_path = current_tab.directory_service.get_folder_path_from_breadcrumb(current_tab.current_breadcrumb)
            self.folder_dialog.show_for_new_folder(folder_path)

    # Dialog Callbacks
    def _on_project_created(self, success_data):
        """Handle successful project creation"""
        if isinstance(success_data, dict):
            # New format with project data
            project = success_data.get('project')
            project_data = success_data.get('project_data')
            file_path = success_data.get('file_path')
            message = success_data.get('message', 'Project created successfully')
            
            # Load project into app state if we have the manager
            if self.project_state_manager and project:
                self.project_state_manager.load_project(project, project_data, file_path)
            
            # Navigate to project view
            if self.on_navigate:
                self.on_navigate("project_view")  # Go directly to project view
            
            self._show_success_dialog("Success", message)
        else:
            # Fallback for old string format
            self._refresh_current_view()
            self._show_success_dialog("Success", str(success_data))

    def _on_folder_created(self, folder_name: str):
        """Handle successful folder creation"""
        self._refresh_current_view()
        self._show_success_dialog("Success", f"Folder '{folder_name}' created successfully")

    def _on_dialog_cancelled(self):
        """Handle dialog cancellation"""
        pass  # No special action needed

    def _refresh_current_view(self):
        """Refresh the current tab view"""
        current_tab = self.tab_manager.get_current_tab()
        if current_tab:
            current_tab.refresh()
            self.page.update()

    def _show_error_dialog(self, title: str, message: str):
        """Show error dialog"""
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update())
            ]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _show_success_dialog(self, title: str, message: str):
        """Show success dialog"""
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update())
            ]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
