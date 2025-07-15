from pathlib import Path
from typing import Dict, Any
from .base_controller import BaseController


class ProjectController(BaseController):
    """
    Controller for all project-related actions.
    Orchestrates the flow of data between the data service (disk) and
    the project state manager (memory).
    """

    def open_project(self, project_path: Path):
        """
        Orchestrates opening a project.

        1. Loads the project file from disk via the DataService.
        2. Sets the returned Project object as the current app state.
        3. Updates the user's recent projects list.
        4. Navigates to the project dashboard view.

        Args:
            project_path (Path): The file path to the project's .json file.
        """
        self.logger.info(f"Opening project at path: {project_path}")
        try:
            # Step 1: Use the DataService to load the project from the file.
            project_object = self.controller.data_service.load_project(project_path)

            # Step 2: Check if the load was successful before proceeding.
            if project_object:
                # Step 3: Pass the loaded Project object to the state manager.
                self.controller.project_state_manager.load_project(project_object)

                # Add it to recent projects
                self.controller.user_config_manager.add_recent_project(
                    display_name=project_object.project_title,
                    path=str(project_path),
                )

                # Clear the cache for any views that depend on a project
                self.controller.clear_project_dependent_view_cache()

                # Step 4: Navigate to the project dashboard.
                self.controller.navigate_to("project_dashboard", force_refresh=True)
            else:
                self.controller.show_error_message(
                    f"Failed to load project from path: {project_path}"
                )

        except Exception as e:
            self.logger.error(
                f"An error occurred while opening project: {e}", exc_info=True
            )
            self.controller.show_error_message(f"An error occurred: {e}")

    def create_project(
        self, parent_path: Path, project_type: str, form_data: Dict[str, Any]
    ):
        """
        Orchestrates creating a new project.

        1. Calls the DataService to create the .json file on disk.
        2. If creation is successful, calls the open_project method
           to load the new project into the application state.

        Args:
            parent_path (Path): The directory where the project will be created.
            project_type (str): The project type code (e.g., "STD").
            form_data (Dict[str, Any]): The data collected from the creation dialog.
        """
        self.logger.info(f"Requesting project creation in: {parent_path}")
        try:
            # The DataService now handles creating the project object and file
            success, message, new_project = (
                self.controller.data_service.create_new_project(
                    parent_dir=parent_path, form_data=form_data
                )
            )

            if success and new_project:
                self.controller.show_success_message("Project created successfully.")
                # Automatically open the newly created project
                self.open_project(new_project.file_path)
            else:
                self.controller.show_error_message(f"Failed to create project: {message}")

        except Exception as e:
            self.logger.error(
                f"An error occurred during project creation: {e}", exc_info=True
            )
            self.controller.show_error_message(f"An error occurred: {e}")

    def close_project(self):
        """
        Closes the currently active project and returns to the browser view.
        """
        self.logger.info("Closing current project.")
        self.controller.project_state_manager.unload_project()
        self.controller.clear_project_dependent_view_cache()
        # Navigate back to the project browser
        self.controller.navigate_to("new_project", force_refresh=True)

    def update_project_metadata(self, updated_data: Dict[str, Any]):
        """
        Updates the metadata for the currently loaded project.
        """
        project = self.controller.project_state_manager.current_project
        if not project:
            self.controller.show_error_message("No project is loaded.")
            return

        self.logger.info(f"Updating metadata for project: {project.project_title}")

        # Update the project object's attributes from the form data
        for key, value in updated_data.items():
            if hasattr(project, key):
                setattr(project, key, value)
            elif key in project.metadata:
                project.metadata[key] = value

        # Save the updated project object back to its file
        try:
            self.controller.data_service.save_project(project)
            self.controller.show_success_message("Project metadata saved.")
        except Exception as e:
            self.logger.error(
                f"Failed to save metadata for project {project.project_title}: {e}",
                exc_info=True,
            )
            self.controller.show_error_message("Failed to save metadata.")

    def add_source_to_on_deck(self, source_id: str):
        """
        Adds a source's ID to the current project's 'on deck' list.
        """
        project = self.controller.project_state_manager.current_project
        if not project:
            self.controller.show_error_message("No active project.")
            return

        on_deck_sources = project.metadata.get("on_deck_sources", [])
        if source_id not in on_deck_sources:
            on_deck_sources.append(source_id)
            project.metadata["on_deck_sources"] = on_deck_sources
            self.controller.data_service.save_project(project)
            self.logger.info(
                f"Source '{source_id}' added to on deck for project '{project.project_title}'."
            )
            self.controller.update_view()
        else:
            self.logger.warning(f"Source '{source_id}' is already on deck.")

    def remove_source_from_on_deck(self, source_id: str):
        """
        Removes a source's ID from the current project's 'on deck' list.
        """
        project = self.controller.project_state_manager.current_project
        if not project:
            self.controller.show_error_message("No active project.")
            return

        on_deck_sources = project.metadata.get("on_deck_sources", [])
        if source_id in on_deck_sources:
            on_deck_sources.remove(source_id)
            project.metadata["on_deck_sources"] = on_deck_sources
            self.controller.data_service.save_project(project)
            self.logger.info(
                f"Source '{source_id}' removed from on deck for project '{project.project_title}'."
            )
            self.controller.update_view()
        else:
            self.logger.warning(f"Source '{source_id}' is not on deck.")

    def remove_source_from_project(self, source_id: str):
        """
        Removes a source link from the project.
        """
        project = self.controller.project_state_manager.current_project
        if not project:
            self.controller.show_error_message("No project loaded.")
            return
        
        try:
            self.controller.data_service.remove_source_from_project(project, source_id)
            self.controller.show_success_message("Source removed from project.")
            # Refresh the current view to reflect the change
            self.controller.update_view()
        except Exception as e:
            self.logger.error(f"Failed to remove source {source_id} from project: {e}", exc_info=True)
            self.controller.show_error_message("Failed to remove source.")
