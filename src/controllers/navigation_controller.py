"""
Navigation Controller - Handles navigation-related operations.

This controller could manage navigation history, breadcrumbs, etc.
"""

from pathlib import Path
from .base_controller import BaseController
from src.models import Project


class NavigationController(BaseController):
    """Handles navigation-related operations."""

    def __init__(self, app_controller):
        super().__init__(app_controller)

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

        self.controller.navigate_to(final_page_name)

    def validate_recent_projects(self):
        """
        Validates the list of recent projects, removing any that no longer exist.
        """
        self.logger.info("Validating recent projects list...")
        self.controller.user_config_manager.validate_recent_projects()

    def remove_recent_project(self, project_path: str):
        """
        Removes a project from the recent projects list.

        Args:
            project_path (str): The path of the project to remove.
        """
        self.logger.info(f"Removing recent project: {project_path}")
        self.controller.user_config_manager.remove_recent_project(project_path)
        self.controller.update_view()

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
        self.controller.update_view()
