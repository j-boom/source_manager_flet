"""
Project Browser Manager

Manages the state and business logic for the project browsing interface.
"""

import re
from typing import List, Dict, Any, Optional
from pathlib import Path

# Assuming DataService is in a sibling package
from services import DataService


class ProjectBrowserManager:
    """Manages the state for browsing the project directory structure."""

    def __init__(self, data_service: DataService):
        """
        Initializes the manager.

        Args:
            data_service: An instance of the application's DataService.
        """
        self.data_service = data_service
        self.root_path = Path(self.data_service.project_data_dir)

        # --- State Attributes ---
        self.primary_folders: List[str] = self.data_service.get_primary_folders()
        self.selected_primary_folder: Optional[str] = None
        self.current_path: Path = self.root_path
        self.search_term: str = ""

        # --- Data to be Displayed by the View ---
        # The view will read from these attributes to render itself.
        self.displayed_items: List[Dict[str, Any]] = []
        self.breadcrumb_parts: List[str] = ["Projects"]

    # --- Private Properties for Internal Logic ---
    @property
    def _can_add_folder(self) -> bool:
        """Determines if a new folder can be added."""
        if self.current_path == self.root_path:
            return False

        folder_name = self.current_path.name
        return (
            # TODO THIS IS WHERE WE PUT THE RIGHT REGEX IN
            bool(re.match(r"^\d{4}([A-Z]{2})?$", folder_name))
        )

    @property
    def _can_add_file(self) -> bool:
        """Determines if a new file can be added."""
        if self.current_path == self.root_path:
            return False

        folder_name = self.current_path.name
        return bool(re.match(r"^\d{4}[A-Z]{2}\d{4}\b|^\d{10}\b", folder_name))

    # --- Public Properties for View Display ---
    @property
    def action_button_config(self) -> Dict[str, Any]:
        """Returns the configuration for the action button based on current state."""
        if self._can_add_file:
            return {
                "visible": True,
                "text": "Add Project",
                "icon": "post_add",
                "action": "add_project",
            }

        if self._can_add_folder:
            return {
                "visible": True,
                "text": "New Folder",
                "icon": "create_new_folder_outlined",
                "action": "add_folder",
            }

        return {
            "visible": False,
        }

    # --- Public methods for View Interaction ---

    def select_primary_folder(self, folder_name: Optional[str]):
        """Sets the primary folder and updates the state."""
        self.selected_primary_folder = folder_name
        if folder_name:
            self.current_path = self.root_path / folder_name
        else:
            self.current_path = self.root_path

        self.search_term = ""  # Reset search on folder change
        self.update_state()

    def navigate_to_path(self, path: Path):
        """Navigates to a specific directory path."""
        self.current_path = path
        self.update_state()

    def search(self, term: str):
        """Filters the displayed items based on a search term."""
        self.search_term = term.lower()
        self.update_state()

    def update_state(self):
        """
        The core logic method. It updates the displayed_items and breadcrumb_parts
        based on the current state of the manager.
        """
        # Get all items from the current directory
        all_items = self.data_service.get_folder_contents(str(self.current_path))

        # Apply search filter if a search term exists
        if self.search_term:
            self.displayed_items = [
                item for item in all_items if self.search_term in item["name"].lower()
            ]
        else:
            self.displayed_items = all_items

        # Update breadcrumbs based on the current path
        if self.current_path == self.root_path:
            self.breadcrumb_parts = ["Projects"]
        else:
            try:
                relative_path = self.current_path.relative_to(self.root_path)
                self.breadcrumb_parts = ["Projects"] + list(relative_path.parts)
            except ValueError:
                # This can happen if the path is not within the root, handle gracefully
                self.breadcrumb_parts = ["Projects", "..."]
