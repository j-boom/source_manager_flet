"""
Project Metadata Tab with Configurable Fields
"""

import flet as ft
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

# Inline metadata configuration (avoiding import issues)
DEFAULT_METADATA_CONFIG = {
    'default': {
        'columns': [
            {
                'name': 'Basic Information',
                'fields': [
                    {'key': 'title', 'label': 'Project Title', 'type': 'text', 'required': True, 'tab_order': 1},
                    {'key': 'project_type', 'label': 'Project Type', 'type': 'text', 'required': True, 'tab_order': 2},
                    {'key': 'status', 'label': 'Status', 'type': 'dropdown', 'options': ['active', 'on_hold', 'completed', 'cancelled'], 'required': True, 'tab_order': 3},
                    {'key': 'created_at', 'label': 'Created Date', 'type': 'readonly', 'tab_order': 4}
                ]
            },
            {
                'name': 'Team Members',
                'fields': [
                    {'key': 'engineer', 'label': 'Engineer', 'type': 'text', 'tab_order': 5},
                    {'key': 'drafter', 'label': 'Drafter', 'type': 'text', 'tab_order': 6},
                    {'key': 'reviewer', 'label': 'Reviewer', 'type': 'text', 'tab_order': 7},
                    {'key': 'architect', 'label': 'Architect', 'type': 'text', 'tab_order': 8},
                    {'key': 'geologist', 'label': 'Geologist', 'type': 'text', 'tab_order': 9}
                ]
            },
            {
                'name': 'Project Details',
                'fields': [
                    {'key': 'description', 'label': 'Project Description', 'type': 'multiline', 'min_lines': 3, 'max_lines': 6, 'tab_order': 10},
                    {'key': 'location', 'label': 'Project Location', 'type': 'text', 'tab_order': 11},
                    {'key': 'client', 'label': 'Client', 'type': 'text', 'tab_order': 12}
                ]
            }
        ]
    },
    'commercial': {
        'columns': [
            {
                'name': 'Basic Information',
                'fields': [
                    {'key': 'title', 'label': 'Project Title', 'type': 'text', 'required': True, 'tab_order': 1},
                    {'key': 'project_type', 'label': 'Project Type', 'type': 'text', 'required': True, 'tab_order': 2},
                    {'key': 'status', 'label': 'Status', 'type': 'dropdown', 'options': ['active', 'on_hold', 'completed', 'cancelled'], 'required': True, 'tab_order': 3},
                    {'key': 'building_code', 'label': 'Building Code', 'type': 'text', 'tab_order': 4},
                    {'key': 'created_at', 'label': 'Created Date', 'type': 'readonly', 'tab_order': 5}
                ]
            },
            {
                'name': 'Team & Compliance',
                'fields': [
                    {'key': 'engineer', 'label': 'Lead Engineer', 'type': 'text', 'required': True, 'tab_order': 6},
                    {'key': 'architect', 'label': 'Architect', 'type': 'text', 'required': True, 'tab_order': 7},
                    {'key': 'reviewer', 'label': 'Code Reviewer', 'type': 'text', 'tab_order': 8},
                    {'key': 'drafter', 'label': 'CAD Drafter', 'type': 'text', 'tab_order': 9},
                    {'key': 'permit_status', 'label': 'Permit Status', 'type': 'dropdown', 'options': ['not_started', 'in_progress', 'approved', 'rejected'], 'tab_order': 10}
                ]
            },
            {
                'name': 'Project Details',
                'fields': [
                    {'key': 'client', 'label': 'Client/Owner', 'type': 'text', 'required': True, 'tab_order': 11},
                    {'key': 'location', 'label': 'Project Address', 'type': 'text', 'required': True, 'tab_order': 12},
                    {'key': 'square_footage', 'label': 'Square Footage', 'type': 'number', 'tab_order': 13},
                    {'key': 'description', 'label': 'Project Scope', 'type': 'multiline', 'min_lines': 3, 'max_lines': 6, 'tab_order': 14}
                ]
            }
        ]
    },
    'residential': {
        'columns': [
            {
                'name': 'Basic Information',
                'fields': [
                    {'key': 'title', 'label': 'Project Title', 'type': 'text', 'required': True, 'tab_order': 1},
                    {'key': 'project_type', 'label': 'Project Type', 'type': 'text', 'required': True, 'tab_order': 2},
                    {'key': 'status', 'label': 'Status', 'type': 'dropdown', 'options': ['active', 'on_hold', 'completed', 'cancelled'], 'required': True, 'tab_order': 3},
                    {'key': 'home_type', 'label': 'Home Type', 'type': 'dropdown', 'options': ['single_family', 'townhouse', 'duplex', 'custom'], 'tab_order': 4},
                    {'key': 'created_at', 'label': 'Created Date', 'type': 'readonly', 'tab_order': 5}
                ]
            },
            {
                'name': 'Team Members',
                'fields': [
                    {'key': 'engineer', 'label': 'Structural Engineer', 'type': 'text', 'tab_order': 6},
                    {'key': 'architect', 'label': 'Architect', 'type': 'text', 'tab_order': 7},
                    {'key': 'drafter', 'label': 'Drafter', 'type': 'text', 'tab_order': 8},
                    {'key': 'geologist', 'label': 'Geotechnical Engineer', 'type': 'text', 'tab_order': 9},
                    {'key': 'reviewer', 'label': 'Plan Reviewer', 'type': 'text', 'tab_order': 10}
                ]
            },
            {
                'name': 'Property Details',
                'fields': [
                    {'key': 'client', 'label': 'Homeowner', 'type': 'text', 'tab_order': 11},
                    {'key': 'location', 'label': 'Property Address', 'type': 'text', 'tab_order': 12},
                    {'key': 'lot_size', 'label': 'Lot Size (sq ft)', 'type': 'number', 'tab_order': 13},
                    {'key': 'bedrooms', 'label': 'Bedrooms', 'type': 'number', 'tab_order': 14},
                    {'key': 'bathrooms', 'label': 'Bathrooms', 'type': 'number', 'tab_order': 15},
                    {'key': 'description', 'label': 'Project Description', 'type': 'multiline', 'min_lines': 3, 'max_lines': 6, 'tab_order': 16}
                ]
            }
        ]
    }
}

