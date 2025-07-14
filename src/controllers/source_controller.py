"""
Source Controller - Handles source-related operations.

This controller manages adding sources to projects, on-deck lists, etc.
"""

from typing import TYPE_CHECKING
from .base_controller import BaseController
from models import ProjectSourceLink

if TYPE_CHECKING:
    from .app_controller import AppController


class SourceController(BaseController):
    """Handles all source-related operations."""
    
    def add_source_to_on_deck(self, source_id: str):
        """Adds a source ID to the on_deck_sources list in the current project's metadata."""
        self.logger.info(f"DIAGNOSTIC: SourceController.add_source_to_on_deck called with source_id={source_id}")
        project = self.project_state_manager.current_project
        if not project:
            self.logger.warning("DIAGNOSTIC: Attempted to add source to On Deck, but no project is loaded.")
            return

        self.logger.info(f"DIAGNOSTIC: Adding source '{source_id}' to On Deck for project '{project.project_title}'.")

        # Initialize on_deck_sources if it doesn't exist
        if "on_deck_sources" not in project.metadata:
            project.metadata["on_deck_sources"] = []

        # Add to on deck if not already there
        if source_id not in project.metadata["on_deck_sources"]:
            project.metadata["on_deck_sources"].append(source_id)
            self.data_service.save_project(project)
            self.logger.info(f"DIAGNOSTIC: Source '{source_id}' added to On Deck.")
        else:
            self.logger.info(f"DIAGNOSTIC: Source '{source_id}' is already in On Deck.")

    def remove_source_from_on_deck(self, source_id: str):
        """Removes a source ID from the on_deck_sources list in the current project's metadata."""
        project = self.project_state_manager.current_project
        if not project:
            self.logger.warning("Attempted to remove source from On Deck, but no project is loaded.")
            return

        if "on_deck_sources" in project.metadata and source_id in project.metadata["on_deck_sources"]:
            project.metadata["on_deck_sources"].remove(source_id)
            self.data_service.save_project(project)
            self.logger.info(f"Source '{source_id}' removed from On Deck for project '{project.project_title}'.")
        else:
            self.logger.info(f"Source '{source_id}' not found in On Deck for project '{project.project_title}'.")

    def add_source_to_project(self, source_id: str, notes: str, declassify: str):
        """
        Adds a master source to the currently loaded project, including project-specific
        notes and declassify info, and removes it from 'On Deck'.
        """
        project = self.project_state_manager.current_project
        if not project:
            self.logger.warning("Attempted to add source to project, but no project is loaded.")
            return

        if any(link.source_id == source_id for link in project.sources):
            self.logger.info(f"Source '{source_id}' is already in project '{project.project_title}'.")
            return

        # Delegate the full operation to the data service, which handles all saving.
        self.data_service.add_source_to_project(project, source_id, notes, declassify)

        self.logger.info(f"Source '{source_id}' added to project '{project.project_title}' and removed from On Deck.")