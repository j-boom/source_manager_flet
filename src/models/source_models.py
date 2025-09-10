# src/models/source_models.py

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

@dataclass
class SourceFieldConfig:
    name: str
    label: str
    field_type: str
    required: bool = False
    is_filterable: bool = False
    is_title_part: bool = False
    hint_text: Optional[str] = None
    width: Optional[int] = None

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
    A flexible, dataclass-based representation of a source.
    """
    source_type: str
    fields: List[SourceField]

    # --- Core Metadata ---
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    country: Optional[str] = None
    display_name: Optional[str] = None
    date_created: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    used_in: List[str] = field(default_factory=list)

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
            "source_type": self.source_type,
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
        source_type = data.get("source_type")
        if not source_type:
            raise ValueError("Source data must include a 'source_type'.")

        fields = []
        # In a dynamic system, we don't know all possible fields ahead of time.
        # We will rely on the data dictionary to define the fields.
        reserved_keys = ["id", "source_type", "country", "display_name", "date_created", "last_modified", "used_in"]
        for key, value in data.items():
            if key not in reserved_keys:
                fields.append(SourceField(name=key, value=value))

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
            source_type=source_type,
            country=data.get("country"),
            display_name=data.get("display_name"),
            date_created=date_created,
            last_modified=last_modified,
            used_in=data.get("used_in", []),
            fields=fields,
        )
