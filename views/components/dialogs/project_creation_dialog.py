"""Project creation dialog component"""

import flet as ft
from typing import Callable, Optional
from services import ProjectCreationService


class ProjectCreationDialog:
    """Dialog component for creating new projects"""
    
    def __init__(self, page: ft.Page, project_service: ProjectCreationService, 
                 on_success: Optional[Callable] = None, on_cancel: Optional[Callable] = None):
        self.page = page
        self.project_service = project_service
        self.on_success = on_success
        self.on_cancel = on_cancel
        self.dialog = None
        
        # Form fields
        self.project_type_dropdown = None
        self.suffix_field = None
        self.year_dropdown = None
        self.document_title_field = None
        self.error_text = None
        self.preview_text = None
        
        # Data
        self.ten_digit_number = ""
        self.folder_path = ""
    
    def show(self, ten_digit_number: str, folder_path: str):
        """Show the project creation dialog"""
        self.ten_digit_number = ten_digit_number
        self.folder_path = folder_path
        
        self._create_form_fields()
        self._create_dialog()
        
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()
        
        # Initial preview update
        self._update_preview()
    
    def _create_form_fields(self):
        """Create all form fields"""
        # Project type dropdown
        self.project_type_dropdown = ft.Dropdown(
            label="Project Type *",
            options=[ft.dropdown.Option(ptype) for ptype in self.project_service.PROJECT_TYPES],
            width=400,
            on_change=self._on_project_type_change
        )
        
        # Suffix field
        self.suffix_field = ft.TextField(
            label="Suffix *",
            hint_text="ABC123 format",
            width=400,
            max_length=6,
            on_change=self._on_suffix_change
        )
        
        # Year dropdown
        year_options = self.project_service.get_current_year_options()
        self.year_dropdown = ft.Dropdown(
            label="Request Year *",
            options=[ft.dropdown.Option(year) for year in year_options],
            value=year_options[0],  # Current year as default
            width=400,
            on_change=self._on_field_change
        )
        
        # Document title field
        self.document_title_field = ft.TextField(
            label="Document Title",
            hint_text="Required for OTH projects",
            width=400,
            visible=False,
            on_change=self._on_field_change
        )
        
        # Error and preview text
        self.error_text = ft.Text("", color=ft.colors.RED_400, size=12, visible=False)
        self.preview_text = ft.Text("", size=12, color=ft.colors.BLUE_700, weight=ft.FontWeight.BOLD)
    
    def _create_dialog(self):
        """Create the dialog"""
        dialog_content = ft.Column([
            ft.Text(f"Create New Project: {self.ten_digit_number}", 
                   size=16, weight=ft.FontWeight.BOLD),
            ft.Container(height=15),
            
            # Form fields - vertically stacked
            self.project_type_dropdown,
            ft.Container(height=10),
            self.suffix_field,
            ft.Container(height=10),
            self.year_dropdown,
            ft.Container(height=10),
            self.document_title_field,
            
            ft.Container(height=15),
            self.error_text,
            
            ft.Container(height=10),
            ft.Text("Preview:", size=12, weight=ft.FontWeight.BOLD),
            self.preview_text,
            
        ], spacing=5, tight=True, width=500)
        
        self.dialog = ft.AlertDialog(
            title=ft.Text("Add New Project"),
            content=dialog_content,
            actions=[
                ft.TextButton("Cancel", on_click=self._on_cancel_clicked),
                ft.ElevatedButton(
                    "Create Project", 
                    on_click=self._on_create_clicked,
                    style=ft.ButtonStyle(
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.GREEN_700
                    )
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
    
    def _on_project_type_change(self, e):
        """Handle project type changes"""
        project_type = e.control.value
        
        # Show/hide document title field
        self.document_title_field.visible = self.project_service.is_document_title_required(project_type)
        
        # Update suffix field label
        if self.project_service.is_suffix_required(project_type):
            self.suffix_field.label = "Suffix *"
        else:
            self.suffix_field.label = "Suffix (Optional)"
        
        self._update_preview()
    
    def _on_suffix_change(self, e):
        """Handle suffix field changes with validation"""
        suffix = self.project_service.format_suffix(e.control.value)
        
        if suffix:
            import re
            if re.match(self.project_service.SUFFIX_PATTERN, suffix):
                e.control.value = suffix
                e.control.error_text = None
            else:
                e.control.error_text = "Format: ABC123"
        else:
            e.control.error_text = None
        
        self._update_preview()
    
    def _on_field_change(self, e):
        """Handle any field change"""
        self._update_preview()
    
    def _update_preview(self):
        """Update filename preview"""
        project_type = self.project_type_dropdown.value
        suffix = self.project_service.format_suffix(self.suffix_field.value) if self.suffix_field.value else ""
        year = self.year_dropdown.value
        doc_title = self.document_title_field.value.strip() if self.document_title_field.value else ""
        
        if not project_type or not year:
            self.preview_text.value = "Please fill required fields"
            self.preview_text.color = ft.colors.GREY_500
        else:
            filename = self.project_service.generate_filename(
                self.ten_digit_number, project_type, suffix, year, doc_title
            )
            self.preview_text.value = f"Filename: {filename}"
            self.preview_text.color = ft.colors.BLUE_700
        
        self.page.update()
    
    def _on_create_clicked(self, e):
        """Handle create project button click"""
        # Get form values
        project_type = self.project_type_dropdown.value
        suffix = self.project_service.format_suffix(self.suffix_field.value) if self.suffix_field.value else ""
        year = self.year_dropdown.value
        doc_title = self.document_title_field.value.strip() if self.document_title_field.value else ""
        
        # Validate
        errors = self.project_service.validate_project_data(project_type, suffix, year, doc_title)
        
        if errors:
            self.error_text.value = "; ".join(errors)
            self.error_text.visible = True
            self.page.update()
            return
        
        # Create project data
        project_data = self.project_service.create_project_data(
            self.ten_digit_number, project_type, suffix, year, doc_title, self.folder_path
        )
        
        # Save project file
        success, message = self.project_service.save_project_file(project_data, self.folder_path)
        
        if success:
            self._close_dialog()
            if self.on_success:
                self.on_success(message)
        else:
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