def get_metadata_config(project_type: str) -> Dict[str, Any]:
    """Get metadata configuration for a specific project type"""
    return DEFAULT_METADATA_CONFIG.get(project_type, DEFAULT_METADATA_CONFIG['default'])

def create_field_widget(field_config: Dict[str, Any], value: str = '', is_edit_mode: bool = True) -> ft.Control:
    """Create a Flet widget based on field configuration with proper styling"""
    field_type = field_config.get('type', 'text')
    label = field_config.get('label', '')
    required = field_config.get('required', False)
    is_always_readonly = field_config.get('type') == 'readonly'
    
    # Add asterisk for required fields
    if required:
        label += ' *'
    
    # Determine if field should be read-only
    is_readonly = is_always_readonly or not is_edit_mode
    
    # Define colors based on edit mode
    if is_readonly:
        # Read-only styling - muted colors
        bgcolor = ft.colors.GREY_50
        border_color = ft.colors.GREY_300
        text_color = ft.colors.GREY_700
        cursor_color = None
    else:
        # Editable styling - active colors
        bgcolor = ft.colors.WHITE
        border_color = ft.colors.BLUE_400
        text_color = ft.colors.BLACK
        cursor_color = ft.colors.BLUE_600
    
    if field_type == 'text':
        return ft.TextField(
            label=label, 
            value=value, 
            expand=True,
            read_only=is_readonly,
            bgcolor=bgcolor,
            border_color=border_color,
            color=text_color,
            cursor_color=cursor_color,
            focused_border_color=ft.colors.BLUE_600 if not is_readonly else ft.colors.GREY_400,
            autofocus=False
        )
    elif field_type == 'multiline':
        return ft.TextField(
            label=label, 
            value=value, 
            multiline=True,
            min_lines=field_config.get('min_lines', 3),
            max_lines=field_config.get('max_lines', 6),
            expand=True,
            read_only=is_readonly,
            bgcolor=bgcolor,
            border_color=border_color,
            color=text_color,
            cursor_color=cursor_color,
            focused_border_color=ft.colors.BLUE_600 if not is_readonly else ft.colors.GREY_400,
            autofocus=False
        )
    elif field_type == 'dropdown':
        options = field_config.get('options', [])
        # For dropdowns in read-only mode, we need to handle differently
        # since Flet doesn't have a read-only dropdown
        if is_readonly:
            # In read-only mode, use a TextField that looks like the dropdown value
            display_value = value if value else (options[0] if options else '')
            return ft.TextField(
                label=label,
                value=display_value,
                expand=True,
                read_only=True,
                bgcolor=bgcolor,
                border_color=border_color,
                color=text_color,
                focused_border_color=ft.colors.GREY_400
            )
        else:
            # In edit mode, use normal dropdown
            return ft.Dropdown(
                label=label,
                value=value if value in options else (options[0] if options else ''),
                options=[ft.dropdown.Option(opt) for opt in options],
                expand=True,
                bgcolor=bgcolor,
                border_color=border_color,
                color=text_color,
                focused_border_color=ft.colors.BLUE_600
            )
    elif field_type == 'readonly':
        return ft.TextField(
            label=label, 
            value=value, 
            read_only=True, 
            expand=True,
            bgcolor=ft.colors.GREY_100,
            border_color=ft.colors.GREY_300,
            color=ft.colors.GREY_600,
            focused_border_color=ft.colors.GREY_400
        )
    elif field_type == 'number':
        return ft.TextField(
            label=label, 
            value=value, 
            keyboard_type=ft.KeyboardType.NUMBER, 
            expand=True,
            read_only=is_readonly,
            bgcolor=bgcolor,
            border_color=border_color,
            color=text_color,
            cursor_color=cursor_color,
            focused_border_color=ft.colors.BLUE_600 if not is_readonly else ft.colors.GREY_400,
            autofocus=False
        )
    else:  # Default to text
        return ft.TextField(
            label=label, 
            value=value, 
            expand=True,
            read_only=is_readonly,
            bgcolor=bgcolor,
            border_color=border_color,
            color=text_color,
            cursor_color=cursor_color,
            focused_border_color=ft.colors.BLUE_600 if not is_readonly else ft.colors.GREY_400,
            autofocus=False
        )


