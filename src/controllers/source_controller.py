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
        project = self.project_state_manager.current_project
        if not project:
            self.logger.warning("Attempted to add source to On Deck, but no project is loaded.")
            return

        self.logger.info(f"Adding source '{source_id}' to On Deck for project '{project.title}'.")

        # Initialize on_deck_sources if it doesn't exist
        if "on_deck_sources" not in project.metadata:
            project.metadata["on_deck_sources"] = []

        # Add to on deck if not already there
        if source_id not in project.metadata["on_deck_sources"]:
            project.metadata["on_deck_sources"].append(source_id)
            self.data_service.save_project(project)
            self.logger.info(f"Source '{source_id}' added to On Deck.")
        else:
            self.logger.info(f"Source '{source_id}' is already in On Deck.")

    def add_source_to_project(self, source_id: str):
        """Adds a master source to the currently loaded project and removes it from 'On Deck'."""
        project = self.project_state_manager.current_project
        if not project:
            self.logger.warning("Attempted to add source to project, but no project is loaded.")
            return

        # Check if the source is already in the project
        if any(link.source_id == source_id for link in project.sources):
            self.logger.info(f"Source '{source_id}' is already in project '{project.title}'.")
            return

        # Add the source to the project
        new_order = len(project.sources)
        new_link = ProjectSourceLink(source_id=source_id, order=new_order)
        project.sources.append(new_link)

        # Remove from on deck sources
        if "on_deck_sources" in project.metadata and source_id in project.metadata["on_deck_sources"]:
            project.metadata["on_deck_sources"].remove(source_id)

        self.data_service.save_project(project)
        self.logger.info(f"Source '{source_id}' added to project '{project.title}' and removed from On Deck.")
