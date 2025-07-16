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
    Controller for handling the opening of all dialogs.
    """

    def open_dialog(self, dialog):
        """
        Helper method to open a dialog by adding it to the page overlay.
        """
        self.controller.page.overlay.append(dialog)
        dialog.open = True
        self.controller.page.update()

    def open_new_project_dialog(self, e, parent_path: Path):
        """Opens the new project creation dialog."""

        def on_dialog_closed(form_data: Optional[Dict[str, Any]]):
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
        """Opens the dialog to add an existing source to the current project."""
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
        """
        dialog = SourceEditorDialog(
            controller=self.controller, source=source, on_close=on_close
        )
        self.open_dialog(dialog)

    def new_project_dialog_closed(self, e):
        """
        Callback for when the new project dialog is closed.
        """
        self.controller.page.overlay.remove(e.control)
        self.controller.page.update()

    def show_first_time_setup(self):
        """Shows the initial setup dialog for new users."""

        def on_setup_complete(display_name: str):
            self.controller.settings_manager.save_display_name(display_name)
            self.controller.user_config_manager.mark_setup_completed()
            self.controller.navigate_to("home")

        dialog = FirstTimeSetupDialog(self.controller.page, on_setup_complete)
        dialog.show()