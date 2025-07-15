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

        # Store reference to main column for updates
        self.main_column = ft.Column(
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

        return self.main_column

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
        """Build directory selection section with country dropdown and search"""
        # Get all countries from all primary folders
        countries = self.browser_manager.get_all_countries()

        self.country_dropdown = ft.Dropdown(
            label="Select Country",
            options=[
                ft.dropdown.Option(key=country["path"], text=country["name"])
                for country in countries
            ],
            width=300,
            on_change=self._on_country_selected,
            value=None,  # No country selected initially
        )

        self.search_field = ft.TextField(
            label="Search Benjamin Numbers",
            hint_text="Enter 4-digit year or 10-digit Benjamin number",
            width=300,
            height=40,
            prefix_icon=ft.icons.SEARCH,
            border_radius=8,
            border_color=ft.colors.OUTLINE,
            content_padding=10,
            on_change=self._on_search_change,
            on_submit=self._on_search_change,
            disabled=True,  # Disabled until country is selected
        )

        self.directory_selection_container = ft.Container(
            content=ft.Row(
                [self.country_dropdown, ft.Container(width=20), self.search_field],
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
    def _on_search_change(self, e):
        """Handle search field changes."""
        search_value = e.control.value if e.control.value else ""
        self.browser_manager.search(search_value)
        self._update_view()

    def _on_country_selected(self, e):
        """Handle country selection from dropdown."""
        if e.control.value:
            # Country selected - navigate to it and enable search
            self.browser_manager.select_country(e.control.value)
            self.search_field.disabled = False
            self.search_field.value = ""  # Clear any previous search
        else:
            # No country selected - disable search
            self.search_field.disabled = True
            self.search_field.value = ""
            self.browser_manager.search("")  # Clear search

        self._update_view()

    def _on_breadcrumb_clicked(self, index: int):
        """Handle breadcrumb navigation."""
        parts = self.browser_manager.breadcrumb_parts

        if index == 0:  # Clicked on "Projects" - go to root
            self.browser_manager.current_path = self.browser_manager.root_path
            # Reset country dropdown and disable search
            self.country_dropdown.value = None
            self.search_field.disabled = True
            self.search_field.value = ""
            self.browser_manager.search("")
        else:
            # Navigate to the clicked breadcrumb level
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
        try:
            item_data = e.control.data
            self.logger.info(
                f"--- _on_item_clicked: Item clicked. Raw data: {item_data} ---"
            )

            if not isinstance(item_data, dict):
                self.logger.error(
                    f"--- _on_item_clicked: ERROR! Item data is not a dictionary. Type is {type(item_data)} ---"
                )
                return

            item_path_str = item_data.get("path")
            is_directory = item_data.get("is_directory")

            if item_path_str is None or is_directory is None:
                self.logger.error(
                    f"--- _on_item_clicked: ERROR! Item data is missing 'path' or 'is_directory'. ---"
                )
                return

            item_path = Path(item_path_str)
            if is_directory:
                self.logger.info(
                    f"--- _on_item_clicked: Navigating to directory: {item_path} ---"
                )

                # Clear search when navigating to avoid confusion
                self.search_field.value = ""
                self.browser_manager.search("")

                # Navigate to the clicked folder
                self.browser_manager.navigate_to_path(item_path)

                # Update country dropdown to reflect new location
                self._update_country_dropdown_from_path(item_path)

                self._update_view()
            else:
                self.logger.info(
                    f"--- _on_item_clicked: Calling controller.open_project with path: {item_path} ---"
                )
                self.controller.project_controller.open_project(item_path)

        except Exception as ex:
            self.logger.error(
                f"--- _on_item_clicked: An unexpected exception occurred: {ex} ---",
                exc_info=True,
            )

    def _on_add_project_clicked(self, e):
        """Tells the controller to show the project creation dialog."""
        self.controller.dialog_controller.open_new_project_dialog(
            parent_path=self.browser_manager.current_path
        )

    def _on_add_folder_clicked(self, e):
        """Tells the controller to show the folder creation dialog."""
        print(f"The current path is: {self.browser_manager.current_path}")
        self.controller.dialog_controller.open_folder_creation_dialog(
            parent_path=self.browser_manager.current_path
        )

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
        # Rebuild the breadcrumb bar with updated breadcrumbs
        self.breadcrumb_bar = self._build_breadcrumb_bar()

        # Update the main column controls with the new breadcrumb_bar
        if hasattr(self, "main_column") and self.main_column:
            self.main_column.controls[1] = (
                self.breadcrumb_bar
            )  # breadcrumb_bar is at index 1

        self._update_action_button()
        self._update_file_list()
        if hasattr(self, "page") and self.page:
            self.page.update()

    def _update_file_list(self):
        """Fetches folder contents and filters them based on the search text."""
        if not self.file_list_view:
            return

        items = self.browser_manager.displayed_items
        self.file_list_view.controls.clear()

        if not items:
            message = (
                "No results found."
                if self.browser_manager.search_term
                else "Select a country to begin."
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

    def _update_country_dropdown_from_path(self, current_path: Path):
        """Updates the country dropdown to reflect the current path location."""
        try:
            # Check if we're in a country folder (at least 2 levels deep: primary/country)
            relative_path = current_path.relative_to(self.browser_manager.root_path)
            parts = relative_path.parts

            if len(parts) >= 2:
                # We're in a country or deeper - set the dropdown to the country
                primary_folder = parts[0]
                country_name = parts[1]
                country_path = (
                    self.browser_manager.root_path / primary_folder / country_name
                )

                # Set the dropdown value to the country path
                self.country_dropdown.value = str(country_path)
                self.search_field.disabled = False
            else:
                # We're at root or primary level - reset dropdown
                self.country_dropdown.value = None
                self.search_field.disabled = True

        except ValueError:
            # Path is not within the root directory
            self.country_dropdown.value = None
            self.search_field.disabled = True
