"""
Data Service (Consolidated)

This service acts as the single gateway for all application data operations.
It combines directory management, project creation, and source handling into
a single, unified interface for the rest of the application.
"""

import json
import uuid
import re
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime

# Import the application's configuration and data models
from config import (
    MASTER_SOURCES_DIR,
    PROJECT_DATA_DIR,
    get_project_type_config,
    get_country_from_project_path,
    get_source_file_for_country,
)
from src.models.project_models import Project, ProjectType, ProjectSourceLink
from src.models.source_models import SourceRecord


class DataService:
    """Manages all data loading, saving, and business logic."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("DataService initialized")
        self.master_sources_dir = Path(MASTER_SOURCES_DIR)
        self.project_data_dir = Path(PROJECT_DATA_DIR)
        self.master_sources_dir.mkdir(parents=True, exist_ok=True)
        self.project_data_dir.mkdir(parents=True, exist_ok=True)
        self._master_source_cache: Dict[str, Dict[str, SourceRecord]] = {}


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
 
    def get_all_master_sources(self) -> List[SourceRecord]:
        """Get all master sources from all countries."""
        all_sources = []
        source_files = list(self.master_sources_dir.glob("*_sources.json"))
        for f in source_files:
            country_name = f.name.replace("_sources.json", "")
            all_sources.extend(self.get_master_sources_for_country(country_name))
        return all_sources

    def get_source_by_id(self, source_id: str) -> Optional[SourceRecord]:
        """Find a source by ID across all countries."""
        for country_cache in self._master_source_cache.values():
            if source_id in country_cache:
                return country_cache[source_id]
        
        all_sources = self.get_all_master_sources()
        for source in all_sources:
            if source.id == source_id:
                return source
        return None

    # --- FIX: Add method to update an existing source ---
    def update_master_source(self, source_id: str, updated_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Finds a master source, updates it with new data, and saves the country file."""
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

        country = source.region  # For backward compatibility, the 'region' field stores the country
        source_file_path = self.master_sources_dir / get_source_file_for_country(country)
        
        if not source_file_path.exists():
            return False, f"Master source file for country '{country}' does not exist."

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
            
            if country in self._master_source_cache:
                del self._master_source_cache[country]
            
            return True, "Source updated successfully."
        except Exception as e:
            return False, f"Failed to save updated source: {e}"

    # --- Project and Source Relationship Logic ---
    def get_country_for_project(self, project_path: Path) -> str:
        """Get the country name for a project based on its path."""
        return get_country_from_project_path(project_path)

    def get_hydrated_sources_for_project(self, project: Project) -> List[SourceRecord]:
        """Get all master sources linked to a project."""
        if not project: 
            return []
        country = self.get_country_for_project(project.file_path)
        master_sources = self._load_master_sources_for_country(country)
        hydrated_sources = []
        for link in project.sources:
            if link.source_id in master_sources:
                source = master_sources.get(link.source_id)
                if source is not None:
                    hydrated_sources.append(source)
        return hydrated_sources

    # --- Project Data Modification ---
    def add_source_to_project(self, project: Project, source_id: str, notes: str, declassify: str):
        """Adds a source to the project with notes and declassify info."""
        if source_id not in [s.source_id for s in project.sources]:
            link = ProjectSourceLink(source_id=source_id, notes=notes, declassify=declassify)
            project.sources.append(link)
            
            # Remove from on deck if present
            if "on_deck_sources" in project.metadata:
                if source_id in project.metadata["on_deck_sources"]:
                    project.metadata["on_deck_sources"].remove(source_id)
        
            source_record = self.get_source_by_id(source_id)
            if source_record:
                # Avoid duplicate entries
                if not any(p['project_id'] == project.project_id for p in source_record.used_in):
                    source_record.used_in.append({
                        "project_id": project.project_id,
                        "project_title": project.project_title,
                        "notes": notes
                    })
                    self.update_master_source(source_id, source_record.to_dict())

                project.save()
            try:
                # Save the project file with the new source link
                self.save_project(project)

                source_record = self.get_source_by_id(source_id)
                if source_record:
                    # Ensure this project isn't already listed in 'used_in'
                    if not any(p.get('project_id') == project.project_id for p in source_record.used_in):
                        source_record.used_in.append({
                            "project_id": project.project_id,
                            "project_title": project.project_title,
                            "notes": notes
                        })
                        self.update_master_source(source_id, source_record.to_dict())

            except Exception as e:
                self.logger.error(f"Failed to add source {source_id} to project {project.project_title}: {e}", exc_info=True)

    def remove_source_from_project(self, project: Project, source_id: str):
        project.remove_source(source_id)
        project.save()

    def reorder_sources_in_project(self, project: Project, new_ordered_ids: List[str]):
        """Reorder sources in project by rearranging the list based on new_ordered_ids."""
        links_map = {link.source_id: link for link in project.sources}
        new_source_links = [links_map[source_id] for source_id in new_ordered_ids if source_id in links_map]
        project.sources = new_source_links
        project.save()

        self.logger.info(f"Saving project: {project.project_title} to {project.file_path}")
        try:
            project.save()
            self.logger.info(f"Successfully saved project: {project.project_title}")
        except Exception as e:
            self.logger.error(f"Error saving project {project.project_title}: {e}", exc_info=True)
            raise

   

    # --- Project Number Extraction Logic ---
    
    
   