"""
New Project View (Final)

This view allows users to browse directories, search, and create new projects or folders.
It combines a rich UI with the clean, controller-delegated architecture.
"""

import flet as ft
from typing import Optional
from pathlib import Path
import logging
from src.views.base_view import BaseView
from src.views.components.breadcrumb import Breadcrumb


class NewProjectView(BaseView):
    """A view for browsing folders and creating new projects."""

    def __init__(self, page: ft.Page, controller):
        super().__init__(page, controller)
        # Get a direct reference to the browser manager for convenience
        self.browser_manager = self.controller.project_browser_manager
        self.logger = logging.getLogger(__name__)
        # --- UI State ---
        self.current_path: Path = Path(self.controller.data_service.project_data_dir)
        self.search_text: str = ""

        # --- UI Component Placeholders ---
        self.breadcrumb: Optional[Breadcrumb] = None
        self.file_list_view: Optional[ft.ListView] = None
        self.header_container: Optional[ft.Container] = None

        # --- Action Button Placeholders ---
        self.action_button: Optional[ft.ElevatedButton] = None

    def build(self) -> ft.Control:
        """Builds the UI for the view."""
        self.header_container = self._build_header()
        self.breadcrumb_bar = self._build_breadcrumb_bar()
        self.directory_selection = self._build_directory_selection()
        self.file_list_view = ft.ListView(spacing=5, expand=True)

        self._update_file_list()

        return ft.Column(
            controls=[
                self.header_container,
                self.breadcrumb_bar,
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
        self.header_container = ft.Container(
            content=ft.Row(
                [
                    ft.ElevatedButton(
                        "Back",
                        icon=ft.icons.ARROW_BACK,
                        on_click=self._on_back_clicked,
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.PRIMARY, color=ft.colors.ON_PRIMARY
                        ),
                    ),
                    ft.Container(expand=True),
                    ft.Text("New Project", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "Recent Projects",
                        icon=ft.icons.HISTORY,
                        on_click=self._on_recent_projects_clicked,
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.PRIMARY, color=ft.colors.ON_PRIMARY
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.all(20),
            bgcolor=ft.colors.SURFACE_VARIANT,
            border=ft.border.only(bottom=ft.BorderSide(1, ft.colors.OUTLINE)),
        )

        return self.header_container

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

    def _build_breadcrumb_bar(self) -> ft.Container:
        """Builds the breadcrumb bar for navigation."""
        self.breadcrumb = self._build_breadcrumb()
        self.action_button = ft.ElevatedButton(
            text="Add Project",
            icon=ft.icons.POST_ADD,
            on_click=self._on_add_project_clicked,
            bgcolor=ft.colors.TERTIARY_CONTAINER,
            color=ft.colors.ON_TERTIARY_CONTAINER,
            visible=False,  # Initially hidden, updated later
        )

        return ft.Container(
            content=ft.Row(
                controls=[self.breadcrumb, self.action_button],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=5),
        )

    def _build_breadcrumb(self) -> Breadcrumb:
        """Builds the breadcrumb component."""
        return Breadcrumb(
            crumbs=self.browser_manager.breadcrumb_parts,
            on_crumb_click=self._on_breadcrumb_clicked,
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

    def _on_back_clicked(self, e):
        """Handles the back button click to navigate to the home view."""
        self.controller.navigate_to("home")

    def _on_recent_projects_clicked(self, e):
        """Handles the recent projects button click."""
        self.controller.navigate_to("recent_projects")

    def _on_item_clicked(self, e):
        """Handles a click on a file or folder in the list."""
        # --- DEBUGGING: Added detailed logging and error handling ---
        try:
            item_data = e.control.data
            self.logger.info(f"--- _on_item_clicked: Item clicked. Raw data: {item_data} ---")

            if not isinstance(item_data, dict):
                self.logger.error(f"--- _on_item_clicked: ERROR! Item data is not a dictionary. Type is {type(item_data)} ---")
                return

            item_path_str = item_data.get("path")
            is_directory = item_data.get("is_directory")

            if item_path_str is None or is_directory is None:
                self.logger.error(f"--- _on_item_clicked: ERROR! Item data is missing 'path' or 'is_directory'. ---")
                return

            item_path = Path(item_path_str)
            if is_directory:
                self.logger.info(f"--- _on_item_clicked: Navigating to directory: {item_path} ---")
                self.browser_manager.navigate_to_path(item_path)
                self._update_view()
            else:
                self.logger.info(f"--- _on_item_clicked: Calling controller.open_project with path: {item_path} ---")
                self.controller.open_project(item_path)

        except Exception as ex:
            self.logger.error(f"--- _on_item_clicked: An unexpected exception occurred: {ex} ---", exc_info=True)
        # --- END DEBUGGING ---

    def _on_add_project_clicked(self, e):
        """Tells the controller to show the project creation dialog."""
        self.controller.show_create_project_dialog(parent_path=self.browser_manager.current_path)

    def _on_add_folder_clicked(self, e):
        """Tells the controller to show the folder creation dialog."""
        print(f"The current path is: {self.browser_manager.current_path}")
        self.controller.show_create_folder_dialog(parent_path=self.browser_manager.current_path)

    # --- View Update Logic ---
    def _update_action_button(self):
        config = self.browser_manager.action_button_config
        if not self.action_button:
            return

        self.action_button.visible = config.get("visible", False)

        if self.action_button.visible:
            self.action_button.text = config.get("text")
            self.action_button.icon = config.get("icon")
            action = config.get("action")

            if action == "add_project":
                self.action_button.on_click = self._on_add_project_clicked
            elif action == "add_folder":
                self.action_button.on_click = self._on_add_folder_clicked
            else:
                self.action_button.on_click = None

    def _update_view(self):
        """Refreshes the breadcrumb, header, and file list."""
        self.breadcrumb.update_crumbs(self.browser_manager.breadcrumb_parts)
        self._update_action_button()
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
