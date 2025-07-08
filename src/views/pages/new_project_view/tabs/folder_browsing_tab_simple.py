"""
Simplified Folder browsing tab for the New Project View that works with the actual DirectoryService
"""

import flet as ft
from .base_tab import BaseTab
from typing import Optional, List, Dict, Any


class FolderBrowsingTab(BaseTab):
    """Tab for browsing and selecting folders for new projects"""
    
    def __init__(self, page: ft.Page, theme_manager=None, directory_service=None, **kwargs):
        super().__init__(page, theme_manager, **kwargs)
        self.directory_service = directory_service
        
        # UI components
        self.primary_dropdown: Optional[ft.Dropdown] = None
        self.search_field: Optional[ft.TextField] = None
        self.content_container: Optional[ft.Container] = None
        
        # State
        self.selected_primary_folder = None
        self.current_breadcrumb = []
        self.current_folders = []
        
        # Callbacks
        self.on_add_project_clicked = kwargs.get('on_add_project_clicked')
        self.on_create_folder_clicked = kwargs.get('on_create_folder_clicked')
    
    def get_tab_text(self) -> str:
        return "Browse Folders"
    
    def get_tab_icon(self) -> str:
        return ft.icons.FOLDER_OPEN
    
    def build(self) -> ft.Control:
        """Build the folder browsing tab content"""
        if not self.directory_service or not self.directory_service.directory_source_citations_path:
            return self._build_error_view("Directory_Source_Citations not found")
        
        return ft.Column([
            self._build_directory_selection(),
            self._build_content_area()
        ], expand=True, spacing=0)
    
    def _build_error_view(self, message: str) -> ft.Control:
        """Build error view"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.ERROR_OUTLINE, size=48, color=ft.colors.RED_400),
                ft.Text(message, size=16, color=ft.colors.RED_400, text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
            alignment=ft.alignment.center,
            expand=True
        )
    
    def _build_directory_selection(self) -> ft.Control:
        """Build directory selection section"""
        self.primary_dropdown = ft.Dropdown(
            label="Select Primary Folder",
            options=[ft.dropdown.Option(folder) for folder in self.directory_service.primary_folders],
            width=300,
            on_change=self._on_primary_folder_changed
        )
        
        self.search_field = ft.TextField(
            label="Search (e.g., 1001)",
            hint_text="Search for 4-digit folders",
            width=300,
            prefix_icon=ft.icons.SEARCH,
            on_submit=self._on_search_submit
        )
        
        # Theme-aware background color
        if self.page.theme_mode == ft.ThemeMode.DARK:
            selection_bg = ft.colors.GREY_900
        else:
            selection_bg = ft.colors.GREY_50
        
        return ft.Container(
            content=ft.Row([
                self.primary_dropdown,
                ft.Container(width=20),
                self.search_field
            ], alignment=ft.MainAxisAlignment.CENTER),
            padding=ft.padding.all(20),
            bgcolor=selection_bg
        )
    
    def _build_content_area(self) -> ft.Control:
        """Build main content area"""
        # Theme-aware colors for initial state
        if self.page.theme_mode == ft.ThemeMode.DARK:
            icon_color = ft.colors.GREY_600
            text_color = ft.colors.GREY_400
        else:
            icon_color = ft.colors.GREY_400
            text_color = ft.colors.GREY_500
        
        self.content_container = ft.Container(
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
        
        return self.content_container
    
    def _on_primary_folder_changed(self, e):
        """Handle primary folder selection"""
        if not e.control.value:
            return
        
        self.selected_primary_folder = e.control.value
        self.current_breadcrumb = [self.selected_primary_folder]
        
        # Get four-digit folders using the correct DirectoryService method
        four_digit_folders = self.directory_service.get_four_digit_folders(self.selected_primary_folder)
        
        self._update_folder_view(four_digit_folders, "four_digit")
    
    def _on_search_submit(self, e):
        """Handle search submit"""
        if not self.search_field or not self.search_field.value or not self.selected_primary_folder:
            return
        
        search_term = self.search_field.value.strip()
        if not search_term:
            return
        
        # Use the DirectoryService search method
        four_digit_folders, ten_digit_folders = self.directory_service.search_four_digit_folders(
            self.selected_primary_folder, 
            search_term
        )
        
        # Show four-digit results first, or ten-digit if no four-digit found
        if four_digit_folders:
            self._update_folder_view(four_digit_folders, "search_results")
        elif ten_digit_folders:
            self._update_folder_view(ten_digit_folders, "search_results")
        else:
            self._show_no_results()
        
        # Clear search after submission
        self.search_field.value = ""
        self.page.update()
    
    def _update_folder_view(self, folders: List[Dict[str, Any]], view_type: str):
        """Update the folder view with given folders"""
        if not self.content_container:
            return
        
        if not folders:
            self._show_no_results()
            return
        
        # Create folder items
        content_controls = []
        
        # Add action buttons for ten-digit folders (when we have navigated to a 4-digit folder)
        if view_type == "ten_digit" and len(self.current_breadcrumb) >= 2:
            action_row = ft.Row([
                ft.ElevatedButton(
                    "Add Project",
                    icon=ft.icons.ADD,
                    on_click=self.on_add_project_clicked,
                    style=ft.ButtonStyle(
                        bgcolor=self._get_theme_color(),
                        color=ft.colors.WHITE
                    )
                ),
                ft.ElevatedButton(
                    "Create New Folder",
                    icon=ft.icons.CREATE_NEW_FOLDER,
                    on_click=self.on_create_folder_clicked,
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.GREEN_600,
                        color=ft.colors.WHITE
                    )
                )
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
            content_controls.append(action_row)
            content_controls.append(ft.Divider())
        
        # Add breadcrumb navigation if we're deeper than primary level
        if len(self.current_breadcrumb) > 1:
            breadcrumb_items = []
            for i, crumb in enumerate(self.current_breadcrumb):
                if i > 0:
                    breadcrumb_items.append(ft.Text(" > ", color=ft.colors.GREY_500))
                breadcrumb_items.append(
                    ft.TextButton(
                        crumb,
                        on_click=lambda e, index=i: self._on_breadcrumb_clicked(index)
                    )
                )
            
            breadcrumb_row = ft.Row(breadcrumb_items, spacing=5)
            content_controls.append(breadcrumb_row)
            content_controls.append(ft.Container(height=10))
        
        # Add folder grid
        folder_items = []
        for folder in folders[:50]:  # Limit to 50 items for performance
            folder_items.append(self._create_folder_item(folder, view_type))
        
        # Create responsive grid
        grid = ft.GridView(
            controls=folder_items,
            runs_count=0,  # Auto-sizing
            max_extent=200,
            child_aspect_ratio=1.0,
            spacing=10,
            run_spacing=10,
            expand=True
        )
        
        content_controls.append(grid)
        
        self.content_container.content = ft.Column(content_controls, expand=True, spacing=10)
        self.content_container.alignment = None
        self.content_container.visible = True
        self.page.update()
    
    def _create_folder_item(self, folder: Dict[str, Any], view_type: str) -> ft.Control:
        """Create a folder item for the grid"""
        # Theme-aware colors
        if self.page.theme_mode == ft.ThemeMode.DARK:
            folder_bg = ft.colors.GREY_800
            folder_hover = ft.colors.GREY_700
            text_color = ft.colors.WHITE
        else:
            folder_bg = ft.colors.BLUE_50
            folder_hover = ft.colors.BLUE_100
            text_color = ft.colors.BLUE_900
        
        folder_name = folder.get('name', str(folder))
        
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.FOLDER, size=48, color=self._get_theme_color()),
                ft.Text(
                    folder_name,
                    size=12,
                    color=text_color,
                    text_align=ft.TextAlign.CENTER,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
            bgcolor=folder_bg,
            border_radius=8,
            padding=ft.padding.all(15),
            ink=True,
            on_click=lambda e, folder_data=folder: self._on_folder_clicked(folder_data, view_type),
            on_hover=lambda e: setattr(e.control, 'bgcolor', folder_hover if e.data == 'true' else folder_bg) or self.page.update()
        )
    
    def _on_folder_clicked(self, folder: Dict[str, Any], view_type: str):
        """Handle folder click"""
        folder_name = folder.get('name', str(folder))
        
        if view_type == "four_digit" or view_type == "search_results":
            # Navigate into four-digit folder to show ten-digit folders
            self.current_breadcrumb.append(folder_name)
            folder_path = self.directory_service.get_folder_path_from_breadcrumb(self.current_breadcrumb)
            
            # Get contents of this folder (should be ten-digit folders)
            contents = self.directory_service.get_folder_contents(folder_path)
            self._update_folder_view(contents, "ten_digit")
    
    def _on_breadcrumb_clicked(self, index: int):
        """Handle breadcrumb click"""
        if index == 0:
            # Back to primary folder selection - show four-digit folders
            self.current_breadcrumb = self.current_breadcrumb[:1]
            four_digit_folders = self.directory_service.get_four_digit_folders(self.current_breadcrumb[0])
            self._update_folder_view(four_digit_folders, "four_digit")
        else:
            # Navigate to specific breadcrumb level
            self.current_breadcrumb = self.current_breadcrumb[:index + 1]
            folder_path = self.directory_service.get_folder_path_from_breadcrumb(self.current_breadcrumb)
            contents = self.directory_service.get_folder_contents(folder_path)
            self._update_folder_view(contents, "folder_contents")
    
    def _show_no_results(self):
        """Show no results found message"""
        if not self.content_container:
            return
        
        self.content_container.content = ft.Column([
            ft.Icon(ft.icons.SEARCH_OFF, size=64, color=ft.colors.GREY_400),
            ft.Text("No folders found", size=16, color=ft.colors.GREY_500)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)
        self.content_container.alignment = ft.alignment.center
        self.page.update()
