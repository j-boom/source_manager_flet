"""
Project Types Configuration
Defines project types and their specific fields, validation rules, and database schemas
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class FieldType(Enum):
    """Field types for form generation"""
    TEXT = "text"
    DROPDOWN = "dropdown"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"
    TEXTAREA = "textarea"


class ValidationRule(Enum):
    """Validation rule types"""
    REQUIRED = "required"
    PATTERN = "pattern"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"


@dataclass
class FieldConfig:
    """Configuration for a form field"""
    name: str
    label: str
    field_type: FieldType
    required: bool = False
    hint_text: str = ""
    options: Optional[List[str]] = None  # For dropdown fields
    validation_rules: Optional[Dict[ValidationRule, Any]] = None
    width: int = 300
    visible: bool = True
    depends_on: Optional[str] = None  # Field name this depends on
    depends_value: Optional[str] = None  # Value that makes this field visible
    tab_order: int = 0  # Order for tabbing through fields
    min_lines: Optional[int] = None  # For textarea fields
    max_lines: Optional[int] = None  # For textarea fields
    column_group: Optional[str] = None  # For organizing fields into columns/groups


@dataclass
class ProjectTypeConfig:
    """Configuration for a project type"""
    name: str
    display_name: str
    description: str
    fields: List[FieldConfig]
    filename_pattern: str  # Pattern for generating filenames
    validation_rules: Optional[Dict[str, Any]] = None


# Base facility fields (common to all project types)
FACILITY_FIELDS = [
    FieldConfig(
        name="facility_number",
        label="Facility Number *",
        field_type=FieldType.TEXT,
        required=True,
        hint_text="10-digit folder number",
        width=200,
        tab_order=1,
        column_group="Facility Information"
    ),
    FieldConfig(
        name="facility_name",
        label="Facility Name *",
        field_type=FieldType.TEXT,
        required=True,
        hint_text="Full facility name",
        width=400,
        tab_order=2,
        column_group="Facility Information"
    ),
    FieldConfig(
        name="building_number",
        label="Building Number",
        field_type=FieldType.TEXT,
        hint_text="Format: [A-Z]{2}\\d{3} (e.g., DC123)",
        width=200,
        validation_rules={ValidationRule.PATTERN: r'^[A-Z]{2}\d{3}$'},
        tab_order=3,
        column_group="Facility Information"
    ),
    FieldConfig(
        name="customer_suffix",
        label="Customer Suffix",
        field_type=FieldType.TEXT,
        hint_text="Optional suffix",
        width=200,
        tab_order=4,
        column_group="Facility Information"
    )
]

# Base project fields (common to all project types)
BASE_PROJECT_FIELDS = [
    FieldConfig(
        name="project_title",
        label="Project Title *",
        field_type=FieldType.TEXT,
        required=True,
        hint_text="Descriptive project title",
        width=400,
        tab_order=10,
        column_group="Basic Information"
    ),
    FieldConfig(
        name="project_description",
        label="Project Description",
        field_type=FieldType.TEXTAREA,
        hint_text="Optional project description",
        width=400,
        min_lines=3,
        max_lines=6,
        tab_order=11,
        column_group="Basic Information"
    ),
    FieldConfig(
        name="request_year",
        label="Request Year *",
        field_type=FieldType.DROPDOWN,
        required=True,
        options=[str(year) for year in range(2020, 2031)],
        width=150,
        tab_order=12,
        column_group="Basic Information"
    ),
]

# Team fields (commented out as per request - no longer used in dialog)
# TEAM_FIELDS = [
#     FieldConfig(
#         name="engineer",
#         label="Engineer",
#         field_type=FieldType.TEXT,
#         hint_text="Lead engineer name",
#         width=300
#     ),
#     FieldConfig(
#         name="drafter",
#         label="Drafter",
#         field_type=FieldType.TEXT,
#         hint_text="Drafter name",
#         width=300
#     ),
#     FieldConfig(
#         name="reviewer",
#         label="Reviewer",
#         field_type=FieldType.TEXT,
#         hint_text="Reviewer name",
#         width=300
#     ),
#     FieldConfig(
#         name="architect",
#         label="Architect",
#         field_type=FieldType.TEXT,
#         hint_text="Architect name",
#         width=300
#     ),
#     FieldConfig(
#         name="geologist",
#         label="Geologist",
#         field_type=FieldType.TEXT,
#         hint_text="Geologist name",
#         width=300
#     ),
# ]

# Project type specific configurations
PROJECT_TYPES_CONFIG = {
    "CCR": ProjectTypeConfig(
        name="CCR",
        display_name="Construction Change Request",
        description="Construction Change Request projects",
        filename_pattern="{facility_number} - {building_number} - CCR - {request_year}.json",
        fields=FACILITY_FIELDS + BASE_PROJECT_FIELDS + [
            FieldConfig(
                name="suffix",
                label="Suffix *",
                field_type=FieldType.TEXT,
                required=True,
                hint_text="Format: [A-Z]{3}\\d{3} (e.g., ABC123)",
                width=200,
                validation_rules={ValidationRule.PATTERN: r'^[A-Z]{3}\d{3}$'},
                tab_order=20,
                column_group="CCR Specific"
            ),
            FieldConfig(
                name="change_order_number",
                label="Change Order Number",
                field_type=FieldType.TEXT,
                hint_text="Associated change order number",
                width=200,
                tab_order=21,
                column_group="CCR Specific"
            ),
            FieldConfig(
                name="estimated_cost",
                label="Estimated Cost",
                field_type=FieldType.NUMBER,
                hint_text="Estimated cost in USD",
                width=200,
                tab_order=22,
                column_group="Financial Information"
            ),
        ]
    ),
    
    "GSC": ProjectTypeConfig(
        name="GSC",
        display_name="Geotechnical Site Characterization",
        description="Geotechnical Site Characterization projects",
        filename_pattern="{facility_number} - {building_number} - GSC - {request_year}.json",
        fields=FACILITY_FIELDS + BASE_PROJECT_FIELDS + [
            FieldConfig(
                name="site_location",
                label="Site Location *",
                field_type=FieldType.TEXT,
                required=True,
                hint_text="Specific site location description",
                width=400,
                tab_order=20,
                column_group="GSC Specific"
            ),
            FieldConfig(
                name="investigation_type",
                label="Investigation Type",
                field_type=FieldType.DROPDOWN,
                options=["Boring", "Test Pit", "Monitoring Well", "Geophysical", "Other"],
                width=200,
                tab_order=21,
                column_group="GSC Specific"
            ),
            FieldConfig(
                name="depth_required",
                label="Depth Required (ft)",
                field_type=FieldType.NUMBER,
                hint_text="Investigation depth in feet",
                width=200,
                tab_order=22,
                column_group="Technical Information"
            ),
        ]
    ),
    
    "STD": ProjectTypeConfig(
        name="STD",
        display_name="Standard Design",
        description="Standard Design projects",
        filename_pattern="{facility_number} - {building_number} - STD - {suffix} - {request_year}.json",
        fields=FACILITY_FIELDS + BASE_PROJECT_FIELDS + [
            FieldConfig(
                name="suffix",
                label="Suffix *",
                field_type=FieldType.TEXT,
                required=True,
                hint_text="Format: [A-Z]{3}\\d{3} (e.g., ABC123)",
                width=200,
                validation_rules={ValidationRule.PATTERN: r'^[A-Z]{3}\d{3}$'},
                tab_order=20,
                column_group="STD Specific"
            ),
            FieldConfig(
                name="design_category",
                label="Design Category",
                field_type=FieldType.DROPDOWN,
                options=["Structural", "Mechanical", "Electrical", "Civil", "Environmental"],
                width=200,
                tab_order=21,
                column_group="STD Specific"
            ),
            FieldConfig(
                name="applicable_codes",
                label="Applicable Codes",
                field_type=FieldType.TEXTAREA,
                hint_text="List applicable design codes and standards",
                width=400,
                min_lines=3,
                max_lines=6,
                tab_order=22,
                column_group="Technical Information"
            ),
        ]
    ),
    
    "FCR": ProjectTypeConfig(
        name="FCR",
        display_name="Facility Change Request",
        description="Facility Change Request projects",
        filename_pattern="{facility_number} - {building_number} - FCR - {suffix} - {request_year}.json",
        fields=FACILITY_FIELDS + BASE_PROJECT_FIELDS + [
            FieldConfig(
                name="suffix",
                label="Suffix *",
                field_type=FieldType.TEXT,
                required=True,
                hint_text="Format: [A-Z]{3}\\d{3} (e.g., ABC123)",
                width=200,
                validation_rules={ValidationRule.PATTERN: r'^[A-Z]{3}\d{3}$'},
                tab_order=20,
                column_group="FCR Specific"
            ),
            FieldConfig(
                name="change_type",
                label="Change Type",
                field_type=FieldType.DROPDOWN,
                options=["Addition", "Modification", "Demolition", "Renovation", "Other"],
                width=200,
                tab_order=21,
                column_group="FCR Specific"
            ),
            FieldConfig(
                name="justification",
                label="Justification *",
                field_type=FieldType.TEXTAREA,
                required=True,
                hint_text="Justification for the facility change",
                width=400,
                min_lines=3,
                max_lines=8,
                tab_order=22,
                column_group="Documentation"
            ),
        ]
    ),
    
    "COM": ProjectTypeConfig(
        name="COM",
        display_name="Commissioning",
        description="Commissioning projects",
        filename_pattern="{facility_number} - {building_number} - COM - {suffix} - {request_year}.json",
        fields=FACILITY_FIELDS + BASE_PROJECT_FIELDS + [
            FieldConfig(
                name="suffix",
                label="Suffix *",
                field_type=FieldType.TEXT,
                required=True,
                hint_text="Format: [A-Z]{3}\\d{3} (e.g., ABC123)",
                width=200,
                validation_rules={ValidationRule.PATTERN: r'^[A-Z]{3}\d{3}$'},
                tab_order=20,
                column_group="COM Specific"
            ),
            FieldConfig(
                name="commissioning_phase",
                label="Commissioning Phase",
                field_type=FieldType.DROPDOWN,
                options=["Pre-Commissioning", "Initial Commissioning", "Re-Commissioning", "Ongoing Commissioning"],
                width=250,
                tab_order=21,
                column_group="COM Specific"
            ),
            FieldConfig(
                name="systems_involved",
                label="Systems Involved",
                field_type=FieldType.TEXTAREA,
                hint_text="List systems to be commissioned",
                width=400,
                min_lines=3,
                max_lines=6,
                tab_order=22,
                column_group="Technical Information"
            ),
        ]
    ),
    
    "CRS": ProjectTypeConfig(
        name="CRS",
        display_name="Corrective Action",
        description="Corrective Action projects",
        filename_pattern="{facility_number} - {building_number} - CRS - {suffix} - {request_year}.json",
        fields=FACILITY_FIELDS + BASE_PROJECT_FIELDS + [
            FieldConfig(
                name="suffix",
                label="Suffix *",
                field_type=FieldType.TEXT,
                required=True,
                hint_text="Format: [A-Z]{3}\\d{3} (e.g., ABC123)",
                width=200,
                validation_rules={ValidationRule.PATTERN: r'^[A-Z]{3}\d{3}$'},
                tab_order=20,
                column_group="CRS Specific"
            ),
            FieldConfig(
                name="deficiency_description",
                label="Deficiency Description *",
                field_type=FieldType.TEXTAREA,
                required=True,
                hint_text="Description of the deficiency requiring correction",
                width=400,
                min_lines=4,
                max_lines=8,
                tab_order=21,
                column_group="Problem Definition"
            ),
            FieldConfig(
                name="priority_level",
                label="Priority Level",
                field_type=FieldType.DROPDOWN,
                options=["Critical", "High", "Medium", "Low"],
                width=150,
                tab_order=22,
                column_group="CRS Specific"
            ),
        ]
    ),
    
    "OTH": ProjectTypeConfig(
        name="OTH",
        display_name="Other",
        description="Other project types",
        filename_pattern="{document_title}- OTH - {request_year}.json",
        fields=FACILITY_FIELDS + BASE_PROJECT_FIELDS + [
            FieldConfig(
                name="document_title",
                label="Document Title *",
                field_type=FieldType.TEXT,
                required=True,
                hint_text="Custom document title for OTH projects",
                width=400,
                tab_order=20,
                column_group="OTH Specific"
            ),
            FieldConfig(
                name="project_category",
                label="Project Category",
                field_type=FieldType.DROPDOWN,
                options=["Study", "Assessment", "Report", "Analysis", "Investigation", "Other"],
                width=200,
                tab_order=21,
                column_group="OTH Specific"
            ),
            FieldConfig(
                name="deliverables",
                label="Expected Deliverables",
                field_type=FieldType.TEXTAREA,
                hint_text="List expected project deliverables",
                width=400,
                min_lines=3,
                max_lines=6,
                tab_order=22,
                column_group="Documentation"
            ),
        ]
    ),
}


def get_project_type_config(project_type: str) -> Optional[ProjectTypeConfig]:
    """Get configuration for a specific project type"""
    return PROJECT_TYPES_CONFIG.get(project_type)


def get_all_project_types() -> List[str]:
    """Get list of all available project types"""
    return list(PROJECT_TYPES_CONFIG.keys())


def get_project_type_display_names() -> Dict[str, str]:
    """Get mapping of project type codes to display names"""
    return {code: config.display_name for code, config in PROJECT_TYPES_CONFIG.items()}


def create_field_widget(field_config: FieldConfig, value: str = ''):
    """Create a Flet widget based on field configuration
    
    Returns a Flet Control that can be used in the UI.
    Note: This function requires flet to be imported in the calling module.
    """
    try:
        import flet as ft
    except ImportError:
        raise ImportError("Flet is required to create field widgets")
    
    label = field_config.label
    
    # Add asterisk for required fields
    if field_config.required:
        label += ' *'
    
    if field_config.field_type == FieldType.TEXT:
        return ft.TextField(
            label=label,
            value=value,
            hint_text=field_config.hint_text,
            width=field_config.width,
            expand=True
        )
    
    elif field_config.field_type == FieldType.TEXTAREA:
        return ft.TextField(
            label=label,
            value=value,
            hint_text=field_config.hint_text,
            multiline=True,
            min_lines=field_config.min_lines or 3,
            max_lines=field_config.max_lines or 6,
            width=field_config.width,
            expand=True
        )
    
    elif field_config.field_type == FieldType.DROPDOWN:
        options = field_config.options or []
        return ft.Dropdown(
            label=label,
            hint_text=field_config.hint_text,
            value=value if value in options else (options[0] if options else ''),
            options=[ft.dropdown.Option(opt) for opt in options],
            width=field_config.width,
            expand=True
        )
    
    elif field_config.field_type == FieldType.NUMBER:
        return ft.TextField(
            label=label,
            value=value,
            hint_text=field_config.hint_text,
            keyboard_type=ft.KeyboardType.NUMBER,
            width=field_config.width,
            expand=True
        )
    
    elif field_config.field_type == FieldType.DATE:
        return ft.TextField(
            label=label,
            value=value,
            hint_text=field_config.hint_text or "YYYY-MM-DD",
            width=field_config.width,
            expand=True
        )
    
    elif field_config.field_type == FieldType.BOOLEAN:
        return ft.Checkbox(
            label=label,
            value=value.lower() in ['true', '1', 'yes'] if value else False,
            expand=True
        )
    
    else:  # Default to text
        return ft.TextField(
            label=label,
            value=value,
            hint_text=field_config.hint_text,
            width=field_config.width,
            expand=True
        )


def get_fields_by_column_group(fields: List[FieldConfig]) -> Dict[str, List[FieldConfig]]:
    """Group fields by their column_group for layout purposes"""
    groups = {}
    
    for field in fields:
        group_name = field.column_group or "Main"
        if group_name not in groups:
            groups[group_name] = []
        groups[group_name].append(field)
    
    # Sort fields within each group by tab_order
    for group_fields in groups.values():
        group_fields.sort(key=lambda f: f.tab_order)
    
    return groups


def get_all_fields_sorted(project_type_config: ProjectTypeConfig) -> List[FieldConfig]:
    """Get all fields for a project type, sorted by tab order"""
    return sorted(project_type_config.fields, key=lambda f: f.tab_order)


def validate_field_value(field_config: FieldConfig, value: str) -> tuple[bool, str]:
    """Validate a field value against its configuration
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if field_config.required and not value:
        return False, f"{field_config.label} is required"
    
    if not field_config.validation_rules:
        return True, ""
    
    for rule, rule_value in field_config.validation_rules.items():
        if rule == ValidationRule.PATTERN:
            import re
            if value and not re.match(rule_value, value):
                return False, f"{field_config.label} format is invalid"
        
        elif rule == ValidationRule.MIN_LENGTH:
            if len(value) < rule_value:
                return False, f"{field_config.label} must be at least {rule_value} characters"
        
        elif rule == ValidationRule.MAX_LENGTH:
            if len(value) > rule_value:
                return False, f"{field_config.label} must be no more than {rule_value} characters"
        
        elif rule == ValidationRule.MIN_VALUE:
            try:
                if float(value) < rule_value:
                    return False, f"{field_config.label} must be at least {rule_value}"
            except ValueError:
                return False, f"{field_config.label} must be a valid number"
        
        elif rule == ValidationRule.MAX_VALUE:
            try:
                if float(value) > rule_value:
                    return False, f"{field_config.label} must be no more than {rule_value}"
            except ValueError:
                return False, f"{field_config.label} must be a valid number"
    
    return True, ""
