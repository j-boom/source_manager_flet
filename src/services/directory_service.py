"""
Directory Service

Handles generic file and directory operations for the application.
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

from config import PROJECT_DATA_DIR

class DirectoryService:
    """Manages file and directory interactions."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.project_data_dir = Path(PROJECT_DATA_DIR)
        self.project_data_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info("DirectoryService initialized")

    def get_primary_folders(self) -> List[str]:
        """Gets the list of primary region folders (e.g., 'ROW', 'CONUS')."""
        if not self.project_data_dir.exists():
            return []
        return sorted([p.name for p in self.project_data_dir.iterdir() if p.is_dir()])

    def get_folder_contents(self, folder_path: str) -> List[Dict[str, Any]]:
        """Gets the contents of a given folder path."""
        path = Path(folder_path)
        if not path.is_dir():
            return []
        contents = [
            {"name": p.name, "path": str(p), "is_directory": p.is_dir()}
            for p in path.iterdir()
        ]
        # Sort by type (directories first), then by name
        return sorted(contents, key=lambda x: (not x["is_directory"], x["name"].lower()))

    def create_new_folder(self, parent_path: Path, folder_name: str, description: Optional[str] = None) -> Tuple[bool, str]:
        """Creates a new folder with an optional description."""
        sanitized_filename = re.sub(r'[<>:"/\\|?*]', "", folder_name).strip()
        sanitized_description = (re.sub(r'[<>:"/\\|?*]', "", description).strip() if description else None)

        if not sanitized_filename:
            return False, f"Invalid folder name '{folder_name}'."

        new_folder_path = (parent_path / f"{sanitized_filename} {sanitized_description}" if sanitized_description else parent_path / sanitized_filename)

        if new_folder_path.exists():
            return False, f"A folder or file named '{new_folder_path.name}' already exists."
        try:
            new_folder_path.mkdir(parents=True, exist_ok=False)
            self.logger.info(f"Successfully created folder: {new_folder_path}")
            return True, f"Successfully created folder '{new_folder_path.name}'."
        except OSError as e:
            self.logger.error(f"Failed to create directory {new_folder_path}: {e}")
            return False, f"Failed to create directory: {e}"
        
    def get_country_folders(self) -> List[str]:
        """Gets all country-level folders from within the primary region folders."""
        countries = []
        primary_folders = self.get_primary_folders()
        for region in primary_folders:
            region_path = self.project_data_dir / region
            if region_path.is_dir():
                for country_path in region_path.iterdir():
                    if country_path.is_dir() and not country_path.name.startswith('.') and not country_path.name == 'Non CR Products':
                        countries.append(country_path.name)
        # Use set to ensure uniqueness and then sort alphabetically
        return sorted(list(set(countries)))