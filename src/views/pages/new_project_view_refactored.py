"""Refactored New Project View using service and component architecture"""

import flet as ft
from ..base_view import BaseView
from typing import List, Dict, Any, Optional
from services import DirectoryService, ProjectCreationService
from ..components.dialogs.project_creation_dialog import ProjectCreationDialog
from ..components.dialogs.folder_creation_dialog import FolderCreationDialog
from models.database_manager import DatabaseManager


class NewProjectViewRefactored(BaseView):
    """Refactored new project view with better separation of concerns"""
    
    def __init__(self, page: ft.Page, theme_manager=None, user_config=None, on_back=None, on_project_selected=None):
        super().__init__(page)
        self.theme_manager = theme_manager
        self.user_config = user_config
        self.on_back = on_back
        self.on_project_selected = on_project_selected
        
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
        
        # UI state
        self.selected_primary_folder = None
        self.search_text = ""
        self.current_breadcrumb = []
        
        # UI components
        self.primary_dropdown = None
        self.search_field = None
        self.breadcrumb_row = None
        self.content_container = None
    
    def build(self) -> ft.Control:
        """Build the view"""
        if not self.directory_service.directory_source_citations_path:
            return self._build_error_view("Directory_Source_Citations not found")
        
        return ft.Column([
            self._build_header(),
            self._build_directory_selection(),
            self._build_breadcrumb(),
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
        # Theme-aware header colors
        if self.page.theme_mode == ft.ThemeMode.DARK:
            header_bg = ft.colors.GREY_800
            border_color = ft.colors.GREY_600
        else:
            header_bg = ft.colors.WHITE
            border_color = ft.colors.GREY_300
        
        # Get theme color for button
        theme_color = self._get_icon_color()  # This uses the theme manager's primary color
        
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
                ft.Text("New Project", size=20, weight=ft.FontWeight.BOLD)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.all(20),
            bgcolor=header_bg,
            border=ft.border.only(bottom=ft.BorderSide(1, border_color))
        )
        
        return self.header_container
    
    def _build_directory_selection(self) -> ft.Control:
        """Build directory selection section"""
        self.primary_dropdown = ft.Dropdown(
            label="Select Primary Folder",
            options=[ft.dropdown.Option(folder) for folder in self.directory_service.primary_folders],
            width=300,
            on_change=self._on_primary_folder_changed
        )
        
        self.search_field = ft.TextField(
            label="Search Folders",
            hint_text="Search for 4-digit or 10-digit folders",
            width=300,
            prefix_icon=ft.icons.SEARCH,
            on_change=self._on_search_changed,
            on_submit=self._on_search_submit
        )
        
        # Theme-aware background color
        if self.page.theme_mode == ft.ThemeMode.DARK:
            selection_bg = ft.colors.GREY_900
        else:
            selection_bg = ft.colors.GREY_50
        
        self.directory_selection_container = ft.Container(
            content=ft.Row([
                self.primary_dropdown,
                ft.Container(width=20),
                self.search_field
            ], alignment=ft.MainAxisAlignment.CENTER),
            padding=ft.padding.all(20),
            bgcolor=selection_bg
        )
        
        return self.directory_selection_container
    
    def _build_breadcrumb(self) -> ft.Control:
        """Build breadcrumb navigation"""
        self.breadcrumb_row = ft.Row([], spacing=5)
        return ft.Container(
            content=self.breadcrumb_row,
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            visible=False
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
                ft.Icon(ft.icons.FOLDER_OPEN, size=48, color=icon_color),
                ft.Text("Select a primary folder to begin", color=text_color)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            alignment=ft.alignment.center,
            expand=True,
            visible=True
        )
        
        return self.content_container
    
    # Theme-aware color methods
    def _get_icon_color(self) -> str:
        """Get icon color based on theme"""
        if self.theme_manager:
            current_mode = "dark" if self.page.theme_mode == ft.ThemeMode.DARK else "light"
            return self.theme_manager.get_primary_color() if hasattr(self.theme_manager, 'get_primary_color') else ft.colors.BLUE_700
        return ft.colors.BLUE_700 if self.page.theme_mode != ft.ThemeMode.DARK else ft.colors.BLUE_400

    def _get_text_color(self) -> Optional[str]:
        """Get text color based on theme"""
        if self.theme_manager:
            current_mode = "dark" if self.page.theme_mode == ft.ThemeMode.DARK else "light"
            return self.theme_manager.get_text_color(current_mode) if hasattr(self.theme_manager, 'get_text_color') else None
        return None  # Let Flet use default text color

    def _get_subtitle_color(self) -> str:
        """Get subtitle color based on theme"""
        if self.theme_manager:
            current_mode = "dark" if self.page.theme_mode == ft.ThemeMode.DARK else "light"
            return self.theme_manager.get_subtitle_color(current_mode) if hasattr(self.theme_manager, 'get_subtitle_color') else ft.colors.GREY_600
        return ft.colors.GREY_600 if self.page.theme_mode != ft.ThemeMode.DARK else ft.colors.GREY_400

    def _get_bg_color(self) -> str:
        """Get background color based on theme"""
        return ft.colors.GREY_300 if self.page.theme_mode != ft.ThemeMode.DARK else ft.colors.GREY_600

    # Event Handlers
    def _on_primary_folder_changed(self, e):
        """Handle primary folder selection"""
        self.selected_primary_folder = e.control.value
        if self.selected_primary_folder:
            self.search_field.value = ""
            self.current_breadcrumb = [self.selected_primary_folder]
            self._show_four_digit_folders()
            self._update_breadcrumb()
    
    def _on_search_changed(self, e):
        """Handle search text changes"""
        self.search_text = e.control.value
    
    def _on_search_submit(self, e):
        """Handle search submission"""
        if not self.selected_primary_folder or not self.search_text:
            return
        
        search_term = self.search_text.strip()
        matching_folders, exact_match, four_digit_folder = self.directory_service.search_four_digit_folders(
            self.selected_primary_folder, search_term
        )
        
        if exact_match:
            # Found exact 10-digit match - navigate to it
            self._navigate_to_folder(exact_match['path'], exact_match['name'])
        elif four_digit_folder:
            # Found 4-digit folder but not 10-digit - show creation option
            self._navigate_to_four_digit_with_create_option(four_digit_folder, search_term)
        elif matching_folders:
            # Show matching 4-digit folders
            self._show_search_results(matching_folders)
        else:
            self._show_no_results()
    
    def _on_item_clicked(self, item_path: str, item_name: str, is_directory: Optional[bool] = None):
        """Handle clicking on folder/file items"""
        # Use the is_directory flag if provided, otherwise fall back to path checking
        if is_directory is True or (is_directory is None and (item_path.endswith('/') or self.directory_service.get_folder_contents(item_path))):
            # It's a folder - navigate into it
            self._navigate_to_folder(item_path, item_name)
        else:
            # It's a file - handle selection
            if self.on_project_selected:
                self.on_project_selected(item_path, item_name)
    
    def _on_breadcrumb_clicked(self, index: int):
        """Handle breadcrumb navigation"""
        if index == 0:
            # Back to primary folder view
            self._show_four_digit_folders()
            self.current_breadcrumb = [self.current_breadcrumb[0]]
        else:
            # Navigate to specific breadcrumb level
            self.current_breadcrumb = self.current_breadcrumb[:index + 1]
            folder_path = self.directory_service.get_folder_path_from_breadcrumb(self.current_breadcrumb)
            contents = self.directory_service.get_folder_contents(folder_path)
            self._update_folder_view(contents, "folder_contents")
        
        self._update_breadcrumb()
    
    def _on_add_project_clicked(self, e):
        """Handle add project button click"""
        if not self.directory_service.is_ten_digit_folder(self.current_breadcrumb):
            self._show_error_dialog("Cannot Create Project", 
                                  "Please navigate to a ten-digit folder first to create a project.")
            return
        
        folder_path = self.directory_service.get_folder_path_from_breadcrumb(self.current_breadcrumb)
        ten_digit_number = self.directory_service.extract_ten_digit_number(self.current_breadcrumb[-1])
        
        if ten_digit_number:
            self.project_dialog.show(ten_digit_number, folder_path)
    
    def _on_create_folder_clicked(self, e):
        """Handle create new ten-digit folder button click"""
        if not self.directory_service.is_four_digit_folder(self.current_breadcrumb):
            self._show_error_dialog("Cannot Create Folder", 
                                  "Please navigate to a four-digit folder first to create a ten-digit folder.")
            return
        
        folder_path = self.directory_service.get_folder_path_from_breadcrumb(self.current_breadcrumb)
        self.folder_dialog.show_for_new_folder(folder_path)
    
    def _on_create_specific_folder_clicked(self, ten_digit_number: str):
        """Handle creating a specific ten-digit folder"""
        folder_path = self.directory_service.get_folder_path_from_breadcrumb(self.current_breadcrumb)
        self.folder_dialog.show_for_specific_number(folder_path, ten_digit_number)
    
    def _on_back_clicked(self):
        """Handle back button click"""
        if self.on_back:
            self.on_back()
    
    # Dialog Callbacks
    def _on_project_created(self, message: str):
        """Handle successful project creation"""
        self._refresh_current_view()
        self._show_success_dialog("Success", message)
    
    def _on_folder_created(self, message: str):
        """Handle successful folder creation"""
        self._refresh_current_view()
        self._show_success_dialog("Success", message)
    
    def _on_dialog_cancelled(self):
        """Handle dialog cancellation"""
        pass  # Nothing to do
    
    # Navigation and Display Methods
    def _show_four_digit_folders(self):
        """Show four-digit folders for selected primary folder"""
        if not self.selected_primary_folder:
            return
        
        folders = self.directory_service.get_four_digit_folders(self.selected_primary_folder)
        self._update_folder_view(folders, "folders")
    
    def _show_search_results(self, folders: List[Dict[str, Any]]):
        """Show search results"""
        self._update_folder_view(folders, "search_results")
    
    def _show_no_results(self):
        """Show no results found"""
        # Use theme-aware colors for empty search state
        subtitle_color = self._get_subtitle_color()
        
        self.content_container.content = ft.Column([
            ft.Icon(ft.icons.SEARCH_OFF, size=48, color=subtitle_color),
            ft.Text("No folders found matching your search", color=subtitle_color)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
        self.content_container.alignment = ft.alignment.center
        self.page.update()
    
    def _navigate_to_folder(self, folder_path: str, folder_name: str):
        """Navigate to a specific folder"""
        # Update breadcrumb
        self.current_breadcrumb.append(folder_name)
        
        # Get folder contents
        contents = self.directory_service.get_folder_contents(folder_path)
        self._update_folder_view(contents, "folder_contents")
        self._update_breadcrumb()
    
    def _navigate_to_four_digit_with_create_option(self, four_digit_folder: Dict[str, Any], missing_ten_digit: str):
        """Navigate to four-digit folder with option to create missing ten-digit folder"""
        self._navigate_to_folder(four_digit_folder['path'], four_digit_folder['name'])
        # Show additional create button for the missing folder
        # This could be implemented as an additional UI element
    
    def _update_folder_view(self, items: List[Dict[str, Any]], view_type: str):
        """Update the folder content view"""
        content_controls = []
        
        # Add header with appropriate action button
        if view_type == "folder_contents":
            if self.directory_service.is_four_digit_folder(self.current_breadcrumb):
                # In four-digit folder - show create ten-digit folder button
                header = self._create_header_with_button(
                    f"Contents ({len(items)} items)",
                    "Create New Ten-Digit Folder",
                    ft.icons.CREATE_NEW_FOLDER,
                    ft.colors.BLUE_700,
                    self._on_create_folder_clicked
                )
            elif self.directory_service.is_ten_digit_folder(self.current_breadcrumb):
                # In ten-digit folder - show add project button
                header = self._create_header_with_button(
                    f"Contents ({len(items)} items)",
                    "Add Project",
                    ft.icons.ADD,
                    ft.colors.GREEN_700,
                    self._on_add_project_clicked
                )
            else:
                header = ft.Text(f"Contents ({len(items)} items)", 
                               size=16, weight=ft.FontWeight.BOLD, color=ft.colors.GREY_800)
            
            content_controls.append(header)
            content_controls.append(ft.Container(height=15))
        
        # Add items list or empty state
        if items:
            items_list = self._create_items_list(items)
            content_controls.append(items_list)
        else:
            # Use theme-aware empty state colors
            subtitle_color = self._get_subtitle_color()
                
            empty_state = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.FOLDER_OPEN, size=48, color=subtitle_color),
                    ft.Text("No items found", color=subtitle_color)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                alignment=ft.alignment.center,
                expand=True
            )
            content_controls.append(empty_state)
        
        # Update container
        self.content_container.content = ft.Column(content_controls, expand=True, spacing=10)
        self.content_container.alignment = None
        self.content_container.visible = True
        self.page.update()
    
    def _create_header_with_button(self, title: str, button_text: str, icon, color, on_click) -> ft.Control:
        """Create header row with action button"""
        # Use theme-aware text color
        text_color = self._get_text_color()
        if not text_color:  # Fallback if theme manager doesn't provide text color
            text_color = ft.colors.GREY_200 if self.page.theme_mode == ft.ThemeMode.DARK else ft.colors.GREY_800
        
        return ft.Row([
            ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=text_color),
            ft.Container(expand=True),
            ft.ElevatedButton(
                text=button_text,
                icon=icon,
                on_click=on_click,
                style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=color)
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    def _create_items_list(self, items: List[Dict[str, Any]]) -> ft.Control:
        """Create list view of items"""
        list_items = []
        
        # Get theme-appropriate colors
        icon_color = self._get_icon_color()
        subtitle_color = self._get_subtitle_color()
        
        for item in items:
            icon = ft.icons.FOLDER if item['is_directory'] else ft.icons.DESCRIPTION
            
            tile = ft.ListTile(
                leading=ft.Icon(icon, size=24, color=icon_color),
                title=ft.Text(item['name'], size=14),
                subtitle=ft.Text(f"Path: {item['path']}", size=12, color=subtitle_color),
                on_click=lambda e, path=item['path'], name=item['name'], is_dir=item['is_directory']: self._on_item_clicked(path, name, is_dir),
                content_padding=ft.padding.all(10)
            )
            list_items.append(tile)
        
        return ft.ListView(
            controls=list_items,
            expand=True,
            spacing=5,
            padding=ft.padding.all(10)
        )
    
    def _update_breadcrumb(self):
        """Update breadcrumb navigation"""
        breadcrumb_items = []
        
        for i, part in enumerate(self.current_breadcrumb):
            if i > 0:
                breadcrumb_items.append(ft.Text(" / ", color=ft.colors.GREY_400))
            
            breadcrumb_items.append(
                ft.TextButton(
                    part,
                    on_click=lambda e, idx=i: self._on_breadcrumb_clicked(idx)
                )
            )
        
        self.breadcrumb_row.controls = breadcrumb_items
        self.breadcrumb_row.parent.visible = len(self.current_breadcrumb) > 0
        self.page.update()
    
    def _refresh_current_view(self):
        """Refresh the current folder view"""
        if self.current_breadcrumb:
            folder_path = self.directory_service.get_folder_path_from_breadcrumb(self.current_breadcrumb)
            contents = self.directory_service.get_folder_contents(folder_path)
            self._update_folder_view(contents, "folder_contents")
    
    # Utility Methods
    def _show_success_dialog(self, title: str, message: str):
        """Show success dialog"""
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=lambda e: self._close_dialog(dialog))]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _show_error_dialog(self, title: str, message: str):
        """Show error dialog"""
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=lambda e: self._close_dialog(dialog))]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _close_dialog(self, dialog):
        """Close dialog"""
        dialog.open = False
        self.page.update()

    def refresh_theme(self):
        """Refresh all theme-dependent UI elements"""
        # Refresh header with new theme colors
        if hasattr(self, 'header_container') and self.header_container:
            # Update header background colors
            if self.page.theme_mode == ft.ThemeMode.DARK:
                header_bg = ft.colors.GREY_800
                border_color = ft.colors.GREY_600
            else:
                header_bg = ft.colors.WHITE
                border_color = ft.colors.GREY_300
            
            self.header_container.bgcolor = header_bg
            self.header_container.border = ft.border.only(bottom=ft.BorderSide(1, border_color))
            
            # Update back button with theme color
            theme_color = self._get_icon_color()
            header_row = self.header_container.content
            if header_row and hasattr(header_row, 'controls') and len(header_row.controls) > 0:
                back_button = header_row.controls[0]  # First control is the back button
                back_button.style = ft.ButtonStyle(
                    bgcolor=theme_color,
                    color=ft.colors.WHITE
                )
        
        # Refresh directory selection container
        if hasattr(self, 'directory_selection_container') and self.directory_selection_container:
            if self.page.theme_mode == ft.ThemeMode.DARK:
                selection_bg = ft.colors.GREY_900
            else:
                selection_bg = ft.colors.GREY_50
                
            self.directory_selection_container.bgcolor = selection_bg
        
        # Refresh the current view to update item colors
        if hasattr(self, 'current_breadcrumb') and self.current_breadcrumb:
            folder_path = self.directory_service.get_folder_path_from_breadcrumb(self.current_breadcrumb)
            contents = self.directory_service.get_folder_contents(folder_path)
            self._update_folder_view(contents, "folder_contents")
        
        self.page.update()
