"""Simple Project Creation Dialog for folder creation only"""

import flet as ft
import os
from typing import Callable, Optional
import sys
from pathlib import Path

# Add src to path so we can import services and models directly
src_dir = Path(__file__).parent.parent.parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from services import ProjectManagementService
from config.project_types_config import get_project_type_display_names
import uuid


class SimpleProjectCreationDialog:
    """Simple dialog for basic project creation with folder support"""
    
    def __init__(self, page: ft.Page, project_service: ProjectManagementService,
                 on_success: Optional[Callable] = None, on_cancel: Optional[Callable] = None):
        self.page = page
        self.project_service = project_service
        self.on_success = on_success
        self.on_cancel = on_cancel
        
        # Dialog state
        self.dialog = None
        self.ten_digit_number = ""
        self.folder_path = ""
        
        # Form fields
        self.project_title_field: Optional[ft.TextField] = None
        self.project_type_dropdown: Optional[ft.Dropdown] = None
        self.description_field: Optional[ft.TextField] = None
        self.error_text: Optional[ft.Text] = None
    
    def show(self, ten_digit_number: str, folder_path: str):
        """Show the project creation dialog"""
        self.ten_digit_number = ten_digit_number
        self.folder_path = folder_path
        
        self._create_form_fields()
        self._create_dialog()
        
        self.page.dialog = self.dialog
        if self.dialog:
            self.dialog.open = True
        self.page.update()
    
    def _create_form_fields(self):
        """Create form fields"""
        # Project Title
        self.project_title_field = ft.TextField(
            label="Project Title *",
            hint_text="Enter project title",
            width=300
        )
        
        # Project Type
        project_type_options = get_project_type_display_names()
        self.project_type_dropdown = ft.Dropdown(
            label="Project Type *",
            width=300,
            options=[ft.dropdown.Option(display_name) for display_name in project_type_options.values()],
        )
        
        # Description
        self.description_field = ft.TextField(
            label="Description",
            hint_text="Optional project description",
            width=300,
            multiline=True,
            max_lines=3
        )
        
        # Error text
        self.error_text = ft.Text("", color=ft.colors.RED_400, size=12, visible=False)
    
    def _create_dialog(self):
        """Create the main dialog"""
        # Ensure fields are created
        if not all([self.project_title_field, self.project_type_dropdown, self.description_field, self.error_text]):
            return
            
        self.dialog = ft.AlertDialog(
            title=ft.Text(f"Create Project - {self.ten_digit_number}"),
            content=ft.Column([
                ft.Text(f"Creating project in facility: {self.ten_digit_number}"),
                ft.Container(height=10),
                self.project_title_field,
                ft.Container(height=10),
                self.project_type_dropdown,
                ft.Container(height=10),
                self.description_field,
                ft.Container(height=10),
                self.error_text
            ], tight=True, width=400),
            actions=[
                ft.TextButton("Cancel", on_click=self._on_cancel_clicked),
                ft.ElevatedButton("Create Project", on_click=self._on_create_clicked)
            ]
        )
    
    def _on_create_clicked(self, e):
        """Handle create project button click"""
        # Validate required fields
        title = self.project_title_field.value.strip() if self.project_title_field and self.project_title_field.value else ""
        project_type = self.project_type_dropdown.value if self.project_type_dropdown and self.project_type_dropdown.value else ""
        description = self.description_field.value.strip() if self.description_field and self.description_field.value else ""
        
        if not title:
            self._show_error("Project title is required")
            return
        
        if not project_type:
            self._show_error("Project type is required")
            return
        
        # Create basic project data
        project_data = {
            "title": title,
            "project_type": project_type,
            "description": description,
            "facility_number": self.ten_digit_number,
            "folder_path": self.folder_path
        }
        
        try:
            # Create project using service
            success, message, project_uuid = self.project_service.create_project(project_data)
            
            if success:
                self._close_dialog()
                if self.on_success:
                    self.on_success(f"Project created successfully: {title}")
            else:
                self._show_error(f"Failed to create project: {message}")
                
        except Exception as e:
            self._show_error(f"Error creating project: {str(e)}")
    
    def _show_error(self, message: str):
        """Show error message"""
        if self.error_text:
            self.error_text.value = message
            self.error_text.visible = True
            self.page.update()
    
    def _on_cancel_clicked(self, e):
        """Handle cancel button click"""
        self._close_dialog()
        if self.on_cancel:
            self.on_cancel()
    
    def _close_dialog(self):
        """Close the dialog"""
        if self.dialog:
            self.dialog.open = False
            self.page.update()
