"""
Source Types Configuration

Defines the fields required for each type of master source.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Reusing FieldType definition for consistency
class FieldType(Enum):
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"

class ValidationRule(Enum):
    """Defines validation rules for source fields."""
    REQUIRED = "required"
    EMAIL = "email"
    URL = "url"
    NUMBER = "number"

@dataclass
class SourceFieldConfig:
    """Configuration for a single source metadata field."""
    name: str
    label: str
    field_type: FieldType
    required: bool = False
    hint_text: str = ""
    width: int = 400
    is_filterable: bool = False
    is_title_part: bool = False
    validation_rules: Optional[Dict[ValidationRule, Any]] = None

# A master registry of all possible fields for any source type.
ALL_SOURCE_FIELDS: Dict[str, SourceFieldConfig] = {
    "source_title": SourceFieldConfig(name="source_title", label="Source Title", field_type=FieldType.TEXT, required=True, is_filterable=True, is_title_part=True),
    "authors": SourceFieldConfig(name="authors", label="Authors (comma-separated)", field_type=FieldType.TEXT, hint_text="e.g., Smith, J., Doe, A.,", is_filterable=True),
    "publication_year": SourceFieldConfig(name="publication_year", label="Year", field_type=FieldType.NUMBER, hint_text="e.g., 2023", is_filterable=True, is_title_part=True),
    "publisher": SourceFieldConfig(name="publisher", label="Publisher / Journal", field_type=FieldType.TEXT),
    "url": SourceFieldConfig(name="url", label="URL", field_type=FieldType.TEXT, hint_text="https://..."),
    "report_number": SourceFieldConfig(name="report_number", label="Report / Document No.", field_type=FieldType.TEXT, is_title_part=True),
    "manual_version": SourceFieldConfig(name="manual_version", label="Version", field_type=FieldType.TEXT),
}

# Maps a SourceType enum value to a list of field names from the registry above.
SOURCE_TYPE_FIELDS: Dict[str, List[str]] = {
    "book": ["source_title", "authors", "publication_year", "publisher"],
    "article": ["source_title", "authors", "publication_year", "publisher"],
    "standard": ["source_title", "publication_year", "publisher", "report_number"],
    "website": ["source_title", "url", "authors"],
    "report": ["source_title", "authors", "publication_year", "report_number"],
    "manual": ["source_title", "manual_version", "publisher", "publication_year"],
}

def get_fields_for_source_type(source_type_value: str) -> List[SourceFieldConfig]:
    """
    Returns the list of FieldConfig objects for a given source type value (e.g., 'book').
    """
    field_names = SOURCE_TYPE_FIELDS.get(source_type_value, ["title"]) # Default to just title
    return [ALL_SOURCE_FIELDS[name] for name in field_names if name in ALL_SOURCE_FIELDS]

def get_filterable_fields() -> List[SourceFieldConfig]:
    """New: Returns the list of all field configurations marked as filterable."""
    return [field for field in ALL_SOURCE_FIELDS.values() if field.is_filterable]