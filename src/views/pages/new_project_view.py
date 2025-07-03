"""
New Project View (Refactored)

This view allows users to browse directories and create new projects or folders.
It has been refactored to align with the application's MVC-like architecture.
"""

import flet as ft
from typing import List
from pathlib import Path

# --- Core Imports ---
from ..base_view import BaseView
from ..components import Breadcrumb


class NewProjectView(BaseView):
    """
    A view for Browse folders and creating new projects.
    This view is a "dumb" component that builds the UI and delegates all
    logic and actions to the AppController.
    """

    def __init__(self, page: ft.Page, controller):
        # Call the parent constructor FIRST to ensure self.page and self.controller are set.
        super().__init__(page, controller)

        # Initialize state. The current_path is set using the controller, which is now safe.
        self.current_path = Path(self.controller.data_service.project_data_dir)

        # Define placeholders for controls that will be built later.
        self.breadcrumb: Breadcrumb | None = None
        self.file_list_view: ft.ListView | None = None
        self.add_project_button: ft.IconButton | None = None
        self.add_folder_button: ft.IconButton | None = None

    def build(self) -> ft.Control:
        """
        Builds and returns the view's root Flet control.
        This method is called by the AppController AFTER the theme is set.
        """
        # Build the components now that we know the theme and controller exist.
        self.breadcrumb = self._build_breadcrumb()
        self.file_list_view = ft.ListView(spacing=5, expand=True)
        self.add_project_button = self._build_action_button(
            icon=ft.icons.POST_ADD_ROUNDED,
            tooltip="Create New Project",
            on_click=self._on_add_project_clicked,
        )
        self.add_folder_button = self._build_action_button(
            icon=ft.icons.CREATE_NEW_FOLDER_OUTLINED,
            tooltip="Create New Folder",
            on_click=self._on_add_folder_clicked,
        )

        # Populate the file list for the initial view.
        self._update_file_list()

        return ft.Column(
            controls=[
                # Header with a title and action buttons
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(
                                "Project Browser",
                                theme_style=ft.TextThemeStyle.HEADLINE_SMALL,
                            ),
                            ft.Row([self.add_folder_button, self.add_project_button]),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.padding.only(left=20, right=10, top=10, bottom=10),
                    border=ft.border.only(
                        bottom=ft.BorderSide(1, self.colors.outline_variant)
                    ),
                ),
                # Breadcrumb for navigation
                ft.Container(
                    self.breadcrumb,
                    padding=ft.padding.symmetric(horizontal=20, vertical=5),
                ),
                # The main list of files and folders
                ft.Container(
                    content=self.file_list_view,
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=20),
                ),
            ],
            expand=True,
            spacing=0,
        )

    # --- UI Builder Methods ---

    def _build_breadcrumb(self) -> Breadcrumb:
        """Builds the breadcrumb component."""
        return Breadcrumb(
            crumbs=self._get_breadcrumb_parts(),
            on_crumb_click=self._on_breadcrumb_clicked,
        )

    def _build_action_button(self, icon: str, tooltip: str, on_click) -> ft.IconButton:
        """Builds a consistent IconButton for the header."""
        return ft.IconButton(
            icon=icon,
            tooltip=tooltip,
            on_click=on_click,
            icon_color=self.colors.primary,
        )

    # --- Event Handlers ---

    def _on_breadcrumb_clicked(self, index: int):
        """Handles a click on a breadcrumb part."""
        root_path = Path(self.controller.data_service.project_data_dir)
        parts = self._get_breadcrumb_parts()
        new_parts = parts[: index + 1]

        # The first part is the root label, so we join from the second part onwards
        if len(new_parts) > 1:
            self.current_path = root_path.joinpath(*new_parts[1:])
        else:
            self.current_path = root_path
        self._update_view()

    def _on_item_clicked(self, e):
        """Handles a click on a file or folder in the list."""
        item_path_str = e.control.data["path"]
        is_directory = e.control.data["is_directory"]

        if is_directory:
            self.current_path = Path(item_path_str)
            self._update_view()
        else:
            self.controller.open_project(item_path_str)

    def _on_add_project_clicked(self, e):
        """Tells the controller to show the project creation dialog."""
        self.controller.show_create_project_dialog(parent_path=self.current_path)

    def _on_add_folder_clicked(self, e):
        """Tells the controller to show the folder creation dialog."""
        self.controller.show_create_folder_dialog(parent_path=self.current_path)

    # --- View Update Logic ---

    def _update_view(self):
        """Refreshes the breadcrumb and file list."""
        self.breadcrumb.update_crumbs(self._get_breadcrumb_parts())
        self._update_file_list()
        self.page.update()

    def _update_file_list(self):
        """Fetches folder contents from the DataService and updates the ListView."""
        contents = self.controller.data_service.get_folder_contents(
            str(self.current_path)
        )
        self.file_list_view.controls.clear()

        if not contents:
            self.file_list_view.controls.append(
                self.show_empty_state(
                    "This folder is empty.", icon=ft.icons.FOLDER_OFF_OUTLINED
                )
            )
        else:
            for item in contents:
                icon = (
                    ft.icons.FOLDER_OUTLINED
                    if item["is_directory"]
                    else ft.icons.INSERT_DRIVE_FILE_OUTLINED
                )
                self.file_list_view.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(icon),
                        title=ft.Text(item["name"]),
                        on_click=self._on_item_clicked,
                        data={
                            "path": item["path"],
                            "is_directory": item["is_directory"],
                        },
                    )
                )

    def _get_breadcrumb_parts(self) -> List[str]:
        """Calculates breadcrumb parts from the current path."""
        root_path = Path(self.controller.data_service.project_data_dir)
        if self.current_path == root_path:
            return ["Projects"]

        relative_path = self.current_path.relative_to(root_path)
        return ["Projects"] + list(relative_path.parts)
