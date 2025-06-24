"""Project creation dialog component"""

import flet as ft
import os
from typing import Callable, Optional
import sys
from pathlib import Path

# Add src to path so we can import services and models directly
src_dir = Path(__file__).parent.parent.parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from services import ProjectCreationService
import uuid


class ProjectCreationDialog:
    """Dialog component for creating new projects with database integration"""
    
    def __init__(self, page: ft.Page, project_service: ProjectCreationService, 
                 on_success: Optional[Callable] = None, on_cancel: Optional[Callable] = None):
        self.page = page
        self.project_service = project_service
        self.on_success = on_success
        self.on_cancel = on_cancel
        self.dialog: Optional[ft.AlertDialog] = None
        
        # Form fields will be created in _create_form_fields
        # We'll initialize them as proper controls there
        
        # Data
        self.ten_digit_number = ""
        self.folder_path = ""
        
        # Track if we're editing an existing customer
        self.existing_customer = None
    
    def show(self, ten_digit_number: str, folder_path: str):
        """Show the project creation dialog"""
        self.ten_digit_number = ten_digit_number
        self.folder_path = folder_path
        
        # Check if customer exists based on the first 4 digits
        customer_key = ten_digit_number[:4]
        self.existing_customer = None  # No database lookup needed
        
        self._create_form_fields()
        self._create_dialog()
        
        self.page.dialog = self.dialog
        if self.dialog:
            self.dialog.open = True
        self.page.update()
    
    def _create_form_fields(self):
        """Create all form fields"""
        # Customer Information Section
        self.customer_key_field = ft.TextField(
            hint_text="Facility Number *",
            value=self.ten_digit_number,
            width=330,
            read_only=True
        )
        
        self.customer_name_field = ft.TextField(
            hint_text="Facility Name *",
            value=self.existing_customer.name if self.existing_customer else "",
            width=660
        )
        
        self.customer_number_field = ft.TextField(
            hint_text="Building Number (e.g., DC123)",
            value=self.existing_customer.number if self.existing_customer else "",
            width=330,
            on_change=self._on_building_number_change
        )
        
        # Project Information Section
        self.project_title_field = ft.TextField(
            hint_text="Project Title *",
            width=660
        )
        
        # Project type dropdown (moved to top)
        self.project_type_dropdown = ft.Dropdown(
            label="Project Type *",
            options=[ft.dropdown.Option(display_name) for display_name in self.project_service.get_project_type_options()],
            width=300,
            on_change=self._on_project_type_change
        )
        
        # Document title field 
        self.document_title_field = ft.TextField(
            hint_text="Document Title",
            width=660,
            visible=False,
            on_change=self._on_field_change
        )
        
        # Error text
        self.error_text = ft.Text("", color=ft.colors.RED_400, size=12, visible=False)
    
    def _create_dialog(self):
        """Create the dialog with organized sections"""
        # Project type selection at the top (for future functionality)
        project_type_section = ft.Container(
            content=ft.Column([
                ft.Text("Project Type", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700),
                ft.Container(height=5),
                # Row 1: Project Type dropdown
                ft.Row([
                    self.project_type_dropdown,
                ], spacing=10),
                # Row 2: Document title field (conditional visibility)
                ft.Row([
                    self.document_title_field,
                ], spacing=10),
            ], spacing=5),
            padding=ft.padding.all(5),
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=5
        )

        # Customer section - two rows, no customer suffix
        self.customer_section = ft.Container(
            content=ft.Column([
                ft.Text("Customer Information", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700),
                ft.Container(height=5),
                # Row 1: Facility Number and Building Number
                ft.Row([
                    self.customer_key_field,
                    self.customer_number_field,
                ], spacing=10),
                # Row 2: Facility Name (full width)
                ft.Row([
                    self.customer_name_field,
                ], spacing=10),
            ], spacing=5),
            padding=ft.padding.all(5),
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=5
        )

        # Project section - single row with just title
        self.project_section = ft.Container(
            content=ft.Column([
                ft.Text("Project Information", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700),
                ft.Container(height=5),
                # Row 1: Project Title (full width)
                ft.Row([
                    self.project_title_field,
                ], spacing=10),
            ], spacing=5),
            padding=ft.padding.all(5),
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=5
        )

        # Create scrollable content
        dialog_content = ft.Column([
            project_type_section,
            self.customer_section,
            self.project_section,
            self.error_text,
        ], spacing=10, scroll=ft.ScrollMode.AUTO, height=450)
        
        self.dialog = ft.AlertDialog(
            title=ft.Text("Add New Project"),
            content=ft.Container(
                content=dialog_content,
                width=700,
                height=450
            ),
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
        display_name = e.control.value
        project_type_code = self.project_service.get_project_type_code(display_name)
        
        # Show/hide document title field
        if self.document_title_field:
            self.document_title_field.visible = self.project_service.is_document_title_required(project_type_code)
        
        # For "Other" type, hide customer and project sections, only show document title
        is_other_type = project_type_code == "OTH"
        
        if hasattr(self, 'customer_section'):
            self.customer_section.visible = not is_other_type
        if hasattr(self, 'project_section'):
            self.project_section.visible = not is_other_type
        
        self.page.update()
    
    def _on_building_number_change(self, e):
        """Handle building number field changes with validation"""
        building_number = e.control.value.upper() if e.control.value else ""
        
        if building_number:
            import re
            building_pattern = r'^[A-Z]{2}\d{3}$'
            if re.match(building_pattern, building_number):
                e.control.value = building_number
                e.control.error_text = None
            else:
                e.control.error_text = "Format: Two letters + three digits (e.g., DC123)"
        else:
            e.control.error_text = None
        
        self.page.update()
    
    def _on_field_change(self, e):
        """Handle any field change"""
        pass
    
    def _on_create_clicked(self, e):
        """Handle create project button click with database integration"""
        try:
            # Get form values with proper null checks
            project_type_display = self.project_type_dropdown.value if self.project_type_dropdown.value else ""
            project_type = self.project_service.get_project_type_code(project_type_display)
            doc_title = self.document_title_field.value.strip() if self.document_title_field.value else ""
            
            # Use current year automatically
            import datetime
            current_year = str(datetime.datetime.now().year)
            
            # For "Other" type, we only need document title
            if project_type == "OTH":
                # Validate required fields for Other type
                errors = []
                if not project_type:
                    errors.append("Project type is required")
                if not doc_title:
                    errors.append("Document title is required for Other projects")
                
                if errors:
                    self.error_text.value = "; ".join(errors)
                    self.error_text.visible = True
                    self.page.update()
                    return
                
                # For Other type, create minimal project data
                project_data = self.project_service.create_project_data(
                    self.ten_digit_number, project_type, current_year, doc_title, self.folder_path
                )
                
                # Save project file
                success, message = self.project_service.save_project_file(project_data, self.folder_path, doc_title)
                
                if success:
                    # Get the created file path
                    filename = project_data["metadata"]["filename"]
                    file_path = os.path.join(self.folder_path, filename)
                    
                    print(f"Project created successfully. File path: {file_path}")
                    
                    self._close_dialog()
                    if self.on_success:
                        print(f"Calling success callback with message and file_path")
                        self.on_success(f"Other project created successfully: {message}", file_path)
                    else:
                        print("No success callback defined")
                else:
                    self.error_text.value = f"Failed to create project: {message}"
                    self.error_text.visible = True
                    self.page.update()
                return
            
            # For all other project types, require customer and project information
            # Get database fields
            customer_key = self.customer_key_field.value if self.customer_key_field.value else ""
            customer_name = self.customer_name_field.value.strip() if self.customer_name_field.value else ""
            customer_number = self.customer_number_field.value if self.customer_number_field.value else ""
            
            project_title = self.project_title_field.value.strip() if self.project_title_field.value else ""
            
            # Validate required fields
            errors = []
            if not project_type:
                errors.append("Project type is required")
            if not customer_name:
                errors.append("Facility name is required")
            if not customer_number:
                errors.append("Building number is required")
            if not project_title:
                errors.append("Project title is required")
            
            # Validate building number pattern
            if customer_number:
                import re
                building_pattern = r'^[A-Z]{2}\d{3}$'
                if not re.match(building_pattern, customer_number):
                    errors.append("Building number must follow pattern: two letters followed by three digits (e.g., DC123)")
            
            # Add existing validation (simplified for no suffix/year)
            if self.project_service.is_document_title_required(project_type) and not doc_title:
                errors.append("Document title is required for this project type")
            
            if errors:
                self.error_text.value = "; ".join(errors)
                self.error_text.visible = True
                self.page.update()
                return
            
            # Create project data structure  
            project_uuid = str(uuid.uuid4())
            
            # Create or get customer data (JSON-only)
            customer_data = {
                'key': customer_key,
                'name': customer_name,
                'number': customer_number,
                'suffix': None
            }
            
            # No project code since we removed suffix
            project_code = None
            
            # Create legacy JSON file for compatibility (with current year appended)
            project_data = self.project_service.create_project_data(
                self.ten_digit_number, project_type, current_year, doc_title, self.folder_path
            )
            
            # Add fields to JSON 
            project_data.update({
                'uuid': project_uuid,
                'customer': customer_data,
                'title': project_title,
                'description': None
            })
            
            # Save project file
            success, message = self.project_service.save_project_file(project_data, self.folder_path, project_title)
            
            if success:
                # Get the created file path
                filename = project_data["metadata"]["filename"]
                file_path = os.path.join(self.folder_path, filename)
                
                print(f"Regular project created successfully. File path: {file_path}")
                
                self._close_dialog()
                if self.on_success:
                    print(f"Calling success callback with message and file_path")
                    self.on_success(f"Project created successfully and file saved: {message}", file_path)
                else:
                    print("No success callback defined")
            else:
                # If file save failed
                self.error_text.value = f"File save failed: {message}"
                self.error_text.visible = True
                self.page.update()
                
        except Exception as ex:
            self.error_text.value = f"Error creating project: {str(ex)}"
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
