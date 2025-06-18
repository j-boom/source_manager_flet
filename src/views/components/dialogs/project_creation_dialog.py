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
        
        # Initial setup complete
    
    def _create_form_fields(self):
        """Create all form fields"""
        # Facility Information Section
        self.facility_name_field = ft.TextField(
            label="Facility Name *",
            value="",  # Always start empty - user input required
            expand=True,  # Fill the full width of the dialog
            hint_text="Full facility name",
            on_change=self._on_field_change
        )
        
        self.facility_number_field = ft.TextField(
            label="Facility Number *",
            value=self.ten_digit_number,  # Only this field is auto-populated
            width=200,
            read_only=False,  # Allow tab navigation
            border_color=ft.colors.GREY_400,  # Make it look read-only
            focused_border_color=ft.colors.GREY_400,
            hint_text="Derived from folder structure",
            on_change=self._reset_facility_number  # Prevent actual editing
        )
        
        self.facility_suffix_field = ft.TextField(
            label="Suffix *",
            value="",  # Always start empty - user input required
            width=200,
            hint_text="Required suffix",
            on_change=self._on_field_change
        )
        
        self.facility_surrogate_key_field = ft.TextField(
            label="Facility Surrogate Key *",
            value="",  # Always start empty - user input required
            expand=True,  # Fill remaining width
            hint_text="Required key",
            on_change=self._on_field_change
        )
        
        # Project Information Section
        # Project title is now user-editable and required
        self.project_title_field = ft.TextField(
            label="Project Title *",
            expand=True,  # Fill the full width of the dialog
            hint_text="Enter custom project title",
            on_change=self._on_field_change
        )
        
        # Project type dropdown (existing)
        self.project_type_dropdown = ft.Dropdown(
            label="Project Type *",
            options=[ft.dropdown.Option(ptype) for ptype in self.project_service.PROJECT_TYPES],
            width=280,  # Increased width to accommodate longer project type names
            on_change=self._on_project_type_change
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
            expand=True,  # Fill the full width of the dialog
            visible=False,
            on_change=self._on_field_change
        )
        
        # Error and status text - make it more prominent
        self.error_text = ft.Text("", color=ft.colors.RED_400, size=14, visible=False, weight=ft.FontWeight.BOLD)
    
    def _create_dialog(self):
        """Create the dialog with organized sections"""
        # Facility section
        facility_section = ft.Container(
            content=ft.Column([
                ft.Text("Facility Information", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700),
                ft.Row([
                    self.facility_name_field,
                ]),
                ft.Row([
                    self.facility_number_field,
                    self.facility_suffix_field,
                    self.facility_surrogate_key_field,
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
                    self.project_type_dropdown,
                    self.year_dropdown,
                ], spacing=10),
                self.document_title_field,
            ], spacing=8),
            padding=ft.padding.all(10),
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=5
        )
        
        # Create scrollable content
        dialog_content = ft.Column([
            ft.Text(f"Create New Project: {self.ten_digit_number}", 
                   size=16, weight=ft.FontWeight.BOLD),
            
            # Error message at the top where it's visible
            ft.Container(
                content=self.error_text,
                bgcolor=ft.colors.RED_50,
                border=ft.border.all(1, ft.colors.RED_300),
                border_radius=5,
                padding=ft.padding.all(10),
                visible=False,
                ref=ft.Ref[ft.Container]()
            ),
            
            ft.Container(height=10),
            facility_section,
            ft.Container(height=10),
            project_section,
            
        ], spacing=5, scroll=ft.ScrollMode.AUTO, height=400)
        
        # Store reference to error container for easy show/hide
        self.error_container = dialog_content.controls[1]
        
        self.dialog = ft.AlertDialog(
            title=ft.Text("Add New Project"),
            content=ft.Container(
                content=dialog_content,
                width=700,
                height=400
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
        # Clear errors when user makes a selection
        self.error_container.visible = False
        e.control.border_color = None
        
        project_type = e.control.value
        
        # Show/hide document title field
        if self.document_title_field:
            self.document_title_field.visible = self.project_service.is_document_title_required(project_type)
        
        self.page.update()
    
    def _reset_facility_number(self, e):
        """Prevent editing of facility number while allowing tab navigation"""
        e.control.value = self.ten_digit_number
        self.page.update()

    def _on_field_change(self, e):
        """Handle any field change - clear errors when user starts typing"""
        # Clear error styling when user starts fixing issues
        self.error_container.visible = False
        e.control.border_color = None
        e.control.focused_border_color = None
        self.page.update()    
    def _clear_field_errors(self):
        """Clear error styling from all fields"""
        # Reset all fields to normal border colors
        fields = [
            self.facility_name_field,
            self.facility_suffix_field,
            self.facility_surrogate_key_field,
            self.project_title_field
        ]
        
        for field in fields:
            field.border_color = None
            field.focused_border_color = None
        
        # Reset dropdowns
        self.project_type_dropdown.border_color = None
        self.year_dropdown.border_color = None
    
    def _highlight_error_fields(self, errors):
        """Highlight fields that have validation errors"""
        error_color = ft.colors.RED_400
        
        for error in errors:
            if "facility name" in error.lower():
                self.facility_name_field.border_color = error_color
                self.facility_name_field.focused_border_color = error_color
            elif "facility suffix" in error.lower() or "suffix" in error.lower():
                self.facility_suffix_field.border_color = error_color
                self.facility_suffix_field.focused_border_color = error_color
            elif "facility surrogate key" in error.lower() or "surrogate" in error.lower():
                self.facility_surrogate_key_field.border_color = error_color
                self.facility_surrogate_key_field.focused_border_color = error_color
            elif "project title" in error.lower():
                self.project_title_field.border_color = error_color
                self.project_title_field.focused_border_color = error_color
            elif "project type" in error.lower():
                self.project_type_dropdown.border_color = error_color
            elif "year" in error.lower():
                self.year_dropdown.border_color = error_color

    def _on_create_clicked(self, e):
        """Handle create project button click with database integration"""
        print("DEBUG: Create button clicked!")  # Debug output
        try:
            # Get form values with proper null checks
            project_type_display = self.project_type_dropdown.value if self.project_type_dropdown.value else ""
            # Convert display name to code for backend processing
            project_type = self.project_service.PROJECT_TYPE_CODES.get(project_type_display, project_type_display)
            
            # Use facility suffix instead of project suffix
            facility_suffix = self.facility_suffix_field.value if self.facility_suffix_field.value else ""
            year = self.year_dropdown.value if self.year_dropdown.value else ""
            doc_title = self.document_title_field.value.strip() if self.document_title_field.value else ""
            
            # Get database fields
            facility_key = self.facility_surrogate_key_field.value.strip() if self.facility_surrogate_key_field.value else ""
            facility_name = self.facility_name_field.value.strip() if self.facility_name_field.value else ""
            facility_number = self.facility_number_field.value if self.facility_number_field.value else ""
            
            # Project title is now user-entered
            project_title = self.project_title_field.value.strip() if self.project_title_field.value else ""
            
            # Validate required fields
            errors = []
            print(f"DEBUG: Validation - project_type_display: '{project_type_display}'")
            print(f"DEBUG: Validation - project_type_code: '{project_type}'")
            print(f"DEBUG: Validation - year: '{year}'") 
            print(f"DEBUG: Validation - facility_name: '{facility_name}'")
            print(f"DEBUG: Validation - facility_number: '{facility_number}'")
            print(f"DEBUG: Validation - facility_suffix: '{facility_suffix}'")
            print(f"DEBUG: Validation - facility_key: '{facility_key}'")
            print(f"DEBUG: Validation - project_title: '{project_title}'")
            
            if not project_type_display:
                errors.append("Project type is required")
            if not year:
                errors.append("Request year is required")
            if not facility_name:
                errors.append("Facility name is required")
            if not facility_number:
                errors.append("Facility number is required")
            if not facility_suffix:
                errors.append("Facility suffix is required")
            if not facility_key:
                errors.append("Facility surrogate key is required")
            if not project_title:
                errors.append("Project title is required")
            
            # Add existing validation (using facility_suffix instead of project suffix)
            validation_errors = self.project_service.validate_project_data(project_type_display, facility_suffix, year, doc_title)
            errors.extend(validation_errors)
            
            if errors:
                print(f"DEBUG: Validation errors: {errors}")
                
                # Clear any previous field error styling
                self._clear_field_errors()
                
                # Highlight fields with errors and show prominent error message
                self._highlight_error_fields(errors)
                
                # Show error message prominently at the top
                self.error_text.value = "Please fix the following issues:\n• " + "\n• ".join(errors)
                self.error_text.visible = True
                self.error_container.visible = True
                
                # Scroll to top to ensure error is visible
                self.page.update()
                return
            
            # Clear any error styling on successful validation
            self._clear_field_errors()
            self.error_container.visible = False
            
            print("DEBUG: Validation passed, creating project...")
            
            # Create or get customer (still using customer terminology in backend)
            customer_data = {
                'key': facility_key,
                'name': facility_name,
                'number': facility_number,
                'suffix': facility_suffix if facility_suffix else None
            }
            customer_id = self.db_manager.get_or_create_customer(customer_data)
            
            # Generate project code from facility suffix and year
            project_code = f"{facility_suffix}" if facility_suffix else None
            
            # Create project in database (team fields will be set in metadata tab)
            project_uuid = str(uuid.uuid4())
            project = Project(
                uuid=project_uuid,
                customer_id=customer_id,
                engineer=None,  # Will be set in metadata tab
                drafter=None,   # Will be set in metadata tab
                reviewer=None,  # Will be set in metadata tab
                architect=None, # Will be set in metadata tab
                project_code=project_code,
                project_type=project_type,
                title=project_title,
                description=None  # No longer using project description
            )
            
            project_id = self.db_manager.create_project(project)
            
            # Create legacy JSON file for compatibility
            project_data = self.project_service.create_project_data(
                self.ten_digit_number, project_type_display, facility_suffix, year, doc_title, self.folder_path
            )
            
            # Add database fields to JSON for compatibility  
            project_data.update({
                'uuid': project_uuid,
                'customer': customer_data,  # Still called 'customer' in JSON for compatibility
                'title': project_title,
                'description': None,  # No longer using project description
                'engineer': None,     # Will be set in metadata tab
                'drafter': None,      # Will be set in metadata tab
                'reviewer': None,     # Will be set in metadata tab
                'architect': None,    # Will be set in metadata tab
                'database_id': project_id
            })
            
            # Save project file
            success, message = self.project_service.save_project_file(project_data, self.folder_path)
            
            if success:
                self._close_dialog()
                if self.on_success:
                    # Pass project data for loading into app state
                    success_data = {
                        'project': project,
                        'project_data': project_data,
                        'file_path': self.folder_path,
                        'message': f"Project created successfully in database (ID: {project_id}) and file saved: {message}"
                    }
                    self.on_success(success_data)
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
