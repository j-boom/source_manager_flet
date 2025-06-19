"""
Dynamic Project Creation Dialog
Uses configuration-driven forms for different project types
"""

import flet as ft
import uuid
from typing import Optional, Callable, Dict, Any
from config.project_types_config import get_project_type_config, get_all_project_types
from src.views.components.forms.dynamic_form_generator import DynamicFormGenerator
from src.models.database_manager import DatabaseManager, Customer, Project
from src.services.project_creation_service import ProjectCreationService


class DynamicProjectCreationDialog:
    """Dynamic project creation dialog using configuration-driven forms"""
    
    def __init__(self, 
                 page: ft.Page,
                 theme_manager,
                 user_config,
                 ten_digit_number: str,
                 folder_path: str,
                 existing_customer: Optional[Customer] = None,
                 on_success: Optional[Callable] = None):
        
        self.page = page
        self.theme_manager = theme_manager
        self.user_config = user_config
        self.ten_digit_number = ten_digit_number
        self.folder_path = folder_path
        self.existing_customer = existing_customer
        self.on_success = on_success
        
        # Initialize services
        self.db_manager = DatabaseManager()
        self.project_service = ProjectCreationService(user_config)
        
        # Initialize form generator
        self.form_generator = DynamicFormGenerator(
            theme_manager=theme_manager,
            on_field_change=self._on_field_change
        )
        
        # UI components
        self.project_type_dropdown = None
        self.dialog = None
        self.error_text = ft.Text("", color=ft.colors.RED_400, size=12, visible=False)
        self.preview_text = ft.Text("", size=12, color=ft.colors.BLUE_700, weight=ft.FontWeight.BOLD)
        self.form_container = ft.Column([], spacing=10)
        self.current_project_type = None
        
        self._create_dialog()
    
    def _create_dialog(self):
        """Create the dynamic dialog"""
        # Project type selection
        self.project_type_dropdown = self.form_generator.get_project_type_dropdown(
            on_change=self._on_project_type_change
        )
        
        # Initial form container
        self.form_container = ft.Column([], spacing=10, scroll=ft.ScrollMode.AUTO, height=500)
        
        # Dialog content
        dialog_content = ft.Column([
            ft.Text(f"Create New Project: {self.ten_digit_number}", 
                   size=16, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            
            # Project type selection
            ft.Container(
                content=ft.Column([
                    ft.Text("Project Type", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700),
                    self.project_type_dropdown,
                ], spacing=8),
                padding=ft.padding.all(10),
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=5
            ),
            
            ft.Container(height=10),
            
            # Dynamic form container
            self.form_container,
            
            ft.Container(height=15),
            self.error_text,
            
            ft.Container(height=10),
            ft.Text("File Preview:", size=12, weight=ft.FontWeight.BOLD),
            self.preview_text,
            
        ], spacing=5, scroll=ft.ScrollMode.AUTO, height=600)
        
        self.dialog = ft.AlertDialog(
            title=ft.Text("Add New Project"),
            content=ft.Container(
                content=dialog_content,
                width=800,
                height=600
            ),
            actions=[
                ft.TextButton("Cancel", on_click=self._close_dialog),
                ft.ElevatedButton("Create Project", on_click=self._create_project),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    
    def _on_project_type_change(self, e):
        """Handle project type selection change"""
        project_type = e.control.value
        if not project_type:
            self.form_container.controls.clear()
            self.page.update()
            return
        
        self.current_project_type = project_type
        
        # Generate form for selected project type
        sections = self.form_generator.generate_form(project_type)
        
        # Clear and rebuild form container
        self.form_container.controls.clear()
        
        # Add sections in order
        for section_name in ["facility", "project", "team"]:
            if section_name in sections:
                self.form_container.controls.append(sections[section_name])
        
        # Pre-populate facility information if available
        self._populate_facility_data()
        
        # Update preview
        self._update_preview()
        
        self.page.update()
    
    def _populate_facility_data(self):
        """Pre-populate facility data from existing customer or folder structure"""
        if not self.form_generator.fields:
            return
        
        # Set facility number
        facility_field = self.form_generator.get_field("facility_number")
        if facility_field:
            facility_field.value = self.ten_digit_number
            facility_field.control.read_only = True
        
        # Set existing customer data if available
        if self.existing_customer:
            name_field = self.form_generator.get_field("facility_name")
            if name_field:
                name_field.value = self.existing_customer.name
            
            number_field = self.form_generator.get_field("building_number")
            if number_field:
                number_field.value = self.existing_customer.number or ""
            
            suffix_field = self.form_generator.get_field("customer_suffix")
            if suffix_field:
                suffix_field.value = self.existing_customer.suffix or ""
    
    def _on_field_change(self, e):
        """Handle field value changes"""
        self._update_preview()
    
    def _update_preview(self):
        """Update the filename preview"""
        if not self.current_project_type:
            return
        
        config = get_project_type_config(self.current_project_type)
        if not config:
            return
        
        # Get current field values
        values = self.form_generator.get_field_values()
        
        try:
            # Generate filename using the pattern
            filename = config.filename_pattern.format(**values)
            self.preview_text.value = f"File: {filename}"
        except KeyError as e:
            self.preview_text.value = f"Preview: Missing field {e}"
        except Exception as e:
            self.preview_text.value = f"Preview: {str(e)}"
        
        if self.page:
            self.page.update()
    
    def _create_project(self, e):
        """Create the project"""
        if not self.current_project_type:
            self._show_error("Please select a project type")
            return
        
        # Validate form
        errors = self.form_generator.validate_form()
        if errors:
            self._show_error("; ".join(errors))
            return
        
        try:
            # Get form values
            values = self.form_generator.get_field_values()
            
            # Create or get customer
            customer_data = {
                'key': values.get('facility_number', ''),
                'name': values.get('facility_name', ''),
                'number': values.get('building_number', ''),
                'suffix': values.get('customer_suffix', '')
            }
            
            customer_id = self.db_manager.create_or_get_customer(
                Customer(**customer_data)
            )
            
            # Create project in base table
            project_uuid = str(uuid.uuid4())
            base_project_data = {
                'uuid': project_uuid,
                'customer_id': customer_id,
                'project_type': self.current_project_type,
                'status': 'active'
            }
            
            # This would need to be implemented in DatabaseManager
            base_project_id = self._create_base_project(base_project_data)
            
            # Create project type specific record
            type_project_data = values.copy()
            type_project_data['project_base_id'] = base_project_id
            
            config = get_project_type_config(self.current_project_type)
            self._create_type_project(config.table_name, type_project_data)
            
            # Create JSON file for compatibility
            filename = config.filename_pattern.format(**values)
            project_json_data = {
                'uuid': project_uuid,
                'project_type': self.current_project_type,
                'customer': customer_data,
                'created_at': '',
                'filename': filename,
                'folder_path': self.folder_path,
                **values
            }
            
            # Save project file
            success, message = self.project_service.save_project_file(
                project_json_data, self.folder_path
            )
            
            if success:
                self._close_dialog()
                if self.on_success:
                    self.on_success(self.folder_path, filename)
            else:
                self._show_error(f"Failed to save project file: {message}")
                
        except Exception as ex:
            self._show_error(f"Error creating project: {str(ex)}")
    
    def _create_base_project(self, data: Dict[str, Any]) -> int:
        """Create base project record (to be implemented in DatabaseManager)"""
        # This is a placeholder - would need to implement in DatabaseManager
        return 1
    
    def _create_type_project(self, table_name: str, data: Dict[str, Any]):
        """Create project type specific record (to be implemented in DatabaseManager)"""
        # This is a placeholder - would need to implement in DatabaseManager
        pass
    
    def _show_error(self, message: str):
        """Show error message"""
        self.error_text.value = message
        self.error_text.visible = True
        self.page.update()
    
    def _close_dialog(self, e=None):
        """Close the dialog"""
        if self.dialog:
            self.dialog.open = False
            self.page.update()
    
    def show(self):
        """Show the dialog"""
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()
