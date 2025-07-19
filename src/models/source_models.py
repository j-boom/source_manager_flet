# src/models/new_source_models.py

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum

# Updated import to use the new configuration structure and functions
from config.source_types_config import (
    ALL_SOURCE_FIELDS,
    SOURCE_TYPE_FIELDS,
    get_fields_for_source_type,
)

logger = logging.getLogger(__name__)
# =============================================================================
# Core Enumerations
# =============================================================================

class SourceType(Enum):
    """Defines the type of a research source."""
    BOOK = "book"
    ARTICLE = "article"
    STANDARD = "standard"
    WEBSITE = "website"
    REPORT = "report"
    MANUAL = "manual"

@dataclass
class SourceField:
    """
    Represents a single, dynamic field within a source record (e.g., author, title, url).
    """
    name: str
    value: Any
    type: str = "text"
    required: bool = False
    label: Optional[str] = None

    def __post_init__(self):
        if self.label is None:
            self.label = self.name.replace("_", " ").title()


@dataclass
class SourceRecord:
    """
    A flexible, dataclass-based representation of a source that uses the
    SourceType Enum internally for type safety.
    """
    # The model now holds the source_type as an Enum member
    source_type: SourceType
    fields: List[SourceField]

    # --- Core Metadata ---
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    country: Optional[str] = None
    display_name: Optional[str] = None
    date_created: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    used_in: List[str] = field(default_factory=list)

    def get_title(self) -> str:
        """Generates a user-friendly title for the source, driven by the config."""
        if self.display_name:
            return self.display_name

        title_parts = []
        # Use the enum's value (the string) to look up the config
        ordered_field_names = SOURCE_TYPE_FIELDS.get(self.source_type.value, [])
        source_fields_dict = {f.name: f.value for f in self.fields}

        for name in ordered_field_names:
            field_config = ALL_SOURCE_FIELDS.get(name)
            if field_config and field_config.is_title_part:
                value = source_fields_dict.get(name)
                if value:
                    title_parts.append(str(value))

        if title_parts:
            return " - ".join(title_parts)

        return f"Untitled {self.source_type.value} ({self.id[-4:]})"

    def get_field_value(self, field_name: str, default: Any = None) -> Any:
        """Gets the value of a dynamic field by its name."""
        for f in self.fields:
            if f.name == field_name:
                return f.value
        return default

    def set_field_value(self, field_name: str, value: Any):
        """Sets the value of an existing dynamic field by its name."""
        field_found = False
        for f in self.fields:
            if f.name == field_name:
                if f.value != value:
                    f.value = value
                    self.last_modified = datetime.now()
                field_found = True
                break
        if not field_found:
             logger.warning(
                f"Attempted to set value for non-existent field '{field_name}' on source {self.id}"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the SourceRecord to a dictionary for JSON storage."""
        field_values = {f.name: f.value for f in self.fields}
        return {
            "id": self.id,
            # Convert the Enum to its string value for serialization
            "source_type": self.source_type.value,
            "country": self.country,
            "display_name": self.display_name,
            "date_created": self.date_created.isoformat(),
            "last_modified": self.last_modified.isoformat(),
            "used_in": self.used_in,
            **field_values,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SourceRecord":
        """Creates a SourceRecord from a dictionary."""
        source_type_str = data.get("source_type")
        if not source_type_str:
            raise ValueError("Source data must include a 'source_type'.")

        # Convert the string from JSON back into a SourceType Enum member
        try:
            source_type_enum = SourceType(source_type_str)
        except ValueError:
            logger.error(f"Invalid source type '{source_type_str}' found in data.")
            # Fallback or raise a more specific error
            raise ValueError(f"Invalid source type: {source_type_str}")

        fields = []
        expected_fields = get_fields_for_source_type(source_type_str)
        expected_field_names = {f.name for f in expected_fields}

        for field_name, field_config in ALL_SOURCE_FIELDS.items():
            if field_name in expected_field_names or field_name in data:
                fields.append(
                    SourceField(
                        name=field_name,
                        value=data.get(field_name),
                        type=field_config.field_type.value,
                        required=field_config.required,
                        label=field_config.label,
                    )
                )

        date_created_val = data.get("date_created")
        date_created = (
            datetime.fromisoformat(date_created_val)
            if isinstance(date_created_val, str) else datetime.now()
        )
        last_modified_val = data.get("last_modified")
        last_modified = (
            datetime.fromisoformat(last_modified_val)
            if isinstance(last_modified_val, str) else datetime.now()
        )

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            source_type=source_type_enum,
            country=data.get("country"),
            display_name=data.get("display_name"),
            date_created=date_created,
            last_modified=last_modified,
            used_in=data.get("used_in", []),
            fields=fields,
        )


class SourceRecordFactory:
    """A factory to create new SourceRecord objects based on a source type."""
    @staticmethod
    def create_source_record(
        source_type: Union[str, SourceType], initial_values: Optional[Dict[str, Any]] = None
    ) -> SourceRecord:
        """Creates a new SourceRecord instance for a given source type."""
        if initial_values is None:
            initial_values = {}

        # Handle both string and Enum input for flexibility
        if isinstance(source_type, str):
            source_type_str = source_type
            source_type_enum = SourceType(source_type)
        else:
            source_type_str = source_type.value
            source_type_enum = source_type

        field_configs = get_fields_for_source_type(source_type_str)
        if not field_configs:
             raise ValueError(f"Unknown or misconfigured source type: {source_type_str}")

        source_fields = []
        for config in field_configs:
            initial_value = initial_values.get(config.name)
            source_fields.append(
                SourceField(
                    name=config.name,
                    value=initial_value,
                    type=config.field_type.value,
                    required=config.required,
                    label=config.label,
                )
            )
        # Create the record with the Enum member
        return SourceRecord(source_type=source_type_enum, fields=source_fields)