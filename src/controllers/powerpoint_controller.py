"""
PowerPoint Controller - Handles PowerPoint integration operations.

This controller manages PowerPoint file processing and slide extraction.
"""

from pathlib import Path
import flet as ft
from .base_controller import BaseController


class PowerPointController(BaseController):
    """Handles all PowerPoint integration operations."""
    def __init__(self, controller):
        super().__init__(controller)
        
    
    def associate_powerpoint_file(self, force_reselect: bool = False):
        """
        Associates a PowerPoint file with the current project.
        If force_reselect is True, it will prompt the user to select a new file.
        Otherwise, it will use the existing PowerPoint file if available.
        """
        project = self.controller.project_controller.get_current_project()
        if not project:
            self.controller.show_error_message("No project loaded. Please open a project first.")
            return
        
        # Check if there's already a PowerPoint file associated with the project
        existing_ppt_path = project.metadata.get("powerpoint_file_path")
        if existing_ppt_path:
            self.controller.powerpoint_manager.set_powerpoint_file(existing_ppt_path)
            return
        
        # Show file picker to select a PowerPoint file
        def on_file_selected(e: ft.FilePickerResultEvent):
            if e.files and len(e.files) > 0:
                file_path = e.files[0].path
                self.logger.info(f"PowerPoint file selected: {file_path}")
                self.controller.powerpoint_manager.set_powerpoint_file(file_path)
                self.controller.project_service.associate_powerpoint_file(project, file_path)
                self.controller.show_success_message(f"PowerPoint file associated: {file_path}")
                self.logger.info(f"Successfully associated PowerPoint file: {file_path}")
            else:
                self.logger.info("No PowerPoint file selected")
        
        file_picker = ft.FilePicker(on_result=on_file_selected)
        self.controller.page.overlay.append(file_picker)
        self.controller.page.update()

        # Open file picker for PowerPoint files
        file_picker.pick_files(
            dialog_title="Select PowerPoint File",
            allowed_extensions=["pptx", "ppt"],
            allow_multiple=False
        )


    def get_slides_for_current_project(self, force_reselect: bool = False):
        """
        Shows a file picker to select a PowerPoint file and extracts slide data.
        If force_reselect is True and there's an existing PowerPoint path, reloads that file.
        Stores the slide data in the current project's metadata.
        """
        project = self.project_state_manager.current_project
        if not project:
            self.app._show_error("No project loaded. Please open a project first.")
            return None
        
        # Check if we already have a PowerPoint file path and should reuse it
        existing_ppt_path = project.metadata.get("powerpoint_file_path")
        if force_reselect and existing_ppt_path and Path(existing_ppt_path).exists():
            self.logger.info(f"Force reselecting existing PowerPoint file: {existing_ppt_path}")
            return self.process_powerpoint_file(existing_ppt_path)
        
        # Show file picker
        
    
    def process_powerpoint_file(self, file_path: str):
        """
        Processes the selected PowerPoint file using the PowerPointService
        and stores the slide data in the project metadata.
        """
        try:
            project = self.project_state_manager.current_project
            if not project:
                self.app._show_error("No project loaded")
                return None
            
            self.logger.info(f"Processing PowerPoint file: {file_path}")
            
            # Use PowerPointService to extract slide data
            slides_data = self.app.powerpoint_service.extract_slides(file_path)
            
            if slides_data:
                # Store the slide data and file path in project metadata
                project.metadata["powerpoint_slides"] = slides_data
                project.metadata["powerpoint_file_path"] = file_path
                
                # Save the project
                self.controller.project_service.save_project(project)
                
                self.logger.info(f"Successfully processed PowerPoint file with {len(slides_data)} slides")
                
                # Show success message
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        ft.Text(f"Successfully loaded {len(slides_data)} slides from PowerPoint"),
                        bgcolor=ft.colors.GREEN
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                
                return slides_data
            else:
                self.app._show_error("Failed to extract slides from PowerPoint file")
                return None
                
        except Exception as e:
            error_msg = f"Error processing PowerPoint file: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.app._show_error(error_msg)
            return None
