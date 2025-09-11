from .base_controller import BaseController
from typing import List, Dict, Any
from src.models.user_config_models import UserRole

class AdminController(BaseController):
    """Controller for handling admin-related operations."""

    def __init__(self, app_controller):
        super().__init__(app_controller)
        self.admin_service = self.controller.admin_service

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Returns a list of all user profiles."""
        return self.controller.admin_auth_service.get_all_users()

    def get_all_source_types(self):
        """Returns a list of all source types."""
        return self.admin_service.get_source_types().items()

    def get_all_project_types(self):
        """Returns a list of all project types."""
        return self.admin_service.get_project_types().items()

    def get_source_type_config(self, type_name: str):
        """Returns the configuration for a given source type."""
        source_types = self.admin_service.get_source_types()
        return source_types.get(type_name, {})

    def get_field_types(self):
        """Returns a list of all field types."""
        return ["text", "number", "date", "boolean", "textarea", "checkbox", "dropdown"]

    def save_source_type_config(self, type_name: str, config: dict):
        """Saves the configuration for a given source type."""
        source_types = self.admin_service.get_source_types()
        source_types[type_name] = config
        self.admin_service.save_source_types(source_types)

    def add_new_source_type(self, type_name: str):
        """Adds a new, empty source type configuration."""
        source_types = self.admin_service.get_source_types()
        if type_name in source_types:
            self.controller.show_error_message(f"Source type '{type_name}' already exists.")
            return

        # Create a default empty config
        source_types[type_name] = {"display_order": 99, "citation_format": "", "fields": []}
        self.admin_service.save_source_types(source_types)
        self.controller.show_success_message(f"Source type '{type_name}' created.")
        self.controller.update_view("admin")

    def get_project_type_config(self, type_name: str):
        """Returns the configuration for a given project type."""
        project_types = self.admin_service.get_project_types()
        return project_types.get(type_name, {})

    def save_project_type_config(self, type_name: str, config: dict):
        """Saves the configuration for a given project type."""
        project_types = self.admin_service.get_project_types()
        project_types[type_name] = config
        self.admin_service.save_project_types(project_types)

    def add_new_project_type(self, type_name: str):
        """Adds a new, empty project type configuration."""
        project_types = self.admin_service.get_project_types()
        if type_name in project_types:
            self.controller.show_error_message(f"Project type '{type_name}' already exists.")
            return

        # Create a default empty config
        project_types[type_name] = {
            "display_name": type_name.replace("_", " ").title(),
            "description": "A new project type.",
            "filename_pattern": "{project_title} - {current_year}",
            "display_order": 99,
            "fields": [],
        }
        self.admin_service.save_project_types(project_types)
        self.controller.show_success_message(f"Project type '{type_name}' created.")
        self.controller.update_view("admin")

    def add_user(self, user_data: Dict[str, Any]):
        """Adds a new user."""
        success = self.controller.admin_auth_service.add_user(
            display_name=user_data["display_name"],
            role=UserRole(user_data["role"]),
            is_active=user_data["is_active"]
        )
        if success:
            self.controller.show_success_message(f"User '{user_data['display_name']}' created.")
            self.controller.update_view("admin")
        else:
            self.controller.show_error_message(f"Failed to create user '{user_data['display_name']}'. Name may already exist.")

    def update_user(self, original_name: str, updated_data: Dict[str, Any]):
        """Updates an existing user's profile."""
        success = self.controller.admin_auth_service.update_user(original_name, updated_data)
        if success:
            self.controller.show_success_message(f"User '{updated_data['display_name']}' updated.")
            self.controller.update_view("admin")
        else:
            self.controller.show_error_message(f"Failed to update user '{original_name}'.")

    def delete_user(self, user_name: str):
        """Deletes a user and their associated config file."""
        if self.controller.admin_auth_service.remove_user(user_name):
            self.controller.user_config_manager.delete_user_config(user_name)
            self.controller.show_success_message(f"User '{user_name}' deleted.")
            self.controller.update_view("admin")
        else:
            self.controller.show_error_message(f"Failed to delete user '{user_name}'.")