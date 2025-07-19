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
        self.file_picker = ft.FilePicker(on_result=self._on_powerpoint_file_picked)
        self.controller.page.overlay.append(self.file_picker)

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

    def get_synced_slide_data(self) -> Optional[List[Dict]]:
        """
        Ensures the project's slide data is synced with the linked .pptx file.

        This is the primary method for loading slide data. It reads the file,
        merges it with existing citation data, and saves the result back to the
        project's metadata.

        Returns:
            The list of synced slide dictionaries, or None if an error occurs.
        """
        project = self._get_project_or_handle_error("Get Synced Slide Data")
        if not project:
            return None

        filepath = project.metadata.get("powerpoint_file")
        if not filepath:
            self.logger.info("No PowerPoint file is associated with this project.")
            # Ensure old slide data is cleared if file is unlinked
            if "slide_data" in project.metadata:
                del project.metadata["slide_data"]
                self.controller.project_service.save_project(project)
            return None

        fresh_slides = self.powerpoint_manager.get_slides_from_file(filepath)
        if fresh_slides is None:
            self.controller.show_error_message(
                f"Could not read the PowerPoint file at:\n{filepath}"
            )
            return None

        # Merge with existing citation data
        saved_slide_data = project.metadata.get("slide_data", [])
        saved_map = {
            item["slide_id"]: item.get("sources", []) for item in saved_slide_data
        }
        for slide in fresh_slides:
            if slide["slide_id"] in saved_map:
                slide["sources"] = saved_map[slide["slide_id"]]

        # Save the synced data back to the 'slide_data' key within metadata.
        project.metadata["slide_data"] = fresh_slides
        self.controller.project_service.save_project(project)
        self.logger.info(f"Successfully synced {len(fresh_slides)} slides for project.")
        return fresh_slides

    def link_source_to_slide(self, slide_id: str, source_ids: List[str]):
        """Adds a list of source UUIDs to a specific slide's source list."""
        project = self._get_project_or_handle_error("Link Source")
        if not project:
            return

        slide_data = project.metadata.get("slide_data", [])
        slide_entry = next(
            (s for s in slide_data if str(s.get("slide_id")) == str(slide_id)), None
        )

        if not slide_entry:
            title = "Untitled Slide"
            slide_entry = {"slide_id": slide_id, "title": title, "sources": []}
            slide_data.append(slide_entry)

        for source_id in source_ids:
            if source_id not in slide_entry["sources"]:
                slide_entry["sources"].append(source_id)

        project.metadata["slide_data"] = slide_data
        self.controller.project_service.save_project(project)
        self.controller.show_success_message("Sources linked successfully!")
        self.controller.update_view()

    def unlink_source_from_slide(self, slide_id: str, source_ids: List[str]):
        """Removes a list of source UUIDs from a specific slide's source list."""
        project = self._get_project_or_handle_error("Unlink Source")
        if not project:
            return

        slide_data = project.metadata.get("slide_data", [])
        slide_entry = next(
            (s for s in slide_data if str(s.get("slide_id")) == str(slide_id)), None
        )

        if slide_entry:
            slide_entry["sources"] = [
                s_id
                for s_id in slide_entry.get("sources", [])
                if s_id not in source_ids
            ]

        project.metadata["slide_data"] = slide_data
        self.controller.project_service.save_project(project)
        self.controller.show_success_message("Sources unlinked successfully!")
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

    def pick_powerpoint_file(self):
        """
        Callback method that is executed after the user selects a file from the picker (or cancels).
        """
        self.logger.info("Requesting PowerPoint file selection...")
        self.file_picker.pick_files(
            allow_multiple=False,
            dialog_title="Select PowerPoint File",
            allowed_extensions=["pptx"],
            initial_directory=self.controller.settings_manager.get_default_save_directory(),
        )

    def _on_powerpoint_file_picked(self, e: ft.FilePickerResultEvent):
        """Callback method that executes after the user selects a file."""
        if not e.files:
            self.logger.info("File picking cancelled by user.")
            return

        selected_file_path = e.files[0].path
        self.logger.info(f"PowerPoint file selected: {selected_file_path}")

        project = self.controller.project_controller.get_current_project()
        if not project:
            return

        project.metadata["powerpoint_file"] = selected_file_path
        self.controller.project_service.save_project(project)

        slides = self.get_synced_slide_data()

        if slides is not None:
            self.controller.show_success_message(
                f"Successfully linked and imported {len(slides)} slides!"
            )

        self.controller.update_view()
