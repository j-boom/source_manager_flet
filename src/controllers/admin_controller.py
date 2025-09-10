"""
Admin Controller

Handles the business logic for the AdminView.
"""
from .base_controller import BaseController

class AdminController(BaseController):
    """Controller for the admin view."""

    def __init__(self, controller):
        super().__init__(controller)
        self.admin_service = self.controller.admin_service

    def get_project_types_config(self):
        """Fetches the project types config from the service."""
        return self.admin_service.get_project_types()

    def get_source_types_config(self):
        """Fetches the source types config from the service."""
        return self.admin_service.get_source_types()

    def save_project_types_config(self, new_config):
        """Saves the project types config via the service."""
        if self.admin_service.save_project_types(new_config):
            self.controller.show_success_message("Project types saved successfully.")
            # Here you might trigger a notification that a restart is needed
        else:
            self.controller.show_error_message("Failed to save project types.")

    def save_source_types_config(self, new_config):
        """Saves the source types config via the service."""
        if self.admin_service.save_source_types(new_config):
            self.controller.show_success_message("Source types saved successfully.")
        else:
            self.controller.show_error_message("Failed to save source types.")
