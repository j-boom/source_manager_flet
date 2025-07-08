import flet as ft
from ..base_view import BaseView
import os
from typing import List, Dict, Any, Optional
import re


class NewProjectView(BaseView):
    """New project view - allows browsing and selecting project directories"""
    
    def __init__(self, page: ft.Page, theme_manager=None, user_config=None, on_back=None, on_project_selected=None):
        super().__init__(page)
        self.theme_manager = theme_manager
        self.user_config = user_config
        self.on_back = on_back
        self.on_project_selected = on_project_selected
        
        # File structure paths
        self.directory_source_citations_path = self._find_directory_source_citations()
        self.primary_folders = self._get_primary_folders()
        
        # UI state
        self.selected_primary_folder = None
        self.search_text = ""
        self.current_breadcrumb = []
        self.current_folder_content = []
        
        # UI components (will be initialized in build)
        self.primary_dropdown = None
        self.search_field = None
        self.breadcrumb_row = None
        self.folder_view = None
        self.content_container = None
    
    def _find_directory_source_citations(self) -> Optional[str]:
        """Find the Directory_Source_Citations file/folder"""
        # Look for the file in current directory and common locations
        possible_paths = [
            "./Directory_Source_Citations",
            "../Directory_Source_Citations",
            "../../Directory_Source_Citations",
            "./data/Directory_Source_Citations",
            "./sources/Directory_Source_Citations"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return os.path.abspath(path)
        
        # If not found, return None - we'll handle this in the UI
        return None
    
    def _get_primary_folders(self) -> List[str]:
        """Get the list of primary folders (6 main directories)"""
        if not self.directory_source_citations_path or not os.path.exists(self.directory_source_citations_path):
            return []
        
        try:
            items = os.listdir(self.directory_source_citations_path)
            folders = [item for item in items if os.path.isdir(os.path.join(self.directory_source_citations_path, item))]
            return sorted(folders)
        except (OSError, PermissionError):
            return []
    
    def _get_four_digit_folders(self, primary_folder: str) -> List[Dict[str, str]]:
        """Get all four-digit folders within a primary folder"""
        if not self.directory_source_citations_path:
            return []
        
        primary_path = os.path.join(self.directory_source_citations_path, primary_folder)
        if not os.path.exists(primary_path):
            return []
        
        four_digit_folders = []
        try:
            items = os.listdir(primary_path)
            for item in items:
                item_path = os.path.join(primary_path, item)
                if os.path.isdir(item_path) and re.match(r'^\d{4}$', item):
                    four_digit_folders.append({
                        'name': item,
                        'path': item_path,
                        'full_path': f"{primary_folder}/{item}",
                        'is_directory': True  # Add this key that _create_items_list expects
                    })
        except (OSError, PermissionError):
            pass
        
        return sorted(four_digit_folders, key=lambda x: x['name'])
    
    def _get_folder_contents(self, folder_path: str) -> List[Dict[str, Any]]:
        """Get contents of a folder (files and subdirectories)"""
        if not os.path.exists(folder_path):
            return []
        
        contents = []
        try:
            items = os.listdir(folder_path)
            for item in items:
                item_path = os.path.join(folder_path, item)
                is_dir = os.path.isdir(item_path)
                
                # Check if it's a ten-digit file/folder
                ten_digit_match = re.match(r'^(\d{10})(.*)$', item)
                
                contents.append({
                    'name': item,
                    'path': item_path,
                    'is_directory': is_dir,
                    'is_ten_digit': bool(ten_digit_match),
                    'ten_digit_prefix': ten_digit_match.group(1) if ten_digit_match else None,
                    'suffix': ten_digit_match.group(2).strip() if ten_digit_match else None
                })
        except (OSError, PermissionError):
            pass
        
        # Sort: directories first, then files, then by name
        contents.sort(key=lambda x: (not x['is_directory'], x['name']))
        return contents
    
    def _search_four_digit_folders(self, primary_folder: str, search_term: str) -> tuple:
        """Search for four-digit folders containing the search term
        Returns: (matching_folders, exact_ten_digit_match_path, four_digit_with_missing_ten_digit)
        """
        if not search_term.strip():
            return self._get_four_digit_folders(primary_folder), None, None
        
        all_folders = self._get_four_digit_folders(primary_folder)
        search_lower = search_term.lower().strip()
        
        # Check if search term is a 10-digit number
        ten_digit_search = re.match(r'^(\d{10}).*$', search_term.strip())
        exact_ten_digit_match = None
        four_digit_with_missing_ten_digit = None
        
        if ten_digit_search:
            ten_digit_number = ten_digit_search.group(1)
            four_digit_prefix = ten_digit_number[:4]
            
            # Find the four-digit folder that should contain this ten-digit folder
            target_four_digit_folder = None
            for folder in all_folders:
                if folder['name'] == four_digit_prefix:
                    target_four_digit_folder = folder
                    break
            
            if target_four_digit_folder:
                # Check if the ten-digit folder exists within it
                contents = self._get_folder_contents(target_four_digit_folder['path'])
                ten_digit_found = False
                
                for content in contents:
                    if content['is_ten_digit'] and content['ten_digit_prefix'] == ten_digit_number:
                        exact_ten_digit_match = content['path']
                        ten_digit_found = True
                        break
                
                if not ten_digit_found:
                    # Ten-digit folder doesn't exist, but four-digit folder does
                    four_digit_with_missing_ten_digit = {
                        'folder': target_four_digit_folder,
                        'missing_ten_digit': ten_digit_number
                    }
                
                # Return early for ten-digit searches
                return [target_four_digit_folder] if target_four_digit_folder else [], exact_ten_digit_match, four_digit_with_missing_ten_digit
        
        # Regular search in folder contents
        matching_folders = []
        for folder in all_folders:
            contents = self._get_folder_contents(folder['path'])
            folder_matches = False
            
            for content in contents:
                if content['is_ten_digit'] and search_lower in content['name'].lower():
                    folder_matches = True
                    break
            
            if folder_matches:
                matching_folders.append(folder)
        
        return matching_folders, exact_ten_digit_match, four_digit_with_missing_ten_digit
    
    def build(self) -> ft.Control:
        """Build the new project page content"""
        return ft.Container(
            content=ft.Column([
                # Header Section
                self._build_header(),
                
                # Directory Selection Section
                self._build_directory_selection(),
                
                # Breadcrumb Section
                self._build_breadcrumb(),
                
                # Folder Content Section
                self._build_folder_content(),
                
            ], spacing=20),
            padding=20,
            expand=True,
        )
    
    def _build_header(self) -> ft.Control:
        """Build the header section"""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.IconButton(
                        icon=ft.icons.ARROW_BACK,
                        icon_color=ft.colors.BLUE_700,
                        on_click=self._on_back_clicked,
                        tooltip="Back"
                    ),
                    ft.Text(
                        "Create New Project",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.BLUE_700
                    ),
                ], alignment=ft.MainAxisAlignment.START),
                ft.Text(
                    "Browse and select a source directory for your new project",
                    size=16,
                    color=ft.colors.GREY_600
                ),
            ]),
            padding=ft.padding.only(bottom=10)
        )
    
    def _build_directory_selection(self) -> ft.Control:
        """Build the directory selection section with dropdown and search"""
        # Primary folder dropdown
        self.primary_dropdown = ft.Dropdown(
            label="Select Primary Folder",
            options=[ft.dropdown.Option(folder) for folder in self.primary_folders],
            on_change=self._on_primary_folder_changed,
            width=300,
            disabled=len(self.primary_folders) == 0
        )
        
        # Search field
        self.search_field = ft.TextField(
            label="Search for content",
            hint_text="Search for files or folders...",
            on_change=self._on_search_changed,
            on_submit=self._on_search_submit,
            disabled=True,  # Enabled when primary folder is selected
            width=400,
            prefix_icon=ft.icons.SEARCH
        )
        
        # Status message
        status_text = "Select a primary folder to begin" if len(self.primary_folders) > 0 else "Directory_Source_Citations not found"
        status_color = ft.colors.GREY_600 if len(self.primary_folders) > 0 else ft.colors.RED_400
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    self.primary_dropdown,
                    self.search_field,
                ], spacing=20),
                ft.Text(
                    status_text,
                    size=12,
                    color=status_color
                ),
            ], spacing=10),
            padding=ft.padding.only(bottom=10)
        )
    
    def _build_breadcrumb(self) -> ft.Control:
        """Build the breadcrumb navigation"""
        self.breadcrumb_row = ft.Row(
            controls=[],
            spacing=5,
            visible=False
        )
        return self.breadcrumb_row
    
    def _build_folder_content(self) -> ft.Control:
        """Build the folder content view"""
        self.content_container = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Folder contents will appear here",
                    size=14,
                    color=ft.colors.GREY_500,
                    text_align=ft.TextAlign.CENTER
                )
            ]),
            padding=20,
            bgcolor=self._get_card_bg_color(),
            border=ft.border.all(1, self._get_card_border_color()),
            border_radius=8,
            visible=False,
            expand=True,
            width=None  # Allow full width expansion
        )
        return self.content_container
    
    def _get_card_bg_color(self) -> str:
        """Get card background color based on theme"""
        if self.theme_manager:
            current_mode = "dark" if self.page.theme_mode == ft.ThemeMode.DARK else "light"
            return self.theme_manager.get_card_bg_color(current_mode)
        return ft.colors.WHITE if self.page.theme_mode != ft.ThemeMode.DARK else ft.colors.GREY_700
    
    def _get_card_border_color(self) -> str:
        """Get card border color based on theme"""
        if self.theme_manager:
            current_mode = "dark" if self.page.theme_mode == ft.ThemeMode.DARK else "light"
            return self.theme_manager.get_card_border_color(current_mode)
        return ft.colors.GREY_300 if self.page.theme_mode != ft.ThemeMode.DARK else ft.colors.GREY_600
    
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
    
    def _on_primary_folder_changed(self, e):
        """Handle primary folder selection"""
        self.selected_primary_folder = e.control.value
        if self.search_field:
            self.search_field.disabled = False
            self.search_field.value = ""
        self.search_text = ""
        
        # Update breadcrumb
        self._update_breadcrumb([self.selected_primary_folder])
        
        # Show all four-digit folders in this primary folder
        self._show_four_digit_folders()
        
        self.page.update()
    
    def _on_search_changed(self, e):
        """Handle search text changes"""
        self.search_text = e.control.value
    
    def _on_search_submit(self, e):
        """Handle search submission"""
        if not self.selected_primary_folder or not self.search_text.strip():
            return
        
        # Search for matching folders
        matching_folders, exact_ten_digit_match, four_digit_with_missing_ten_digit = self._search_four_digit_folders(self.selected_primary_folder, self.search_text)
        
        if exact_ten_digit_match:
            # Exact ten-digit match found, open that specific folder
            relative_path = os.path.relpath(exact_ten_digit_match, self.directory_source_citations_path)
            breadcrumb_path = relative_path.replace(os.sep, '/')
            self._open_folder(exact_ten_digit_match, breadcrumb_path)
        elif four_digit_with_missing_ten_digit:
            # Four-digit folder exists but ten-digit folder is missing
            folder_info = four_digit_with_missing_ten_digit['folder']
            missing_ten_digit = four_digit_with_missing_ten_digit['missing_ten_digit']
            self._open_folder_with_create_option(folder_info['path'], folder_info['full_path'], missing_ten_digit)
        elif len(matching_folders) == 1:
            # Single four-digit folder match, open the folder
            folder = matching_folders[0]
            self._open_folder(folder['path'], folder['full_path'])
        else:
            # Show search results (multiple matches or no matches)
            self._show_search_results(matching_folders)
    
    def _update_breadcrumb(self, path_parts: List[str]):
        """Update the breadcrumb navigation"""
        self.current_breadcrumb = path_parts
        
        if not self.breadcrumb_row:
            return
        
        controls = []
        for i, part in enumerate(path_parts):
            if i > 0:
                controls.append(ft.Text(" / ", color=ft.colors.GREY_400))
            
            controls.append(ft.TextButton(
                text=part,
                on_click=lambda e, idx=i: self._on_breadcrumb_clicked(idx)
            ))
        
        self.breadcrumb_row.controls = controls
        self.breadcrumb_row.visible = len(path_parts) > 0
        self.page.update()
    
    def _update_folder_view(self, items: List[Dict], view_type: str):
        """Update the folder content view"""
        if not self.content_container:
            return

        # Create the main content column
        content_controls = []
        
        # Determine if we're in a four-digit folder
        is_four_digit_folder = False
        if (len(self.current_breadcrumb) == 2 and 
            len(self.current_breadcrumb[1]) == 4 and 
            self.current_breadcrumb[1].isdigit()):
            is_four_digit_folder = True

        # Add header with appropriate buttons
        if view_type == "folder_contents":
            if is_four_digit_folder:
                # In four-digit folder - show "Create New Ten-Digit Folder" button
                header_row = ft.Row([
                    ft.Text(
                        f"Contents ({len(items)} items)",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.GREY_800
                    ),
                    ft.Container(expand=True),  # Spacer
                    ft.ElevatedButton(
                        text="Create New Ten-Digit Folder",
                        icon=ft.icons.CREATE_NEW_FOLDER,
                        on_click=self._on_create_new_ten_digit_folder_clicked,
                        style=ft.ButtonStyle(
                            color=ft.colors.WHITE,
                            bgcolor=ft.colors.BLUE_700
                        )
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            else:
                # In ten-digit folder - show "Add Project" button
                header_row = ft.Row([
                    ft.Text(
                        f"Contents ({len(items)} items)",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.GREY_800
                    ),
                    ft.Container(expand=True),  # Spacer
                    ft.ElevatedButton(
                        text="Add Project",
                        icon=ft.icons.ADD,
                        on_click=self._on_add_project_clicked,
                        style=ft.ButtonStyle(
                            color=ft.colors.WHITE,
                            bgcolor=ft.colors.GREEN_700
                        )
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            content_controls.append(header_row)
            content_controls.append(ft.Container(height=15))  # Spacing
        elif view_type == "folders":
            # Show header for four-digit folders list
            header_row = ft.Text(
                f"Four-Digit Folders ({len(items)} folders)",
                size=16,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.GREY_800
            )
            content_controls.append(header_row)
            content_controls.append(ft.Container(height=15))  # Spacing
        
        # Add the items content
        if not items:
            items_content = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.FOLDER_OPEN, size=48, color=ft.colors.GREY_400),
                    ft.Text("No items found", color=ft.colors.GREY_500)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                alignment=ft.alignment.center,
                expand=True
            )
        else:
            items_content = self._create_items_list(items, view_type)
        
        content_controls.append(items_content)
        
        # Set the content
        self.content_container.content = ft.Column(
            controls=content_controls,
            spacing=0,
            expand=True
        )
        self.content_container.visible = True
        self.page.update()
    
    def _show_four_digit_folders(self):
        """Show all four-digit folders in the selected primary folder"""
        if not self.selected_primary_folder:
            return
        
        folders = self._get_four_digit_folders(self.selected_primary_folder)
        self._update_folder_view(folders, "folders")
    
    def _show_search_results(self, matching_folders: List[Dict[str, str]]):
        """Show search results"""
        self._update_folder_view(matching_folders, "search_results")
    
    def _open_folder(self, folder_path: str, breadcrumb_path: str):
        """Open a specific folder and show its contents"""
        contents = self._get_folder_contents(folder_path)
        breadcrumb_parts = breadcrumb_path.split('/')
        self._update_breadcrumb(breadcrumb_parts)
        self._update_folder_view(contents, "folder_contents")
    
    def _open_folder_with_create_option(self, folder_path: str, breadcrumb_path: str, missing_ten_digit: str):
        """Open a four-digit folder and show option to create missing ten-digit folder"""
        contents = self._get_folder_contents(folder_path)
        breadcrumb_parts = breadcrumb_path.split('/')
        self._update_breadcrumb(breadcrumb_parts)
        
        # Store the missing ten-digit info for later use
        self.missing_ten_digit_folder = missing_ten_digit
        
        # Update the folder view with a special indicator for the missing folder
        self._update_folder_view_with_create_option(contents, missing_ten_digit)
    
    def _update_folder_view_with_create_option(self, items: List[Dict], missing_ten_digit: str):
        """Update folder view with option to create missing ten-digit folder"""
        if not self.content_container:
            return
        
        # Create the main content column
        content_controls = []
        
        # Add header with "Add" button and "Create Missing Folder" button
        header_row = ft.Row([
            ft.Text(
                f"Contents ({len(items)} items)",
                size=16,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.GREY_800
            ),
            ft.Container(expand=True),  # Spacer
            ft.ElevatedButton(
                text=f"Create {missing_ten_digit}",
                icon=ft.icons.CREATE_NEW_FOLDER,
                on_click=lambda e: self._on_create_ten_digit_folder_clicked(missing_ten_digit),
                style=ft.ButtonStyle(
                    color=ft.colors.WHITE,
                    bgcolor=ft.colors.ORANGE_700
                )
            ),
            ft.Container(width=10),  # Small spacer
            ft.ElevatedButton(
                text="Add Project",
                icon=ft.icons.ADD,
                on_click=self._on_add_project_clicked,
                style=ft.ButtonStyle(
                    color=ft.colors.WHITE,
                    bgcolor=ft.colors.GREEN_700
                )
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Add info message about missing folder
        info_message = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.INFO_OUTLINE, size=20, color=ft.colors.ORANGE_700),
                ft.Text(
                    f"The ten-digit folder '{missing_ten_digit}' doesn't exist. Click 'Create {missing_ten_digit}' to create it.",
                    size=12,
                    color=ft.colors.ORANGE_700
                )
            ], spacing=8),
            padding=ft.padding.all(10),
            bgcolor=ft.colors.ORANGE_50,
            border=ft.border.all(1, ft.colors.ORANGE_200),
            border_radius=5
        )
        
        content_controls.extend([header_row, ft.Container(height=10), info_message, ft.Container(height=15)])
        
        # Add the items content
        if not items:
            items_content = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.FOLDER_OPEN, size=48, color=ft.colors.GREY_400),
                    ft.Text("No items found", color=ft.colors.GREY_500)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                alignment=ft.alignment.center,
                expand=True
            )
        else:
            items_content = self._create_items_list(items, "folder_contents")
        
        content_controls.append(items_content)
        
        # Set the content
        self.content_container.content = ft.Column(
            controls=content_controls,
            spacing=0,
            expand=True
        )
        self.content_container.visible = True
        self.page.update()
    
    def _on_create_ten_digit_folder_clicked(self, ten_digit_number: str):
        """Handle creating a new ten-digit folder"""
        # Show dialog to get folder name
        folder_name_field = ft.TextField(
            label="Folder Name (optional)",
            hint_text="e.g., Project Description",
            width=300
        )
        
        def create_folder(e):
            folder_name = folder_name_field.value or ""
            folder_name = folder_name.strip()
            full_folder_name = ten_digit_number
            if folder_name:
                full_folder_name += f" {folder_name}"
            
            # Create the folder
            current_path = self._get_current_folder_path()
            if current_path:
                new_folder_path = os.path.join(current_path, full_folder_name)
                try:
                    os.makedirs(new_folder_path, exist_ok=True)
                    print(f"Created folder: {new_folder_path}")
                    
                    # Close dialog and refresh the view
                    dialog.open = False
                    self.page.update()
                    
                    # Refresh the current folder view
                    contents = self._get_folder_contents(current_path)
                    breadcrumb_parts = self.current_breadcrumb
                    self._update_breadcrumb(breadcrumb_parts)
                    self._update_folder_view(contents, "folder_contents")
                    
                except OSError as ex:
                    print(f"Error creating folder: {ex}")
                    # Show error message
                    error_dialog = ft.AlertDialog(
                        title=ft.Text("Error"),
                        content=ft.Text(f"Failed to create folder: {ex}"),
                        actions=[ft.TextButton("OK", on_click=lambda e: self._close_dialog(error_dialog))]
                    )
                    self.page.dialog = error_dialog
                    error_dialog.open = True
                    self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"Create {ten_digit_number} Folder"),
            content=ft.Column([
                ft.Text(f"Create a new ten-digit folder: {ten_digit_number}"),
                ft.Container(height=10),
                folder_name_field
            ], tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self._close_dialog(dialog)),
                ft.ElevatedButton("Create Folder", on_click=create_folder)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _on_create_new_ten_digit_folder_clicked(self, e):
        """Handle creating a new ten-digit folder when no specific folder is searched"""
        # Show dialog to get the ten-digit number and optional description
        ten_digit_field = ft.TextField(
            label="Ten-Digit Number *",
            hint_text="e.g., 1001234567",
            width=300,
            max_length=10
        )
        
        folder_name_field = ft.TextField(
            label="Folder Description (optional)",
            hint_text="e.g., Project Description",
            width=300
        )
        
        error_text = ft.Text("", color=ft.colors.RED_400, size=12, visible=False)
        
        def validate_ten_digit(e):
            """Validate ten-digit number format"""
            value = e.control.value.strip() if e.control.value else ""
            
            if value and (not value.isdigit() or len(value) != 10):
                e.control.error_text = "Must be exactly 10 digits"
            else:
                e.control.error_text = None
            self.page.update()
        
        def create_folder(e):
            ten_digit = ten_digit_field.value.strip() if ten_digit_field.value else ""
            folder_desc = folder_name_field.value.strip() if folder_name_field.value else ""
            
            # Validate
            if not ten_digit:
                error_text.value = "Ten-digit number is required"
                error_text.visible = True
                self.page.update()
                return
            
            if not ten_digit.isdigit() or len(ten_digit) != 10:
                error_text.value = "Ten-digit number must be exactly 10 digits"
                error_text.visible = True
                self.page.update()
                return
            
            # Build full folder name
            full_folder_name = ten_digit
            if folder_desc:
                full_folder_name += f" {folder_desc}"
            
            # Create the folder
            current_path = self._get_current_folder_path()
            if current_path:
                new_folder_path = os.path.join(current_path, full_folder_name)
                try:
                    os.makedirs(new_folder_path, exist_ok=True)
                    print(f"Created folder: {new_folder_path}")
                    
                    # Close dialog and refresh the view
                    dialog.open = False
                    self.page.update()
                    
                    # Refresh the current folder view
                    contents = self._get_folder_contents(current_path)
                    breadcrumb_parts = self.current_breadcrumb
                    self._update_breadcrumb(breadcrumb_parts)
                    self._update_folder_view(contents, "folder_contents")
                    
                except OSError as ex:
                    error_text.value = f"Error creating folder: {ex}"
                    error_text.visible = True
                    self.page.update()
        
        # Wire up validation
        ten_digit_field.on_change = validate_ten_digit
        
        dialog = ft.AlertDialog(
            title=ft.Text("Create New Ten-Digit Folder"),
            content=ft.Column([
                ft.Text("Create a new ten-digit folder in this directory:"),
                ft.Container(height=10),
                ten_digit_field,
                ft.Container(height=10),
                folder_name_field,
                ft.Container(height=10),
                error_text
            ], tight=True, width=400),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self._close_dialog(dialog)),
                ft.ElevatedButton("Create Folder", on_click=create_folder)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def refresh_theme(self):
        """Refresh the view with current theme settings"""
        # If we have a current view displayed, refresh it
        if hasattr(self, 'current_breadcrumb') and self.current_breadcrumb:
            if len(self.current_breadcrumb) == 1:
                # We're showing four-digit folders
                self._show_four_digit_folders()
            else:
                # We're showing folder contents
                folder_path = self._get_current_folder_path()
                if folder_path:
                    contents = self._get_folder_contents(folder_path)
                    self._update_folder_view(contents, "folder_contents")
        
        # Update the page
        self.page.update()

    def _get_current_folder_path(self) -> str:
        """Get the current folder path from breadcrumb"""
        if self.current_breadcrumb and self.directory_source_citations_path:
            path_parts = [self.directory_source_citations_path] + self.current_breadcrumb
            return os.path.join(*path_parts)
        return ""

    def _create_items_list(self, items: List[Dict], view_type: str) -> ft.Control:
        """Create a list view of items"""
        list_items = []
        
        # Get theme-appropriate colors
        icon_color = self._get_icon_color()
        text_color = self._get_text_color()
        subtitle_color = self._get_subtitle_color()
        
        for item in items:
            # Determine icon based on type
            icon = ft.icons.FOLDER if item['is_directory'] else ft.icons.DESCRIPTION
            
            # Create the list tile
            tile = ft.ListTile(
                leading=ft.Icon(icon, size=24, color=icon_color),
                title=ft.Text(item['name'], size=14, color=text_color),
                subtitle=ft.Text(f"Path: {item['path']}", size=12, color=subtitle_color),
                on_click=lambda e, path=item['path'], name=item['name']: self._on_item_clicked(path, name),
                content_padding=ft.padding.all(10),
            )
            
            list_items.append(tile)
        
        return ft.ListView(
            controls=list_items,
            expand=True,
            spacing=5,
            padding=ft.padding.all(10)
        )

    def _on_item_clicked(self, item_path: str, item_name: str):
        """Handle item click"""
        if os.path.isdir(item_path):
            # It's a folder - navigate into it
            relative_path = os.path.relpath(item_path, self.directory_source_citations_path)
            breadcrumb_path = relative_path.replace(os.sep, '/')
            self._open_folder(item_path, breadcrumb_path)
        else:
            # It's a file - handle file selection
            if self.on_project_selected:
                self.on_project_selected(item_path, item_name)

    def _close_dialog(self, dialog):
        """Close the dialog"""
        dialog.open = False
        self.page.update()

    def _on_breadcrumb_clicked(self, index: int):
        """Handle breadcrumb navigation"""
        if index == 0:
            # Back to primary folder view (show four-digit folders)
            self._show_four_digit_folders()
            self._update_breadcrumb([self.current_breadcrumb[0]])
        else:
            # Navigate to a specific level in the breadcrumb
            target_breadcrumb = self.current_breadcrumb[:index + 1]
            
            # Build the path to the target folder
            if self.directory_source_citations_path and len(target_breadcrumb) >= 2:
                path_parts = [self.directory_source_citations_path] + target_breadcrumb
                target_path = os.path.join(*path_parts)
                
                if os.path.exists(target_path):
                    # Update breadcrumb and show contents
                    self._update_breadcrumb(target_breadcrumb)
                    contents = self._get_folder_contents(target_path)
                    self._update_folder_view(contents, "folder_contents")

    def _on_add_project_clicked(self, e):
        """Handle add project button click"""
        # Get the current folder path for context
        current_folder_path = ""
        ten_digit_number = ""
        
        if self.current_breadcrumb and len(self.current_breadcrumb) >= 2 and self.directory_source_citations_path:
            # We're in a specific folder, get its path
            primary_folder = self.current_breadcrumb[0]
            folder_name = self.current_breadcrumb[-1]
            current_folder_path = os.path.join(self.directory_source_citations_path, primary_folder, folder_name)
            
            # Extract ten-digit number from folder name
            import re
            ten_digit_match = re.match(r'^(\d{10})', folder_name)
            if ten_digit_match:
                ten_digit_number = ten_digit_match.group(1)
        
        if not current_folder_path or not ten_digit_number:
            # Show error if we're not in a proper ten-digit folder
            error_dialog = ft.AlertDialog(
                title=ft.Text("Cannot Create Project"),
                content=ft.Text("Please navigate to a ten-digit folder first to create a project."),
                actions=[ft.TextButton("OK", on_click=lambda e: self._close_dialog(error_dialog))]
            )
            self.page.dialog = error_dialog
            error_dialog.open = True
            self.page.update()
            return
        
        # Show project creation form
        self._show_project_creation_form(current_folder_path, ten_digit_number)

    def _show_project_creation_form(self, folder_path: str, ten_digit_number: str):
        """Show the project creation form dialog"""
        import datetime
        
        # Create form fields
        project_type_dropdown = ft.Dropdown(
            label="Project Type *",
            options=[
                ft.dropdown.Option("CCR"),
                ft.dropdown.Option("GSC"), 
                ft.dropdown.Option("STD"),
                ft.dropdown.Option("FCR"),
                ft.dropdown.Option("COM"),
                ft.dropdown.Option("CRS"),
                ft.dropdown.Option("OTH")
            ],
            width=400
        )
        
        suffix_field = ft.TextField(
            label="Suffix *",
            hint_text="ABC123 format",
            width=400,
            max_length=6
        )
        
        # Year dropdown
        current_year = datetime.datetime.now().year
        year_dropdown = ft.Dropdown(
            label="Request Year *",
            options=[ft.dropdown.Option(str(year)) for year in range(current_year, current_year + 5)],
            value=str(current_year),
            width=400
        )
        
        document_title_field = ft.TextField(
            label="Document Title",
            hint_text="Required for OTH projects",
            width=400,
            visible=False
        )
        
        error_text = ft.Text("", color=ft.colors.RED_400, size=12, visible=False)
        preview_text = ft.Text("", size=12, color=ft.colors.BLUE_700, weight=ft.FontWeight.BOLD)
        
        def update_preview():
            """Update filename preview"""
            project_type = project_type_dropdown.value
            suffix = suffix_field.value.strip().upper() if suffix_field.value else ""
            year = year_dropdown.value
            doc_title = document_title_field.value.strip() if document_title_field.value else ""
            
            if not project_type or not year:
                preview_text.value = "Please fill required fields"
                preview_text.color = ft.colors.GREY_500
            else:
                parts = [ten_digit_number]
                if suffix:
                    parts.append(suffix)
                if project_type:
                    parts.append(project_type)
                if project_type == "OTH" and doc_title:
                    parts.append(doc_title)
                if year:
                    parts.append(year)
                
                filename = " - ".join(parts) + ".json"
                preview_text.value = f"Filename: {filename}"
                preview_text.color = ft.colors.BLUE_700
            
            self.page.update()
        
        def on_project_type_change(e):
            """Handle project type changes"""
            project_type = e.control.value
            document_title_field.visible = (project_type == "OTH")
            
            if project_type == "GSC":
                suffix_field.label = "Suffix (Optional)"
            else:
                suffix_field.label = "Suffix *"
            
            update_preview()
        
        def on_field_change(e):
            """Handle any field change"""
            update_preview()
        
        def validate_suffix(e):
            """Validate suffix format"""
            import re
            suffix = e.control.value.strip().upper() if e.control.value else ""
            
            if suffix:
                if re.match(r'^[A-Z]{3}\d{3}$', suffix):
                    e.control.value = suffix
                    e.control.error_text = None
                else:
                    e.control.error_text = "Format: ABC123"
            else:
                e.control.error_text = None
            
            update_preview()
        
        def create_project(e):
            """Create the project file"""
            import json
            import re
            
            # Get values
            project_type = project_type_dropdown.value
            suffix = suffix_field.value.strip().upper() if suffix_field.value else ""
            year = year_dropdown.value
            doc_title = document_title_field.value.strip() if document_title_field.value else ""
            
            # Validate
            errors = []
            if not project_type:
                errors.append("Project type is required")
            if not year:
                errors.append("Request year is required")
            if project_type != "GSC" and not suffix:
                errors.append("Suffix is required for this project type")
            if project_type == "OTH" and not doc_title:
                errors.append("Document title is required for OTH projects")
            if suffix and not re.match(r'^[A-Z]{3}\d{3}$', suffix):
                errors.append("Suffix must be in format ABC123")
            
            if errors:
                error_text.value = "; ".join(errors)
                error_text.visible = True
                self.page.update()
                return
            
            # Build filename
            parts = [ten_digit_number]
            if suffix:
                parts.append(suffix)
            if project_type:
                parts.append(project_type)
            if project_type == "OTH" and doc_title:
                parts.append(doc_title)
            if year:
                parts.append(year)
            
            filename = " - ".join(parts) + ".json"
            file_path = os.path.join(folder_path, filename)
            
            # Create project data
            project_data = {
                "project_id": ten_digit_number,
                "project_type": project_type,
                "suffix": suffix if suffix else None,
                "document_title": doc_title if doc_title else None,
                "request_year": int(year) if year else None,
                "created_date": datetime.datetime.now().isoformat(),
                "status": "active",
                "metadata": {
                    "folder_path": folder_path,
                    "filename": filename
                }
            }
            
            try:
                # Write JSON file
                with open(file_path, 'w') as f:
                    json.dump(project_data, f, indent=4)
                
                # Add to recent projects
                if self.user_config:
                    display_name = " - ".join(parts)
                    self.user_config.add_recent_site(display_name, folder_path)
                
                # Close dialog
                self._close_dialog(dialog)
                
                # Refresh view
                contents = self._get_folder_contents(folder_path)
                self._update_folder_view(contents, "folder_contents")
                
                # Show success
                success_dialog = ft.AlertDialog(
                    title=ft.Text("Success"),
                    content=ft.Text(f"Project '{filename}' created successfully!"),
                    actions=[ft.TextButton("OK", on_click=lambda e: self._close_dialog(success_dialog))]
                )
                self.page.dialog = success_dialog
                success_dialog.open = True
                self.page.update()
                
            except Exception as ex:
                error_text.value = f"Error creating file: {str(ex)}"
                error_text.visible = True
                self.page.update()
        
        # Wire up events
        project_type_dropdown.on_change = on_project_type_change
        suffix_field.on_change = validate_suffix
        year_dropdown.on_change = on_field_change
        document_title_field.on_change = on_field_change
        
        # Create dialog content
        dialog_content = ft.Column([
            ft.Text(f"Create New Project: {ten_digit_number}", 
                   size=16, weight=ft.FontWeight.BOLD),
            ft.Container(height=15),
            
            # Form fields - vertically stacked
            project_type_dropdown,
            ft.Container(height=10),
            suffix_field,
            ft.Container(height=10),
            year_dropdown,
            ft.Container(height=10),
            document_title_field,
            
            ft.Container(height=15),
            error_text,
            
            ft.Container(height=10),
            ft.Text("Preview:", size=12, weight=ft.FontWeight.BOLD),
            preview_text,
            
        ], spacing=5, tight=True, width=500)
        
        # Create dialog
        dialog = ft.AlertDialog(
            title=ft.Text("Add New Project"),
            content=dialog_content,
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self._close_dialog(dialog)),
                ft.ElevatedButton(
                    "Create Project", 
                    on_click=create_project,
                    style=ft.ButtonStyle(
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.GREEN_700
                    )
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
        
        # Initial preview
        update_preview()

    def _on_back_clicked(self, e):
        """Handle back button click"""
        if self.on_back:
            self.on_back()
        else:
            print("Back clicked")
