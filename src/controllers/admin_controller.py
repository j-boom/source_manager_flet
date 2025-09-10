from .base_controller import BaseController

class AdminController(BaseController):
    """Controller for handling admin-related operations."""

    def __init__(self, app_controller):
        super().__init__(app_controller)
        self.admin_service = self.controller.admin_service

    def get_all_source_types(self):
        """Returns a list of all source types."""
        return list(self.admin_service.get_source_types().keys())

    def get_all_project_types(self):
        """Returns a list of all project types."""
        return list(self.admin_service.get_project_types().keys())

    def get_source_type_config(self, type_name: str):
        """Returns the configuration for a given source type."""
        source_types = self.admin_service.get_source_types()
        return source_types.get(type_name, {})

    def get_field_types(self):
        """Returns a list of all field types."""
        return ["text", "number", "date", "boolean", "textarea", "checkbox"]

    def save_source_type_config(self, type_name: str, config: dict):
        """Saves the configuration for a given source type."""
        source_types = self.admin_service.get_source_types()
        source_types[type_name] = config
        self.admin_service.save_source_types(source_types)

    def get_project_type_config(self, type_name: str):
        """Returns the configuration for a given project type."""
        project_types = self.admin_service.get_project_types()
        return project_types.get(type_name, {})

    def save_project_type_config(self, type_name: str, config: dict):
        """Saves the configuration for a given project type."""
        project_types = self.admin_service.get_project_types()
        project_types[type_name] = config
        self.admin_service.save_project_types(project_types)