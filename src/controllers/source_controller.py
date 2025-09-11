from typing import Dict, Any, TYPE_CHECKING, Optional, List
from .base_controller import BaseController

if TYPE_CHECKING:
    from src.models.source_models import SourceRecord, ProjectSourceLink
    from src.models.project_models import Project


class SourceController(BaseController):
    """
    Controller for all source-related actions, implementing the logic
    for creating master records and project-specific links.
    """

    def create_new_source(
        self, source_data: Dict[str, Any], add_to_project: bool = False
    ):
        """
        Creates a new master source record. If add_to_project is True,
        it also creates the project-specific link.
        """
        try:
            # Step 1: Separate core data from link data based on the configuration
            source_type = source_data.get("source_type")
            source_type_config = self.controller.admin_controller.get_source_type_config(source_type)
            all_fields_map = {f.get("name"): f for f in source_type_config.get("fields", [])}

            core_data = {"source_type": source_type}
            link_data = {}

            for key, value in source_data.items():
                # These are handled separately or are not part of the dynamic fields
                if key in ["source_type", "country", "title"]:
                    continue

                field_config = all_fields_map.get(key)
                if field_config and field_config.get("storage_scope") == "link":
                    link_data[key] = value
                else: # Belongs to core if it's in the config as core, or not in the config at all.
                    core_data[key] = value
            
            # The generated title should be stored in the canonical 'display_name' field.
            core_data['display_name'] = source_data.get('title')

            # Step 2: Extract country from the form data and create the master record
            country = source_data.pop("country", None)  # Get country from dropdown
            if not country:
                self.controller.show_error_message(
                    "Country/Region is required to create a source."
                )
                return
            
            success, message, source_record = self.controller.source_service.create_new_source(country, core_data)

            if not success or not source_record:
                self.controller.show_error_message(
                    f"Failed to create master source: {message}"
                )
                return

            self.logger.info(f"Master source record '{source_record.id}' created.")

            # Step 3: If the flag is set, add the new source to the current project
            if add_to_project:
                project = self.controller.project_controller.get_current_project()
                if project:
                    self.add_source_to_project(source_record.id, link_data)
                else:
                    self.logger.warning(
                        "add_to_project was True, but no project is loaded."
                    )

            self.controller.show_success_message("Source created successfully.")
            # Refresh the view to show the new source
            self.controller.update_view()

        except Exception as e:
            self.controller.show_error_message(f"Failed to create source: {e}")

    def add_source_to_project(self, source_id: str, link_data: Dict[str, Any]):
        """
        Creates the link between a source and a project, storing notes
        and declassify info in the project file and updating the master record.
        """
        project: Project | None = self.controller.project_state_manager.current_project
        if not project:
            self.controller.show_error_message("No active project to add a source to.")
            return

        try:
            # Data service handles creating the link and updating the master record
            self.controller.project_service.add_source_to_project(project, source_id, link_data)

            # If the source was on deck, remove it
            if "on_deck_sources" in project.metadata and source_id in project.metadata["on_deck_sources"]:
                project.metadata["on_deck_sources"].remove(source_id)
                self.controller.project_service.save_project(project)


            self.logger.info(
                f"Source '{source_id}' successfully linked to project '{project.project_id}'."
            )
            self.controller.update_view()  # Refresh to show the new source in the project list
        except Exception as e:
            self.logger.error(f"Failed to add source to project: {e}", exc_info=True)
            self.controller.show_error_message(f"Failed to add source to project: {e}")

    def remove_source_from_project(self, source_id: str):
        """
        Removes the link between a source and a project.
        """
        project = self.controller.project_controller.get_current_project()
        if not project:
            return

        try:
            # Data service handles removing the link and updating the master record
            self.controller.project_service.remove_source_from_project(
                project, source_id
            )
            self.logger.info(
                f"Source '{source_id}' unlinked from project '{project.id}'."
            )
            self.controller.show_success_message("Source removed from project.")
            self.controller.update_view()
        except Exception as e:
            self.controller.show_error_message(f"Failed to remove source: {e}")

    def submit_master_source_update(self, source_id: str, master_data: Dict[str, Any]):
        """
        Submits an update for a source's master record.
        """
        self.logger.info(f"Updating master record for source ID {source_id}.")
        try:
            self.controller.source_service.update_master_source(source_id, master_data)
        except Exception as e:
            self.controller.show_error_message(
                f"Failed to update source master record: {e}"
            )
            raise  # Re-raise to let the dialog know the update failed

    def submit_project_link_update(self, source_id: str, link_data: Dict[str, Any]):
        """
        Submits an update for a project-specific source link.
        """
        self.logger.info(f"Updating project link for source ID {source_id}.")
        project = self.controller.project_controller.get_current_project()
        if not project:
            self.logger.error("No active project to update source link.")
            return

        self.logger.info(f"Updating project link for source ID {source_id}.")
        try:
            self.controller.project_service.update_project_source_link(
                project=project, source_id=source_id, link_data=link_data
            )
            self.controller.show_success_message("Source usage details updated.")
            self.controller.update_view()
        except Exception as e:
            self.controller.show_error_message(
                f"Failed to update source usage details: {e}"
            )

    def get_all_source_records(self):
        """
        Retrieves all master source records from the data service.
        """
        return self.controller.source_service.get_all_master_sources()

    def get_source_record_by_id(self, source_id: str) -> Optional["SourceRecord"]:
        """
        Retrieves a master source record by its ID.
        """
        return self.controller.source_service.get_source_by_id(source_id)

    def get_project_source_link(self, source_id: str) -> Optional["ProjectSourceLink"]:
        """
        Retrieves a project-specific source link by source ID from the current project.
        """
        project = self.controller.project_controller.get_current_project()
        if project:
            for link in project.sources:
                if link.source_id == source_id:
                    return link
        return None

    def get_available_countries(self) -> List[str]:
        """Gets a list of all countries with source files."""
        return self.controller.source_service.get_available_countries()

    def get_sources_by_country(self, country: str) -> List["SourceRecord"]:
        """Gets all master source records for a specific country."""
        return self.controller.source_service.get_sources_by_country(country)