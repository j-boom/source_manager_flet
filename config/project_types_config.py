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


@dataclass
class ProjectTypeConfig:
    """Configuration for a project type"""
    name: str
    display_name: str
    description: str
    table_name: str  # Database table name for this project type
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
        width=200
    ),
    FieldConfig(
        name="facility_name",
        label="Facility Name *",
        field_type=FieldType.TEXT,
        required=True,
        hint_text="Full facility name",
        width=400
    ),
    FieldConfig(
        name="building_number",
        label="Building Number",
        field_type=FieldType.TEXT,
        hint_text="Format: [A-Z]{2}\\d{3} (e.g., DC123)",
        width=200,
        validation_rules={ValidationRule.PATTERN: r'^[A-Z]{2}\d{3}$'}
    ),
    FieldConfig(
        name="customer_suffix",
        label="Customer Suffix",
        field_type=FieldType.TEXT,
        hint_text="Optional suffix",
        width=200
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
        width=400
    ),
    FieldConfig(
        name="project_description",
        label="Project Description",
        field_type=FieldType.TEXTAREA,
        hint_text="Optional project description",
        width=400
    ),
    FieldConfig(
        name="request_year",
        label="Request Year *",
        field_type=FieldType.DROPDOWN,
        required=True,
        options=[str(year) for year in range(2020, 2031)],
        width=150
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
        table_name="projects_ccr",
        filename_pattern="{facility_number} - {building_number} - CCR - {request_year}.json",
        fields=FACILITY_FIELDS + BASE_PROJECT_FIELDS + [
            FieldConfig(
                name="suffix",
                label="Suffix *",
                field_type=FieldType.TEXT,
                required=True,
                hint_text="Format: [A-Z]{3}\\d{3} (e.g., ABC123)",
                width=200,
                validation_rules={ValidationRule.PATTERN: r'^[A-Z]{3}\d{3}$'}
            ),
            FieldConfig(
                name="change_order_number",
                label="Change Order Number",
                field_type=FieldType.TEXT,
                hint_text="Associated change order number",
                width=200
            ),
            FieldConfig(
                name="estimated_cost",
                label="Estimated Cost",
                field_type=FieldType.NUMBER,
                hint_text="Estimated cost in USD",
                width=200
            ),
        ]
    ),
    
    "GSC": ProjectTypeConfig(
        name="GSC",
        display_name="Geotechnical Site Characterization",
        description="Geotechnical Site Characterization projects",
        table_name="projects_gsc",
        filename_pattern="{facility_number} - {building_number} - GSC - {request_year}.json",
        fields=FACILITY_FIELDS + BASE_PROJECT_FIELDS + [
            FieldConfig(
                name="site_location",
                label="Site Location *",
                field_type=FieldType.TEXT,
                required=True,
                hint_text="Specific site location description",
                width=400
            ),
            FieldConfig(
                name="investigation_type",
                label="Investigation Type",
                field_type=FieldType.DROPDOWN,
                options=["Boring", "Test Pit", "Monitoring Well", "Geophysical", "Other"],
                width=200
            ),
            FieldConfig(
                name="depth_required",
                label="Depth Required (ft)",
                field_type=FieldType.NUMBER,
                hint_text="Investigation depth in feet",
                width=200
            ),
        ]
    ),
    
    "STD": ProjectTypeConfig(
        name="STD",
        display_name="Standard Design",
        description="Standard Design projects",
        table_name="projects_std",
        filename_pattern="{facility_number} - {building_number} - STD - {suffix} - {request_year}.json",
        fields=FACILITY_FIELDS + BASE_PROJECT_FIELDS + [
            FieldConfig(
                name="suffix",
                label="Suffix *",
                field_type=FieldType.TEXT,
                required=True,
                hint_text="Format: [A-Z]{3}\\d{3} (e.g., ABC123)",
                width=200,
                validation_rules={ValidationRule.PATTERN: r'^[A-Z]{3}\d{3}$'}
            ),
            FieldConfig(
                name="design_category",
                label="Design Category",
                field_type=FieldType.DROPDOWN,
                options=["Structural", "Mechanical", "Electrical", "Civil", "Environmental"],
                width=200
            ),
            FieldConfig(
                name="applicable_codes",
                label="Applicable Codes",
                field_type=FieldType.TEXTAREA,
                hint_text="List applicable design codes and standards",
                width=400
            ),
        ]
    ),
    
    "FCR": ProjectTypeConfig(
        name="FCR",
        display_name="Facility Change Request",
        description="Facility Change Request projects",
        table_name="projects_fcr",
        filename_pattern="{facility_number} - {building_number} - FCR - {suffix} - {request_year}.json",
        fields=FACILITY_FIELDS + BASE_PROJECT_FIELDS + [
            FieldConfig(
                name="suffix",
                label="Suffix *",
                field_type=FieldType.TEXT,
                required=True,
                hint_text="Format: [A-Z]{3}\\d{3} (e.g., ABC123)",
                width=200,
                validation_rules={ValidationRule.PATTERN: r'^[A-Z]{3}\d{3}$'}
            ),
            FieldConfig(
                name="change_type",
                label="Change Type",
                field_type=FieldType.DROPDOWN,
                options=["Addition", "Modification", "Demolition", "Renovation", "Other"],
                width=200
            ),
            FieldConfig(
                name="justification",
                label="Justification *",
                field_type=FieldType.TEXTAREA,
                required=True,
                hint_text="Justification for the facility change",
                width=400
            ),
        ]
    ),
    
    "COM": ProjectTypeConfig(
        name="COM",
        display_name="Commissioning",
        description="Commissioning projects",
        table_name="projects_com",
        filename_pattern="{facility_number} - {building_number} - COM - {suffix} - {request_year}.json",
        fields=FACILITY_FIELDS + BASE_PROJECT_FIELDS + [
            FieldConfig(
                name="suffix",
                label="Suffix *",
                field_type=FieldType.TEXT,
                required=True,
                hint_text="Format: [A-Z]{3}\\d{3} (e.g., ABC123)",
                width=200,
                validation_rules={ValidationRule.PATTERN: r'^[A-Z]{3}\d{3}$'}
            ),
            FieldConfig(
                name="commissioning_phase",
                label="Commissioning Phase",
                field_type=FieldType.DROPDOWN,
                options=["Pre-Commissioning", "Initial Commissioning", "Re-Commissioning", "Ongoing Commissioning"],
                width=250
            ),
            FieldConfig(
                name="systems_involved",
                label="Systems Involved",
                field_type=FieldType.TEXTAREA,
                hint_text="List systems to be commissioned",
                width=400
            ),
        ]
    ),
    
    "CRS": ProjectTypeConfig(
        name="CRS",
        display_name="Corrective Action",
        description="Corrective Action projects",
        table_name="projects_crs",
        filename_pattern="{facility_number} - {building_number} - CRS - {suffix} - {request_year}.json",
        fields=FACILITY_FIELDS + BASE_PROJECT_FIELDS + [
            FieldConfig(
                name="suffix",
                label="Suffix *",
                field_type=FieldType.TEXT,
                required=True,
                hint_text="Format: [A-Z]{3}\\d{3} (e.g., ABC123)",
                width=200,
                validation_rules={ValidationRule.PATTERN: r'^[A-Z]{3}\d{3}$'}
            ),
            FieldConfig(
                name="deficiency_description",
                label="Deficiency Description *",
                field_type=FieldType.TEXTAREA,
                required=True,
                hint_text="Description of the deficiency requiring correction",
                width=400
            ),
            FieldConfig(
                name="priority_level",
                label="Priority Level",
                field_type=FieldType.DROPDOWN,
                options=["Critical", "High", "Medium", "Low"],
                width=150
            ),
        ]
    ),
    
    "OTH": ProjectTypeConfig(
        name="OTH",
        display_name="Other",
        description="Other project types",
        table_name="projects_oth",
        filename_pattern="{facility_number} - {building_number} - OTH - {document_title} - {request_year}.json",
        fields=FACILITY_FIELDS + BASE_PROJECT_FIELDS + [
            FieldConfig(
                name="document_title",
                label="Document Title *",
                field_type=FieldType.TEXT,
                required=True,
                hint_text="Custom document title for OTH projects",
                width=400
            ),
            FieldConfig(
                name="project_category",
                label="Project Category",
                field_type=FieldType.DROPDOWN,
                options=["Study", "Assessment", "Report", "Analysis", "Investigation", "Other"],
                width=200
            ),
            FieldConfig(
                name="deliverables",
                label="Expected Deliverables",
                field_type=FieldType.TEXTAREA,
                hint_text="List expected project deliverables",
                width=400
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
