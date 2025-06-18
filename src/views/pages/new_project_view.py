"""Simple New Project View - List-based folder browsing"""

import flet as ft
from views.base_view import BaseView
from typing import List, Dict, Any, Optional
from services import DirectoryService, ProjectCreationService
from views.components.dialogs.project_creation_dialog import ProjectCreationDialog
from views.components.dialogs.folder_creation_dialog import FolderCreationDialog
from models.database_manager import DatabaseManager


class NewProjectView(BaseView):
    """Simple new project view with list-based folder browsing"""
    
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
        self.db_manager = DatabaseManager()
        
        # Dialog components
        self.project_dialog = ProjectCreationDialog(
            page, self.project_service, self.db_manager,
            on_success=self._on_project_created,
            on_cancel=self._on_dialog_cancelled
        )
        self.folder_dialog = FolderCreationDialog(
            page, self.directory_service,
            on_success=self._on_folder_created,
            on_cancel=self._on_dialog_cancelled
        )
        
        # UI state
        self.selected_primary_folder = None
        self.current_breadcrumb = []
        self.current_folders = []
        
        # UI components
        self.primary_dropdown = None
        self.search_field = None
        self.content_area = None

    def build(self) -> ft.Control:
        """Build the view"""
        if not self.directory_service.directory_source_citations_path:
            return self._build_error_view("Directory_Source_Citations not found")

        return ft.Column([
            self._build_header(),
            self._build_controls(),
            self._build_content_area()
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
        if self.page.theme_mode == ft.ThemeMode.DARK:
            header_bg = ft.colors.GREY_800
            border_color = ft.colors.GREY_600
        else:
            header_bg = ft.colors.WHITE
            border_color = ft.colors.GREY_300
        
        theme_color = self._get_theme_color()
        
        return ft.Container(
            content=ft.Row([
                ft.ElevatedButton(
                    "Back",
                    icon=ft.icons.ARROW_BACK,
                    on_click=lambda e: self._on_back_clicked(),
                    style=ft.ButtonStyle(bgcolor=theme_color, color=ft.colors.WHITE)
                ),
                ft.Container(expand=True),
                ft.Text("New Project", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Recent Projects",
                    icon=ft.icons.HISTORY,
                    on_click=lambda e: self._on_recent_projects_clicked(),
                    style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_600, color=ft.colors.WHITE)
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.all(20),
            bgcolor=header_bg,
            border=ft.border.only(bottom=ft.BorderSide(1, border_color))
        )

    def _build_controls(self) -> ft.Control:
        """Build the dropdown and search controls"""
        self.primary_dropdown = ft.Dropdown(
            label="Select Primary Folder",
            options=[ft.dropdown.Option(folder) for folder in self.directory_service.primary_folders],
            width=300,
            on_change=self._on_primary_folder_changed
        )
        
        self.search_field = ft.TextField(
            label="Search (4-digit folders)",
            hint_text="e.g., 1001",
            width=300,
            prefix_icon=ft.icons.SEARCH,
            on_submit=self._on_search_submit
        )

        if self.page.theme_mode == ft.ThemeMode.DARK:
            controls_bg = ft.colors.GREY_900
        else:
            controls_bg = ft.colors.GREY_50

        return ft.Container(
            content=ft.Row([
                self.primary_dropdown,
                ft.Container(width=20),
                self.search_field
            ], alignment=ft.MainAxisAlignment.CENTER),
            padding=ft.padding.all(20),
            bgcolor=controls_bg
        )

    def _build_content_area(self) -> ft.Control:
        """Build the main content area"""
        if self.page.theme_mode == ft.ThemeMode.DARK:
            icon_color = ft.colors.GREY_600
            text_color = ft.colors.GREY_400
        else:
            icon_color = ft.colors.GREY_400
            text_color = ft.colors.GREY_500

        self.content_area = ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.FOLDER_OUTLINED, size=64, color=icon_color),
                ft.Text(
                    "Select a primary folder to begin",
                    size=18,
                    color=text_color,
                    text_align=ft.TextAlign.CENTER
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
            alignment=ft.alignment.center,
            expand=True
        )
        
        return self.content_area

    def _get_theme_color(self) -> str:
        """Get the theme accent color"""
        if self.theme_manager:
            return self.theme_manager.get_accent_color()
        return ft.colors.BLUE_600

    def _on_back_clicked(self):
        """Handle back button click"""
        if self.on_back:
            self.on_back()

    def _on_recent_projects_clicked(self):
        """Handle recent projects button click"""
        if self.on_navigate:
            self.on_navigate("recent_projects")

    def _on_primary_folder_changed(self, e):
        """Handle primary folder selection"""
        if not e.control.value:
            return
        
        self.selected_primary_folder = e.control.value
        self.current_breadcrumb = [self.selected_primary_folder]
        
        # Get four-digit folders and display them as a list
        four_digit_folders = self.directory_service.get_four_digit_folders(self.selected_primary_folder)
        self._display_folder_list(four_digit_folders, "four_digit")

    def _on_search_submit(self, e):
        """Handle search submission"""
        if not self.search_field or not self.search_field.value or not self.selected_primary_folder:
            return
        
        search_term = self.search_field.value.strip()
        if not search_term:
            return
        
        # Use DirectoryService search
        four_digit_folders, ten_digit_folders = self.directory_service.search_four_digit_folders(
            self.selected_primary_folder, search_term
        )
        
        if four_digit_folders:
            self._display_folder_list(four_digit_folders, "search_results")
        elif ten_digit_folders:
            self._display_folder_list(ten_digit_folders, "search_results")
        else:
            self._show_no_results()
        
        self.search_field.value = ""
        self.page.update()

    def _display_folder_list(self, folders: List[Dict[str, Any]], folder_type: str):
        """Display folders as a simple list"""
        if not folders:
            self._show_no_results()
            return

        # Create list items
        list_items = []
        
        # Add breadcrumb if we're deeper than primary level
        if len(self.current_breadcrumb) > 1:
            breadcrumb_text = " > ".join(self.current_breadcrumb)
            list_items.append(
                ft.Container(
                    content=ft.Text(f"📁 {breadcrumb_text}", size=14, weight=ft.FontWeight.BOLD),
                    padding=ft.padding.symmetric(vertical=10, horizontal=15),
                    bgcolor=ft.colors.BLUE_50 if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.colors.GREY_800
                )
            )
        
        # Add action buttons for ten-digit folders
        if folder_type == "ten_digit" and len(self.current_breadcrumb) >= 2:
            action_buttons = ft.Row([
                ft.ElevatedButton(
                    "Add Project",
                    icon=ft.icons.ADD,
                    on_click=self._on_add_project_clicked,
                    style=ft.ButtonStyle(bgcolor=self._get_theme_color(), color=ft.colors.WHITE)
                ),
                ft.ElevatedButton(
                    "Create Folder",
                    icon=ft.icons.CREATE_NEW_FOLDER,
                    on_click=self._on_create_folder_clicked,
                    style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_600, color=ft.colors.WHITE)
                )
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
            
            list_items.append(
                ft.Container(content=action_buttons, padding=ft.padding.all(15))
            )

        # Add folder items
        for folder in folders:
            folder_name = folder.get('name', str(folder))
            list_items.append(self._create_folder_list_item(folder, folder_type))

        # Create scrollable list
        folder_list = ft.ListView(
            controls=list_items,
            expand=True,
            spacing=2
        )

        self.content_area.content = folder_list
        self.content_area.alignment = None
        self.page.update()

    def _create_folder_list_item(self, folder: Dict[str, Any], folder_type: str) -> ft.Control:
        """Create a list item for a folder"""
        folder_name = folder.get('name', str(folder))
        
        if self.page.theme_mode == ft.ThemeMode.DARK:
            item_bg = ft.colors.GREY_800
            item_hover = ft.colors.GREY_700
            text_color = ft.colors.WHITE
        else:
            item_bg = ft.colors.WHITE
            item_hover = ft.colors.GREY_100
            text_color = ft.colors.BLACK

        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.FOLDER, color=self._get_theme_color(), size=20),
                ft.Text(folder_name, color=text_color, size=14),
                ft.Container(expand=True),
                ft.Icon(ft.icons.CHEVRON_RIGHT, color=ft.colors.GREY_500, size=16)
            ], spacing=10),
            padding=ft.padding.symmetric(vertical=12, horizontal=15),
            bgcolor=item_bg,
            border_radius=5,
            ink=True,
            on_click=lambda e, f=folder: self._on_folder_clicked(f, folder_type),
            on_hover=lambda e: setattr(e.control, 'bgcolor', item_hover if e.data == 'true' else item_bg) or self.page.update()
        )

    def _on_folder_clicked(self, folder: Dict[str, Any], folder_type: str):
        """Handle folder click"""
        folder_name = folder.get('name', str(folder))
        
        if folder_type == "four_digit":
            # Navigate into four-digit folder
            self.current_breadcrumb.append(folder_name)
            folder_path = self.directory_service.get_folder_path_from_breadcrumb(self.current_breadcrumb)
            contents = self.directory_service.get_folder_contents(folder_path)
            self._display_folder_list(contents, "ten_digit")

    def _show_no_results(self):
        """Show no results message"""
        self.content_area.content = ft.Column([
            ft.Icon(ft.icons.SEARCH_OFF, size=64, color=ft.colors.GREY_400),
            ft.Text("No folders found", size=16, color=ft.colors.GREY_500)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)
        self.content_area.alignment = ft.alignment.center
        self.page.update()

    def _on_add_project_clicked(self, e):
        """Handle add project button"""
        if len(self.current_breadcrumb) < 2:
            self._show_error("Please navigate to a ten-digit folder first")
            return
        
        if not self.directory_service.is_ten_digit_folder(self.current_breadcrumb):
            self._show_error("Please navigate to a ten-digit folder first")
            return
        
        folder_path = self.directory_service.get_folder_path_from_breadcrumb(self.current_breadcrumb)
        ten_digit_number = self.directory_service.extract_ten_digit_number(self.current_breadcrumb[-1])
        
        if ten_digit_number:
            self.project_dialog.show(ten_digit_number, folder_path)

    def _on_create_folder_clicked(self, e):
        """Handle create folder button"""
        if len(self.current_breadcrumb) < 2:
            self._show_error("Please navigate to a four-digit folder first")
            return
        
        if not self.directory_service.is_four_digit_folder(self.current_breadcrumb):
            self._show_error("Please navigate to a four-digit folder first")
            return
        
        folder_path = self.directory_service.get_folder_path_from_breadcrumb(self.current_breadcrumb)
        self.folder_dialog.show_for_new_folder(folder_path)

    def _on_project_created(self, success_data):
        """Handle successful project creation"""
        if isinstance(success_data, dict):
            project = success_data.get('project')
            project_data = success_data.get('project_data')
            file_path = success_data.get('file_path')
            message = success_data.get('message', 'Project created successfully')
            
            if self.project_state_manager and project:
                self.project_state_manager.load_project(project, project_data, file_path)
            
            if self.on_navigate:
                self.on_navigate("project_view")
            
            self._show_success("Success", message)
        else:
            self._show_success("Success", str(success_data))

    def _on_folder_created(self, folder_name: str):
        """Handle successful folder creation"""
        # Refresh current view
        if len(self.current_breadcrumb) >= 2:
            folder_path = self.directory_service.get_folder_path_from_breadcrumb(self.current_breadcrumb)
            contents = self.directory_service.get_folder_contents(folder_path)
            self._display_folder_list(contents, "ten_digit")
        self._show_success("Success", f"Folder '{folder_name}' created successfully")

    def _on_dialog_cancelled(self):
        """Handle dialog cancellation"""
        pass

    def _show_error(self, message: str):
        """Show error dialog"""
        dialog = ft.AlertDialog(
            title=ft.Text("Error"),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update())]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _show_success(self, title: str, message: str):
        """Show success dialog"""
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update())]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
