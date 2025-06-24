"""
Project Metadata Tab with Configurable Fields
"""

import flet as ft
import json
import uuid
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from config.project_types_config import (
    get_project_type_config, 
    get_fields_by_column_group, 
    create_field_widget as create_typed_field_widget,
    validate_field_value,
    get_metadata_fields_for_project_type,
    DIALOG_COLLECTED_FIELDS
)

# Simple fallback configuration for backward compatibility
FALLBACK_METADATA_CONFIG = {
    'default': {
        'columns': [
            {
                'name': 'Basic Information',
                'fields': [
                    {'key': 'title', 'label': 'Project Title', 'type': 'text', 'required': True, 'tab_order': 1},
                    {'key': 'project_type', 'label': 'Project Type', 'type': 'text', 'required': True, 'tab_order': 2},
                    {'key': 'status', 'label': 'Status', 'type': 'dropdown', 'options': ['active', 'on_hold', 'completed', 'cancelled'], 'required': True, 'tab_order': 3},
                    {'key': 'description', 'label': 'Project Description', 'type': 'multiline', 'min_lines': 3, 'max_lines': 6, 'tab_order': 4}
                ]
            }
        ]
    }
}

def get_metadata_config(project_type: str) -> Dict[str, Any]:
    """Get metadata configuration for a specific project type using only metadata fields (excluding dialog fields)"""
    try:
        # Get metadata-only fields (excluding dialog-collected fields)
        metadata_fields = get_metadata_fields_for_project_type(project_type)
        if metadata_fields:
            # Convert to the old format for backward compatibility
            field_groups = get_fields_by_column_group(metadata_fields)
            
            columns = []
            for group_name, fields in field_groups.items():
                column = {
                    'name': group_name,
                    'fields': []
                }
                
                for field in fields:
                    # Skip fields that are hidden or collected in dialog
                    if hasattr(field, 'visible') and field.visible == False:
                        continue
                    if field.name in DIALOG_COLLECTED_FIELDS:
                        continue
                        
                    field_dict = {
                        'key': field.name,
                        'label': field.label,
                        'type': field.field_type.value,
                        'required': field.required,
                        'tab_order': field.tab_order
                    }
                    
                    if hasattr(field, 'options') and field.options:
                        field_dict['options'] = field.options
                    if hasattr(field, 'min_lines') and field.min_lines:
                        field_dict['min_lines'] = field.min_lines
                    if hasattr(field, 'max_lines') and field.max_lines:
                        field_dict['max_lines'] = field.max_lines
                    
                    column['fields'].append(field_dict)
                
                # Only add columns that have fields
                if column['fields']:
                    columns.append(column)
            
            return {'columns': columns}
    
    except Exception as e:
        print(f"Warning: Could not load project type config for {project_type}: {e}")
    
    # Fallback to simple default config with only metadata fields
    return {
        'columns': [
            {
                'name': 'Basic Information',
                'fields': [
                    {'key': 'request_year', 'label': 'Request Year', 'type': 'dropdown', 'options': [str(year) for year in range(2019, 2031)], 'required': True, 'tab_order': 1},
                    {'key': 'status', 'label': 'Status', 'type': 'dropdown', 'options': ['active', 'on_hold', 'completed', 'cancelled'], 'required': False, 'tab_order': 2},
                    {'key': 'description', 'label': 'Project Description', 'type': 'multiline', 'min_lines': 3, 'max_lines': 6, 'tab_order': 3}
                ]
            }
        ]
    }

