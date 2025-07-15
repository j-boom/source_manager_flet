from typing import Dict, Any
from .base_controller import BaseController
from src.models.project_models import Project

class ProjectController(BaseController):
    """
    Controller for all project-related actions.
    """
    def get_current_project(self) -> Project | None:
        """
        Gets the current project from the state manager.
        """
        return self.controller.project_state.get_project()

    def open_project(self, project_path: str):
        """
        Opens a project from the given path.
        """
        self.logger.info(f"Opening project at path: {project_path}")
        try:
            project = self.controller.data_service.load_project(project_path)
            self.controller.project_state.load_project(project)
            self.controller.user_config.add_recent_project(project_path)
            self.controller.clear_project_dependent_view_cache()
            self.controller.navigate('project_dashboard')
        except Exception as e:
            self.controller.show_error_message(f"Failed to open project: {e}")

    def close_project(self):
        """
        Closes the current project.
        """
        self.controller.project_state.clear_project()
        self.controller.clear_project_dependent_view_cache()
        self.controller.navigate('home', force_refresh=True)

    def create_project(self, project_data: Dict[str, Any]):
        """
        Creates a new project.
        """
        try:
            project_path = self.controller.data_service.create_project(project_data)
            self.open_project(project_path)
            self.controller.show_success_message("Project created successfully.")
        except Exception as e:
            self.controller.show_error_message(f"Failed to create project: {e}")


    def add_source_to_on_deck(self, source_id: str):
        """
        Adds a source's ID to the current project's 'on deck' list.
        """
        project = self.get_current_project()
        if not project:
            self.controller.show_error_message("No active project.")
            return

        if source_id not in project.on_deck_sources:
            project.on_deck_sources.append(source_id)
            self.controller.data_service.save_project(project)
            self.logger.info(f"Source '{source_id}' added to on deck for project '{project.id}'.")
            self.controller.update_view()
        else:
            self.logger.warning(f"Source '{source_id}' is already on deck.")

    def remove_source_from_on_deck(self, source_id: str):
        """
        Removes a source's ID from the current project's 'on deck' list.
        """
        project = self.get_current_project()
        if not project:
            self.controller.show_error_message("No active project.")
            return

        if source_id in project.on_deck_sources:
            project.on_deck_sources.remove(source_id)
            self.controller.data_service.save_project(project)
            self.logger.info(f"Source '{source_id}' removed from on deck for project '{project.id}'.")
            self.controller.update_view()
        else:
            self.logger.warning(f"Source '{source_id}' is not on deck.")