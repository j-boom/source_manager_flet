"""
Navigation Controller - Handles navigation-related operations.

This controller could manage navigation history, breadcrumbs, etc.
"""

from pathlib import Path
from typing import Dict, Optional

import flet as ft

from .base_controller import BaseController
from src.models import Project
from config.app_config import PAGES, SPECIAL_PAGES


class NavigationController(BaseController):
    """Handles navigation-related operations."""

    def __init__(self, app_controller):
        super().__init__(app_controller)

    def build_view_class_map(self) -> Dict[str, type]:
        """Creates a mapping from page names to view classes for the factory."""
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
        return {
            name: view_classes[class_name]
            for name, class_name in all_pages.items()
            if class_name in view_classes
        }

    def navigate_to_page(self, page_name: str):
        """
        Navigates to a specified page.

        Args:
            page_name (str): The name of the page to navigate to.
        """
        self.logger.info(f"Navigating to page: {page_name}")
        final_page_name = page_name

        if page_name == "project_view":
            if self.controller.project_state_manager.has_loaded_project():
                final_page_name = "project_dashboard"
            else:
                final_page_name = "new_project"

        if page_name == "recent_projects":
            self._validate_recent_projects()

        self.controller.navigation_manager.set_current_page(final_page_name)
        if page_name in self.controller.views:
            self.controller.views.pop(page_name)

        self.controller.views[final_page_name] = self.create_view_for_page(final_page_name)
        view_instance = self.controller.views.get(page_name)
        if view_instance:
            content_to_display = (
                view_instance.build() if hasattr(view_instance, "build") and callable(getattr(view_instance, "build")) else view_instance
            )
            self.controller.main_view.set_content(content_to_display)
            self.controller.main_view.update_navigation(final_page_name)

        else:
            self.logger.error(
                f"Could not find view for page: {page_name}. "
            )
            
    def _validate_recent_projects(self):
        """Checks the recent projects list and removes any that no longer exist on disk."""
        self.logger.info("Validating recent projects list...")
        for project in list(self.controller.user_config_manager.get_recent_projects()):
            if not Path(project.path).exists():
                self.logger.warning(
                    f"Recent project file not found, removing from list: {project.path}"
                )
                self.controller.user_config_manager.remove_recent_project(project.path)

    def remove_recent_project(self, project_path: str):
        """
        Removes a project from the recent projects list.

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
        Submits a new folder path to the user configuration.

        Args:
            folder_path (str): The path of the new folder.
        """
        self.logger.info(f"Submitting new folder: {folder_name} at {parent_path}")
        self.controller.data_service.create_new_folder(
            parent_path, folder_name, description
        )
        self.controller.page.update()

    def setup_callbacks(self):
        """Connects components together using callbacks for loose coupling."""
        self.controller.settings_manager.set_callbacks(
            on_theme_change=self.apply_theme_and_update_views,
            on_display_name_change=self.handle_display_name_change,
        )

    def apply_theme_and_update_views(self):
        """Applies the current theme to the page and refreshes all visible views."""
        self.controller.page.theme_mode = (
            ft.ThemeMode.DARK
            if self.controller.theme_manager.mode == "dark"
            else ft.ThemeMode.LIGHT
        )
        self.controller.page.theme = self.controller.theme_manager.get_theme_data()
        self.controller.main_view.refresh_theme()
        current_page_name = self.controller.navigation_manager.get_current_page()

        if current_page_name in self.controller.views:
            self.controller.views.pop(current_page_name, None)
        self.controller.navigate_to(current_page_name)
                         
    def handle_display_name_change(self):
        """Handles display name updates from the settings manager."""
        self.controller.main_view.update_greeting()
        if self.controller.navigation_manager.get_current_page() == "settings":
            self.controller.views.pop("settings", None)
            self.controller.navigate_to("settings")

    def create_view_for_page(self, page_name: str) -> Optional[ft.Control]:
        """Factory method to create view instances on demand using the config."""
        view_class = self.controller.navigation_controller.build_view_class_map().get(page_name)
        if view_class:
            return view_class(self.controller.page, self.controller)
        return ft.Text(f"View for '{page_name}' not implemented.", color="red")
