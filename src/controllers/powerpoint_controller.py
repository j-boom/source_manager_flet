import logging

import flet as ft

from src.controllers.base_controller import BaseController
from src.models.project_models import Project
from typing import Optional, List, Dict


class PowerPointController(BaseController):
    """
    Orchestrates the linking of sources to PowerPoint slides.
    """

    def __init__(self, controller):
        super().__init__(controller)
        self.powerpoint_manager = self.controller.powerpoint_manager
        self.logger = logging.getLogger(self.__class__.__name__)
        self.file_picker = ft.FilePicker(
            on_result=self._on_powerpoint_file_picked
        )

    def _get_project_or_handle_error(self, operation_name: str) -> Optional[Project]:
        """
        A helper method to get the current project or handle the error if none exists.
        This centralizes the repeated check and improves code clarity.
        """
        project = self.controller.project_controller.get_current_project()
        if not project:
            self.logger.error(f"{operation_name} called with no active project.")
            self.controller.show_error_message(
                "No active project found to perform this operation."
            )
            return None
        return project

    def get_synced_slide_data(self) -> list[dict]:
        """
        Gets the slide list from the .pptx file and syncs it with the saved
        source mappings in the project's 'slide_data'.
        """
        project = self._get_project_or_handle_error("Get Synced Slide Data")
        if not project:
            return []

        filepath = project.metadata.get("powerpoint_file", None)
        if not filepath:
            self.logger.warning(
                "Attempted to get slide data for a project with no linked PowerPoint file."
            )
            return []

        fresh_slides = self.powerpoint_manager.get_slides_from_file(filepath)
        if fresh_slides is None:
            self.controller.show_error_message(
                f"Could not read the PowerPoint file at:\n{filepath}"
            )
            return []

        saved_slide_data = getattr(project, "slide_data", [])
        saved_map = {
            item["slide_id"]: item.get("sources", []) for item in saved_slide_data
        }

        for slide in fresh_slides:
            if slide["slide_id"] in saved_map:
                slide["sources"] = saved_map[slide["slide_id"]]

        return fresh_slides

    def link_source_to_slide(self, slide_id: int, source_id: str):
        """
        Adds a source's UUID to a specific slide's source list and saves the project.
        """
        project = self._get_project_or_handle_error("Link Source")
        if not project:
            return

        self.logger.info(f"Linking source {source_id} to slide {slide_id}")

        slide_data = getattr(project, "slide_data", [])

        slide_found = False
        for slide in slide_data:
            if slide["slide_id"] == slide_id:
                if source_id not in slide.get("sources", []):
                    slide.setdefault("sources", []).append(source_id)
                slide_found = True
                break

        if not slide_found:
            powerpoint_file = project.metadata.get("powerpoint_file", None)
            fresh_slides = self.powerpoint_manager.get_slides_from_file(powerpoint_file)
            title = "Untitled Slide"
            if fresh_slides:
                for s in fresh_slides:
                    if s["slide_id"] == slide_id:
                        title = s["title"]
                        break
            slide_data.append(
                {"slide_id": slide_id, "title": title, "sources": [source_id]}
            )

        project.metadata["slide_data"] = slide_data

        self.controller.project_service.save_project(project)
        self.controller.show_success_message("Source linked successfully!")

        self.controller.update_view()

    def unlink_source_from_slide(self, slide_id: int, source_id: str):
        """
        Removes a source's UUID from a specific slide's source list and saves the project.
        """
        project = self._get_project_or_handle_error("Unlink Source")
        if not project:
            return

        self.logger.info(f"Unlinking source {source_id} from slide {slide_id}")

        slide_data = project.metadata.get("slide_data", [])

        for slide in slide_data:
            if slide["slide_id"] == slide_id:
                if "sources" in slide and source_id in slide["sources"]:
                    slide["sources"].remove(source_id)
                break

        project.metadata["slide_data"] = slide_data

        self.controller.project_service.save_project(project)
        self.controller.show_success_message("Source unlinked successfully!")
        self.controller.update_view()

    # --- Source Group Management Methods (Project-Specific) ---

    def get_source_groups(self) -> Dict[str, List[str]]:
        """Retrieves the source groups from the current project."""
        project = self._get_project_or_handle_error("Get Source Groups")
        if not project:
            return {}
        # Safely get the source_groups attribute, returning an empty dict if not present.
        return getattr(project, "source_groups", {})

    def save_source_group(self, group_name: str, source_ids: List[str]):
        """Saves a new source group or updates an existing one on the current project."""
        project = self._get_project_or_handle_error("Save Source Group")
        if not project:
            return

        if not group_name.strip():
            self.controller.show_error_message("Group name cannot be empty.")
            return

        self.logger.info(
            f"Saving source group '{group_name}' to project '{project.project_title}'"
        )
        # Get the current groups, update them, and set them back on the project object.
        all_groups = self.get_source_groups()
        all_groups[group_name] = source_ids
        project.metadata["source_groups"] = all_groups

        # Save the entire updated project.
        self.controller.project_service.save_project(project)
        self.controller.show_success_message(f"Source group '{group_name}' saved.")
        self.controller.update_view()

    def delete_source_group(self, group_name: str):
        """Deletes a source group from the current project."""
        project = self._get_project_or_handle_error("Delete Source Group")
        if not project:
            return

        self.logger.info(
            f"Deleting source group '{group_name}' from project '{project.project_title}'"
        )
        all_groups = self.get_source_groups()
        if group_name in all_groups:
            del all_groups[group_name]
            project.metadata["source_groups"] = all_groups

            # Save the entire updated project.
            self.controller.project_service.save_project(project)
            self.controller.show_success_message(
                f"Source group '{group_name}' deleted."
            )
            self.controller.update_view()
        else:
            self.controller.show_error_message(
                f"Source group '{group_name}' not found."
            )

    # --- New Methods for File Picking ---

    def handle_link_powerpoint_request(self, e):
        """
        Callback method that is executed after the user selects a file from the picker (or cancels).
        """
        if e.files:
            # If files were selected, get the path of the first file.
            filepath = e.files[0].path
            self.logger.info(f"PowerPoint file selected: {filepath}")

            # Get the currently active project from the state manager.
            project = self.controller.project_controller.get_current_project()

            if project:
                # Update the project model with the path to the PowerPoint file.
                project.metadata['powerpoint_file'] = filepath

                # Use the project state manager to update the project data.
                # This will save the changes and notify all subscribers (like the view)
                # that the project has been updated, triggering a UI refresh.
                self.controller.project_service.save_project(project)
                self.logger.info(
                    f"Associated '{filepath}' with project '{project.project_title}'"
                )
        else:
            self.logger.info("File picker was cancelled. No file selected.")

        # There's no need to call self.page.update() here directly.
        # The ProjectStateManager's event system is responsible for notifying the
        # view to update itself, which is a better separation of concerns.

    def _on_powerpoint_file_picked(self, e: ft.FilePickerResultEvent):
        """
        Callback method that executes after the user selects a file (or cancels).
        """
        if e.files:
            # A file was selected
            selected_file_path = e.files[0].path
            self.logger.info(f"PowerPoint file selected: {selected_file_path}")

            project = self.controller.project_controller.get_current_project()
            if project:
                # Update the project object in memory
                project.metadata["powerpoint_file"] = selected_file_path
                # Save the change to the JSON file
                project.save()
                self.controller.show_success_message(
                    "PowerPoint file linked successfully!"
                )
                # Refresh the CiteSourcesTab to show the editor view
                self.controller.update_view()
        else:
            # The user cancelled the dialog
            self.logger.info("File picking cancelled by user.")
