"""
Metadata Configuration for Project Types
Defines the fields and layout for different project types
"""

from typing import Dict, List, Any
import flet as ft

# Field type definitions
FIELD_TYPES = {
    'text': 'TextField',
    'multiline': 'TextField with multiline=True',
    'dropdown': 'Dropdown with options',
    'date': 'TextField with date formatting',
    'readonly': 'TextField with read_only=True',
    'number': 'TextField with number input'
}

# Default metadata configuration for different project types
METADATA_CONFIG = {
    'default': {
        'columns': [
            {
                'name': 'Basic Information',
                'fields': [
                    {
                        'key': 'title',
                        'label': 'Project Title',
                        'type': 'text',
                        'required': True,
                        'tab_order': 1
                    },
                    {
                        'key': 'project_type',
                        'label': 'Project Type',
                        'type': 'text',
                        'required': True,
                        'tab_order': 2
                    },
                    {
                        'key': 'status',
                        'label': 'Status',
                        'type': 'dropdown',
                        'options': ['active', 'on_hold', 'completed', 'cancelled'],
                        'required': True,
                        'tab_order': 3
                    },
                    {
                        'key': 'created_at',
                        'label': 'Created Date',
                        'type': 'readonly',
                        'tab_order': 4
                    }
                ]
            },
            {
                'name': 'Team Members',
                'fields': [
                    {
                        'key': 'engineer',
                        'label': 'Engineer',
                        'type': 'text',
                        'tab_order': 5
                    },
                    {
                        'key': 'drafter',
                        'label': 'Drafter',
                        'type': 'text',
                        'tab_order': 6
                    },
                    {
                        'key': 'reviewer',
                        'label': 'Reviewer',
                        'type': 'text',
                        'tab_order': 7
                    },
                    {
                        'key': 'architect',
                        'label': 'Architect',
                        'type': 'text',
                        'tab_order': 8
                    },
                    {
                        'key': 'geologist',
                        'label': 'Geologist',
                        'type': 'text',
                        'tab_order': 9
                    }
                ]
            },
            {
                'name': 'Project Details',
                'fields': [
                    {
                        'key': 'description',
                        'label': 'Project Description',
                        'type': 'multiline',
                        'min_lines': 3,
                        'max_lines': 6,
                        'tab_order': 10
                    },
                    {
                        'key': 'location',
                        'label': 'Project Location',
                        'type': 'text',
                        'tab_order': 11
                    },
                    {
                        'key': 'client',
                        'label': 'Client',
                        'type': 'text',
                        'tab_order': 12
                    }
                ]
            }
        ]
    },
    'commercial': {
        'columns': [
            {
                'name': 'Basic Information',
                'fields': [
                    {
                        'key': 'title',
                        'label': 'Project Title',
                        'type': 'text',
                        'required': True,
                        'tab_order': 1
                    },
                    {
                        'key': 'project_type',
                        'label': 'Project Type',
                        'type': 'text',
                        'required': True,
                        'tab_order': 2
                    },
                    {
                        'key': 'status',
                        'label': 'Status',
                        'type': 'dropdown',
                        'options': ['active', 'on_hold', 'completed', 'cancelled'],
                        'required': True,
                        'tab_order': 3
                    },
                    {
                        'key': 'building_code',
                        'label': 'Building Code',
                        'type': 'text',
                        'tab_order': 4
                    },
                    {
                        'key': 'created_at',
                        'label': 'Created Date',
                        'type': 'readonly',
                        'tab_order': 5
                    }
                ]
            },
            {
                'name': 'Team & Compliance',
                'fields': [
                    {
                        'key': 'engineer',
                        'label': 'Lead Engineer',
                        'type': 'text',
                        'required': True,
                        'tab_order': 6
                    },
                    {
                        'key': 'architect',
                        'label': 'Architect',
                        'type': 'text',
                        'required': True,
                        'tab_order': 7
                    },
                    {
                        'key': 'reviewer',
                        'label': 'Code Reviewer',
                        'type': 'text',
                        'tab_order': 8
                    },
                    {
                        'key': 'drafter',
                        'label': 'CAD Drafter',
                        'type': 'text',
                        'tab_order': 9
                    },
                    {
                        'key': 'permit_status',
                        'label': 'Permit Status',
                        'type': 'dropdown',
                        'options': ['not_started', 'in_progress', 'approved', 'rejected'],
                        'tab_order': 10
                    }
                ]
            },
            {
                'name': 'Project Details',
                'fields': [
                    {
                        'key': 'client',
                        'label': 'Client/Owner',
                        'type': 'text',
                        'required': True,
                        'tab_order': 11
                    },
                    {
                        'key': 'location',
                        'label': 'Project Address',
                        'type': 'text',
                        'required': True,
                        'tab_order': 12
                    },
                    {
                        'key': 'square_footage',
                        'label': 'Square Footage',
                        'type': 'number',
                        'tab_order': 13
                    },
                    {
                        'key': 'description',
                        'label': 'Project Scope',
                        'type': 'multiline',
                        'min_lines': 3,
                        'max_lines': 6,
                        'tab_order': 14
                    }
                ]
            }
        ]
    },
    'residential': {
        'columns': [
            {
                'name': 'Basic Information',
                'fields': [
                    {
                        'key': 'title',
                        'label': 'Project Title',
                        'type': 'text',
                        'required': True,
                        'tab_order': 1
                    },
                    {
                        'key': 'project_type',
                        'label': 'Project Type',
                        'type': 'text',
                        'required': True,
                        'tab_order': 2
                    },
                    {
                        'key': 'status',
                        'label': 'Status',
                        'type': 'dropdown',
                        'options': ['active', 'on_hold', 'completed', 'cancelled'],
                        'required': True,
                        'tab_order': 3
                    },
                    {
                        'key': 'home_type',
                        'label': 'Home Type',
                        'type': 'dropdown',
                        'options': ['single_family', 'townhouse', 'duplex', 'custom'],
                        'tab_order': 4
                    },
                    {
                        'key': 'created_at',
                        'label': 'Created Date',
                        'type': 'readonly',
                        'tab_order': 5
                    }
                ]
            },
            {
                'name': 'Team Members',
                'fields': [
                    {
                        'key': 'engineer',
                        'label': 'Structural Engineer',
                        'type': 'text',
                        'tab_order': 6
                    },
                    {
                        'key': 'architect',
                        'label': 'Architect',
                        'type': 'text',
                        'tab_order': 7
                    },
                    {
                        'key': 'drafter',
                        'label': 'Drafter',
                        'type': 'text',
                        'tab_order': 8
                    },
                    {
                        'key': 'geologist',
                        'label': 'Geotechnical Engineer',
                        'type': 'text',
                        'tab_order': 9
                    },
                    {
                        'key': 'reviewer',
                        'label': 'Plan Reviewer',
                        'type': 'text',
                        'tab_order': 10
                    }
                ]
            },
            {
                'name': 'Property Details',
                'fields': [
                    {
                        'key': 'client',
                        'label': 'Homeowner',
                        'type': 'text',
                        'tab_order': 11
                    },
                    {
                        'key': 'location',
                        'label': 'Property Address',
                        'type': 'text',
                        'tab_order': 12
                    },
                    {
                        'key': 'lot_size',
                        'label': 'Lot Size (sq ft)',
                        'type': 'number',
                        'tab_order': 13
                    },
                    {
                        'key': 'bedrooms',
                        'label': 'Bedrooms',
                        'type': 'number',
                        'tab_order': 14
                    },
                    {
                        'key': 'bathrooms',
                        'label': 'Bathrooms',
                        'type': 'number',
                        'tab_order': 15
                    },
                    {
                        'key': 'description',
                        'label': 'Project Description',
                        'type': 'multiline',
                        'min_lines': 3,
                        'max_lines': 6,
                        'tab_order': 16
                    }
                ]
            }
        ]
    },
    'industrial': {
        'columns': [
            {
                'name': 'Basic Information',
                'fields': [
                    {
                        'key': 'title',
                        'label': 'Project Title',
                        'type': 'text',
                        'required': True,
                        'tab_order': 1
                    },
                    {
                        'key': 'project_type',
                        'label': 'Project Type',
                        'type': 'text',
                        'required': True,
                        'tab_order': 2
                    },
                    {
                        'key': 'status',
                        'label': 'Status',
                        'type': 'dropdown',
                        'options': ['active', 'on_hold', 'completed', 'cancelled'],
                        'required': True,
                        'tab_order': 3
                    },
                    {
                        'key': 'facility_type',
                        'label': 'Facility Type',
                        'type': 'dropdown',
                        'options': ['warehouse', 'manufacturing', 'distribution', 'processing'],
                        'tab_order': 4
                    },
                    {
                        'key': 'created_at',
                        'label': 'Created Date',
                        'type': 'readonly',
                        'tab_order': 5
                    }
                ]
            },
            {
                'name': 'Engineering Team',
                'fields': [
                    {
                        'key': 'engineer',
                        'label': 'Lead Engineer',
                        'type': 'text',
                        'required': True,
                        'tab_order': 6
                    },
                    {
                        'key': 'structural_engineer',
                        'label': 'Structural Engineer',
                        'type': 'text',
                        'tab_order': 7
                    },
                    {
                        'key': 'mep_engineer',
                        'label': 'MEP Engineer',
                        'type': 'text',
                        'tab_order': 8
                    },
                    {
                        'key': 'geologist',
                        'label': 'Geotechnical Engineer',
                        'type': 'text',
                        'tab_order': 9
                    },
                    {
                        'key': 'reviewer',
                        'label': 'QA Reviewer',
                        'type': 'text',
                        'tab_order': 10
                    },
                    {
                        'key': 'drafter',
                        'label': 'CAD Specialist',
                        'type': 'text',
                        'tab_order': 11
                    }
                ]
            },
            {
                'name': 'Facility Details',
                'fields': [
                    {
                        'key': 'client',
                        'label': 'Industrial Client',
                        'type': 'text',
                        'required': True,
                        'tab_order': 12
                    },
                    {
                        'key': 'location',
                        'label': 'Facility Location',
                        'type': 'text',
                        'required': True,
                        'tab_order': 13
                    },
                    {
                        'key': 'total_area',
                        'label': 'Total Area (sq ft)',
                        'type': 'number',
                        'tab_order': 14
                    },
                    {
                        'key': 'capacity',
                        'label': 'Design Capacity',
                        'type': 'text',
                        'tab_order': 15
                    },
                    {
                        'key': 'environmental_considerations',
                        'label': 'Environmental Factors',
                        'type': 'multiline',
                        'min_lines': 2,
                        'max_lines': 4,
                        'tab_order': 16
                    },
                    {
                        'key': 'description',
                        'label': 'Project Scope',
                        'type': 'multiline',
                        'min_lines': 3,
                        'max_lines': 6,
                        'tab_order': 17
                    }
                ]
            }
        ]
    }
}


