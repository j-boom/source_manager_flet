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
        """
        Progressive search within the current country folder.
        Only works when a country is selected.
        """
        if not self.is_country_selected():
            # Don't search if we're not in a country folder
            self.search_term = ""
            self.displayed_items = []
            return
            
        self.search_term = term.strip() if term else ""
        self.update_state()

    def update_state(self):
        """
        The core logic method. It updates the displayed_items and breadcrumb_parts
        based on the current state of the manager.
        """
        # If we have a search term and we're in a country, do progressive search
        if self.search_term and self.is_country_selected():
            # When searching, only show matching folders
            self.displayed_items = self._progressive_search(self.search_term)
        else:
            # Normal directory browsing - show both folders and files
            all_items = self.data_service.get_folder_contents(str(self.current_path))
            # Filter out hidden files (starting with .), but show both directories and files
            self.displayed_items = [item for item in all_items if not item['name'].startswith('.')]

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

    def get_all_countries(self) -> List[Dict[str, str]]:
        """
        Gets all countries from all primary folders.
        Returns a list of dictionaries with 'name' and 'path' keys.
        Only includes actual country names, not year folders (4-digit numbers).
        """
        countries = []
        for primary_folder in self.primary_folders:
            primary_path = self.root_path / primary_folder
            if primary_path.exists() and primary_path.is_dir():
                # Get all subdirectories (countries) in this primary folder
                country_items = self.data_service.get_folder_contents(str(primary_path))
                for item in country_items:
                    if (item.get('is_directory', False) and 
                        not item['name'].startswith('.') and
                        not item['name'].isdigit()):  # Exclude 4-digit year folders
                        countries.append({
                            'name': item['name'],
                            'path': item['path'],
                            'region': primary_folder
                        })
        
        # Sort countries alphabetically by name
        countries.sort(key=lambda x: x['name'])
        return countries

    def select_country(self, country_path: str):
        """Navigates directly to a country folder and enables search."""
        country_path_obj = Path(country_path)
        self.current_path = country_path_obj
        self.search_term = ""  # Reset search when selecting new country
        self.update_state()

    def is_country_selected(self) -> bool:
        """Returns True if we're currently in a country folder (not at root or primary folder level)."""
        try:
            relative_path = self.current_path.relative_to(self.root_path)
            parts = relative_path.parts
            # We're in a country if we have at least 2 parts: primary_folder/country
            return len(parts) >= 2
        except ValueError:
            return False

    def _progressive_search(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Performs progressive search within the current country folder.
        Searches recursively for folders that start with the search term.
        """
        import os
        
        matching_folders = []
        search_term = search_term.lower()
        
        # Walk through all subdirectories starting from current path
        for root, dirs, files in os.walk(str(self.current_path)):
            # Filter out hidden directories and files
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for dir_name in dirs:
                # Check if folder name starts with search term
                if dir_name.lower().startswith(search_term):
                    full_path = os.path.join(root, dir_name)
                    matching_folders.append({
                        'name': dir_name,
                        'path': full_path,
                        'is_directory': True
                    })
        
        # Sort results by name
        matching_folders.sort(key=lambda x: x['name'])
        return matching_folders
