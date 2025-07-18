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
    CHECKBOX = "checkbox"


class ValidationRule(Enum):
    """Validation rule types"""

    REQUIRED = "required"
    PATTERN = "pattern"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"


class CollectionStage(Enum):
    """Defines the stage of collection for field data"""

    DIALOG = "dialog"
    METADATA = "metadata"
    IMPLICIT = "implicit"  # Data is added by the system, not the user


@dataclass
class FieldConfig:
    """Configuration for a form field"""

    name: str
    label: str
    field_type: FieldType
    collection_stage: CollectionStage = CollectionStage.METADATA
    required: bool = False
    hint_text: str = ""
    options: Optional[List[str]] = None
    validation_rules: Optional[Dict[ValidationRule, Any]] = None
    width: int = 300
    tab_order: int = 0
    column_group: Optional[str] = "Details"


@dataclass
class ProjectTypeConfig:
    """Configuration for a project type"""

    name: str
    display_name: str
    description: str
    field_names: List[str]
    filename_pattern: str


# =============================================================================
# MASTER FIELD REGISTRY
# =============================================================================
ALL_FIELDS: Dict[str, FieldConfig] = {
    # --- Implicit Fields (System-generated) ---
    "project_type": FieldConfig(
        name="project_type",
        label="Project Type",
        field_type=FieldType.TEXT,
        collection_stage=CollectionStage.IMPLICIT,
    ),
    "current_year": FieldConfig(
        name="current_year",
        label="Current Year",
        field_type=FieldType.TEXT,
        collection_stage=CollectionStage.IMPLICIT,
    ),
    # --- Dialog Fields ---
    "project_title": FieldConfig(
        name="project_title",
        label="Project Title",
        field_type=FieldType.TEXT,
        required=True,
        collection_stage=CollectionStage.METADATA,
        tab_order=0,
        column_group="Project Info",
    ),
    "document_title": FieldConfig(
        name="document_title",
        label="Document Title",
        field_type=FieldType.TEXT,
        required=True,
        collection_stage=CollectionStage.IMPLICIT,  # Hide from all forms
        tab_order=1,
        column_group="Project Info",
    ),
    "be_number": FieldConfig(
        name="be_number",
        label="BE Number",
        field_type=FieldType.TEXT,
        required=True,
        collection_stage=CollectionStage.DIALOG,
        tab_order=2,
        validation_rules={ValidationRule.PATTERN: r"^\d{4}([A-Z]{2}\d{4}|\d{6})$"},
        width=200,
        column_group="Facility Information",
    ),
    "facility_name": FieldConfig(
        name="facility_name",
        label="Facility Name",
        field_type=FieldType.TEXT,
        required=True,
        collection_stage=CollectionStage.DIALOG,
        tab_order=4,
        column_group="Facility Information",
    ),
    "osuffix": FieldConfig(
        name="osuffix",
        label="OSuffix",
        field_type=FieldType.TEXT,
        hint_text="e.g., DC123",
        validation_rules={ValidationRule.PATTERN: r"^[A-Z]{2}\d{3}$"},
        collection_stage=CollectionStage.DIALOG,
        tab_order=3,
        width=150,
        column_group="Facility Information",
    ),
    # --- Metadata Fields ---
    "request_year": FieldConfig(
        name="request_year",
        label="Request Year",
        field_type=FieldType.TEXT,
        required=True,
        hint_text="YYYY QX",
        validation_rules={ValidationRule.PATTERN: r"^\d{4}\sQ[1-4]$"},
        collection_stage=CollectionStage.METADATA,
        tab_order=5,
        width=150,
        column_group="Project Info",
    ),
    "relook": FieldConfig(
        name="relook",
        label="Relook",
        field_type=FieldType.CHECKBOX,
        collection_stage=CollectionStage.METADATA,
        tab_order=6,
        column_group="Project Info",
    ),
    "engineer": FieldConfig(
        name="engineer",
        label="Engineer",
        field_type=FieldType.TEXT,
        collection_stage=CollectionStage.METADATA,
        width=300,
        column_group="Team",
    ),
    "imagery": FieldConfig(
        name="imagery",
        label="Imagery",
        field_type=FieldType.TEXT,
        collection_stage=CollectionStage.METADATA,
        width=300,
        column_group="Team",
    ),
    "reviewer": FieldConfig(
        name="reviewer",
        label="Reviewer",
        field_type=FieldType.TEXT,
        collection_stage=CollectionStage.METADATA,
        column_group="Team",
        width=300,
    ),
    "analyst": FieldConfig(
        name="analyst",
        label="Analyst",
        field_type=FieldType.TEXT,
        collection_stage=CollectionStage.METADATA,
        width=300,
        column_group="Team",
    ),
    "geologist": FieldConfig(
        name="geologist",
        label="Geologist",
        field_type=FieldType.TEXT,
        collection_stage=CollectionStage.METADATA,
        width=300,
        column_group="Team",
    ),
    "requestor": FieldConfig(
        name="requestor",
        label="Requestor",
        field_type=FieldType.TEXT,
        width=300,
        collection_stage=CollectionStage.METADATA,
        column_group="Project Info",
    ),
    "facility_number": FieldConfig(
        name="facility_number",
        label="Facility Number",
        field_type=FieldType.TEXT,
        required=True,
        validation_rules={ValidationRule.PATTERN: r"^\d{10}$"},
        collection_stage=CollectionStage.METADATA,
        column_group="Facility Information",
    ),
}

