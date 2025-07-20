import logging
from typing import Optional, List, Dict

import flet as ft

from src.controllers.base_controller import BaseController
from src.models.project_models import Project


class PowerPointController(BaseController):
    """
    Orchestrates the linking of sources to PowerPoint slides.
    This controller follows the pattern of preparing update payloads and
    delegating the final state update and save to the ProjectController.
    """

    def __init__(self, controller):
        super().__init__(controller)
        self.powerpoint_manager = self.controller.powerpoint_manager
        self.logger = logging.getLogger(self.__class__.__name__)
        self.file_picker = ft.FilePicker(on_result=self._on_powerpoint_file_picked)
        # Ensure the file picker is added to the page overlay to be visible
        if self.controller.page:
            self.controller.page.overlay.append(self.file_picker)

    def _get_project_or_handle_error(self, operation_name: str) -> Optional[Project]:
        """A helper method to get the current project or handle the error if none exists."""
        project = self.controller.project_controller.get_current_project()
        if not project:
            self.logger.error(f"{operation_name} called with no active project.")
            self.controller.show_error_message("No active project found to perform this operation.")
            return None
        return project

    def sync_powerpoint_file(self):
        """
        Performs a one-time sync from the linked .pptx file to the project.
        This should only be called on explicit user action (e.g., picking a file, clicking a 'Sync' button).
        """
        project = self._get_project_or_handle_error("Sync PowerPoint File")
        if not project:
            return

        filepath = project.metadata.get("powerpoint_file")
        if not filepath:
            self.logger.info("No PowerPoint file is associated. Clearing slide data if it exists.")
            if "slide_data" in project.metadata and project.metadata["slide_data"]:
                update_payload = {"slide_data": []}
                self.controller.project_controller.update_project_metadata(update_payload)
            return

        fresh_slides = self.powerpoint_manager.get_slides_from_file(filepath)
        if fresh_slides is None:
            self.controller.show_error_message(f"Could not read the PowerPoint file at:\n{filepath}")
            return

        saved_slide_data = project.metadata.get("slide_data", [])
        saved_map = {item["slide_id"]: item.get("sources", []) for item in saved_slide_data}
        for slide in fresh_slides:
            if slide["slide_id"] in saved_map:
                slide["sources"] = saved_map[slide["slide_id"]]

        # Prepare the payload and delegate the update to the central controller
        update_payload = {"slide_data": fresh_slides}
        self.controller.project_controller.update_project_metadata(update_payload)

        self.logger.info(f"Successfully synced {len(fresh_slides)} slides for project.")
        # The view that initiates the sync is responsible for its own UI update.
        self.controller.show_success_message(f"Successfully synced {len(fresh_slides)} slides!")

    def get_slide_data_from_project(self) -> List[Dict]:
        """
        Safely retrieves the current slide data from the in-memory project state.
        This is a read-only operation and is safe to call during UI builds.
        """
        project = self._get_project_or_handle_error("Get Slide Data")
        if not project:
            return []
        return project.metadata.get("slide_data", [])

    def link_source_to_slide(self, slide_id: str, source_ids: List[str]):
        """Links sources to a slide by preparing an update payload and delegating."""
        project = self._get_project_or_handle_error("Link Source")
        if not project:
            return

        slide_data = project.metadata.get("slide_data", []).copy()
        slide_entry = next((s for s in slide_data if str(s.get("slide_id")) == str(slide_id)), None)

        if not slide_entry:
            slide_entry = {"slide_id": slide_id, "title": "Untitled Slide", "sources": []}
            slide_data.append(slide_entry)

        for source_id in source_ids:
            if source_id not in slide_entry["sources"]:
                slide_entry["sources"].append(source_id)

        update_payload = {"slide_data": slide_data}
        self.controller.project_controller.update_project_metadata(update_payload)
        self.controller.update_view()

    def unlink_source_from_slide(self, slide_id: str, source_ids: List[str]):
        """Unlinks sources from a slide by preparing an update payload and delegating."""
        project = self._get_project_or_handle_error("Unlink Source")
        if not project:
            return

        slide_data = project.metadata.get("slide_data", []).copy()
        slide_entry = next((s for s in slide_data if str(s.get("slide_id")) == str(slide_id)), None)

        if slide_entry:
            slide_entry["sources"] = [s_id for s_id in slide_entry.get("sources", []) if s_id not in source_ids]

            update_payload = {"slide_data": slide_data}
            self.controller.project_controller.update_project_metadata(update_payload)
            self.controller.update_view()

    def save_source_group(self, group_name: str, source_ids: List[str]):
        """Saves a source group by preparing an update payload and delegating."""
        project = self._get_project_or_handle_error("Save Source Group")
        if not project:
            return
        if not group_name.strip():
            self.controller.show_error_message("Group name cannot be empty.")
            return

        all_groups = project.metadata.get("source_groups", {}).copy()
        all_groups[group_name] = source_ids

        update_payload = {"source_groups": all_groups}
        self.controller.project_controller.update_project_metadata(update_payload)

        self.controller.show_success_message(f"Source group '{group_name}' saved.")
        self.controller.update_view()

    def delete_source_group(self, group_name: str):
        """Deletes a source group by preparing an update payload and delegating."""
        project = self._get_project_or_handle_error("Delete Source Group")
        if not project:
            return

        all_groups = project.metadata.get("source_groups", {}).copy()
        if group_name in all_groups:
            del all_groups[group_name]

            update_payload = {"source_groups": all_groups}
            self.controller.project_controller.update_project_metadata(update_payload)

            self.controller.show_success_message(f"Source group '{group_name}' deleted.")
            self.controller.update_view()
        else:
            self.controller.show_error_message(f"Source group '{group_name}' not found.")

    def pick_powerpoint_file(self):
        """Opens the file picker to select a PowerPoint file."""
        self.logger.info("Requesting PowerPoint file selection...")
        self.file_picker.pick_files(
            allow_multiple=False,
            dialog_title="Select PowerPoint File",
            allowed_extensions=["pptx"],
            initial_directory=self.controller.settings_manager.get_default_save_directory(),
        )

    def _on_powerpoint_file_picked(self, e: ft.FilePickerResultEvent):
        """Callback that handles the result of the file picker."""
        if not e.files:
            self.logger.info("File picking cancelled by user.")
            return

        selected_file_path = e.files[0].path
        self.logger.info(f"PowerPoint file selected: {selected_file_path}")

        # First, save the new file path. This is a discrete update.
        update_payload = {"powerpoint_file": selected_file_path}
        self.controller.project_controller.update_project_metadata(update_payload)

        # Now, trigger the one-time sync process.
        self.sync_powerpoint_file()
        
        # After the sync, the main view needs to be updated to show the new slides.
        self.controller.update_view()
