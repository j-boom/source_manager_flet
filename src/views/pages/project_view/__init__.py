"""
Project View - Main project management interface with three tabs
"""

import flet as ft
from views.base_view import BaseView
from services.project_creation_service import ProjectCreationService
from typing import Optional, Callable


class ProjectView(BaseView):
    """Project management view with three tabs: Metadata, Sources, and Slide Assignments"""
    
    def __init__(self, page: ft.Page, theme_manager=None, database_manager=None, project_state_manager=None, on_navigate=None):
        super().__init__(page)
        self.theme_manager = theme_manager
        self.database_manager = database_manager
        self.project_state_manager = project_state_manager
        self.on_navigate = on_navigate
        
        # Tab index
        self.current_tab_index = 0
        
        # UI components
        self.header_container = None
        self.tabs_container = None
        self.content_container = None
        
    def build(self) -> ft.Control:
        """Build the project view with tabs"""
        return ft.Column([
            self._build_header(),
            self._build_tabs(),
            self._build_content()
        ], expand=True, spacing=0)
    
    def _build_header(self) -> ft.Control:
        """Build header with project title and back button"""
        # Get project info if available
        project_title = "No Project Loaded"
        if self.project_state_manager and self.project_state_manager.has_loaded_project():
            project_title = self.project_state_manager.get_project_title()
        
        # Theme-aware colors
        if self.page.theme_mode == ft.ThemeMode.DARK:
            header_bg = ft.colors.GREY_800
            border_color = ft.colors.GREY_600
        else:
            header_bg = ft.colors.WHITE
            border_color = ft.colors.GREY_300
        
        # Get theme color for back button
        theme_color = self._get_theme_color()
        
        # Create subtitle text with reference for easy updating
        self.subtitle_text = ft.Text(project_title, size=14, color=ft.colors.GREY_600)
        
        self.header_container = ft.Container(
            content=ft.Row([
                ft.ElevatedButton(
                    "Back",
                    icon=ft.icons.ARROW_BACK,
                    on_click=lambda e: self._on_back_clicked(),
                    style=ft.ButtonStyle(
                        bgcolor=theme_color,
                        color=ft.colors.WHITE
                    )
                ),
                ft.Container(expand=True),
                ft.Column([
                    ft.Text("Project View", size=20, weight=ft.FontWeight.BOLD),
                    self.subtitle_text
                ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.END)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.all(20),
            bgcolor=header_bg,
            border=ft.border.only(bottom=ft.BorderSide(1, border_color))
        )
        
        return self.header_container
    
    def _build_tabs(self) -> ft.Control:
        """Build tab navigation"""
        # Theme-aware colors
        if self.page.theme_mode == ft.ThemeMode.DARK:
            tab_bg = ft.colors.GREY_900
            border_color = ft.colors.GREY_600
        else:
            tab_bg = ft.colors.GREY_50
            border_color = ft.colors.GREY_300
        
        theme_color = self._get_theme_color()
        
        # Create tab buttons
        tabs = [
            ("Metadata", ft.icons.EDIT, 0),
            ("Sources", ft.icons.FOLDER_OPEN, 1),
            ("Slide Assignments", ft.icons.SLIDESHOW, 2)
        ]
        
        tab_buttons = []
        for title, icon, index in tabs:
            is_selected = index == self.current_tab_index
            
            button_style = ft.ButtonStyle(
                bgcolor=theme_color if is_selected else ft.colors.TRANSPARENT,
                color=ft.colors.WHITE if is_selected else None,
                padding=ft.padding.symmetric(horizontal=20, vertical=15)
            )
            
            tab_button = ft.ElevatedButton(
                content=ft.Row([
                    ft.Icon(icon, size=16),
                    ft.Text(title)
                ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                style=button_style,
                on_click=lambda e, idx=index: self._on_tab_clicked(idx)
            )
            
            tab_buttons.append(tab_button)
        
        self.tabs_container = ft.Container(
            content=ft.Row(tab_buttons, spacing=5),
            padding=ft.padding.all(20),
            bgcolor=tab_bg,
            border=ft.border.only(bottom=ft.BorderSide(1, border_color))
        )
        
        return self.tabs_container
    
    def _build_content(self) -> ft.Control:
        """Build tab content area"""
        self.content_container = ft.Container(
            content=self._get_tab_content(self.current_tab_index),
            padding=ft.padding.all(20),
            expand=True
        )
        
        return self.content_container
    
    def _get_tab_content(self, tab_index: int) -> ft.Control:
        """Get content for specific tab"""
        if tab_index == 0:
            return self._build_metadata_tab()
        elif tab_index == 1:
            return self._build_sources_tab()
        elif tab_index == 2:
            return self._build_slide_assignments_tab()
        else:
            return ft.Text("Invalid tab")
    
    def _build_metadata_tab(self) -> ft.Control:
        """Build metadata editing tab with three columns"""
        # Get project info if available
        project_info = {}
        if self.project_state_manager and self.project_state_manager.has_loaded_project():
            project_info = self.project_state_manager.get_project_info()
        
        # Initialize edit mode state
        if not hasattr(self, 'edit_mode'):
            self.edit_mode = False
        
        # Store field references for easy access
        if not hasattr(self, 'metadata_fields'):
            self.metadata_fields = {}
        
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
                        on_click=lambda e: self._cancel_metadata_changes(),
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.RED_600,
                            color=ft.colors.WHITE
                        )
                    ) if self.edit_mode else None,
                ] if control is not None
            ], spacing=10),
            
            ft.Container(height=20),
            
            # Three-column layout with improved alignment
            ft.Row([
                # Column 1: Basic Information (width: 280px)
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
                    ], spacing=15, tight=True),
                    width=280,
                    alignment=ft.alignment.top_left
                ),
                
                # Spacer between columns
                ft.Container(width=40),
                
                # Column 2: Team Information (width: 280px)
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
                
                # Spacer between columns
                ft.Container(width=40),
                
                # Column 3: Requestor Information (width: 280px)
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
                        # Add invisible container to match height of other columns
                        ft.Container(height=56),  # Approximate height of one text field
                    ], spacing=15, tight=True),
                    width=280,
                    alignment=ft.alignment.top_left
                ),
                
            ], alignment=ft.MainAxisAlignment.START, 
               vertical_alignment=ft.CrossAxisAlignment.START,
               spacing=0),
            
        ], spacing=5, scroll=ft.ScrollMode.AUTO)
    
    def _build_sources_tab(self) -> ft.Control:
        """Build sources management tab"""
        return ft.Column([
            ft.Text("Source Management", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            
            # Source management controls
            ft.Row([
                ft.ElevatedButton(
                    "Add Source Manually",
                    icon=ft.icons.ADD,
                    on_click=lambda e: self._add_source_manually(),
                    style=ft.ButtonStyle(
                        bgcolor=self._get_theme_color(),
                        color=ft.colors.WHITE
                    )
                ),
                ft.ElevatedButton(
                    "Import Sources",
                    icon=ft.icons.UPLOAD_FILE,
                    on_click=lambda e: self._import_sources()
                ),
                ft.ElevatedButton(
                    "Scan Directory",
                    icon=ft.icons.FOLDER_OPEN,
                    on_click=lambda e: self._scan_directory()
                )
            ], spacing=10),
            
            ft.Container(height=20),
            
            # Sources list (placeholder)
            ft.Container(
                content=ft.Column([
                    ft.Text("Sources will be listed here", size=14, color=ft.colors.GREY_600),
                    ft.Text("• Add sources manually", size=12, color=ft.colors.GREY_500),
                    ft.Text("• Import from other projects", size=12, color=ft.colors.GREY_500),
                    ft.Text("• Scan project directories", size=12, color=ft.colors.GREY_500),
                ], spacing=5),
                padding=ft.padding.all(20),
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=5,
                height=300
            )
            
        ], spacing=5, scroll=ft.ScrollMode.AUTO)
    
    def _build_slide_assignments_tab(self) -> ft.Control:
        """Build slide assignments tab"""
        return ft.Column([
            ft.Text("Slide Assignments", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            
            # Slide assignment controls
            ft.Row([
                ft.ElevatedButton(
                    "Add Slide",
                    icon=ft.icons.ADD_BOX,
                    on_click=lambda e: self._add_slide(),
                    style=ft.ButtonStyle(
                        bgcolor=self._get_theme_color(),
                        color=ft.colors.WHITE
                    )
                ),
                ft.ElevatedButton(
                    "Assign Sources",
                    icon=ft.icons.ASSIGNMENT,
                    on_click=lambda e: self._assign_sources()
                ),
                ft.ElevatedButton(
                    "Generate Report",
                    icon=ft.icons.DESCRIPTION,
                    on_click=lambda e: self._generate_report()
                )
            ], spacing=10),
            
            ft.Container(height=20),
            
            # Slide assignments list (placeholder)
            ft.Container(
                content=ft.Column([
                    ft.Text("Slide assignments will be shown here", size=14, color=ft.colors.GREY_600),
                    ft.Text("• Create slide definitions", size=12, color=ft.colors.GREY_500),
                    ft.Text("• Assign sources to slides", size=12, color=ft.colors.GREY_500),
                    ft.Text("• Generate assignment reports", size=12, color=ft.colors.GREY_500),
                ], spacing=5),
                padding=ft.padding.all(20),
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=5,
                height=300
            )
            
        ], spacing=5, scroll=ft.ScrollMode.AUTO)
    
    def _get_theme_color(self):
        """Get the current theme color"""
        if self.theme_manager:
            # Get the accent color or use a default
            if hasattr(self.theme_manager, 'get_accent_color'):
                return self.theme_manager.get_accent_color()
            else:
                return ft.colors.BLUE_700
        return ft.colors.BLUE_700
    
    def _on_back_clicked(self):
        """Handle back button click"""
        if self.on_navigate:
            self.on_navigate("home")
    
    def _on_tab_clicked(self, tab_index: int):
        """Handle tab selection"""
        self.current_tab_index = tab_index
        
        # Rebuild the tab buttons with new selection
        self._rebuild_tab_buttons()
        
        # Update content
        if self.content_container:
            self.content_container.content = self._get_tab_content(tab_index)
        
        self.page.update()
    
    def _rebuild_tab_buttons(self):
        """Rebuild tab buttons with current selection state"""
        if not self.tabs_container:
            return
            
        # Theme-aware colors
        theme_color = self._get_theme_color()
        
        # Create tab buttons
        tabs = [
            ("Metadata", ft.icons.EDIT, 0),
            ("Sources", ft.icons.FOLDER_OPEN, 1),
            ("Slide Assignments", ft.icons.SLIDESHOW, 2)
        ]
        
        tab_buttons = []
        for title, icon, index in tabs:
            is_selected = index == self.current_tab_index
            
            button_style = ft.ButtonStyle(
                bgcolor=theme_color if is_selected else ft.colors.TRANSPARENT,
                color=ft.colors.WHITE if is_selected else None,
                padding=ft.padding.symmetric(horizontal=20, vertical=15)
            )
            
            tab_button = ft.ElevatedButton(
                content=ft.Row([
                    ft.Icon(icon, size=16),
                    ft.Text(title)
                ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                style=button_style,
                on_click=lambda e, idx=index: self._on_tab_clicked(idx)
            )
            
            tab_buttons.append(tab_button)
        
        # Update the tab container content
        if (self.tabs_container and 
            hasattr(self.tabs_container, 'content') and 
            self.tabs_container.content and
            hasattr(self.tabs_container.content, 'controls')):
            self.tabs_container.content.controls = tab_buttons

    def get_content(self) -> ft.Control:
        """Get the view content"""
        return self.build()
    
    def refresh_theme(self):
        """Refresh theme colors"""
        # For theme refresh, just rebuild the entire view
        self.page.update()
    
    # Placeholder methods for tab functionality
    def _create_text_field(self, key: str, label: str, value: str, width: int = 300, hint_text: str = "") -> ft.TextField:
        """Create a text field with edit mode support and visual indicators"""
        # Get theme-appropriate colors for edit mode
        edit_mode = getattr(self, 'edit_mode', False)
        
        if edit_mode:
            # Use theme color for edit mode indication
            theme_color = self._get_theme_color()
            if self.page.theme_mode == ft.ThemeMode.DARK:
                # Lighter version for dark mode
                bgcolor = ft.colors.with_opacity(0.1, theme_color)
                border_color = theme_color
            else:
                # Subtle tint for light mode
                bgcolor = ft.colors.with_opacity(0.05, theme_color)
                border_color = theme_color
        else:
            # Standard colors for read-only mode
            bgcolor = None
            border_color = ft.colors.GREY_400
        
        field = ft.TextField(
            label=label,
            value=value,
            width=width,
            hint_text=hint_text,
            read_only=not edit_mode,
            bgcolor=bgcolor,
            border_color=border_color,
            focused_border_color=self._get_theme_color() if edit_mode else None
        )
        
        # Store field reference for later access
        if not hasattr(self, 'metadata_fields'):
            self.metadata_fields = {}
        self.metadata_fields[key] = field
        
        return field
    
    def _create_checkbox_field(self, key: str, label: str, value: bool) -> ft.Checkbox:
        """Create a checkbox field with edit mode support"""
        field = ft.Checkbox(
            label=label,
            value=value,
            disabled=not getattr(self, 'edit_mode', False)
        )
        
        # Store field reference for later access
        if not hasattr(self, 'metadata_fields'):
            self.metadata_fields = {}
        self.metadata_fields[key] = field
        
        return field
    
    def _create_dropdown_field(self, key: str, label: str, value: str, options: list, width: int = 300) -> ft.Dropdown:
        """Create a dropdown field with edit mode support and visual indicators"""
        # Get theme-appropriate colors for edit mode
        edit_mode = getattr(self, 'edit_mode', False)
        
        if edit_mode:
            # Use solid theme color for edit mode indication (not translucent)
            theme_color = self._get_theme_color()
            border_color = theme_color
            bgcolor = None  # Keep background solid/default
        else:
            bgcolor = None
            border_color = ft.colors.GREY_400
        
        # Create dropdown options
        dropdown_options = [ft.dropdown.Option(option) for option in options]
        
        field = ft.Dropdown(
            label=label,
            value=value,
            width=width,
            options=dropdown_options,
            disabled=not edit_mode,
            bgcolor=bgcolor,
            border_color=border_color,
            focused_border_color=self._get_theme_color() if edit_mode else None
        )
        
        # Store field reference for later access
        if not hasattr(self, 'metadata_fields'):
            self.metadata_fields = {}
        self.metadata_fields[key] = field
        
        return field

    def _toggle_edit_mode(self):
        """Toggle between edit and read-only mode"""
        if not hasattr(self, 'edit_mode'):
            self.edit_mode = False
        
        if self.edit_mode:
            # Save changes
            self._save_metadata()
        else:
            # Enter edit mode
            self.edit_mode = True
            self._update_field_edit_state()
            
        # Rebuild the metadata tab to reflect new state
        if self.content_container:
            self.content_container.content = self._get_tab_content(self.current_tab_index)
        self.page.update()
    
    def _update_field_edit_state(self):
        """Update the read-only state and visual appearance of all metadata fields"""
        # Rebuild the metadata tab to update colors and states
        if self.content_container:
            self.content_container.content = self._get_tab_content(self.current_tab_index)
        self.page.update()
    
    def _save_metadata(self):
        """Save metadata changes to database"""
        if not self.project_state_manager or not self.project_state_manager.has_loaded_project():
            print("No project loaded to save")
            return
        
        if not hasattr(self, 'metadata_fields'):
            print("No metadata fields to save")
            return
        
        try:
            # Get current project
            current_project = self.project_state_manager.current_project
            print(f"Saving metadata for project: {current_project}")
            
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
            
            print(f"Updated fields: {updated_fields}")
            
            # Save to database if database manager is available
            if self.database_manager:
                print("Attempting to save to database...")
                try:
                    success = self.database_manager.update_project(current_project)
                    if success:
                        print("✓ Project metadata saved successfully")
                        # Exit edit mode
                        self.edit_mode = False
                        self._update_field_edit_state()
                        # Update header with new project title
                        self._update_header()
                    else:
                        print("✗ Failed to save project metadata - database operation failed")
                        print("Trying to create project instead...")
                        # Try to create the project if update failed
                        success = self.database_manager.create_project(current_project)
                        if success:
                            print("✓ Project created successfully")
                            self.edit_mode = False
                            self._update_field_edit_state()
                            self._update_header()
                        else:
                            print("✗ Failed to create project as well")
                except Exception as db_error:
                    print(f"✗ Database error: {db_error}")
                    import traceback
                    traceback.print_exc()
            else:
                print("✗ No database manager available")
                
        except Exception as e:
            print(f"✗ Error saving metadata: {e}")
            import traceback
            traceback.print_exc()
    
    def _cancel_metadata_changes(self):
        """Cancel metadata changes and revert to read-only mode"""
        self.edit_mode = False
        
        # Reload the tab to reset form values
        if self.content_container:
            self.content_container.content = self._get_tab_content(self.current_tab_index)
        self.page.update()
    
    def _update_header(self):
        """Update the header with current project title"""
        if not self.project_state_manager:
            return
        
        # Get updated project title
        project_title = "No Project Loaded"
        if self.project_state_manager.has_loaded_project():
            project_title = self.project_state_manager.get_project_title()
        
        # Update the subtitle text if we have a reference to it
        if hasattr(self, 'subtitle_text') and self.subtitle_text:
            self.subtitle_text.value = project_title
            self.page.update()
        else:
            print("Could not find subtitle text reference")

    # Placeholder methods for Sources tab functionality
    def _add_source_manually(self):
        """Add a source manually"""
        print("Add source manually - to be implemented")
    
    def _import_sources(self):
        """Import sources from external systems"""
        print("Import sources - to be implemented")
    
    def _scan_directory(self):
        """Scan directory for sources"""
        print("Scan directory - to be implemented")
    
    # Placeholder methods for Slide Assignments tab functionality
    def _add_slide(self):
        """Add a new slide"""
        print("Add slide - to be implemented")
    
    def _assign_sources(self):
        """Assign sources to slides"""
        print("Assign sources - to be implemented")
    
    def _generate_report(self):
        """Generate assignment report"""
        print("Generate report - to be implemented")
    
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
    
    def refresh_project_data(self):
        """Refresh the view when project data changes"""
        if self.content_container:
            self.content_container.content = self._get_tab_content(self.current_tab_index)
            self.page.update()