# =============================================================================
# PROJECT TYPE DEFINITIONS
# =============================================================================
PROJECT_TYPES_CONFIG: Dict[str, ProjectTypeConfig] = {
    "CCR": ProjectTypeConfig(
        name="CCR",
        display_name="Construction Change Request",
        description="Construction Change Request projects",
        filename_pattern="{be_number} - {osuffix} - CCR - {current_year}",
        field_names=[
            "project_type",
            "current_year",
            "project_title",
            "be_number",
            "osuffix",
            "facility_name",
            "facility_number",
            "engineer",
            "imagery",
            "reviewer",
            "analyst",
            "geologist",
            "requestor",
            "request_year",
            "relook",
        ],
    ),
    "GSC": ProjectTypeConfig(
        name="GSC",
        display_name="Geotechnical Site Characterization",
        description="Geotechnical Site Characterization projects",
        filename_pattern="{be_number} - GSC - {current_year}",
        field_names=[
            "project_type",
            "current_year",
            "project_title",
            "be_number",
            "facility_name",
            "osuffix",
            "geologist",
            "imagery",
            "reviewer",
            "requestor",
            "request_year",
            "relook",
        ],
    ),
    "STD": ProjectTypeConfig(
        name="STD",
        display_name="Standard Design",
        description="Standard Design projects",
        filename_pattern="{be_number} - {osuffix} - STD - {current_year}",
        field_names=[
            "project_type",
            "current_year",
            "project_title",
            "facility_name",
            "be_number",
            "osuffix",
            "facility_number",
            "engineer",
            "imagery",
            "reviewer",
            "analyst",
            "geologist",
            "requestor",
            "request_year",
            "relook",
        ],
    ),
    "FCR": ProjectTypeConfig(
        name="FCR",
        display_name="Facility Change Request",
        description="Facility Change Request projects",
        filename_pattern="{be_number} - {osuffix} - FCR - {current_year}",
        field_names=[
            "project_type",
            "current_year",
            "project_title",
            "be_number",
            "osuffix",
            "facility_name",
            "facility_number",
            "engineer",
            "imagery",
            "analyst",
            "geologist",
            "reviewer",
            "requestor",
            "request_year",
            "relook",
        ],
    ),
    "COM": ProjectTypeConfig(
        name="COM",
        display_name="Commissioning",
        description="Commissioning projects",
        filename_pattern="{be_number} - COM - {current_year}",
        field_names=[
            "project_type",
            "current_year",
            "project_title",
            "be_number",
            "osuffix",
            "facility_name",
            "engineer",
            "reviewer",
            "imagery",
            "analyst",
            "geologist",
            "requestor",
        ],
    ),
    "CRS": ProjectTypeConfig(
        name="CRS",
        display_name="Corrective Action",
        description="Corrective Action projects",
        filename_pattern="{facility_number} - CRS - {current_year}",
        field_names=[
            "project_type",
            "current_year",
            "project_title",
            "be_number",
            "osuffix",
            "facility_name",
            "facility_number",
            "engineer",
            "imagery",
            "reviewer",
            "analyst",
            "geologist",
            "requestor",
            "request_year",
            "relook",
        ],
    ),
    "OTH": ProjectTypeConfig(
        name="OTH",
        display_name="Other",
        description="Other project types",
        filename_pattern="{document_title} - {current_year}",
        field_names=["project_type", "project_title", "current_year", "document_title", "request_year"],
    ),
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
# (The rest of the helper functions remain the same)


def _get_fields_by_names(field_names: List[str]) -> List[FieldConfig]:
    """A helper to look up full FieldConfig objects from the master registry."""
    return [ALL_FIELDS[name] for name in field_names if name in ALL_FIELDS]


def get_project_type_config(project_type_code: str) -> Optional[ProjectTypeConfig]:
    """Gets the configuration for a specific project type."""
    return PROJECT_TYPES_CONFIG.get(project_type_code)


def get_dialog_fields(project_type_code: str) -> List[FieldConfig]:
    """Gets all fields that should be collected in the creation dialog."""
    config = get_project_type_config(project_type_code)
    if not config:
        return []
    all_fields_for_type = _get_fields_by_names(config.field_names)
    dialog_fields = [
        field
        for field in all_fields_for_type
        if field.collection_stage == CollectionStage.DIALOG
    ]
    return sorted(dialog_fields, key=lambda f: f.tab_order)


def get_metadata_fields(project_type_code: str) -> List[FieldConfig]:
    """Gets all fields that should be collected/edited in the metadata view."""
    config = get_project_type_config(project_type_code)
    if not config:
        return []
    all_fields_for_type = _get_fields_by_names(config.field_names)
    metadata_fields = [
        field
        for field in all_fields_for_type
        if field.collection_stage == CollectionStage.METADATA
    ]
    return sorted(metadata_fields, key=lambda f: (f.column_group or "", f.tab_order))


def get_project_type_display_names() -> Dict[str, str]:
    """Get mapping of project type codes to display names"""
    return {code: config.display_name for code, config in PROJECT_TYPES_CONFIG.items()}
