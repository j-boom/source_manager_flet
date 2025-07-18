"""
Source Data Models

This file defines the authoritative data structures for all types of sources.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict, fields
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime

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

# =============================================================================
# Source Model
# =============================================================================

@dataclass
class SourceRecord:
    """
    Represents a single, master source record stored in a country file.
    This is the "master copy" of a source, identified by a unique ID.
    """
    id: str  # Unique ID for this source
    source_type: SourceType
    title: str # Generated title display
    country: str  # The country this master source belongs to (e.g., "USA", "Canada")

    # Core metadata for the master record
    source_title: str
    authors: List[str] = field(default_factory=list)
    publication_year: Optional[int] = None
    publisher: Optional[str] = None
    url: Optional[str] = None
    
    # Timestamps for the master record
    date_created: str = field(default_factory=lambda: datetime.now().isoformat())
    last_modified: str = field(default_factory=lambda: datetime.now().isoformat())
    report_number: Optional[str] = None  # For reports and standards
    used_in: List[Dict[str, str]] = field(default_factory=list) # project_id: notes
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializes the dataclass to a dictionary."""
        data = asdict(self)
        data['source_type'] = self.source_type.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SourceRecord:
        """Deserializes a dictionary into a dataclass instance."""
        data['source_type'] = SourceType(data['source_type'])
        # Filter out keys that are not in the dataclass to handle old formats
        field_names = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in field_names}
        return cls(**filtered_data)
@dataclass
class ProjectSourceLink:
    """
    Represents the link between a master SourceRecord and a specific project.
    This object is stored within the project's .json file and holds all
    project-specific context about the source.
    """
    source_id: str  # The ID of the master SourceRecord
    notes: Optional[str] = None
    declassify: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializes the dataclass to a dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ProjectSourceLink:
        """Deserializes a dictionary into a dataclass instance."""
        return cls(**data)
    
