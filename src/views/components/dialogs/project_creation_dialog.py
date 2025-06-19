"""Project creation dialog component"""

import flet as ft
from typing import Callable, Optional
from services import ProjectCreationService
from models.database_manager import DatabaseManager, Customer, Project
import uuid


class ProjectCreationDialog:
    """Dialog component for creating new projects with database integration"""
    
    def __init__(self, page: ft.Page, project_service: ProjectCreationService, 
                 db_manager: DatabaseManager,
                 on_success: Optional[Callable] = None, on_cancel: Optional[Callable] = None):
        self.page = page
        self.project_service = project_service
        self.db_manager = db_manager
        self.on_success = on_success
        self.on_cancel = on_cancel
        self.dialog: Optional[ft.AlertDialog] = None
        
        # Form fields will be created in _create_form_fields
        # We'll initialize them as proper controls there
        
        # Data
        self.ten_digit_number = ""
        self.folder_path = ""
        
        # Track if we're editing an existing customer
        self.existing_customer: Optional[Customer] = None
    
    def show(self, ten_digit_number: str, folder_path: str):
        """Show the project creation dialog"""
        self.ten_digit_number = ten_digit_number
        self.folder_path = folder_path
        
        # Check if customer exists based on the first 4 digits
        customer_key = ten_digit_number[:4]
        self.existing_customer = self.db_manager.get_customer(customer_key)
        
        self._create_form_fields()
        self._create_dialog()
        
        self.page.dialog = self.dialog
        if self.dialog:
            self.dialog.open = True
        self.page.update()
        
        # Initial preview update
        self._update_preview()
    
    def _create_form_fields(self):
        """Create all form fields"""
        # Customer Information Section
        self.customer_key_field = ft.TextField(
            label="Facility Number *",
            value=self.ten_digit_number,
            width=200,
            read_only=True,  # Derived from folder structure
            helper_text="10-digit folder number"
        )
        
        self.customer_name_field = ft.TextField(
            label="Facility Name *",
            value=self.existing_customer.name if self.existing_customer else "",
            width=400,
            hint_text="Full facility name"
        )
        
        self.customer_number_field = ft.TextField(
            label="Building Number",
            value=self.existing_customer.number if self.existing_customer else "",
            width=200,
            hint_text=r"Format: [A-Z]{2}\d{3} (e.g., DC123)"
        )
        
        self.customer_suffix_field = ft.TextField(
            label="Customer Suffix",
            value=self.existing_customer.suffix if self.existing_customer else "",
            width=200,
            hint_text="Optional suffix"
        )
        
        # Project Information Section
        self.project_title_field = ft.TextField(
            label="Project Title *",
            width=400,
            hint_text="Descriptive project title"
        )
        
        self.project_description_field = ft.TextField(
            label="Project Description",
            width=400,
            max_lines=3,
            hint_text="Optional project description"
        )
        
        # Project type dropdown (existing)
        self.project_type_dropdown = ft.Dropdown(
            label="Project Type *",
            options=[ft.dropdown.Option(ptype) for ptype in self.project_service.PROJECT_TYPES],
            width=200,
            on_change=self._on_project_type_change
        )
        
        # Suffix field (existing)
        self.suffix_field = ft.TextField(
            label="Suffix *",
            hint_text="ABC123 format",
            width=200,
            max_length=6,
            on_change=self._on_suffix_change
        )
        
        # Year dropdown (existing)
        year_options = self.project_service.get_current_year_options()
        self.year_dropdown = ft.Dropdown(
            label="Request Year *",
            options=[ft.dropdown.Option(year) for year in year_options],
            value=year_options[0],  # Current year as default
            width=200,
            on_change=self._on_field_change
        )
        
        # Document title field (existing)
        self.document_title_field = ft.TextField(
            label="Document Title",
            hint_text="Required for OTH projects",
            width=400,
            visible=False,
            on_change=self._on_field_change
        )
        
        # Team Information Section
        self.engineer_field = ft.TextField(
            label="Engineer",
            width=300,
            hint_text="Lead engineer name"
        )
        
        self.drafter_field = ft.TextField(
            label="Drafter",
            width=300,
            hint_text="Drafter name"
        )
        
        self.reviewer_field = ft.TextField(
            label="Reviewer",
            width=300,
            hint_text="Reviewer name"
        )
        
        self.architect_field = ft.TextField(
            label="Architect",
            width=300,
            hint_text="Architect name"
        )
        
        self.geologist_field = ft.TextField(
            label="Geologist",
            width=300,
            hint_text="Geologist name"
        )
        
        # Error and preview text
        self.error_text = ft.Text("", color=ft.colors.RED_400, size=12, visible=False)
        self.preview_text = ft.Text("", size=12, color=ft.colors.BLUE_700, weight=ft.FontWeight.BOLD)
    
    def _create_dialog(self):
        """Create the dialog with organized sections"""
        # Customer section
        customer_section = ft.Container(
            content=ft.Column([
                ft.Text("Customer Information", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700),
                ft.Row([
                    self.customer_key_field,
                    self.customer_number_field,
                ], spacing=10),
                ft.Row([
                    self.customer_name_field,
                ]),
                ft.Row([
                    self.customer_suffix_field,
                ], spacing=10),
            ], spacing=8),
            padding=ft.padding.all(10),
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=5
        )
        
        # Project section
        project_section = ft.Container(
            content=ft.Column([
                ft.Text("Project Information", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700),
                ft.Row([
                    self.project_title_field,
                ]),
                ft.Row([
                    self.project_description_field,
                ]),
                ft.Row([
                    self.project_type_dropdown,
                    self.suffix_field,
                    self.year_dropdown,
                ], spacing=10),
                self.document_title_field,
            ], spacing=8),
            padding=ft.padding.all(10),
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=5
        )
        
        # Team section
        team_section = ft.Container(
            content=ft.Column([
                ft.Text("Project Team", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700),
                ft.Row([
                    self.engineer_field,
                    self.drafter_field,
                ], spacing=10),
                ft.Row([
                    self.reviewer_field,
                    self.architect_field,
                ], spacing=10),
                ft.Row([
                    self.geologist_field,
                ], spacing=10),
            ], spacing=8),
            padding=ft.padding.all(10),
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=5
        )
        
        # Create scrollable content
        dialog_content = ft.Column([
            ft.Text(f"Create New Project: {self.ten_digit_number}", 
                   size=16, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            
            customer_section,
            ft.Container(height=10),
            project_section,
            ft.Container(height=10),
            team_section,
            
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
                width=700,
                height=600
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
        project_type = e.control.value
        
        # Show/hide document title field
        if self.document_title_field:
            self.document_title_field.visible = self.project_service.is_document_title_required(project_type)
        
        # Update suffix field label
        if self.suffix_field:
            if self.project_service.is_suffix_required(project_type):
                self.suffix_field.label = "Suffix *"
            else:
                self.suffix_field.label = "Suffix (Optional)"
        
        self._update_preview()
        self.page.update()
    
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
        self.page.update()
    
    def _on_field_change(self, e):
        """Handle any field change"""
        self._update_preview()
    
    def _update_preview(self):
        """Update filename preview"""
        if not (self.project_type_dropdown and self.suffix_field and self.year_dropdown):
            return
            
        project_type = self.project_type_dropdown.value
        suffix = self.project_service.format_suffix(self.suffix_field.value) if self.suffix_field.value else ""
        year = self.year_dropdown.value
        doc_title = self.document_title_field.value.strip() if self.document_title_field and self.document_title_field.value else ""
        
        if not project_type or not year:
            if self.preview_text:
                self.preview_text.value = "Please fill required fields"
                self.preview_text.color = ft.colors.GREY_500
        else:
            filename = self.project_service.generate_filename(
                self.ten_digit_number, project_type, suffix, year, doc_title
            )
            if self.preview_text:
                self.preview_text.value = f"Filename: {filename}"
                self.preview_text.color = ft.colors.BLUE_700
        
        self.page.update()
    
    def _on_create_clicked(self, e):
        """Handle create project button click with database integration"""
        try:
            # Get form values with proper null checks
            project_type = self.project_type_dropdown.value if self.project_type_dropdown.value else ""
            suffix = self.project_service.format_suffix(self.suffix_field.value) if self.suffix_field.value else ""
            year = self.year_dropdown.value if self.year_dropdown.value else ""
            doc_title = self.document_title_field.value.strip() if self.document_title_field.value else ""
            
            # Get database fields
            customer_key = self.customer_key_field.value if self.customer_key_field.value else ""
            customer_name = self.customer_name_field.value.strip() if self.customer_name_field.value else ""
            customer_number = self.customer_number_field.value if self.customer_number_field.value else ""
            customer_suffix = self.customer_suffix_field.value if self.customer_suffix_field.value else ""
            
            project_title = self.project_title_field.value.strip() if self.project_title_field.value else ""
            project_description = self.project_description_field.value.strip() if self.project_description_field.value else ""
            
            engineer = self.engineer_field.value.strip() if self.engineer_field.value else ""
            drafter = self.drafter_field.value.strip() if self.drafter_field.value else ""
            reviewer = self.reviewer_field.value.strip() if self.reviewer_field.value else ""
            architect = self.architect_field.value.strip() if self.architect_field.value else ""
            geologist = self.geologist_field.value.strip() if self.geologist_field.value else ""
            
            # Validate required fields
            errors = []
            if not project_type:
                errors.append("Project type is required")
            if not year:
                errors.append("Request year is required")
            if not customer_name:
                errors.append("Facility name is required")
            if not project_title:
                errors.append("Project title is required")
            
            # Validate building number pattern if provided
            if customer_number:
                import re
                building_pattern = r'^[A-Z]{2}\d{3}$'
                if not re.match(building_pattern, customer_number):
                    errors.append("Building number must follow pattern: two letters followed by three digits (e.g., DC123)")
            
            # Add existing validation
            validation_errors = self.project_service.validate_project_data(project_type, suffix, year, doc_title)
            errors.extend(validation_errors)
            
            if errors:
                self.error_text.value = "; ".join(errors)
                self.error_text.visible = True
                self.page.update()
                return
            
            # Create or get customer
            customer_data = {
                'key': customer_key,
                'name': customer_name,
                'number': customer_number,
                'suffix': customer_suffix if customer_suffix else None
            }
            customer_id = self.db_manager.get_or_create_customer(customer_data)
            
            # Generate project code from suffix and year
            project_code = f"{suffix}" if suffix else None
            
            # Create project in database
            project_uuid = str(uuid.uuid4())
            project = Project(
                uuid=project_uuid,
                customer_id=customer_id,
                engineer=engineer if engineer else None,
                drafter=drafter if drafter else None,
                reviewer=reviewer if reviewer else None,
                architect=architect if architect else None,
                geologist=geologist if geologist else None,
                project_code=project_code,
                project_type=project_type,
                title=project_title,
                description=project_description if project_description else None
            )
            
            project_id = self.db_manager.create_project(project)
            
            # Create legacy JSON file for compatibility
            project_data = self.project_service.create_project_data(
                self.ten_digit_number, project_type, suffix, year, doc_title, self.folder_path
            )
            
            # Add database fields to JSON for compatibility
            project_data.update({
                'uuid': project_uuid,
                'customer': customer_data,
                'title': project_title,
                'description': project_description,
                'engineer': engineer,
                'drafter': drafter,
                'reviewer': reviewer,
                'architect': architect,
                'geologist': geologist,
                'database_id': project_id
            })
            
            # Save project file
            success, message = self.project_service.save_project_file(project_data, self.folder_path)
            
            if success:
                self._close_dialog()
                if self.on_success:
                    self.on_success(f"Project created successfully in database (ID: {project_id}) and file saved: {message}")
            else:
                # If file save failed, we might want to remove the database entry
                self.error_text.value = f"Database entry created but file save failed: {message}"
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
