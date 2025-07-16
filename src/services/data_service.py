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
        self.logger.info(f"Creating new project in directory: {parent_dir}")
        self.logger.debug(f"Form data: {form_data}")
        
        project_type_code = form_data.get("project_type")
        if not project_type_code:
            self.logger.error("Project type was not specified in form data")
            return False, "Project type was not specified.", None

        project_config = get_project_type_config(project_type_code)
        if not project_config:
            self.logger.error(f"Invalid project type: {project_type_code}")
            return False, f"Invalid project type: {project_type_code}", None

        metadata = form_data.copy()
        metadata["current_year"] = str(datetime.now().year)
        title = metadata.get("project_title") or metadata.get("document_title", "Untitled Project")
        
        self.logger.debug(f"Project title: {title}")

        try:
            filename_pattern = project_config.filename_pattern
            filename = filename_pattern.format(**metadata) + ".json"
            self.logger.debug(f"Generated filename: {filename}")
        except KeyError as e:
            self.logger.error(f"Missing required field for filename: {e}")
            return False, f"Missing required field for filename: {e}", None

        file_path = parent_dir / filename
        if file_path.exists():
            self.logger.warning(f"Project file already exists: {filename}")
            return False, f"A project file named '{filename}' already exists.", None

        project = Project(
            project_id=str(uuid.uuid4()),
            project_type=ProjectType(project_type_code),
            project_title=title,
            file_path=file_path,
            metadata=metadata,
        )
        try:
            project.save()
            self.logger.info(f"Successfully created project: {filename} at {file_path}")
            return True, f"Successfully created project: {filename}", project
        except Exception as e:
            self.logger.error(f"Error saving project: {e}", exc_info=True)
            return False, "An error occurred while saving the project.", None

    # --- Master Source Management ---
    def _load_master_sources_for_country(self, country: str) -> Dict[str, SourceRecord]:
        """Load master sources for a specific country."""
        if country in self._master_source_cache:
            return self._master_source_cache[country]
        source_file_path = self.master_sources_dir / get_source_file_for_country(country)
        if not source_file_path.exists():
            self._master_source_cache[country] = {}
            return {}
        try:
            with open(source_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            sources_list = data.get("sources", [])
            source_map = {record_data["id"]: SourceRecord.from_dict(record_data) for record_data in sources_list}
            self._master_source_cache[country] = source_map
            return source_map
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error loading master sources for country '{country}': {e}")
            return {}

    def get_master_sources_for_country(self, country: str) -> List[SourceRecord]:
        """Get all master sources for a specific country."""
        source_map = self._load_master_sources_for_country(country)
        return list(source_map.values())

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

    def create_new_source(self, country: str, form_data: Dict[str, Any]) -> Tuple[bool, str, Optional[SourceRecord]]:
        """Create a new master source for a specific country."""
        source_type_str = form_data.get("source_type")
        if not source_type_str:
            return False, "Source type not specified.", None

        source_data = form_data.copy()
        source_data['id'] = str(uuid.uuid4())
        source_data['region'] = country  # Keep 'region' field for backward compatibility, but store country
        
        if 'authors' in source_data and isinstance(source_data['authors'], str):
            source_data['authors'] = [author.strip() for author in source_data['authors'].split(',') if author.strip()]

        try:
            new_source = SourceRecord.from_dict(source_data)
        except Exception as e:
            return False, f"Failed to create source model: {e}", None

        source_file_path = self.master_sources_dir / get_source_file_for_country(country)
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
            
            if country in self._master_source_cache:
                del self._master_source_cache[country]
                
            return True, "Source created successfully.", new_source
        except Exception as e:
            return False, f"Failed to save master source file: {e}", None

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

    # --- Project I/O ---
    def load_project(self, file_path: Path) -> Optional[Project]:
        self.logger.info(f"Loading project from: {file_path}")
        try:
            project = Project.load(file_path)
            if project:
                self.logger.info(f"Successfully loaded project: {project.project_title}")
            else:
                self.logger.warning(f"Failed to load project from: {file_path}")
            return project
        except Exception as e:
            self.logger.error(f"Error loading project from {file_path}: {e}", exc_info=True)
            return None

    def save_project(self, project: Project):
        self.logger.info(f"Saving project: {project.project_title} to {project.file_path}")
        try:
            project.save()
            self.logger.info(f"Successfully saved project: {project.project_title}")
        except Exception as e:
            self.logger.error(f"Error saving project {project.project_title}: {e}", exc_info=True)
            raise

    def get_available_countries(self) -> List[str]:
        """Get list of available countries from existing source files."""
        countries = []
        source_files = list(self.master_sources_dir.glob("*_sources.json"))
        for f in source_files:
            country_name = f.name.replace("_sources.json", "")
            countries.append(country_name)
        return countries

    # --- Project Number Extraction Logic ---
    def derive_project_number_from_path(self, parent_path: Path) -> str:
        """
        Extracts the project/BE number from a directory path.
        
        The method looks for numeric patterns in the directory name itself, 
        typically in the format of year + sequential numbers (e.g., 2024333333).
        
        Args:
            parent_path: Path to the directory that might contain a project number
            
        Returns:
            The extracted project number as a string, empty string if not found
        """
        try:
            # Get the directory name from the path
            dir_name = parent_path.name
            
            # Look for numeric patterns that could be BE numbers
            # Common pattern: YYYY followed by digits (e.g., 2024333333)
            # TODO update this in production
            number_match = re.search(r'(\d{4,})', dir_name)
            
            if number_match:
                return number_match.group(1)
            
            # TODO is the following logic still needed?
            # If no number found in current directory, try parent directories
            # but only go up one level to avoid false positives
            if parent_path.parent and parent_path.parent != parent_path:
                parent_dir_name = parent_path.parent.name
                parent_number_match = re.search(r'(\d{4,})', parent_dir_name)
                if parent_number_match:
                    return parent_number_match.group(1)
                    
        except (AttributeError, IndexError, OSError):
            pass
            
        return ""
    
    def update_project_source_link(self, project: Project, source_id: str, link_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Finds a source link within a project, updates it, saves the project,
        and also updates the master source record to track project usage.
        """
        link_found = False
        for link in project.sources:
            if link.source_id == source_id:
                # Update the notes and declassify fields from the provided data
                link.notes = link_data.get("notes", link.notes)
                link.declassify = link_data.get("declassify", link.declassify)
                link_found = True
                break
        
        if not link_found:
            return False, f"Could not find source link with ID '{source_id}' in the project."
            
        try:
            # Save the entire project object, which now contains the updated link
            self.save_project(project)
            
            # Now, update the master source record to ensure it tracks this project's usage
            source_record = self.get_source_by_id(source_id)
            if source_record:
                # Check if this project is already in the 'used_in' list to avoid duplicates
                if not any(p.get('project_id') == project.project_id for p in source_record.used_in):
                    source_record.used_in.append({
                        "project_id": project.project_id,
                        "project_title": project.project_title,
                        "notes": link.notes # Add the specific notes to the usage tracker
                    })
                    # Use the existing update_master_source method to save the change
                    self.update_master_source(source_id, source_record.to_dict())

            return True, "Project source link and master record updated successfully."
        except Exception as e:
            self.logger.error(f"Failed to save project or update master source: {e}", exc_info=True)
            return False, "Failed to save project or update master source."
