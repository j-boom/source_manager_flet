"""
Metadata Tab for Project View
Handles project metadata editing and saving
"""

import flet as ft
from typing import Dict, Any, Optional
from .base_tab import BaseProjectTab
from services.project_creation_service import ProjectCreationService


class MetadataTab(BaseProjectTab):
    """Project metadata editing tab"""
    
    def __init__(self, page: ft.Page, theme_manager=None, database_manager=None, project_state_manager=None):
        super().__init__(page, theme_manager, database_manager, project_state_manager)
        self.metadata_fields = {}
        
    def build(self) -> ft.Control:
        """Build metadata editing tab with three columns"""
        project_info = self._get_project_info()
        
        return ft.Column([
            # Header with edit/save controls
            ft.Row([
                control for control in [
                    ft.Text("Project Metadata", size=18, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "Edit" if not self.edit_mode else "Save",
                        icon=ft.icons.EDIT if not self.edit_mode else ft.icons.SAVE,
                        on_click=lambda e: self._toggle_edit_mode(),
                        style=ft.ButtonStyle(
                            bgcolor=self._get_theme_color(),
                            color=ft.colors.WHITE
                        )
                    ) if project_info else None,
                    ft.ElevatedButton(
                        "Cancel",
                        icon=ft.icons.CANCEL,
                        on_click=lambda e: self._cancel_changes(),
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.RED_600,
                            color=ft.colors.WHITE
                        )
                    ) if self.edit_mode else None,
                ] if control is not None
            ], spacing=10),
            
            ft.Container(height=20),
            
            # Three-column layout
            ft.Row([
                # Column 1: Basic Information
                ft.Container(
                    content=ft.Column([
                        ft.Text("Basic Information", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(height=15),
                        self._create_text_field(
                            "title", "Project Title", 
                            project_info.get('title', ''), 
                            width=280
                        ),
                        self._create_dropdown_field(
                            "project_type", "Project Type",
                            self._get_project_type_display_name(project_info.get('project_type', '')),
                            options=ProjectCreationService.PROJECT_TYPES,
                            width=280
                        ),
                        self._create_text_field(
                            "project_code", "Project Code",
                            project_info.get('project_code', ''),
                            width=280
                        ),
                        self._create_text_field(
                            "status", "Status",
                            project_info.get('status', 'active'),
                            width=280
                        ),
                    ], spacing=15, tight=True),
                    width=280,
                    alignment=ft.alignment.top_left
                ),
                
                ft.Container(width=40),  # Spacer
                
                # Column 2: Team Information
                ft.Container(
                    content=ft.Column([
                        ft.Text("Team Information", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(height=15),
                        self._create_text_field(
                            "engineer", "Engineer",
                            project_info.get('engineer', ''),
                            width=280,
                            hint_text="Lead engineer name"
                        ),
                        self._create_text_field(
                            "drafter", "Drafter",
                            project_info.get('drafter', ''),
                            width=280,
                            hint_text="Drafter name"
                        ),
                        self._create_text_field(
                            "reviewer", "Reviewer",
                            project_info.get('reviewer', ''),
                            width=280,
                            hint_text="Reviewer name"
                        ),
                        self._create_text_field(
                            "architect", "Architect",
                            project_info.get('architect', ''),
                            width=280,
                            hint_text="Architect name"
                        ),
                    ], spacing=15, tight=True),
                    width=280,
                    alignment=ft.alignment.top_left
                ),
                
                ft.Container(width=40),  # Spacer
                
                # Column 3: Requestor Information
                ft.Container(
                    content=ft.Column([
                        ft.Text("Requestor Information", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(height=15),
                        self._create_text_field(
                            "requestor_name", "Requestor Name",
                            project_info.get('requestor_name', ''),
                            width=280,
                            hint_text="Name of person requesting project"
                        ),
                        self._create_text_field(
                            "request_date", "Request Date",
                            project_info.get('request_date', ''),
                            width=280,
                            hint_text="e.g., FY25 Q2"
                        ),
                        ft.Container(height=15),
                        self._create_checkbox_field(
                            "relook", "Relook",
                            project_info.get('relook', False)
                        ),
                        ft.Container(height=56),  # Height matching
                    ], spacing=15, tight=True),
                    width=280,
                    alignment=ft.alignment.top_left
                ),
                
            ], alignment=ft.MainAxisAlignment.START, 
               vertical_alignment=ft.CrossAxisAlignment.START,
               spacing=0),
            
        ], spacing=5, scroll=ft.ScrollMode.AUTO)
    
    def _create_dropdown_field(self, key: str, label: str, value: str, options: list, width: int = 300) -> ft.Dropdown:
        """Create a dropdown field with edit mode support"""
        if self.edit_mode:
            theme_color = self._get_theme_color()
            border_color = theme_color
            bgcolor = None
        else:
            bgcolor = None
            border_color = ft.colors.GREY_400

        dropdown_options = [ft.dropdown.Option(option) for option in options]
        
        field = ft.Dropdown(
            label=label,
            value=value,
            width=width,
            options=dropdown_options,
            disabled=not self.edit_mode,
            bgcolor=bgcolor,
            border_color=border_color,
            focused_border_color=self._get_theme_color() if self.edit_mode else None
        )
        
        self.metadata_fields[key] = field
        return field
        
    def _create_text_field(self, key: str, label: str, value: str, width: int = 300, hint_text: Optional[str] = None) -> ft.TextField:
        """Override to store field references"""
        field = super()._create_text_field(key, label, value, width, hint_text)
        self.metadata_fields[key] = field
        return field
        
    def _create_checkbox_field(self, key: str, label: str, value: bool) -> ft.Checkbox:
        """Override to store field references"""
        field = super()._create_checkbox_field(key, label, value)
        self.metadata_fields[key] = field
        return field
    
    def _get_project_type_display_name(self, code: str) -> str:
        """Convert project type code to display name"""
        if not code or code == "" or code == "None":
            return ""
        code_to_display = {v: k for k, v in ProjectCreationService.PROJECT_TYPE_CODES.items()}
        return code_to_display.get(code, code)
    
    def _get_project_type_code(self, display_name: str) -> str:
        """Convert project type display name to code"""
        if not display_name or display_name == "":
            return ""
        return ProjectCreationService.PROJECT_TYPE_CODES.get(display_name, display_name)
    
    def _toggle_edit_mode(self):
        """Toggle between edit and read-only mode"""
        if self.edit_mode:
            # Save changes
            self._save_metadata()
        else:
            # Enter edit mode
            self.edit_mode = True
            self.refresh()
            
    def _cancel_changes(self):
        """Cancel changes and exit edit mode"""
        self.edit_mode = False
        self.refresh()
    
    def _save_metadata(self):
        """Save metadata changes to database"""
        if not self.project_state_manager or not self.project_state_manager.has_loaded_project():
            print("No project loaded to save")
            return
        
        try:
            current_project = self.project_state_manager.current_project
            
            # Update project with form values
            updated_fields = {}
            for key, field in self.metadata_fields.items():
                old_value = getattr(current_project, key, None)
                if isinstance(field, ft.TextField):
                    new_value = field.value or ""
                    setattr(current_project, key, new_value)
                    updated_fields[key] = {"old": old_value, "new": new_value}
                elif isinstance(field, ft.Checkbox):
                    new_value = field.value or False
                    setattr(current_project, key, new_value)
                    updated_fields[key] = {"old": old_value, "new": new_value}
                elif isinstance(field, ft.Dropdown):
                    new_value = field.value or ""
                    # Special handling for project_type: convert display name to code
                    if key == "project_type":
                        if new_value and new_value in ProjectCreationService.PROJECT_TYPE_CODES:
                            new_value = self._get_project_type_code(new_value)
                    setattr(current_project, key, new_value)
                    updated_fields[key] = {"old": old_value, "new": new_value}
            
            # Save to database
            if self.database_manager:
                try:
                    success = self.database_manager.update_project(current_project)
                    if success:
                        print("✓ Project metadata saved successfully")
                        self.edit_mode = False
                        self.refresh()
                    else:
                        # Try to create the project if update failed
                        success = self.database_manager.create_project(current_project)
                        if success:
                            print("✓ Project created successfully")
                            self.edit_mode = False
                            self.refresh()
                        else:
                            print("✗ Failed to create project")
                except Exception as db_error:
                    print(f"✗ Database error: {db_error}")
            else:
                print("✗ No database manager available")
                
        except Exception as e:
            print(f"✗ Error saving metadata: {e}")
    
    def refresh(self):
        """Refresh the tab to reflect current state"""
        # The parent will handle rebuilding the tab content
        pass
