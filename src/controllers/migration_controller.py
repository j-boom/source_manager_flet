import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

from .base_controller import BaseController


class MigrationController(BaseController):
    """
    Controller to manage the state and logic for migrating legacy project sources.
    """

    def __init__(self, app_controller):
        super().__init__(app_controller)
        self.logger = logging.getLogger(__name__)
        self.state: Dict[str, Any] = self._get_initial_state()

    def _get_initial_state(self) -> Dict[str, Any]:
        """Returns the default state dictionary."""
        return {
            "project_path": None,
            "project_data": None,
            "legacy_source_indices": [],
            "current_index": -1,
            "is_loaded": False,
        }

    def load_legacy_project(self, project_path_str: str) -> bool:
        """
        Loads a project JSON file, creates a backup, and identifies legacy sources.
        """
        self.state = self._get_initial_state()  # Reset state
        project_path = Path(project_path_str)

        if not project_path.exists():
            self.controller.show_error_message("Selected project file does not exist.")
            return False

        # Create a backup
        backup_path = project_path.with_suffix(".json.bak")
        if not backup_path.exists():
            project_path.rename(backup_path)
            backup_path.rename(project_path) # a bit of a dance to copy
            self.logger.info(f"Backup created at: {backup_path}")

        try:
            self.state["project_path"] = project_path
            self.state["project_data"] = json.loads(project_path.read_text(encoding="utf-8"))

            # Identify legacy sources (dictionaries with a 'citation' key)
            sources = self.state["project_data"].get("sources", [])
            self.state["legacy_source_indices"] = [
                i for i, s in enumerate(sources) if isinstance(s, dict) and "citation" in s
            ]

            if not self.state["legacy_source_indices"]:
                self.controller.show_error_message("No legacy sources found in this file.")
                return False

            self.state["current_index"] = 0
            self.state["is_loaded"] = True
            self.logger.info(f"Loaded {len(self.state['legacy_source_indices'])} legacy sources from {project_path.name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to load or parse project file: {e}", exc_info=True)
            self.controller.show_error_message(f"Error loading file: {e}")
            return False

    def get_current_legacy_source(self) -> Optional[Dict[str, Any]]:
        """Returns the legacy source data at the current index."""
        if not self.state["is_loaded"] or self.state["current_index"] >= len(self.state["legacy_source_indices"]):
            return None
        
        source_list_index = self.state["legacy_source_indices"][self.state["current_index"]]
        return self.state["project_data"]["sources"][source_list_index]

    def get_migration_status(self) -> str:
        """Returns a status string like 'Source 1 of 15'."""
        if not self.state["is_loaded"]:
            return "No project loaded."
        
        total = len(self.state["legacy_source_indices"])
        if total == 0:
            return "Migration complete for this file."
            
        current_num = self.state["current_index"] + 1
        return f"Source {current_num} of {total}"

    def parse_legacy_source(self, legacy_source: Dict[str, Any]) -> Dict[str, Any]:
        """
        Uses your custom parsers to pre-populate form fields from the legacy source string.
        
        Args:
            legacy_source: The dict containing `{"citation": "...", "comment": "..."}`.

        Returns:
            A dictionary of pre-filled form data, e.g., `{"authors": "...", "title": "..."}`.
        """
        pre_filled_data = {}
        citation_string = legacy_source.get("citation", "")
        comment_string = legacy_source.get("comment", "")

        # =============================================================================
        # TODO: THIS IS WHERE YOU SHOULD CALL YOUR PRE-WRITTEN PARSERS
        #
        # Example:
        #
        # from my_parsers import parse_author, parse_title
        #
        # if citation_string:
        #     pre_filled_data["authors"] = parse_author(citation_string)
        #     pre_filled_data["title"] = parse_title(citation_string)
        #
        # if comment_string:
        #     pre_filled_data["usage_notes"] = comment_string # 'comment' maps to 'usage_notes'
        #
        # =============================================================================

        # For now, I'll just map the comment to usage_notes as a placeholder
        if comment_string:
            pre_filled_data["usage_notes"] = comment_string

        self.logger.info(f"Pre-filled data from parser: {pre_filled_data}")
        return pre_filled_data

    def save_migrated_source(self, form_data: Dict[str, Any]) -> bool:
        """
        Creates a new master source, replaces the legacy data in the project file
        with a new source link, and saves the project file.
        """
        if not self.state["is_loaded"]:
            self.controller.show_error_message("No project loaded to save to.")
            return False

        # Create the new master source record. This now returns the created object.
        new_source_record = self.controller.source_controller.create_new_source(
            source_data=form_data, add_to_project=False
        )

        if not new_source_record:
            self.controller.show_error_message("Failed to create the new master source. Aborting save.")
            return False

        # Separate link data from the form data
        source_type_config = self.controller.admin_service.get_source_type_config(form_data["source_type"])
        link_data = {}
        if source_type_config:
            for field in source_type_config.get("fields", []):
                if field.get("storage_scope") == "link" and field["name"] in form_data:
                    link_data[field["name"]] = form_data[field["name"]]

        # Create the new link structure
        new_link = {"source_id": new_source_record.id, "metadata": link_data}

        # Replace the old source dict with the new link dict in the project data
        source_list_index = self.state["legacy_source_indices"][self.state["current_index"]]
        self.state["project_data"]["sources"][source_list_index] = new_link

        # Save the entire updated project file
        try:
            project_path = self.state["project_path"]
            project_path.write_text(json.dumps(self.state["project_data"], indent=4), encoding="utf-8")
            self.logger.info(f"Successfully saved migrated source to {project_path.name}")
            
            # Move to the next source
            self.go_to_next_source()
            return True
        except Exception as e:
            self.logger.error(f"Failed to write updated project file: {e}", exc_info=True)
            self.controller.show_error_message(f"Failed to save project file: {e}")
            return False

    def go_to_next_source(self):
        if self.state["is_loaded"] and self.state["current_index"] < len(self.state["legacy_source_indices"]) - 1:
            self.state["current_index"] += 1

    def go_to_previous_source(self):
        if self.state["is_loaded"] and self.state["current_index"] > 0:
            self.state["current_index"] -= 1