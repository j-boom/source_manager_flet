from pathlib import Path
from typing import Callable, Optional, Dict, Any, List

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
    AddBoilerplateSourcesDialog,
    ImportSourcesDialog,
)


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
            """Callback executed on successful dialog submission."""
            self.logger.info("Folder creation dialog confirmed for '%s'", folder_name)
            # Delegate the actual folder creation to the appropriate service/controller
            success, message = self.controller.directory_service.create_new_folder(
                parent_path=parent_path,
                folder_name=folder_name,
                description=description,
            )
            # Show feedback to the user and refresh the view
            if success:
                self.controller.show_success_message(message)
                self.controller.update_view()
            else:
                self.controller.show_error_message(message)

        # Instantiate the dialog, passing the callback to it.
        dialog = FolderCreationDialog(
            page=self.controller.page,
            parent_path=parent_path,
            on_create=on_create_callback,
        )
        # Display the dialog to the user.
        dialog.show()

    def open_new_project_dialog(self, parent_path: Path):
        """
        Opens the refactored project creation dialog.

        This method defines the callback that will be executed when the user
        submits the dialog with valid data.

        Args:
            parent_path: The directory where the project will be created.
        """
        self.logger.info("Opening new project dialog for path: %s", parent_path)
        # Pre-calculate any values the dialog might need, like the BE number.
        initial_be = self.controller.directory_service.derive_project_number_from_path(
            parent_path
        )

        def on_create_callback(form_data: Dict[str, Any]):
            """Callback to handle the collected form data upon successful submission."""
            self.logger.info("Project dialog confirmed. Passing to ProjectController.")
            self.controller.project_controller.create_project(
                parent_path=parent_path,
                project_type=form_data["project_type"],
                form_data=form_data,
            )

        # Fetch data required by the dialog, such as available project types.
        project_types = self.admin_service.get_project_types()
        # Instantiate and show the dialog.
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

        Args:
            project_type_code: The internal code for the project type (e.g., "STD").
        Returns: A list of field configuration dictionaries.
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
        # This private helper centralizes the logic for adding new configuration types,
        # reducing code duplication between adding source types and project types.
        self.logger.info("Opening 'add %s type' dialog.", config_category)
        title = f"Add New {config_category.title()} Type"
        add_method = getattr(
            self.controller.admin_controller, f"add_new_{config_category}_type"
        )

        def on_create_callback(display_name: str, internal_name: str):
            self.logger.info(
                "Dialog confirmed for new %s type: %s (%s)",
                config_category,
                display_name,
                internal_name,
            )
            add_method(display_name, internal_name)

        dialog = AddConfigTypeDialog(
            page=self.controller.page, title=title, on_create=on_create_callback
        )
        dialog.show()

    def open_add_source_type_dialog(self):
        """Opens a dialog to add a new source type."""
        # This is a public-facing convenience method that calls the private helper.
        self._open_add_config_type_dialog("source")

    def open_add_project_type_dialog(self):
        """Opens a dialog to add a new project type."""
        # This is a public-facing convenience method that calls the private helper.
        self._open_add_config_type_dialog("project")

    def open_user_editor_dialog(self, user_data: Optional[Dict[str, Any]] = None):
        """
        Opens a dialog to add a new user or edit an existing one.
        The dialog's behavior (add vs. edit) is determined by whether `user_data` is provided.
        """
        self.logger.info(
            "Opening user editor dialog. User: %s",
            user_data.get("display_name") if user_data else "New",
        )

        def on_save_callback(
            original_name: Optional[str], updated_data: Dict[str, Any]
        ):
            if original_name:  # Editing existing user
                # If an original name exists, it's an update operation.
                self.logger.info(
                    "Dialog confirmed for updating user: %s", original_name
                )
                self.controller.admin_controller.update_user(
                    original_name, updated_data
                )
            else:  # Adding new user
                # Otherwise, it's a create operation.
                self.logger.info(
                    "Dialog confirmed for new user: %s", updated_data["display_name"]
                )
                self.controller.admin_controller.add_user(updated_data)

        dialog = UserEditorDialog(
            page=self.controller.page, on_save=on_save_callback, user_data=user_data
        )
        dialog.show()

    def open_delete_user_confirmation_dialog(self, user_name: str):
        """Opens a confirmation dialog before deleting a user."""
        self.logger.info("Opening delete confirmation for user: %s", user_name)

        def on_confirm_callback():
            self.logger.info("Deletion confirmed for user: %s", user_name)
            self.controller.admin_controller.delete_user(user_name)

        dialog = DeleteConfirmationDialog(
            page=self.controller.page,
            item_name=user_name,
            item_type="user",
            on_confirm=on_confirm_callback,
        )
        dialog.show()

    def open_add_source_to_project_dialog(self, source_id: str, source_type: str):
        """
        Opens the dialog to collect link data before adding a source to a project.
        This is used for "complex" sources that have project-specific fields.

        Args:
            source_id: The ID of the master source being added.
            source_type: The type of the source, used to determine which fields to show.
        """
        self.logger.info(
            "Opening add source to project dialog for source: %s", source_id
        )

        def on_save_callback(link_data: Dict[str, Any]):
            self.logger.info(
                "Dialog confirmed for adding source %s to project.", source_id
            )
            self.controller.source_controller.add_source_to_project(
                source_id, link_data
            )

        dialog = AddSourceToProjectDialog(
            page=self.controller.page,
            source_type=source_type,
            dialog_controller=self,
            on_save=on_save_callback,
        )
        dialog.show()

    def open_add_boilerplate_sources_dialog(self):
        """
        Opens a dialog that allows the user to select one or more boilerplate
        sources to add to the current project.
        """
        self.logger.info("Opening add boilerplate sources dialog.")

        sources = self.controller.source_controller.get_boilerplate_sources()

        def on_add_callback(source_ids: List[str]):
            self.logger.info(
                "Dialog confirmed for adding %s boilerplate sources.", len(source_ids)
            )

            # Separate sources into two groups: those that can be added directly (simple)
            # and those that require more information (complex).
            simple_sources_to_add = []
            complex_sources_to_open_dialog_for = []

            for source_id in source_ids:
                # Determine if a source is "complex" by checking its type configuration for 'link' fields.
                source = self.controller.source_controller.get_source_record_by_id(
                    source_id
                )
                if not source:
                    continue

                source_type_config = (
                    self.controller.admin_controller.get_source_type_config(
                        source.source_type
                    )
                )
                has_link_fields = any(
                    field.get("storage_scope") == "link"
                    for field in source_type_config.get("fields", [])
                )

                if has_link_fields:
                    complex_sources_to_open_dialog_for.append(source)
                else:
                    simple_sources_to_add.append(source_id)

            # Bulk-add all simple sources in a single, efficient operation.
            if simple_sources_to_add:
                self.controller.source_controller.add_simple_boilerplate_sources_to_project(
                    simple_sources_to_add
                )

            # For complex sources, open a separate dialog for each one to collect the required data.
            for source in complex_sources_to_open_dialog_for:
                self.open_add_source_to_project_dialog(source.id, source.source_type)

        dialog = AddBoilerplateSourcesDialog(
            page=self.controller.page, sources=sources, on_add=on_add_callback
        )
        dialog.show()

    def open_import_sources_dialog(self):
        """
        Opens a dialog that allows the user to select another project from which
        to import all sources.
        """
        self.logger.info("Opening import sources dialog.")
        current_project = self.controller.project_controller.get_current_project()
        if not current_project:
            self.controller.show_error_message("No project is currently open.")
            return

        all_projects = self.controller.project_service.get_all_projects_summary()
        # Filter out the currently open project from the list of choices.
        other_projects = [
            (title, path)
            for title, path in all_projects
            if path != str(current_project.file_path)
        ]

        def on_import_callback(source_project_path: str):
            self.logger.info("Dialog confirmed for importing sources to On Deck from: %s", source_project_path)
            self.controller.project_controller.add_sources_to_on_deck_from_project(
                Path(source_project_path)
            )

        dialog = ImportSourcesDialog(
            page=self.controller.page,
            projects=other_projects,
            on_import=on_import_callback,
        )
        dialog.show()

    def open_new_source_dialog(
        self,
        from_project_sources_tab: bool = False,
        target_country_from_view: Optional[str] = None,
        is_boilerplate: bool = False,
    ):
        """
        Opens the primary dialog for creating a new master source record.

        Args:
            from_project_sources_tab: If True, indicates the source should also be
                                      added to the current project.
            target_country_from_view: Pre-selects a country in the dropdown.
            is_boilerplate: If True, configures the dialog for creating a
                            boilerplate source (e.g., hides the country field).
        """
        self.logger.info("Opening new source dialog.")

        # --- Define the callback function ---
        def on_create_callback(form_data: Dict[str, Any]):
            self.logger.info(
                "Source creation dialog confirmed. Passing to SourceController."
            )
            # Delegate the actual creation logic to the SourceController
            self.controller.source_controller.create_new_source(
                source_data=form_data,
                add_to_project=from_project_sources_tab,
                is_boilerplate=is_boilerplate,
            )

        # --- Get data needed by the dialog ---
        # Fetch all available countries for the dropdown.
        available_countries = (
            self.controller.source_controller.get_available_countries()
        )

        # Determine the default country to select.
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

        if is_boilerplate:
            self.logger.info(
                "Filtering source types for boilerplate creation (no link fields)."
            )
            filtered_source_types = {}
            for code, config in source_types.items():
                has_link_fields = any(
                    field.get("storage_scope") == "link"
                    for field in config.get("fields", [])
                )
                if not has_link_fields:
                    filtered_source_types[code] = config
            source_types = filtered_source_types
            if not source_types:
                self.controller.show_error_message(
                    "No source types available for boilerplate. A type must not have any 'Project Link' fields."
                )
                return

        # --- Instantiate and show the dialog ---
        dialog = SourceCreationDialog(
            page=self.controller.page,
            on_create=on_create_callback,
            dialog_controller=self,
            source_types=source_types,
            available_countries=available_countries,
            target_country=target_country,
            from_project_sources_tab=from_project_sources_tab,
            is_boilerplate=is_boilerplate,
        )
        dialog.show()

    def get_source_type_fields(self, source_type_code: str) -> List[Dict[str, Any]]:
        """
        Gets the raw field configuration dictionaries for a given source type.

        Args:
            source_type_code: The internal code for the source type (e.g., "book").
        Returns: A list of field configuration dictionaries.
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

        Args:
            source_id: The unique ID of the source to be edited.
        """
        self.logger.info("Opening source editor for source_id: %s", source_id)

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
            self.logger.info("Editor dialog save confirmed for source_id: %s", s_id)
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
        """
        Opens a read-only dialog to show a source's formatted citation and raw data.

        Args:
            source_id: The ID of the source to display."""
        self.logger.info("Opening source citation dialog for source: %s", source_id)
        source = self.controller.source_controller.get_source_record_by_id(source_id)
        if not source:
            self.controller.show_error_message(
                f"Could not find source with ID {source_id} to show details.", 
            )
            return

        dialog = SourceCitationDialog(
            page=self.controller.page, source=source, controller=self.controller
        )
        dialog.show()

    def show_first_time_setup(self):
        """
        Shows the first-time setup dialog to get the user's display name.
        This is triggered if the settings manager detects that setup is needed.
        """
        self.logger.info("Showing first-time setup dialog.")

        def on_setup_complete(display_name: str):
            """Callback executed when the setup dialog is completed."""
            self.logger.info(
                "First time setup completed. Display name: '%s'", display_name
            )
            # Delegate user creation and setup completion to the AdminController
            self.controller.admin_controller.create_initial_user(display_name)

            # Update UI and navigate to the home screen
            self.controller.main_view.update_greeting()
            self.controller.navigate_to("home")

        dialog = FirstTimeSetupDialog(
            page=self.controller.page, on_complete=on_setup_complete
        )
        dialog.show()
