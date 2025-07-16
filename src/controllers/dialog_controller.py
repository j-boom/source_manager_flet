from pathlib import Path
from typing import Callable, Optional, Dict, Any, TYPE_CHECKING

import flet as ft

from .base_controller import BaseController
from src.views.components.dialogs import (
    ProjectCreationDialog,
    AddSourceToProjectDialog,
    SourceCreationDialog,
    SourceEditorDialog,
    FirstTimeSetupDialog,
)

if TYPE_CHECKING:
    from src.models.source_models import SourceRecord



class DialogController(BaseController):
    """
    Controller for handling the opening and management of all dialogs in the application.

    This class centralizes dialog logic, ensuring consistent dialog behavior and
    separation of concerns from the main controller and views.
    """


    def open_dialog(self, dialog):
        """
        Opens a dialog by adding it to the page overlay and displaying it.

        Args:
            dialog: The dialog instance to open (should be a Flet control).
        """
        self.controller.page.overlay.append(dialog)
        dialog.open = True
        self.controller.page.update()


    def open_new_project_dialog(self, e, parent_path: Path):
        """
        Opens the new project creation dialog.

        Args:
            e: The triggering event (not used).
            parent_path (Path): The directory in which to create the new project.
        """
        def on_dialog_closed(form_data: Optional[Dict[str, Any]]):
            """
            Callback for when the project creation dialog is closed.
            If form_data is provided, creates a new project via the ProjectController.
            """
            if form_data:
                # If we have data, we pass it to the ProjectController to handle the business logic.
                self.logger.info(
                    "Project dialog closed with data. Passing to ProjectController."
                )
                self.controller.data_service.create_new_project(
                    parent_dir=parent_path, form_data=form_data
                )
            else:
                # If form_data is None, the user cancelled.
                self.logger.info("Project creation was cancelled.")

        dialog = ProjectCreationDialog(
            page=self.controller.page,
            controller=self.controller,
            parent_path=parent_path,
            on_close=on_dialog_closed,
        )
        self.open_dialog(dialog)


    def open_add_source_to_project_dialog(self, e):
        """
        Opens the dialog to add an existing source to the current project.

        Args:
            e: The triggering event (not used).
        """
        dialog = AddSourceToProjectDialog(
            page=self.controller.page, controller=self.controller
        )
        self.open_dialog(dialog)


    def open_new_source_dialog(
        self,
        e,
        add_to_project: bool = False,
        initial_data: Optional[Dict[str, Any]] = None,
    ):
        """
        Opens the new source creation dialog, optionally pre-filling some data.

        Args:
            e: The triggering event (not used).
            add_to_project (bool): If True, the new source will be added to a project.
            initial_data (Optional[Dict[str, Any]]): Data to pre-fill the dialog fields.
        """
        dialog = SourceCreationDialog(
            controller=self.controller,
            add_to_project=add_to_project,
            initial_data=initial_data,
        )
        self.open_dialog(dialog)


    def open_source_editor_dialog(
        self, source: "SourceRecord", on_close: Optional[Callable] = None
    ):
        """
        Opens the source editor dialog for a given source.

        Args:
            source (SourceRecord): The source to edit.
            on_close (Optional[Callable]): Callback to invoke when the dialog closes.
        """
        dialog = SourceEditorDialog(
            controller=self.controller, source=source, on_close=on_close
        )
        self.open_dialog(dialog)


    def new_project_dialog_closed(self, e):
        """
        Callback for when the new project dialog is closed (removes it from overlay).

        Args:
            e: The event/control to remove from the overlay.
        """
        self.controller.page.overlay.remove(e.control)
        self.controller.page.update()


    def show_first_time_setup(self):
        """
        Shows the initial setup dialog for new users.
        When setup is complete, saves the display name, marks setup as complete,
        updates the greeting, and navigates to the home page.
        """
        def on_setup_complete(display_name: str):
            """
            Callback for when the first time setup is completed.
            Saves the display name, marks setup as complete, updates greeting, and navigates home.
            """
            self.controller.settings_manager.save_display_name(display_name)
            self.controller.user_config_manager.mark_setup_completed()
            self.controller.main_view.update_greeting()
            self.controller.navigate_to("home")

        dialog = FirstTimeSetupDialog(self.controller.page, on_setup_complete)
        dialog.show()