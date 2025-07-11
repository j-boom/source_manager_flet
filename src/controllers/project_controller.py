"""
Project Controller - Handles project-related operations.

This controller manages project creation, loading, and project-specific dialogs.
"""

from typing import Dict, Any
from pathlib import Path
import flet as ft

from .base_controller import BaseController
from views.components.dialogs import ProjectCreationDialog


class ProjectController(BaseController):
    """Handles all project-related operations."""
    
    def show_create_project_dialog(self, parent_path: Path):
        """Creates and shows the project creation dialog, pre-filling the BE number if found."""
        be_number = ""
        try:
            be_number = self.data_service.derive_project_number_from_path(parent_path)
        except Exception as e:
            self.logger.warning(f"Could not derive BE number from path {parent_path}: {e}")

        def on_dialog_close():
            current_view = self.app.views.get("new_project")
            if current_view and hasattr(current_view, "_update_view"):
                current_view._update_view()

        dialog = ProjectCreationDialog(
            self.page,
            self.app,
            parent_path,
            on_close=on_dialog_close,
            initial_be_number=be_number,
        )
        dialog.show()

    def submit_new_project(self, parent_path: Path, form_data: Dict[str, Any]):
        """Receives data from the dialog and uses the DataService to create the project."""
        self.logger.info(f"Submitting new project for path: {parent_path}")
        try:
            success, message, project = self.data_service.create_new_project(
                parent_path, form_data
            )
            if success and project:
                self.logger.info(f"Successfully created project: {project.file_path}")
                self.app.open_project(project.file_path)
            else:
                self.logger.error(f"Project creation failed: {message}")
        except Exception as e:
            self.logger.error(
                f"An exception occurred during project creation: {e}", exc_info=True
            )

    def handle_old_format_file(self, project_path: Path):
        """Handle opening an old format project file by offering migration."""
        def on_migrate_confirmed():
            """User confirmed migration - proceed with migration"""
            # Show progress dialog
            progress_dialog = self.app._show_migration_progress_dialog()
            
            try:
                # Attempt migration using DataService
                success, new_project_path = self.data_service.migrate_old_project(project_path)
                
                # Close progress dialog
                progress_dialog.open = False
                self.page.update()
                
                if success:
                    self.app._show_success_dialog(
                        "Migration Successful", 
                        f"Project has been migrated to the new format.\nNew location: {new_project_path}"
                    )
                    # Try to open the migrated project
                    self.app.open_project(new_project_path)
                else:
                    self.app._show_error_dialog("Migration Failed", "Could not migrate the project file.")
                    
            except Exception as e:
                # Close progress dialog
                progress_dialog.open = False
                self.page.update()
                
                self.logger.error(f"Migration failed: {e}", exc_info=True)
                self.app._show_error_dialog("Migration Error", f"An error occurred during migration: {str(e)}")
        
        def on_migrate_cancelled():
            """User cancelled migration"""
            self.logger.info("User cancelled project migration")
        
        # Show migration confirmation dialog
        def close_dialog(e):
            dialog.open = False
            self.page.update()
        
        def migrate_clicked(e):
            dialog.open = False
            self.page.update()
            on_migrate_confirmed()
        
        def cancel_clicked(e):
            dialog.open = False
            self.page.update()
            on_migrate_cancelled()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Old Project Format Detected"),
            content=ft.Column([
                ft.Text("This project was created with an older version of Source Manager."),
                ft.Text("Would you like to migrate it to the new format?"),
                ft.Text("The original file will be backed up.", style=ft.TextThemeStyle.BODY_SMALL),
            ], spacing=10),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_clicked),
                ft.TextButton("Migrate", on_click=migrate_clicked)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
