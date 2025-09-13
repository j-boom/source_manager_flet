"""
Project Service

Manages the lifecycle of project files, including creation, loading,
saving, and modification.
"""

import re
import uuid
import logging
from pathlib import Path
from filelock import FileLock, Timeout
from typing import Dict, Any, Optional, Tuple, TYPE_CHECKING
from datetime import datetime

from src.models import Project, ProjectSourceLink, SourceRecord
from .source_service import SourceService

if TYPE_CHECKING:
    from .admin_service import AdminService


class ProjectService:
    """Handles loading, saving, and modifying project data."""

    def __init__(self, source_service: SourceService, admin_service: "AdminService"):
        self.logger = logging.getLogger(__name__)
        self.source_service = source_service
        self.admin_service = admin_service
        self.logger.info("ProjectService initialized")

    def load_project(self, file_path: Path) -> Optional[Project]:
        """Loads a project from a JSON file."""
        self.logger.info(f"Loading project from: {file_path}")
        try:
            project = Project.load(file_path)
            if project:
                # After loading, check if it needs migration and perform it.
                self._migrate_project_if_needed(project)
                self.logger.info(
                    f"Successfully loaded project: {project.project_title}"
                )
            return project
        except Exception as e:
            self.logger.error(
                f"Error loading project from {file_path}: {e}", exc_info=True
            )
            return None

    def _migrate_project_if_needed(self, project: Project):
        """Compares a loaded project's fields against its type config and migrates if necessary."""
        project_configs = self.admin_service.get_project_types()
        current_config = project_configs.get(project.project_type)
        if not current_config:
            self.logger.warning(f"Cannot migrate project '{project.project_title}': Project type '{project.project_type}' not found in config.")
            return

        # Get the set of field names defined in the current configuration
        config_fields = {f['name'] for f in current_config.get('fields', [])}
        # Get the set of field names that already exist in the project's metadata
        project_fields = set(project.metadata.keys())
        
        # Determine which fields need to be added
        added_fields = config_fields - project_fields

        if not added_fields:
            return  # No migration needed

        self.logger.info(f"Migrating project '{project.project_title}' by adding new fields.")
        modified = False
        for field_name in added_fields:
            # Add the new field with a default empty value
            project.metadata[field_name] = ""
            modified = True
            self.logger.debug(f"Added field '{field_name}' to project '{project.project_title}'.")
        
        if modified:
            self.save_project(project)
            self.logger.info(f"Project '{project.project_title}' migration complete.")

    def save_project(self, project: Project):
        """Saves a project to its file path."""
        if not project.file_path:
            raise ValueError("Project has no file_path defined; cannot save.")

        self.logger.info(
            f"Saving project: {project.project_title} to {project.file_path}"
        )
        lock_path = project.file_path.with_suffix('.lock')

        try:
            # Acquire an exclusive lock on the associated .lock file, with a 5-second timeout.
            with FileLock(lock_path, timeout=5):
                self.logger.debug(f"Acquired lock for {project.file_path}")
                project.save()  # This is the original write operation
                self.logger.info(f"Successfully saved project: {project.project_title}")
        except Timeout:
            self.logger.warning(f"Could not acquire lock for {project.file_path}. File may be in use by another user.")
            # Raise a specific, user-friendly error that can be caught by the controller
            raise IOError("The project file is currently in use by another user. Please try again in a moment.")
        except Exception as e:
            self.logger.error(
                f"Error saving project {project.project_title}: {e}", exc_info=True
            )
            raise

    def create_new_project(
        self, parent_dir: Path, form_data: Dict[str, Any]
    ) -> Tuple[bool, str, Optional[Project]]:
        """Creates a new project object and file from form data."""
        project_type_code = form_data.get("project_type")
        project_configs = self.admin_service.get_project_types()
        project_config = project_configs.get(project_type_code)

        if not project_config:
            return False, f"Invalid project type: {project_type_code}", None

        metadata = form_data.copy()
        metadata["current_year"] = str(datetime.now().year)
        title = metadata.get("project_title") or "Untitled Project"

        try:
            filename = project_config['filename_pattern'].format(**metadata) + ".json"
        except KeyError as e:
            return False, f"Missing required field for filename: {e}", None

        file_path = parent_dir / filename
        if file_path.exists():
            return False, f"Project file already exists: {filename}", None

        project = Project(
            project_id=str(uuid.uuid4()),
            project_type=project_type_code,
            project_title=title,
            file_path=file_path,
            metadata=metadata
        )

        try:
            self.save_project(project)
            return True, f"Successfully created project: {filename}", project
        except Exception as e:
            return False, "An error occurred while saving the project.", None

    def add_source_to_project(
        self, project: Project, source_id: str, link_data: Dict[str, Any]
    ):
        """Adds a source link to a project and updates the master source record."""
        project.add_source(source_id, link_data)

        # Update the master source's 'used_in' list
        source_record = self.source_service.get_source_by_id(source_id)
        if source_record:
            if not any(
                p.get("project_id") == project.project_id for p in source_record.used_in
            ):
                source_record.used_in.append(
                    {"project_id": project.project_id, "project_title": project.project_title}
                )
                self.source_service.update_master_source(
                    source_id, source_record.to_dict()
                )

        self.save_project(project)

    def remove_source_from_project(self, project: Project, source_id: str):
        """Removes a source link from a project and updates the master source record."""
        project.remove_source(source_id)

        # Update the master source's 'used_in' list
        source_record = self.source_service.get_source_by_id(source_id)
        if source_record:
            source_record.used_in = [
                p
                for p in source_record.used_in
                if p.get("project_id") != project.project_id
            ]
            self.source_service.update_master_source(source_id, source_record.to_dict())

        self.save_project(project)

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
            number_match = re.search(r"(\d{4,})", dir_name)

            if number_match:
                return number_match.group(1)

            # TODO is the following logic still needed?
            # If no number found in current directory, try parent directories
            # but only go up one level to avoid false positives
            if parent_path.parent and parent_path.parent != parent_path:
                parent_dir_name = parent_path.parent.name
                parent_number_match = re.search(r"(\d{4,})", parent_dir_name)
                if parent_number_match:
                    return parent_number_match.group(1)

        except (AttributeError, IndexError, OSError):
            pass

        return ""

    def update_project_source_link(
        self, project: Project, source_id: str, link_data: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Finds a source link within a project, updates it, saves the project,
        and also updates the master source record to track project usage.
        """
        link_found = False
        for link in project.sources:
            if link.source_id == source_id:
                # Update all fields provided in link_data into the link's metadata
                for key, value in link_data.items():
                    link.metadata[key] = value
                link_found = True
                break

        # If the link wasn't found, it means this is a new source being added.
        if not link_found:
            project.add_source(source_id, link_data)
            self.logger.info(f"No existing link found for source {source_id}. Created a new one.")

        try:
            # Save the entire project object, which now contains the updated link
            self.save_project(project)

            # Now, update the master source record to ensure it tracks this project's usage
            source_record = self.source_service.get_source_by_id(source_id)
            if source_record:
                # Check if this project is already in the 'used_in' list to avoid duplicates
                if not any(
                    p.get("project_id") == project.project_id
                    for p in source_record.used_in
                ):
                    source_record.used_in.append(
                        {"project_id": project.project_id, "project_title": project.project_title}
                    )
                    # Use the existing update_master_source method to save the change
                    self.source_service.update_master_source(
                        source_id, source_record.to_dict()
                    )

            return True, "Project source link and master record updated successfully."
        except Exception as e:
            self.logger.error(
                f"Failed to save project or update master source: {e}", exc_info=True
            )
            return False, "Failed to save project or update master source."

    def associate_powerpoint_file(self, project: Project, powerpoint_file: str):
        """
        Associates a PowerPoint file with the current project.

        Args:
            powerpoint_file_path: The file path of the PowerPoint file to associate.
        """
        try:
            project.associate_powerpoint_file(powerpoint_file)
            self.save_project(project)
        except Exception as e:
            self.logger.error(f"Failed to associate PowerPoint file: {e}", exc_info=True)
