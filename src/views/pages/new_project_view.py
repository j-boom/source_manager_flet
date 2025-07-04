"""
New Project View (Final)

This view allows users to browse directories and create new projects or folders.
It combines a rich UI with the clean, controller-delegated architecture.
"""
import flet as ft
from typing import List, Dict, Any, Optional
from pathlib import Path

from src.views.base_view import BaseView
from ..components import Breadcrumb  # Import the Breadcrumb component

class NewProjectView(BaseView):
    """A view for browsing folders and creating new projects."""

    def __init__(self, page: ft.Page, controller):
        super().__init__(page, controller)
        
        # --- UI State ---
        # This state is specific to this view and manages what the user sees.
        self.current_path: Path = Path(self.controller.data_service.project_data_dir)
        self.search_text: str = ""
        
        # --- UI Component Placeholders ---
        # These are defined here but built inside the build() method.
        self.breadcrumb: Optional[Breadcrumb] = None
        self.file_list_view: Optional[ft.ListView] = None
        self.header_row: Optional[ft.Row] = None

    def build(self) -> ft.Control:
        """Builds the UI for the view."""
        # Build the components now that we know the theme and controller exist.
        self.breadcrumb = self._build_breadcrumb()
        self.file_list_view = ft.ListView(spacing=5, expand=True)
        self.header_row = self._build_header() # The header is now dynamic

        # Populate the file list for the initial view.
        self._update_file_list()

        return ft.Column(
            controls=[
                self.header_row,
                ft.Container(
                    self.breadcrumb,
                    padding=ft.padding.symmetric(horizontal=20, vertical=5)
                ),
                ft.Container(
                    content=self.file_list_view,
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=20)
                )
            ],
            expand=True,
            spacing=0
        )

    # --- UI Builder Methods ---

    def _build_header(self) -> ft.Row:
        """Builds the header, which can be updated dynamically."""
        return ft.Row(
            [
                ft.Text("Project Browser", theme_style=ft.TextThemeStyle.HEADLINE_SMALL),
                ft.Row(self._get_header_actions())
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            # Wrap in a container for padding and border
            # This will be done by the parent that calls this method
        )
    
    def _get_header_actions(self) -> List[ft.Control]:
        """Determines which action buttons to show based on the current path."""
        actions = [
            self._build_action_button(
                icon=ft.icons.CREATE_NEW_FOLDER_OUTLINED,
                tooltip="Create New Folder",
                on_click=self._on_add_folder_clicked
            ),
            self._build_action_button(
                icon=ft.icons.POST_ADD_ROUNDED,
                tooltip="Create New Project",
                on_click=self._on_add_project_clicked
            )
        ]
        return actions

    def _build_breadcrumb(self) -> Breadcrumb:
        """Builds the breadcrumb component."""
        return Breadcrumb(
            crumbs=self._get_breadcrumb_parts(),
            on_crumb_click=self._on_breadcrumb_clicked
        )

    def _build_action_button(self, icon: str, tooltip: str, on_click) -> ft.IconButton:
        """Builds a consistent IconButton for the header."""
        return ft.IconButton(
            icon=icon,
            tooltip=tooltip,
            on_click=on_click,
            icon_color=self.colors.primary
        )

    # --- Event Handlers ---

    def _on_breadcrumb_clicked(self, index: int):
        """Handles a click on a breadcrumb part."""
        root_path = Path(self.controller.data_service.project_data_dir)
        parts = self._get_breadcrumb_parts()
        new_parts = parts[:index + 1]
        
        if len(new_parts) > 1:
            self.current_path = root_path.joinpath(*new_parts[1:])
        else:
            self.current_path = root_path
        self._update_view()

    def _on_item_clicked(self, e):
        """Handles a click on a file or folder in the list."""
        item_path_str = e.control.data['path']
        is_directory = e.control.data['is_directory']
        
        if is_directory:
            self.current_path = Path(item_path_str)
            self._update_view()
        else:
            # Delegate to the controller
            self.controller.open_project(item_path_str)

    def _on_add_project_clicked(self, e):
        """Tells the controller to show the project creation dialog."""
        self.controller.show_create_project_dialog(parent_path=self.current_path)

    def _on_add_folder_clicked(self, e):
        """Tells the controller to show the folder creation dialog."""
        self.controller.show_create_folder_dialog(parent_path=self.current_path)

    # --- View Update Logic ---

    def _update_view(self):
        """Refreshes the breadcrumb, header, and file list."""
        self.breadcrumb.update_crumbs(self._get_breadcrumb_parts())
        self._update_file_list()
        
        # Rebuild the header to show context-aware buttons
        self.header_row.controls = self._build_header().controls

        self.page.update()

    def _update_file_list(self):
        """Fetches folder contents from the DataService and updates the ListView."""
        contents = self.controller.data_service.get_folder_contents(str(self.current_path))
        self.file_list_view.controls.clear()
        
        if not contents:
            self.file_list_view.controls.append(
                self.show_empty_state("This folder is empty.", icon=ft.icons.FOLDER_OFF_OUTLINED)
            )
        else:
            for item in contents:
                icon = ft.icons.FOLDER_OUTLINED if item['is_directory'] else ft.icons.INSERT_DRIVE_FILE_OUTLINED
                self.file_list_view.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(icon),
                        title=ft.Text(item['name']),
                        on_click=self._on_item_clicked,
                        data={'path': item['path'], 'is_directory': item['is_directory']}
                    )
                )

    def _get_breadcrumb_parts(self) -> List[str]:
        """Calculates breadcrumb parts from the current path."""
        root_path = Path(self.controller.data_service.project_data_dir)
        if self.current_path == root_path:
            return ["Projects"]
        
        relative_path = self.current_path.relative_to(root_path)
        return ["Projects"] + list(relative_path.parts)