def create_field_widget(field_config: Dict[str, Any], value: str = '', is_edit_mode: bool = True, page: Optional[ft.Page] = None) -> ft.Control:
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
    
    # Define colors based on edit mode and theme
    is_dark = page and page.theme_mode == ft.ThemeMode.DARK
    
    if is_readonly:
        # Read-only styling - muted colors
        if is_dark:
            bgcolor = ft.colors.GREY_800
            border_color = ft.colors.GREY_700
            text_color = ft.colors.GREY_400
        else:
            bgcolor = ft.colors.GREY_50
            border_color = ft.colors.GREY_300
            text_color = ft.colors.GREY_700
        cursor_color = None
        focused_border_color = border_color
    else:
        # Editable styling - active colors
        if is_dark:
            bgcolor = ft.colors.GREY_900
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
            focused_border_color=focused_border_color,
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
            focused_border_color=focused_border_color,
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
                focused_border_color=focused_border_color
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
                focused_border_color=focused_border_color
            )
    elif field_type == 'readonly':
        # Theme-aware readonly colors
        if is_dark:
            readonly_bgcolor = ft.colors.GREY_800
            readonly_border_color = ft.colors.GREY_700
            readonly_text_color = ft.colors.GREY_400
        else:
            readonly_bgcolor = ft.colors.GREY_100
            readonly_border_color = ft.colors.GREY_300
            readonly_text_color = ft.colors.GREY_600
            
        return ft.TextField(
            label=label, 
            value=value, 
            read_only=True, 
            expand=True,
            bgcolor=readonly_bgcolor,
            border_color=readonly_border_color,
            color=readonly_text_color,
            focused_border_color=readonly_border_color
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
            focused_border_color=focused_border_color,
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
            focused_border_color=focused_border_color,
            autofocus=False
        )


