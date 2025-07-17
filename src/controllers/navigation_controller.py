"""
Navigation Controller - Handles navigation-related operations.

This controller could manage navigation history, breadcrumbs, etc.
"""

from pathlib import Path
from typing import Dict, Optional

import flet as ft

from .base_controller import BaseController
from config.app_config import PAGES, SPECIAL_PAGES


class NavigationController(BaseController):
    """Handles navigation-related operations."""

    def __init__(self, app_controller):
        super().__init__(app_controller)

    def build_view_class_map(self) -> Dict[str, type]:
        """
        Creates a mapping from page names (as used in navigation) to their corresponding view classes.
        This is used as a factory for instantiating views on demand.
        Returns:
            Dict[str, type]: Mapping from page name to view class.
        """
        from views.pages import (
            HomeView,
            RecentProjectsView,
            NewProjectView,
            ProjectView,
            SettingsView,
            SourcesView,
            ReportsView,
            HelpView,
        )

        all_pages = {p["name"]: p["view_name"] for p in PAGES}
        all_pages.update(
            {name: data["view_name"] for name, data in SPECIAL_PAGES.items()}
        )

        view_classes = {
            "HomeView": HomeView,
            "NewProjectView": NewProjectView,
            "ProjectView": ProjectView,
            "RecentProjectsView": RecentProjectsView,
            "ReportsView": ReportsView,
            "SettingsView": SettingsView,
            "SourcesView": SourcesView,
            "HelpView": HelpView,
        }
        # Return a mapping from page name to the actual view class
        return {
            name: view_classes[class_name]
            for name, class_name in all_pages.items()
            if class_name in view_classes
        }

    def navigate_to_page(self, page_name: str):
        """
        Navigates to a specified page by name. Handles special cases (like project_view) and ensures
        the correct view is instantiated and displayed. Also updates navigation state and validates recent projects.

        Args:
            page_name (str): The name of the page to navigate to.
        """
        self.logger.info(f"Navigating to page: {page_name}")
        final_page_name = page_name

        # Special case: project_view is an alias for either project_dashboard or new_project
        if page_name == "project_view":
            if self.controller.project_state_manager.has_loaded_project():
                final_page_name = "project_dashboard"
            else:
                final_page_name = "new_project"

        # Validate recent projects list before showing recent_projects page
        if page_name == "recent_projects":
            self._validate_recent_projects()

        # Update the current page in navigation manager
        self.controller.navigation_manager.set_current_page(final_page_name)

        # Use the factory to get the correct view class for the page
        view_class = self.controller.navigation_controller.build_view_class_map().get(
            final_page_name
        )

        if view_class:
            # Instantiate the view and cache it
            view_instance = self.controller.views.get(final_page_name)
            if not view_instance:
                view_instance = view_class(self.controller.page, self.controller)
                self.controller.views[final_page_name] = view_instance

            # Build the view content
            content_to_display = view_instance.build()

            # Set the content in the main view and update navigation
            self.controller.main_view.set_content(content_to_display)
            self.controller.main_view.update_navigation(final_page_name)

            self.controller.page.update()

        else:
            self.logger.error(f"Could not find view for page: {page_name}. ")

    def _validate_recent_projects(self):
        """
        Checks the recent projects list and removes any that no longer exist on disk.
        This keeps the recent projects UI clean and prevents errors from missing files.
        """
        self.logger.info("Validating recent projects list...")
        for project in list(self.controller.user_config_manager.get_recent_projects()):
            if not Path(project.path).exists():
                self.logger.warning(
                    f"Recent project file not found, removing from list: {project.path}"
                )
                self.controller.user_config_manager.remove_recent_project(project.path)

    def remove_recent_project(self, project_path: str):
        """
        Removes a project from the recent projects list and updates the UI.

        Args:
            project_path (str): The path of the project to remove.
        """
        self.logger.info(f"Removing recent project: {project_path}")
        self.controller.user_config_manager.remove_recent_project(project_path)
        self.controller.page.update()

    def submit_new_folder(
        self, parent_path: Path, folder_name: str, description: str = ""
    ):
        """
        Submits a new folder path to the user configuration and updates the UI.

        Args:
            parent_path (Path): The parent directory for the new folder.
            folder_name (str): The name of the new folder.
            description (str, optional): Optional description for the folder.
        """
        self.logger.info(f"Submitting new folder: {folder_name} at {parent_path}")
        self.controller.directory_service.create_new_folder(
            parent_path, folder_name, description
        )
        self.controller.page.update()

    def create_view_for_page(self, page_name: str) -> Optional[ft.Control]:
        """
        Factory method to create view instances on demand using the config.
        Returns a Flet control for the requested page, or a placeholder if not implemented.

        Args:
            page_name (str): The name of the page to create.

        Returns:
            Optional[ft.Control]: The view control, or a placeholder if not found.
        """
        view_class = self.controller.navigation_controller.build_view_class_map().get(
            page_name
        )
        if view_class:
            return view_class(self.controller.page, self.controller)
        return ft.Text(f"View for '{page_name}' not implemented.", color="red")