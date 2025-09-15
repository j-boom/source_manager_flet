from pathlib import Path
from typing import Callable, Optional, Dict, Any, TYPE_CHECKING, List
from src.models.project_models import FieldConfig

import flet as ft

from .base_controller import BaseController
from src.views.components.dialogs import (
    ProjectCreationDialog,
    AddSourceToProjectDialog,
    SourceCreationDialog,
    SourceEditorDialog,
    FirstTimeSetupDialog,
    FolderCreationDialog,
    AdminLoginDialog,
    AddConfigTypeDialog,
    UserEditorDialog,
    DeleteConfirmationDialog,
    SourceCitationDialog,
)

if TYPE_CHECKING:
    from src.models.source_models import SourceRecord


class DialogController(BaseController):
    """
    Controller for handling the opening and management of all dialogs in the application.

    This class centralizes dialog logic, ensuring consistent dialog behavior and
    separation of concerns from the main controller and views.
    """

    def __init__(self, app_controller):
        super().__init__(app_controller)
        self.admin_service = self.controller.admin_service

    def open_admin_login_dialog(self, on_success: Callable):
        """
        Opens the dialog to prompt for the admin password.

        Args:
            on_success: The function to call if authentication is successful.
        """
        dialog = AdminLoginDialog(
            page=self.controller.page,
            controller=self.controller,
            on_login_success=on_success,
        )
        # Use the show() method from the BaseDialog pattern to correctly display the dialog
        dialog.show()

    def open_folder_creation_dialog(self, parent_path: Path):
        """
        Opens the folder creation dialog.

        This method defines the callback that will be executed when the user
        clicks "Create" in the dialog. The callback contains the business logic,
        while the dialog itself only handles UI.

        Args:
            parent_path: The path where the new folder should be created.
        """

        def on_create_callback(folder_name: str, description: str):
            """This function is passed to the dialog to be called on success."""
            self.logger.info(f"Folder creation dialog confirmed for '{folder_name}'")
            # Delegate the actual folder creation to the appropriate service/controller
            success, message = self.controller.directory_service.create_new_folder(
                parent_path=parent_path,
                folder_name=folder_name,
                description=description,
            )
            if success:
                self.controller.project_browser_manager.update_state()
                self.controller.show_success_message(message)
                self.controller.update_view()
            else:
                self.controller.show_error_message(message)

        # Instantiate the refactored dialog with the callback
        dialog = FolderCreationDialog(
            page=self.controller.page,
            parent_path=parent_path,
            on_create=on_create_callback,
        )
        # Show the dialog
        dialog.show()

    def open_new_project_dialog(self, parent_path: Path):
        """
        Opens the refactored project creation dialog.

        This method defines the callback that will be executed when the user
        submits the dialog with valid data.

        Args:
            parent_path: The directory where the project will be created.
        """
        self.logger.info(f"Opening new project dialog for path: {parent_path}")
        # The BE number can be derived from the parent path's name
        initial_be = self.controller.directory_service.derive_project_number_from_path(
            parent_path
        )

        def on_create_callback(form_data: Dict[str, Any]):
            """This function contains the logic to execute on successful creation."""
            self.logger.info("Project dialog confirmed. Passing to ProjectController.")
            self.controller.project_controller.create_project(
                parent_path=parent_path,
                project_type=form_data["project_type"],
                form_data=form_data,
            )

        project_types = self.admin_service.get_project_types()
        # Instantiate the refactored dialog
        dialog = ProjectCreationDialog(
            page=self.controller.page,
            on_create=on_create_callback,
            initial_be_number=initial_be,
            project_types=project_types,
            dialog_controller=self,
        )
        dialog.show()

    def get_project_type_fields(self, project_type_code: str) -> List[Dict[str, Any]]:
        """
        Gets the raw field configuration dictionaries for a given project type
        that are configured to appear in the creation dialog.
        """
        project_configs = self.admin_service.get_project_types()
        project_config = project_configs.get(project_type_code)
        if project_config:
            all_fields_data = project_config.get("fields", [])
            # Filter for fields meant for the dialog
            dialog_fields_data = [
                f for f in all_fields_data if f.get("collection_stage") == "dialog"
            ]
            return dialog_fields_data
        return []

    def _open_add_config_type_dialog(self, config_category: str):
        """
        A generic helper to open a dialog for adding a new config type.
        
        Args:
            config_category: Either 'source' or 'project'.
        """
        self.logger.info(f"Opening 'add {config_category} type' dialog.")
        title = f"Add New {config_category.title()} Type"
        add_method = getattr(self.controller.admin_controller, f"add_new_{config_category}_type")

        def on_create_callback(display_name: str, internal_name: str):
            self.logger.info(f"Dialog confirmed for new {config_category} type: {display_name} ({internal_name})")
            add_method(display_name, internal_name)

        dialog = AddConfigTypeDialog(page=self.controller.page, title=title, on_create=on_create_callback)
        dialog.show()

    def open_add_source_type_dialog(self):
        """Opens a dialog to add a new source type."""
        self._open_add_config_type_dialog("source")

    def open_add_project_type_dialog(self):
        """Opens a dialog to add a new project type."""
        self._open_add_config_type_dialog("project")

    def open_user_editor_dialog(self, user_data: Optional[Dict[str, Any]] = None):
        """Opens a dialog to add or edit a user."""
        self.logger.info(f"Opening user editor dialog. User: {user_data.get('display_name') if user_data else 'New'}")

        def on_save_callback(original_name: Optional[str], updated_data: Dict[str, Any]):
            if original_name: # Editing existing user
                self.logger.info(f"Dialog confirmed for updating user: {original_name}")
                self.controller.admin_controller.update_user(original_name, updated_data)
            else: # Adding new user
                self.logger.info(f"Dialog confirmed for new user: {updated_data['display_name']}")
                self.controller.admin_controller.add_user(updated_data)

        dialog = UserEditorDialog(page=self.controller.page, on_save=on_save_callback, user_data=user_data)
        dialog.show()

    def open_delete_user_confirmation_dialog(self, user_name: str):
        """Opens a confirmation dialog before deleting a user."""
        self.logger.info(f"Opening delete confirmation for user: {user_name}")

        def on_confirm_callback():
            self.logger.info(f"Deletion confirmed for user: {user_name}")
            self.controller.admin_controller.delete_user(user_name)

        dialog = DeleteConfirmationDialog(page=self.controller.page,
            item_name=user_name,
            item_type="user",
            on_confirm=on_confirm_callback
        )
        dialog.show()

    def open_add_source_to_project_dialog(self, source_id: str, source_type: str):
        """
        Opens the dialog to collect link data before adding a source to a project.
        """
        self.logger.info(f"Opening add source to project dialog for source: {source_id}")

        def on_save_callback(link_data: Dict[str, Any]):
            self.logger.info(f"Dialog confirmed for adding source {source_id} to project.")
            self.controller.source_controller.add_source_to_project(source_id, link_data)

        dialog = AddSourceToProjectDialog(
            page=self.controller.page,
            source_type=source_type,
            dialog_controller=self,
            on_save=on_save_callback
        )
        dialog.show()

    def open_new_source_dialog(
        self,
        from_project_sources_tab: bool = False,
        target_country_from_view: Optional[str] = None,
    ):
        """
        Opens the refactored source creation dialog.
        """
        self.logger.info("Opening new source dialog.")

        # --- Define the callback function ---
        def on_create_callback(form_data: Dict[str, Any]):
            self.logger.info(
                "Source creation dialog confirmed. Passing to SourceController."
            )
            # Delegate the actual creation logic to the SourceController
            self.controller.source_controller.create_new_source(
                source_data=form_data, add_to_project=from_project_sources_tab
            )

        # --- Get data needed by the dialog ---
        available_countries = (
            self.controller.source_controller.get_available_countries()
        )

        target_country = target_country_from_view
        if not target_country:
            project = self.controller.project_controller.get_current_project()
            if project:
                target_country = (
                    self.controller.directory_service.get_country_for_project(
                        project.file_path
                    )
                )

        source_types = self.admin_service.get_source_types()
        # --- Instantiate and show the dialog ---
        dialog = SourceCreationDialog(
            page=self.controller.page,
            on_create=on_create_callback,
            dialog_controller=self,
            source_types=source_types,
            available_countries=available_countries,
            target_country=target_country,
            from_project_sources_tab=from_project_sources_tab,
        )
        dialog.show()

    def get_source_type_fields(self, source_type_code: str) -> List[Dict[str, Any]]:
        """
        Gets the fields for a given source type.
        """
        source_configs = self.admin_service.get_source_types()
        source_config = source_configs.get(source_type_code)
        if source_config:
            return source_config.get("fields", [])
        return []

    def open_source_editor_dialog(self, source_id: str):
        """
        Opens the refactored source editor dialog.

        This method fetches the required data (source and link records) and
        defines the callback for what to do when the user saves changes.
        """
        self.logger.info(f"Opening source editor for source_id: {source_id}")

        source = self.controller.source_controller.get_source_record_by_id(source_id)
        link = self.controller.source_controller.get_project_source_link(source_id)

        if not source or not link:
            self.controller.show_error_message(
                "Could not find source details for editing."
            )
            return

        # --- Define the callback function ---
        def on_save_callback(
            s_id: str, master_data: Dict[str, Any], link_data: Dict[str, Any]
        ):
            self.logger.info(f"Editor dialog confirmed for source_id: {s_id}")
            # Delegate saving to the SourceController
            try:
                self.controller.source_controller.submit_master_source_update(
                    s_id, master_data
                )
                self.controller.source_controller.submit_project_link_update(
                    s_id, link_data
                )
                self.controller.show_success_message("Source updated successfully.")
                self.controller.update_view()  # Refresh the view to show changes
            except Exception as e:
                self.logger.error(f"Failed to save source updates: {e}")
                # The controller methods will show their own error messages

        # --- Instantiate and show the dialog ---
        dialog = SourceEditorDialog(
            page=self.controller.page,
            source=source,
            link=link,
            on_save=on_save_callback,
            admin_service=self.admin_service,
        )
        dialog.show()

    def open_source_citation_dialog(self, source_id: str):
        """Opens the dialog to show source citation and details."""
        self.logger.info(f"Opening source citation dialog for source: {source_id}")
        source = self.controller.source_controller.get_source_record_by_id(source_id)
        if not source:
            self.controller.show_error_message(
                f"Could not find source with ID {source_id} to show details."
            )
            return

        dialog = SourceCitationDialog(
            page=self.controller.page,
            source=source,
            controller=self.controller
        )
        dialog.show()

    def new_project_dialog_closed(self, e):
        """
        Callback for when the new project dialog is closed (removes it from overlay).

        Args:
            e: The event/control to remove from the overlay.
        """
        self.controller.page.overlay.remove(e.control)
        self.controller.page.update()

    def show_first_time_setup(self):
        """Shows the first-time setup dialog to get the user's display name."""
        self.logger.info("Showing first-time setup dialog.")

        def on_setup_complete(display_name: str):
            """Callback executed when the setup dialog is completed."""
            self.logger.info(f"First time setup completed. Display name: '{display_name}'")
            # Delegate user creation and setup completion to the AdminController
            self.controller.admin_controller.create_initial_user(display_name)
            
            # Update UI and navigate to the home screen
            self.controller.main_view.update_greeting()
            self.controller.navigate_to("home")

        dialog = FirstTimeSetupDialog(
            page=self.controller.page, on_complete=on_setup_complete
        )
        dialog.show()