class ProjectMetadataTab:
    """Tab for viewing and editing project metadata with configurable fields"""
    
    def __init__(self, page: ft.Page, database_manager=None, project_data=None, project_path=None):
        self.page = page
        self.database_manager = database_manager
        self.project_data = project_data or {}
        self.project_path = project_path
        
        # Get project type for configuration
        self.project_type = self.project_data.get('project_type', 'default')
        
        # Dynamic field storage
        self.field_widgets = {}  # key -> widget mapping
        self.field_configs = {}  # key -> config mapping
        
        # Edit/Save mode state
        self.is_edit_mode = False
        self.is_fully_populated = False
        
        # Initialize form fields based on configuration
        self._init_configurable_fields()
        
        # Load data from database and JSON
        self._load_project_data()
        
        # Update form fields with loaded data
        self._update_form_fields()
        
        # Determine initial mode - always check completeness after loading data
        self.is_fully_populated = self._check_data_completeness()
        self.is_edit_mode = not self.is_fully_populated
        
        print(f"Initial mode check: fully_populated={self.is_fully_populated}, edit_mode={self.is_edit_mode}")
        
        # Create action button (Edit or Save)
        self.action_button = ft.ElevatedButton(
            "Edit" if self.is_fully_populated else "Save Changes",
            icon=ft.icons.EDIT if self.is_fully_populated else ft.icons.SAVE,
            on_click=self._on_action_button_click,
            style=ft.ButtonStyle(
                color=ft.colors.WHITE,
                bgcolor=ft.colors.GREEN_600 if self.is_fully_populated else ft.colors.BLUE_600
            )
        )
        
        # Error/Success message
        self.message_text = ft.Text("", color=ft.colors.GREEN_600, size=12, visible=False)
        self.error_text = ft.Text("", color=ft.colors.RED_400, size=12, visible=False)
        
        # Set initial field states
        self._update_field_states()
    
    def _load_project_data(self):
        """Load project data from JSON and database"""
        try:
            # First, map data from JSON that's already loaded in project_data
            if self.project_data:
                print(f"Initial project_data keys: {list(self.project_data.keys())}")
                
                # Map customer data to location and client fields if not already set
                if 'customer_name' in self.project_data and not self.project_data.get('location'):
                    self.project_data['location'] = self.project_data['customer_name']
                
                if 'customer_name' in self.project_data and not self.project_data.get('client'):
                    self.project_data['client'] = self.project_data['customer_name']
                
                # Set default status if not present
                if not self.project_data.get('status'):
                    self.project_data['status'] = 'active'
                
                # Ensure created_at field exists for display
                if 'created_date' in self.project_data and not self.project_data.get('created_at'):
                    self.project_data['created_at'] = self.project_data['created_date']
                
                print(f"Project data after JSON mapping: {self.project_data}")
            
            # Then load additional data from database if available
            if self.database_manager and self.project_data.get('uuid'):
                project_uuid = self.project_data.get('uuid')
                db_project = self.database_manager.get_project(project_uuid)
                
                if db_project:
                    print(f"Loading additional data from database for UUID: {project_uuid}")
                    # Convert database project to dictionary and merge with existing data
                    db_data = {
                        'uuid': db_project.uuid,
                        'title': db_project.title,
                        'project_type': db_project.project_type,
                        'engineer': db_project.engineer,
                        'drafter': db_project.drafter,
                        'reviewer': db_project.reviewer,
                        'architect': db_project.architect,
                        'geologist': db_project.geologist,
                        'project_code': db_project.project_code,
                        'description': db_project.description,
                        'status': db_project.status,
                        'created_at': db_project.created_at,
                        'updated_at': db_project.updated_at
                    }
                    
                    # Only update with database values that are not None and not empty
                    for key, value in db_data.items():
                        if value is not None and str(value).strip():
                            self.project_data[key] = value
                    
                    print(f"Project data after database merge: {self.project_data}")
            
            # Update form fields with all loaded data
            self._update_form_fields()
            
            # Update the page to reflect the changes
            if hasattr(self, 'page'):
                self.page.update()
                
        except Exception as e:
            print(f"Error loading project data: {e}")
            import traceback
            traceback.print_exc()
    
    def _check_data_completeness(self) -> bool:
        """Check if all required fields have data"""
        try:
            config = get_metadata_config(self.project_type)
            
            for column in config.get('columns', []):
                for field_config in column.get('fields', []):
                    if field_config.get('required', False):
                        field_key = field_config['key']
                        field_value = self.project_data.get(field_key, '')
                        
                        # Check if field is empty or None
                        if not field_value or str(field_value).strip() == '':
                            return False
            
            return True
            
        except Exception as e:
            print(f"Error checking data completeness: {e}")
            return False
    
    def _update_field_states(self):
        """Update field styling and states based on current mode by modifying existing widgets"""
        try:
            # Update existing widgets instead of recreating them
            for field_key, widget in self.field_widgets.items():
                field_config = self.field_configs.get(field_key, {})
                is_always_readonly = field_config.get('type') == 'readonly'
                
                # Determine if field should be read-only
                is_readonly = is_always_readonly or not self.is_edit_mode
                
                # Define colors based on edit mode and theme
                if is_readonly:
                    # Read-only styling - background color, invisible borders
                    if self.page.theme_mode == ft.ThemeMode.DARK:
                        bgcolor = ft.colors.GREY_900  # Same as dark background
                        border_color = ft.colors.GREY_900
                        text_color = ft.colors.GREY_400
                        focused_border_color = ft.colors.GREY_900
                    else:
                        bgcolor = ft.colors.GREY_50  # Same as light background
                        border_color = ft.colors.GREY_50
                        text_color = ft.colors.GREY_600
                        focused_border_color = ft.colors.GREY_50
                    cursor_color = None
                else:
                    # Editable styling - theme-appropriate colors
                    if self.page.theme_mode == ft.ThemeMode.DARK:
                        bgcolor = ft.colors.GREY_800
                        border_color = ft.colors.BLUE_400
                        text_color = ft.colors.WHITE
                        cursor_color = ft.colors.BLUE_400
                        focused_border_color = ft.colors.BLUE_300
                    else:
                        bgcolor = ft.colors.WHITE
                        border_color = ft.colors.BLUE_400
                        text_color = ft.colors.BLACK
                        cursor_color = ft.colors.BLUE_600
                        focused_border_color = ft.colors.BLUE_600
                
                # Update widget properties based on type
                if isinstance(widget, ft.TextField):
                    widget.read_only = is_readonly
                    widget.bgcolor = bgcolor
                    widget.border_color = border_color
                    widget.color = text_color
                    widget.cursor_color = cursor_color
                    widget.focused_border_color = focused_border_color
                elif isinstance(widget, ft.Dropdown):
                    widget.disabled = is_readonly
                    widget.bgcolor = bgcolor
                    widget.border_color = border_color
                    widget.color = text_color
                    widget.focused_border_color = focused_border_color
            
            # Update the page to reflect changes
            if hasattr(self, 'page'):
                self.page.update()
            
            print(f"Updated field states: edit_mode={self.is_edit_mode}")
            
        except Exception as e:
            print(f"Error updating field states: {e}")
    
    def _rebuild_layout(self):
        """Rebuild the entire layout with updated field widgets"""
        # Not needed with the new approach - we update widgets in place
        pass
    
    def _build_layout_content(self) -> ft.Control:
        """Build the layout content with current field widgets"""
        try:
            # Get configuration for project type
            config = get_metadata_config(self.project_type)
            columns = config.get('columns', [])
            
            # Create column layout
            column_controls = []
            
            for i, column_config in enumerate(columns):
                column_name = column_config.get('name', f'Column {i+1}')
                column_fields = column_config.get('fields', [])
                
                # Create field containers for this column - wrap in GestureDetector for better click handling
                field_containers = []
                for field_config in column_fields:
                    field_key = field_config.get('key')
                    if field_key in self.field_widgets:
                        widget = self.field_widgets[field_key]
                        
                        # Wrap in GestureDetector to handle clicks properly
                        if not getattr(widget, 'read_only', False) and not getattr(widget, 'disabled', False):
                            gesture_detector = ft.GestureDetector(
                                content=widget,
                                on_tap=lambda e, w=widget: w.focus()
                            )
                            field_containers.append(gesture_detector)
                        else:
                            field_containers.append(widget)
                
                # Create column card with equal height - minimal nesting and no click interference
                column_card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(column_name, size=16, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700),
                            ft.Container(height=10),
                            *field_containers,
                            # Add flexible spacer to fill remaining height
                            ft.Container(expand=True)
                        ], spacing=10, expand=True),  # Add spacing between fields
                        padding=ft.padding.all(15),
                        expand=True,
                        # Ensure container doesn't interfere with child clicks
                        ink=False
                    ),
                    expand=True,
                    # Ensure card doesn't interfere with child clicks
                    elevation=1,
                    surface_tint_color=None
                )
                
                column_controls.append(column_card)
            
            # Create rows of columns (max 3 columns per row) with equal heights
            column_rows = []
            for i in range(0, len(column_controls), 3):
                row_columns = column_controls[i:i+3]
                column_rows.append(
                    ft.Row(
                        controls=row_columns,
                        spacing=15,
                        expand=True,
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.STRETCH  # This ensures equal heights
                    )
                )
            
            # Return the complete layout content
            return ft.Column([
                # Action button (Edit or Save) with mode indicator
                ft.Container(
                    content=ft.Column([
                        # Mode indicator
                        ft.Container(
                            content=ft.Row([
                                ft.Container(expand=True),  # Spacer
                                self.action_button
                            ]),
                            padding=ft.padding.symmetric(horizontal=5)
                        ),
                        # Warning for incomplete data
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.icons.WARNING, size=16, color=ft.colors.ORANGE_600),
                                ft.Text(
                                    "Please complete all required fields (*) before navigating to other tabs.",
                                    size=12,
                                    color=ft.colors.ORANGE_600
                                )
                            ]),
                            visible=not self.is_fully_populated,
                            padding=ft.padding.symmetric(horizontal=5, vertical=5)
                        )
                    ]),
                    padding=ft.padding.only(bottom=20)
                ),
                
                # Form content in scrollable container - configurable column layout
                ft.Container(
                    content=ft.Column([
                        *column_rows,
                        
                        # Messages
                        self.message_text,
                        self.error_text,
                        
                    ], spacing=15),  # Removed scroll mode to test focus
                    expand=True
                )
            ], spacing=0)
            
        except Exception as e:
            print(f"Error building layout content: {e}")
            return ft.Text("Error building layout", color=ft.colors.RED)
    
    def _on_action_button_click(self, e):
        """Handle Edit/Save button click"""
        if self.is_edit_mode:
            # Save mode - validate and save data
            self._save_metadata(e)
        else:
            # Edit mode - switch to edit mode
            self.is_edit_mode = True
            self.action_button.text = "Save Changes"
            self.action_button.icon = ft.icons.SAVE
            self.action_button.style = ft.ButtonStyle(
                color=ft.colors.WHITE,
                bgcolor=ft.colors.BLUE_600
            )
            self._update_field_states()  # This will rebuild the layout
            # No need to call page.update() here as _rebuild_layout() handles it
    
    def can_navigate_away(self) -> bool:
        """Check if user can navigate away from this tab"""
        if not self.is_fully_populated:
            # If data is not complete, don't allow navigation
            self._show_error("Please complete all required fields before continuing.")
            return False
        return True
    
    def _init_configurable_fields(self):
        """Initialize form fields based on metadata configuration"""
        try:
            # Get configuration for project type
            config = get_metadata_config(self.project_type)
            
            # Create widgets for each field
            for column in config['columns']:
                for field_config in column['fields']:
                    field_key = field_config['key']
                    field_value = self.project_data.get(field_key, '')
                    
                    # Create widget based on configuration with current edit mode
                    widget = create_field_widget(field_config, field_value, self.is_edit_mode)
                    
                    # Store widget and config
                    self.field_widgets[field_key] = widget
                    self.field_configs[field_key] = field_config
                    
        except Exception as e:
            print(f"Error initializing configurable fields: {e}")
            # Fallback to basic fields if configuration fails
            self._init_fallback_fields()
    
    def _init_fallback_fields(self):
        """Fallback field initialization if configuration fails"""
        # Basic fallback fields
        basic_fields = [
            ('title', 'Project Title', 'text'),
            ('project_type', 'Project Type', 'text'),
            ('status', 'Status', 'dropdown'),
            ('description', 'Description', 'multiline')
        ]
        
        for key, label, field_type in basic_fields:
            value = self.project_data.get(key, '')
            
            if field_type == 'text':
                widget = ft.TextField(label=label, value=value, expand=True)
            elif field_type == 'dropdown':
                widget = ft.Dropdown(
                    label=label,
                    value=value if value else 'active',
                    options=[ft.dropdown.Option(opt) for opt in ['active', 'on_hold', 'completed', 'cancelled']],
                    expand=True
                )
            elif field_type == 'multiline':
                widget = ft.TextField(label=label, value=value, multiline=True, min_lines=3, max_lines=6, expand=True)
            else:
                widget = ft.TextField(label=label, value=value, expand=True)
            
            self.field_widgets[key] = widget
            self.field_configs[key] = {'key': key, 'label': label, 'type': field_type}
    
    def build(self) -> ft.Control:
        """Build the metadata tab content with configurable three-column layout"""
        try:
            # Store the layout container for rebuilding
            self.layout_container = ft.Container(
                content=self._build_layout_content(),
                padding=ft.padding.all(20),
                expand=True
            )
            
            return self.layout_container
            
        except Exception as e:
            print(f"Error building metadata tab: {e}")
            # Fallback to simple layout
            return self._build_fallback_layout()
    
    def refresh_layout(self):
        """Refresh the layout after field state changes"""
        self._update_field_states()  # This will rebuild the layout
    
    def _build_fallback_layout(self) -> ft.Control:
        """Build a simple fallback layout if configuration fails"""
        return ft.Container(
            content=ft.Column([
                ft.Text("Error loading metadata configuration. Using basic layout.", 
                       color=ft.colors.ORANGE_600, size=14),
                ft.Container(height=20),
                
                # Save button
                ft.Container(
                    content=ft.Row([
                        ft.Container(expand=True),
                        ft.ElevatedButton(
                            "Save Changes",
                            icon=ft.icons.SAVE,
                            on_click=self._save_metadata,
                            style=ft.ButtonStyle(
                                color=ft.colors.WHITE,
                                bgcolor=ft.colors.BLUE_600
                            )
                        )
                    ]),
                    padding=ft.padding.only(bottom=20)
                ),
                
                # Basic fields
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Basic Fields", size=16, weight=ft.FontWeight.BOLD),
                            ft.Container(height=10),
                            *[ft.Container(
                                content=widget,
                                padding=ft.padding.symmetric(vertical=5)
                            ) for widget in self.field_widgets.values()]
                        ]),
                        padding=ft.padding.all(15)
                    )
                ),
                
                # Messages
                self.message_text,
                self.error_text,
            ], spacing=15),  # Removed scroll mode to test focus
            padding=ft.padding.all(20),
            expand=True
        )
    
    def _save_metadata(self, e):
        """Save the metadata changes using configurable fields"""
        try:
            # Collect form data from all field widgets
            updated_data = {}
            
            for field_key, widget in self.field_widgets.items():
                if hasattr(widget, 'value'):
                    updated_data[field_key] = widget.value
            
            # Add timestamp
            updated_data['updated_at'] = datetime.now().isoformat()
            
            # Update the project data
            self.project_data.update(updated_data)
            
            # Validate required fields
            if not self._validate_required_fields():
                return  # Error message already shown
            
            # Save to database if available
            if self.database_manager and self.project_data.get('uuid'):
                print(f"Attempting database save for project: {self.project_data.get('uuid')}")
                # Update project in database
                success = self._update_database_project(updated_data)
                if not success:
                    self._show_error("Failed to update project in database")
                    return
                else:
                    print("Database save successful")
            else:
                print(f"Skipping database save - manager: {bool(self.database_manager)}, uuid: {self.project_data.get('uuid')}")
            
            # Save to JSON file if available
            if self.project_path:
                success = self._save_json_file()
                if not success:
                    self._show_error("Failed to save project file")
                    return
            
            # Check if data is now complete
            self.is_fully_populated = self._check_data_completeness()
            
            # Switch to view mode if data is complete
            if self.is_fully_populated:
                self.is_edit_mode = False
                self.action_button.text = "Edit"
                self.action_button.icon = ft.icons.EDIT
                self.action_button.style = ft.ButtonStyle(
                    color=ft.colors.WHITE,
                    bgcolor=ft.colors.GREEN_600
                )
                self._update_field_states()  # This will rebuild the layout
            
            # No need to call page.update() here as _rebuild_layout() handles it
            
        except Exception as ex:
            self._show_error(f"Error saving metadata: {str(ex)}")
    
    def _validate_required_fields(self) -> bool:
        """Validate that all required fields have values"""
        try:
            config = get_metadata_config(self.project_type)
            missing_fields = []
            
            for column in config.get('columns', []):
                for field_config in column.get('fields', []):
                    if field_config.get('required', False):
                        field_key = field_config['key']
                        widget = self.field_widgets.get(field_key)
                        
                        if widget and hasattr(widget, 'value'):
                            value = widget.value
                            if not value or str(value).strip() == '':
                                missing_fields.append(field_config.get('label', field_key))
            
            if missing_fields:
                self._show_error(f"Please fill in all required fields: {', '.join(missing_fields)}")
                return False
            
            return True
            
        except Exception as e:
            self._show_error(f"Error validating fields: {str(e)}")
            return False
    
    def _update_database_project(self, updated_data: Dict[str, Any]) -> bool:
        """Update project in database"""
        try:
            if not self.database_manager:
                print("No database manager available")
                return False
            
            # Get project by UUID
            project_uuid = self.project_data.get('uuid')
            if not project_uuid:
                print("No project UUID found in project data")
                return False
            
            print(f"Attempting to update project with UUID: {project_uuid}")
            
            # First check if project exists in database
            existing_project = self.database_manager.get_project(project_uuid)
            if not existing_project:
                print(f"Project with UUID {project_uuid} not found in database")
                return False
            
            print(f"Found existing project: {existing_project.title}")
            
            # Update project in database using the new update_project method
            success = self.database_manager.update_project(project_uuid, updated_data)
            print(f"Database update result: {success}")
            return success
            
        except Exception as ex:
            print(f"Database update error: {ex}")
            import traceback
            traceback.print_exc()
            return False
    
    def _save_json_file(self) -> bool:
        """Save updated data to JSON file"""
        try:
            if not self.project_path:
                return False
            
            # Read current file
            with open(self.project_path, 'r') as f:
                file_data = json.load(f)
            
            # Update with new metadata
            file_data.update(self.project_data)
            
            # Write back to file
            with open(self.project_path, 'w') as f:
                json.dump(file_data, f, indent=4)
            
            return True
            
        except Exception as ex:
            print(f"JSON file save error: {ex}")
            return False
    
    def _show_message(self, message: str):
        """Show success message"""
        self.message_text.value = message
        self.message_text.visible = True
        self.error_text.visible = False
        self.page.update()
    
    def _show_error(self, error: str):
        """Show error message"""
        self.error_text.value = error
        self.error_text.visible = True
        self.message_text.visible = False
        self.page.update()
    
    def update_project_data(self, project_data: Dict[str, Any], project_path: str):
        """Update the tab with new project data"""
        self.project_data = project_data or {}
        self.project_path = project_path
        
        # Check if project type changed
        new_project_type = self.project_data.get('project_type', 'default')
        if new_project_type != self.project_type:
            self.project_type = new_project_type
            # Reinitialize fields with new configuration
            self._init_configurable_fields()
        
        # Load fresh data from database
        self._load_project_data()
        
        # Update form fields with new data
        self._update_form_fields()
        
        # Re-check data completeness and update mode - force edit mode if incomplete
        self.is_fully_populated = self._check_data_completeness()
        self.is_edit_mode = not self.is_fully_populated
        
        print(f"Updated mode check: fully_populated={self.is_fully_populated}, edit_mode={self.is_edit_mode}")
        
        # Update action button
        self.action_button.text = "Edit" if self.is_fully_populated else "Save Changes"
        self.action_button.icon = ft.icons.EDIT if self.is_fully_populated else ft.icons.SAVE
        self.action_button.style = ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=ft.colors.GREEN_600 if self.is_fully_populated else ft.colors.BLUE_600
        )
        
        # Update field states
        self._update_field_states()
    
    def _update_form_fields(self):
        """Update form fields with current project data using configurable fields"""
        try:
            print(f"Updating form fields with data: {self.project_data}")
            updated_count = 0
            
            for field_key, widget in self.field_widgets.items():
                if hasattr(widget, 'value'):
                    # Get the value from project data
                    field_value = self.project_data.get(field_key, '')
                    
                    # Handle special cases for different widget types
                    if isinstance(widget, ft.Dropdown):
                        # For dropdowns, ensure the value is in the options
                        options = [opt.key for opt in widget.options] if widget.options else []
                        if field_value not in options and options:
                            field_value = options[0]  # Default to first option
                    
                    # Only update if the value has changed
                    if widget.value != field_value:
                        widget.value = field_value
                        updated_count += 1
                        print(f"Updated field '{field_key}' with value: '{field_value}'")
            
            print(f"Updated {updated_count} form fields")
                    
        except Exception as e:
            print(f"Error updating form fields: {e}")
            import traceback
            traceback.print_exc()
    
    def refresh_data(self):
        """Refresh the tab data"""
        # Update form fields and refresh UI
        self._update_form_fields()
        if hasattr(self, 'page'):
            self.page.update()
    
    def _focus_field(self, widget):
        """Focus a field widget when its container is clicked"""
        try:
            if hasattr(widget, 'focus') and callable(widget.focus):
                widget.focus()
                if hasattr(self, 'page'):
                    self.page.update()
        except Exception as e:
            print(f"Error focusing field: {e}")
