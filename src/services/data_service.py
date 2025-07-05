"""
Data Service (Consolidated)

This service acts as the single gateway for all application data operations.
It combines directory management, project creation, and source handling into
a single, unified interface for the rest of the application.
"""
import json
import uuid
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime

# Import the application's configuration and data models
from config.app_config import REGIONAL_MAPPINGS, MASTER_SOURCES_DIR, PROJECT_DATA_DIR
from config.project_types_config import PROJECT_TYPES_CONFIG
from src.models.project_models import Project, ProjectSourceLink, ProjectType
from src.models.source_models import SourceRecord

class DataService:
    """Manages all data loading, saving, and business logic."""

    def __init__(self):
        """Initializes the service."""
        self.master_sources_dir = Path(MASTER_SOURCES_DIR)
        self.project_data_dir = Path(PROJECT_DATA_DIR)
        self.master_sources_dir.mkdir(parents=True, exist_ok=True)
        self.project_data_dir.mkdir(parents=True, exist_ok=True)
        self._master_source_cache: Dict[str, Dict[str, SourceRecord]] = {}

    # --- Directory and File System Logic (from DirectoryService) ---

    def get_primary_folders(self) -> List[str]:
        """Gets the list of primary folders (e.g., 'ROW') in the data directory."""
        if not self.project_data_dir.exists():
            return []
        return sorted([p.name for p in self.project_data_dir.iterdir() if p.is_dir()])

    def get_four_digit_folders(self, primary_folder: str) -> List[Dict[str, Any]]:
        """Gets all four-digit subfolders within a primary folder."""
        primary_path = self.project_data_dir / primary_folder
        if not primary_path.is_dir():
            return []
        
        folders = [
            {'name': p.name, 'path': str(p), 'is_directory': True}
            for p in primary_path.iterdir()
            if p.is_dir() and len(p.name) == 4 and p.name.isdigit()
        ]
        return sorted(folders, key=lambda x: x['name'])

    def get_folder_contents(self, folder_path: str) -> List[Dict[str, Any]]:
        """Gets the contents (files and folders) of a specific directory."""
        path = Path(folder_path)
        if not path.is_dir():
            return []

        contents = [
            {'name': p.name, 'path': str(p), 'is_directory': p.is_dir()}
            for p in path.iterdir()
        ]
        # Sort directories first, then files
        return sorted(contents, key=lambda x: (not x['is_directory'], x['name'].lower()))

    # --- Artifact Creation Logic ---

    def create_new_folder(self, parent_path: Path, folder_name: str, description: Optional[str] = None) -> Optional[Path]:
        """
        Creates a new folder at the specified path and optionally adds a description file.

        Args:
            parent_path: The directory in which to create the new folder.
            folder_name: The name for the new folder.
            description: An optional description to be saved in a 'readme.md' file.

        Returns:
            The Path to the newly created folder if successful, otherwise None.
        """
        # Sanitize folder name to prevent directory traversal issues
        # and remove characters that are invalid in file paths on Windows.
        sanitized_name = re.sub(r'[<>:"/\\|?*]', '', folder_name).strip()
        if not sanitized_name:
            print(f"Error: Invalid folder name '{folder_name}'.")
            return None
        
        new_name = f"{sanitized_name} {description}" if description else sanitized_name

        new_folder_path = parent_path / new_name
        
        # Check for existing folder/file to prevent overwriting
        if new_folder_path.exists():
            print(f"Error: A folder or file named '{new_name}' already exists at this location.")
            return None
            
        try:
            # Create the new directory
            new_folder_path.mkdir(parents=True, exist_ok=False)
            print(f"Successfully created folder: {new_folder_path}")
            return new_folder_path
        except OSError as e:
            print(f"Error creating directory {new_folder_path}: {e}")
            return None


    def create_new_project(self, project_type: ProjectType, title: str, parent_dir: Path, metadata: Dict[str, Any]) -> Optional[Project]:
        """Creates a new project, saves it, and returns the Project object."""
        project_id = str(uuid.uuid4()) # Generate a unique ID for the new project
        
        # Use a filename pattern from config or create a simple one
        filename = f"{title.replace(' ', '_')}_{project_id[:8]}.json"
        file_path = parent_dir / filename

        project = Project(
            project_id=project_id,
            project_type=project_type,
            title=title,
            file_path=file_path,
            metadata=metadata
        )
        project.save()
        print(f"Successfully created and saved new project: {file_path}")
        return project

    # --- Master Source Management ---

    def _load_master_sources_for_region(self, region: str) -> Dict[str, SourceRecord]:
        """Loads all master SourceRecords for a region into the cache."""
        if region in self._master_source_cache:
            return self._master_source_cache[region]

        source_file_path = self.master_sources_dir / f"{region}_sources.json"
        if not source_file_path.exists():
            self._master_source_cache[region] = {}
            return {}
        try:
            with open(source_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            sources_list = data.get('sources', [])
            source_map = {
                record_data['id']: SourceRecord.from_dict(record_data)
                for record_data in sources_list
            }
            self._master_source_cache[region] = source_map
            return source_map
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error loading master sources for region '{region}': {e}")
            return {}

    def get_master_sources_for_region(self, region: str) -> List[SourceRecord]:
        """Public method to get all master sources for a region."""
        source_map = self._load_master_sources_for_region(region)
        return list(source_map.values())

    # --- Project and Source Relationship Logic ---

    def get_region_for_project(self, project_path: Path) -> str:
        """Determines the correct region for a project based on its path."""
        sorted_mappings = sorted(REGIONAL_MAPPINGS, key=lambda m: m.priority, reverse=True)
        for mapping in sorted_mappings:
            for pattern in mapping.directory_patterns:
                if project_path.match(pattern):
                    return mapping.region_name
        return "General"

    def get_hydrated_sources_for_project(self, project: Project) -> List[SourceRecord]:
        """Takes a project and returns the full, ordered list of its SourceRecord objects."""
        if not project: return []
        region = self.get_region_for_project(project.file_path)
        master_sources = self._load_master_sources_for_region(region)
        hydrated_sources = []
        for link in project.sources:
            source_record = master_sources.get(link.source_id)
            if source_record:
                hydrated_sources.append(source_record)
        return hydrated_sources
        
    # --- Project Data Modification ---

    def add_source_to_project(self, project: Project, source_id: str):
        """Adds a source to a project and saves the project file."""
        project.add_source(source_id)
        project.save()

    def remove_source_from_project(self, project: Project, source_id: str):
        """Removes a source from a project and saves the project file."""
        project.remove_source(source_id)
        project.save()

    def reorder_sources_in_project(self, project: Project, new_ordered_ids: List[str]):
        """Reorders the sources in a project based on a new list of source IDs."""
        links_map = {link.source_id: link for link in project.sources}
        new_source_links = []
        for i, source_id in enumerate(new_ordered_ids):
            if source_id in links_map:
                link = links_map[source_id]
                link.order = i + 1
                new_source_links.append(link)
        project.sources = new_source_links
        project.save()

    # --- Project I/O ---

    def load_project(self, file_path: Path) -> Optional[Project]:
        """Loads a single project from a file path."""
        return Project.load(file_path)

    def save_project(self, project: Project):
        """Saves a project to its file path."""
        project.save()
