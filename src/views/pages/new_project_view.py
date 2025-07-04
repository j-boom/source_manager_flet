"""
New Project View (Final)

This view allows users to browse directories, search, and create new projects or folders.
It combines a rich UI with the clean, controller-delegated architecture.
"""

import flet as ft
from typing import List, Dict, Any, Optional
from pathlib import Path

from src.views.base_view import BaseView
from src.views.components.breadcrumb import Breadcrumb


class NewProjectView(BaseView):
    """A view for browsing folders and creating new projects."""

    def __init__(self, page: ft.Page, controller):
        super().__init__(page, controller)

        # --- UI State ---
        self.current_path: Path = Path(self.controller.data_service.project_data_dir)
        self.search_text: str = ""

        # --- UI Component Placeholders ---
        self.breadcrumb: Optional[Breadcrumb] = None
        self.file_list_view: Optional[ft.ListView] = None
        self.header_container: Optional[ft.Container] = None

    def build(self) -> ft.Control:
        """Builds the UI for the view."""
        self.breadcrumb = self._build_breadcrumb()
        self.file_list_view = ft.ListView(spacing=5, expand=True)
        self.header_container = self._build_header()

        self._update_file_list()

        return ft.Column(
            controls=[
                self.header_container,
                ft.Container(
                    self.breadcrumb,
                    padding=ft.padding.symmetric(horizontal=20, vertical=5),
                ),
                ft.Container(
                    content=self.file_list_view,
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=20),
                    bgcolor=ft.colors.SURFACE_VARIANT
                ),
            ],
            expand=True,
            spacing=0,
        )

    # --- UI Builder Methods ---

    def _build_header(self) -> ft.Container:
        """Builds the header, which includes a search bar and action buttons."""
        search_bar = ft.TextField(
            hint_text="Search for a facility number...",
            prefix_icon=ft.icons.SEARCH,
            border_radius=8,
            border_color=self.colors.outline_variant,
            height=40,
            content_padding=10,
            on_change=self._on_search_change,
            expand=True,
        )

        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        "Project Browser", theme_style=ft.TextThemeStyle.HEADLINE_SMALL
                    ),
                    search_bar,
                    ft.Row(self._get_header_actions()),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                spacing=20,
            ),
            padding=ft.padding.all(15),
            border=ft.border.only(bottom=ft.BorderSide(1, self.colors.outline_variant)),
        )

    def _get_header_actions(self) -> List[ft.Control]:
        """Determines which action buttons to show."""
        return [
            self._build_action_button(
                icon=ft.icons.CREATE_NEW_FOLDER_OUTLINED,
                tooltip="Create New Folder",
                on_click=self._on_add_folder_clicked,
            ),
            self._build_action_button(
                icon=ft.icons.POST_ADD_ROUNDED,
                tooltip="Create New Project",
                on_click=self._on_add_project_clicked,
            ),
        ]

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

    def _on_search_change(self, e):
        """Updates the search state and refreshes the file list."""
        self.search_text = e.control.value.lower()
        self._update_file_list()
        self.page.update()

    def _on_breadcrumb_clicked(self, index: int):
        """Handles a click on a breadcrumb part."""
        root_path = Path(self.controller.data_service.project_data_dir)
        parts = self._get_breadcrumb_parts()
        new_parts = parts[: index + 1]

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
        """Refreshes the breadcrumb, header, and file list."""
        self.breadcrumb.update_crumbs(self._get_breadcrumb_parts())
        self._update_file_list()
        self.page.update()

    def _update_file_list(self):
        """Fetches folder contents and filters them based on the search text."""
        all_contents = self.controller.data_service.get_folder_contents(
            str(self.current_path)
        )

        # Filter the contents if there is search text
        if self.search_text:
            filtered_contents = [
                item
                for item in all_contents
                if self.search_text in item["name"].lower()
            ]
        else:
            filtered_contents = all_contents

        self.file_list_view.controls.clear()

        if not filtered_contents:
            message = (
                "No results found." if self.search_text else "This folder is empty."
            )
            icon = (
                ft.icons.SEARCH_OFF
                if self.search_text
                else ft.icons.FOLDER_OFF_OUTLINED
            )
            self.file_list_view.controls.append(
                self.show_empty_state(message, icon=icon)
            )
        else:
            for item in filtered_contents:
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
