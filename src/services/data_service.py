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
from config import (
    REGIONAL_MAPPINGS,
    MASTER_SOURCES_DIR,
    PROJECT_DATA_DIR,
    get_project_type_config,
)
from src.models.project_models import Project, ProjectType
from src.models.source_models import SourceRecord, SourceType


class DataService:
    """Manages all data loading, saving, and business logic."""

    def __init__(self):
        """Initializes the service."""
        self.master_sources_dir = Path(MASTER_SOURCES_DIR)
        self.project_data_dir = Path(PROJECT_DATA_DIR)
        self.master_sources_dir.mkdir(parents=True, exist_ok=True)
        self.project_data_dir.mkdir(parents=True, exist_ok=True)
        self._master_source_cache: Dict[str, Dict[str, SourceRecord]] = {}

    # --- Directory and File System Logic ---
    def get_primary_folders(self) -> List[str]:
        if not self.project_data_dir.exists():
            return []
        return sorted([p.name for p in self.project_data_dir.iterdir() if p.is_dir()])

    def get_folder_contents(self, folder_path: str) -> List[Dict[str, Any]]:
        path = Path(folder_path)
        if not path.is_dir():
            return []
        contents = [{"name": p.name, "path": str(p), "is_directory": p.is_dir()} for p in path.iterdir()]
        return sorted(contents, key=lambda x: (not x["is_directory"], x["name"].lower()))

    # --- Artifact Creation Logic ---
    def create_new_folder(self, parent_path: Path, folder_name: str, description: Optional[str] = None) -> Tuple[bool, str]:
        sanitized_filename = re.sub(r'[<>:"/\\|?*]', "", folder_name).strip()
        if description:
            sanitized_description = (re.sub(r'[<>:"/\\|?*]', "", description).strip() if description else None)
        if not sanitized_filename:
            return False, f"Invalid folder name '{folder_name}'."
        new_folder_path = (parent_path / f"{sanitized_filename} {sanitized_description}" if sanitized_description else parent_path / sanitized_filename)
        if new_folder_path.exists():
            return False, f"A folder or file named '{sanitized_filename}' already exists."
        try:
            new_folder_path.mkdir(parents=True, exist_ok=False)
            return True, f"Successfully created folder '{sanitized_filename}'."
        except OSError as e:
            return False, f"Failed to create directory: {e}"

    def create_new_project(self, parent_dir: Path, form_data: Dict[str, Any]) -> Tuple[bool, str, Optional[Project]]:
        """
        Creates a new project file from form data, injecting the current year.
        """
        project_type_code = form_data.get("project_type")
        if not project_type_code:
            return False, "Project type was not specified.", None

        project_config = get_project_type_config(project_type_code)
        if not project_config:
            return False, f"Invalid project type: {project_type_code}", None

        metadata = form_data.copy()
        metadata["current_year"] = str(datetime.now().year)
        title = metadata.get("project_title") or metadata.get("document_title", "Untitled Project")

        try:
            filename_pattern = project_config.filename_pattern
            filename = filename_pattern.format(**metadata) + ".json"
        except KeyError as e:
            return False, f"Missing required field for filename: {e}", None

        file_path = parent_dir / filename
        if file_path.exists():
            return False, f"A project file named '{filename}' already exists.", None

        project = Project(
            project_id=str(uuid.uuid4()),
            project_type=ProjectType(project_type_code),
            title=title,
            file_path=file_path,
            metadata=metadata,
        )
        try:
            project.save()
            return True, f"Successfully created project: {filename}", project
        except Exception as e:
            return False, "An error occurred while saving the project.", None

    # --- Master Source Management ---
    def _load_master_sources_for_region(self, region: str) -> Dict[str, SourceRecord]:
        if region in self._master_source_cache:
            return self._master_source_cache[region]
        source_file_path = self.master_sources_dir / f"{region}_sources.json"
        if not source_file_path.exists():
            self._master_source_cache[region] = {}
            return {}
        try:
            with open(source_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            sources_list = data.get("sources", [])
            source_map = {record_data["id"]: SourceRecord.from_dict(record_data) for record_data in sources_list}
            self._master_source_cache[region] = source_map
            return source_map
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error loading master sources for region '{region}': {e}")
            return {}

    def get_master_sources_for_region(self, region: str) -> List[SourceRecord]:
        source_map = self._load_master_sources_for_region(region)
        return list(source_map.values())

    def get_all_master_sources(self) -> List[SourceRecord]:
        all_sources = []
        source_files = list(self.master_sources_dir.glob("*_sources.json"))
        for f in source_files:
            region_name = f.name.replace("_sources.json", "")
            all_sources.extend(self.get_master_sources_for_region(region_name))
        return all_sources

    def get_source_by_id(self, source_id: str) -> Optional[SourceRecord]:
        for region_cache in self._master_source_cache.values():
            if source_id in region_cache:
                return region_cache[source_id]
        
        all_sources = self.get_all_master_sources()
        for source in all_sources:
            if source.id == source_id:
                return source
        return None

    def create_new_source(self, region: str, form_data: Dict[str, Any]) -> Tuple[bool, str, Optional[SourceRecord]]:
        source_type_str = form_data.get("source_type")
        if not source_type_str:
            return False, "Source type not specified.", None

        source_data = form_data.copy()
        source_data['id'] = str(uuid.uuid4())
        source_data['region'] = region
        
        if 'authors' in source_data and isinstance(source_data['authors'], str):
            source_data['authors'] = [author.strip() for author in source_data['authors'].split(',') if author.strip()]

        try:
            new_source = SourceRecord.from_dict(source_data)
        except Exception as e:
            return False, f"Failed to create source model: {e}", None

        source_file_path = self.master_sources_dir / f"{region}_sources.json"
        if source_file_path.exists():
            with open(source_file_path, "r", encoding="utf-8") as f:
                master_data = json.load(f)
            sources_list = master_data.get("sources", [])
        else:
            sources_list = []
            master_data = {"sources": sources_list}

        sources_list.append(new_source.to_dict())
        
        try:
            with open(source_file_path, "w", encoding="utf-8") as f:
                json.dump(master_data, f, indent=4)
            
            if region in self._master_source_cache:
                del self._master_source_cache[region]
                
            return True, "Source created successfully.", new_source
        except Exception as e:
            return False, f"Failed to save master source file: {e}", None

    # --- FIX: Add method to update an existing source ---
    def update_master_source(self, source_id: str, updated_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Finds a master source, updates it with new data, and saves the regional file."""
        source = self.get_source_by_id(source_id)
        if not source:
            return False, f"Source with ID '{source_id}' not found."

        # Update the source object's attributes
        for key, value in updated_data.items():
            if hasattr(source, key):
                if key == 'authors' and isinstance(value, str):
                    value = [author.strip() for author in value.split(',') if author.strip()]
                setattr(source, key, value)
        
        source.last_modified = datetime.utcnow().isoformat()

        region = source.region
        source_file_path = self.master_sources_dir / f"{region}_sources.json"
        
        if not source_file_path.exists():
            return False, f"Master source file for region '{region}' does not exist."

        try:
            with open(source_file_path, "r", encoding="utf-8") as f:
                master_data = json.load(f)
            
            sources_list = master_data.get("sources", [])
            
            found = False
            for i, record_data in enumerate(sources_list):
                if record_data.get("id") == source_id:
                    sources_list[i] = source.to_dict()
                    found = True
                    break
            
            if not found:
                return False, f"Could not find source ID '{source_id}' in file '{source_file_path.name}'."

            with open(source_file_path, "w", encoding="utf-8") as f:
                json.dump(master_data, f, indent=4)
            
            if region in self._master_source_cache:
                del self._master_source_cache[region]
            
            return True, "Source updated successfully."
        except Exception as e:
            return False, f"Failed to save updated source: {e}"

    # --- Project and Source Relationship Logic ---
    def get_region_for_project(self, project_path: Path) -> str:
        sorted_mappings = sorted(REGIONAL_MAPPINGS, key=lambda m: m.priority, reverse=True)
        for mapping in sorted_mappings:
            for pattern in mapping.directory_patterns:
                if project_path.match(pattern):
                    return mapping.region_name
        return "General"

    def get_hydrated_sources_for_project(self, project: Project) -> List[SourceRecord]:
        if not project: return []
        region = self.get_region_for_project(project.file_path)
        master_sources = self._load_master_sources_for_region(region)
        return [master_sources.get(link.source_id) for link in project.sources if link.source_id in master_sources]

    # --- Project Data Modification ---
    def add_source_to_project(self, project: Project, source_id: str):
        project.add_source(source_id)
        project.save()

    def remove_source_from_project(self, project: Project, source_id: str):
        project.remove_source(source_id)
        project.save()

    def reorder_sources_in_project(self, project: Project, new_ordered_ids: List[str]):
        links_map = {link.source_id: link for link in project.sources}
        new_source_links = [links_map[source_id] for i, source_id in enumerate(new_ordered_ids) if source_id in links_map]
        for i, link in enumerate(new_source_links):
            link.order = i + 1
        project.sources = new_source_links
        project.save()

    # --- Project I/O ---
    def load_project(self, file_path: Path) -> Optional[Project]:
        return Project.load(file_path)

    def save_project(self, project: Project):
        project.save()