def get_metadata_config(project_type: str) -> Dict[str, Any]:
    """Get metadata configuration for a specific project type"""
    return METADATA_CONFIG.get(project_type, METADATA_CONFIG['default'])


def get_all_fields_for_project_type(project_type: str) -> List[Dict[str, Any]]:
    """Get all fields for a project type, sorted by tab order"""
    config = get_metadata_config(project_type)
    all_fields = []
    
    for column in config['columns']:
        all_fields.extend(column['fields'])
    
    # Sort by tab order
    all_fields.sort(key=lambda x: x.get('tab_order', 999))
    return all_fields


def get_column_names(project_type: str) -> List[str]:
    """Get column names for a project type"""
    config = get_metadata_config(project_type)
    return [column['name'] for column in config['columns']]


def create_field_widget(field_config: Dict[str, Any], value: str = '') -> ft.Control:
    """Create a Flet widget based on field configuration"""
    field_type = field_config.get('type', 'text')
    label = field_config.get('label', '')
    required = field_config.get('required', False)
    
    # Add asterisk for required fields
    if required:
        label += ' *'
    
    if field_type == 'text':
        return ft.TextField(
            label=label,
            value=value,
            expand=True
        )
    
    elif field_type == 'multiline':
        return ft.TextField(
            label=label,
            value=value,
            multiline=True,
            min_lines=field_config.get('min_lines', 3),
            max_lines=field_config.get('max_lines', 6),
            expand=True
        )
    
    elif field_type == 'dropdown':
        options = field_config.get('options', [])
        return ft.Dropdown(
            label=label,
            value=value if value in options else (options[0] if options else ''),
            options=[ft.dropdown.Option(opt) for opt in options],
            expand=True
        )
    
    elif field_type == 'readonly':
        return ft.TextField(
            label=label,
            value=value,
            read_only=True,
            expand=True
        )
    
    elif field_type == 'number':
        return ft.TextField(
            label=label,
            value=value,
            keyboard_type=ft.KeyboardType.NUMBER,
            expand=True
        )
    
    else:  # Default to text
        return ft.TextField(
            label=label,
            value=value,
            expand=True
        )
