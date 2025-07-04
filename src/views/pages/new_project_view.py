"""
New Project View (Final)

This view allows users to browse directories, search, and create new projects or folders.
It combines a rich UI with the clean, controller-delegated architecture.
"""

import flet as ft
from typing import Optional
from pathlib import Path

from src.views.base_view import BaseView
from src.views.components.breadcrumb import Breadcrumb


class NewProjectView(BaseView):
    """A view for browsing folders and creating new projects."""

    def __init__(self, page: ft.Page, controller):
        super().__init__(page, controller)
        # Get a direct reference to the browser manager for convenience
        self.browser_manager = self.controller.project_browser_manager

        # --- UI State ---
        self.current_path: Path = Path(self.controller.data_service.project_data_dir)
        self.search_text: str = ""

        # --- UI Component Placeholders ---
        self.breadcrumb: Optional[Breadcrumb] = None
        self.file_list_view: Optional[ft.ListView] = None
        self.header_container: Optional[ft.Container] = None

    def build(self) -> ft.Control:
        """Builds the UI for the view."""
        self.header_container = self._build_header()
        self.directory_selection = self._build_directory_selection()
        self.breadcrumb = self._build_breadcrumb()
        self.file_list_view = ft.ListView(spacing=5, expand=True)
        self._update_file_list()

        return ft.Column(
            controls=[
                self.header_container,
                ft.Container(
                    self.breadcrumb,
                    padding=ft.padding.symmetric(horizontal=20, vertical=5),
                ),
                self.directory_selection,
                ft.Container(
                    content=self.file_list_view,
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=20),
                    bgcolor=ft.colors.SURFACE_VARIANT,
                ),
            ],
            expand=True,
            spacing=0,
        )

    # --- UI Builder Methods ---

    def _build_header(self) -> ft.Container:
        """Builds the header, which includes a search bar and action buttons."""
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        "Project Browser", theme_style=ft.TextThemeStyle.HEADLINE_SMALL
                    ),
                    # ft.Row(self._get_header_actions()),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                spacing=20,
            ),
            padding=ft.padding.all(15),
            border=ft.border.only(bottom=ft.BorderSide(1, self.colors.outline_variant)),
        )

    # def _get_header_actions(self) -> List[ft.Control]:
    #     """Determines which action buttons to show."""
    #     return [
    #         self._build_action_button(
    #             icon=ft.icons.CREATE_NEW_FOLDER_OUTLINED,
    #             tooltip="Create New Folder",
    #             on_click=self._on_add_folder_clicked,
    #         ),
    #         self._build_action_button(
    #             icon=ft.icons.POST_ADD_ROUNDED,
    #             tooltip="Create New Project",
    #             on_click=self._on_add_project_clicked,
    #         ),
    #     ]

    def _build_directory_selection(self) -> ft.Control:
        """Build directory selection section"""
        self.primary_dropdown = ft.Dropdown(
            label="Select Primary Folder",
            options=[
                ft.dropdown.Option(name)
                for name in self.browser_manager.primary_folders
            ],
            width=300,
            on_change=self._on_primary_folder_changed,
        )

        self.search_field = ft.TextField(
            label="Search Folders",
            hint_text="Search for 4-digit or 10-digit folders",
            width=300,
            height=40,
            prefix_icon=ft.icons.SEARCH,
            border_radius=8,
            border_color=ft.colors.OUTLINE,
            content_padding=10,
            on_change=self._on_search_change,
            on_submit=self._on_search_change,
        )

        self.directory_selection_container = ft.Container(
            content=ft.Row(
                [self.primary_dropdown, ft.Container(width=20), self.search_field],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.padding.all(20),
            bgcolor=ft.colors.SURFACE_VARIANT,
        )
        return self.directory_selection_container

    def _build_breadcrumb(self) -> Breadcrumb:
        """Builds the breadcrumb component."""
        return Breadcrumb(
            crumbs=self.browser_manager.breadcrumb_parts,
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
    def _on_primary_folder_changed(self, e):
        """Notifies the manager that the primary folder has changed."""
        self.browser_manager.select_primary_folder(e.control.value)
        self.search_field.value = ""  # Clear search field
        self._update_view()

    def _on_search_change(self, e):
        """Notifies the manager that the search text has changed."""
        self.browser_manager.search(e.control.value)
        self._update_view()

    def _on_breadcrumb_clicked(self, index: int):
        parts = self.browser_manager.breadcrumb_parts
        new_parts = parts[1 : index + 1]  # exclude root "Projects" part
        new_path = self.browser_manager.root_path.joinpath(*new_parts)
        self.browser_manager.navigate_to_path(new_path)
        self._update_view()

    def _on_item_clicked(self, e):
        """Handles a click on a file or folder in the list."""
        item_path = Path(e.control.data["path"])
        if e.control.data["is_directory"]:
            self.browser_manager.navigate_to_path(item_path)
            self._update_view()
        else:
            self.controller.open_project(item_path)

    def _on_add_project_clicked(self, e):
        """Tells the controller to show the project creation dialog."""
        self.controller.show_create_project_dialog(parent_path=self.current_path)

    def _on_add_folder_clicked(self, e):
        """Tells the controller to show the folder creation dialog."""
        self.controller.show_create_folder_dialog(parent_path=self.current_path)

    # --- View Update Logic ---
    def _update_view(self):
        """Refreshes the breadcrumb, header, and file list."""
        self.breadcrumb.update_crumbs(self.browser_manager.breadcrumb_parts)
        self._update_file_list()
        self.page.update()

    def _update_file_list(self):
        """Fetches folder contents and filters them based on the search text."""
        items = self.browser_manager.displayed_items
        self.file_list_view.controls.clear()

        if not items:
            message = (
                "No results found."
                if self.browser_manager.search_term
                else "Select a Primary folder to begin."
            )
            icon = (
                ft.icons.SEARCH_OFF
                if self.browser_manager.search_term
                else ft.icons.FOLDER_OPEN_OUTLINED
            )
            self.file_list_view.controls.append(
                self.show_empty_state(message, icon=icon)
            )
        else:
            for item in items:
                icon = (
                    ft.icons.FOLDER_OUTLINED
                    if item["is_directory"]
                    else ft.icons.INSERT_DRIVE_FILE_OUTLINED
                )
                self.file_list_view.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(icon, color=ft.colors.TERTIARY),
                        title=ft.Text(item["name"]),
                        on_click=self._on_item_clicked,
                        data=item,
                        bgcolor=ft.colors.TERTIARY_CONTAINER,
                    )
                )