class ProjectMetadataTab:
    """Tab for viewing and editing project metadata with configurable fields"""
    
    def __init__(self, page: ft.Page, project_data=None, project_path=None):
        self.page = page
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
        
        # Load data from JSON
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
        """Load project data from JSON"""
        try:
            # First, map data from JSON that's already loaded in project_data
            if self.project_data:
                print(f"Initial project_data keys: {list(self.project_data.keys())}")
                
                # Map dialog creation data to form fields
                self._map_dialog_data_to_form_fields()
                
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
            
            # Update form fields with all loaded data
            self._update_form_fields()
            
            # Update the page to reflect the changes
            if hasattr(self, 'page'):
                self.page.update()
                
        except Exception as e:
            print(f"Error loading project data: {e}")
            import traceback
            traceback.print_exc()
    
    def _map_dialog_data_to_form_fields(self):
        """Map data from project creation dialog to form field names"""
        try:
            # Map dialog field names to form field names
            field_mappings = {
                # Customer/facility data mappings
                'customer_name': ['facility_name', 'client_name'],
                'customer_number': ['building_number'],
                'customer_key': ['facility_number'],
                
                # Project data mappings  
                'title': ['project_title'],
                'description': ['project_description'],
                'project_suffix': ['request_year'],
                
                # Direct mappings (same name in dialog and form)
                'engineer': ['engineer'],
                'imagery_specialist': ['imagery_specialist'],
                'all_source': ['all_source'],
                'geologist': ['geologist'],
                'reviewer': ['reviewer'],
            }
            
            # Apply mappings
            for source_field, target_fields in field_mappings.items():
                if source_field in self.project_data:
                    source_value = self.project_data[source_field]
                    for target_field in target_fields:
                        # Only map if target field doesn't already have a value
                        if not self.project_data.get(target_field):
                            self.project_data[target_field] = source_value
                            print(f"Mapped {source_field} -> {target_field}: {source_value}")
            
            # Ensure we have proper values for dropdown fields
            if 'request_year' in self.project_data:
                # Make sure request_year is a string (for dropdown)
                self.project_data['request_year'] = str(self.project_data['request_year'])
                
        except Exception as e:
            print(f"Error mapping dialog data: {e}")
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
        """Update field styling and states based on current mode by recreating widgets"""
        try:
            # Recreate all field widgets with proper styling for current mode
            config = get_metadata_config(self.project_type)
            
            for column in config.get('columns', []):
                for field_config in column.get('fields', []):
                    field_key = field_config.get('key')
                    if field_key in self.field_widgets:
                        # Get current value from existing widget
                        current_value = ''
                        old_widget = self.field_widgets[field_key]
                        
                        if isinstance(old_widget, ft.TextField):
                            current_value = old_widget.value or ''
                        elif isinstance(old_widget, ft.Dropdown):
                            current_value = old_widget.value or ''
                        
                        # Create new widget with current mode styling
                        new_widget = create_field_widget(field_config, current_value, self.is_edit_mode, self.page)
                        
                        # Replace the widget
                        self.field_widgets[field_key] = new_widget
            
            # Rebuild the layout with new widgets
            self._rebuild_layout()
            
            print(f"Updated field states: edit_mode={self.is_edit_mode}")
            
        except Exception as e:
            print(f"Error updating field states: {e}")
    
    def _rebuild_layout(self):
        """Rebuild the entire layout with updated field widgets"""
        try:
            if hasattr(self, 'layout_container') and self.layout_container:
                # Clear and rebuild the layout content
                new_content = self._build_layout_content()
                self.layout_container.content = new_content
                
                # Update the page
                if hasattr(self, 'page') and self.page:
                    self.page.update()
                    
        except Exception as e:
            print(f"Error rebuilding layout: {e}")
    
    def _build_layout_content(self) -> ft.Control:
        """Build the layout content with current field widgets"""
        try:
            # Get configuration for project type
            config = get_metadata_config(self.project_type)
            columns = config.get('columns', [])
            
            # Create column layout with proper sizing
            column_controls = []
            
            for i, column_config in enumerate(columns):
                column_name = column_config.get('name', f'Column {i+1}')
                column_fields = column_config.get('fields', [])
                
                # Create field containers for this column
                field_containers = []
                for field_config in column_fields:
                    field_key = field_config.get('key')
                    if field_key in self.field_widgets:
                        widget = self.field_widgets[field_key]
                        # Add spacing container around each field
                        field_containers.append(
                            ft.Container(
                                content=widget,
                                margin=ft.margin.only(bottom=10)
                            )
                        )
                
                # Create column with fixed width and theme-aware styling
                # Theme-aware colors
                if self.page.theme_mode == ft.ThemeMode.DARK:
                    card_bgcolor = ft.colors.GREY_800
                    card_border_color = ft.colors.GREY_600
                    title_color = ft.colors.BLUE_300
                    divider_color = ft.colors.GREY_600
                else:
                    card_bgcolor = ft.colors.WHITE
                    card_border_color = ft.colors.GREY_300
                    title_color = ft.colors.BLUE_700
                    divider_color = ft.colors.GREY_300
                
                column_card = ft.Container(
                    content=ft.Column([
                        ft.Text(
                            column_name, 
                            size=16, 
                            weight=ft.FontWeight.BOLD, 
                            color=title_color
                        ),
                        ft.Divider(height=1, color=divider_color),
                        *field_containers
                    ], spacing=5, tight=True),
                    padding=ft.padding.all(15),
                    bgcolor=card_bgcolor,
                    border_radius=8,
                    border=ft.border.all(1, card_border_color),
                    width=300,  # Fixed width for proper column display
                    height=None  # Let height be dynamic
                )
                
                column_controls.append(column_card)
            
            # Create layout - always use horizontal Row layout for proper columns
            if column_controls:
                main_layout = ft.Row(
                    controls=column_controls,
                    spacing=10,
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    wrap=False,  # Don't wrap to prevent overlap
                    scroll=ft.ScrollMode.AUTO,  # Allow horizontal scrolling if needed
                    expand=False  # Don't expand the Row
                )
            else:
                main_layout = ft.Text("No fields configured", color=ft.colors.GREY_500)
            
            # Return the complete layout content
            return ft.Column([
                # Action button (Edit or Save) with mode indicator
                ft.Container(
                    content=ft.Row([
                        ft.Container(expand=True),  # Spacer
                        self.action_button
                    ]),
                    padding=ft.padding.only(bottom=20)
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
                    padding=ft.padding.symmetric(horizontal=5, vertical=10)
                ),
                
                # Form content in scrollable container
                ft.Container(
                    content=main_layout,
                    padding=ft.padding.all(10),
                    expand=True,
                    width=None,  # Let width be determined by content
                    height=None  # Let height be determined by content
                ),
                
                # Messages at bottom
                self.message_text,
                self.error_text
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
        # Always allow navigation in UI-only mode
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
                    widget = create_field_widget(field_config, field_value, self.is_edit_mode, self.page)
                    
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
            print(f"Updating form fields with data: {list(self.project_data.keys())}")
            updated_count = 0
            
            for field_key, widget in self.field_widgets.items():
                if hasattr(widget, 'value'):
                    # Get the value from project data
                    field_value = self.project_data.get(field_key, '')
                    
                    # Handle special cases for different widget types
                    if isinstance(widget, ft.Dropdown):
                        # For dropdowns, ensure the value is in the options
                        options = [opt.key for opt in widget.options] if widget.options else []
                        if str(field_value) in options:
                            field_value = str(field_value)
                        elif options:
                            field_value = options[0]  # Default to first option
                    
                    # Convert to string for text fields
                    field_value = str(field_value) if field_value is not None else ''
                    
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
        # Load fresh data from JSON
        self._load_project_data()
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
