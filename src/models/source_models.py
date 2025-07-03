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
    Represents a single, master source record stored in a regional file.
    This is the "master copy" of a source, identified by a unique ID.
    """
    id: str  # Unique ID for this source (e.g., "src_a1b2c3d4")
    source_type: SourceType
    title: str
    region: str  # The region this master source belongs to (e.g., "ROW", "General")
    
    # Core metadata for the master record
    authors: List[str] = field(default_factory=list)
    publication_year: Optional[int] = None
    publisher: Optional[str] = None
    url: Optional[str] = None
    
    # Timestamps for the master record
    date_created: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_modified: str = field(default_factory=lambda: datetime.utcnow().isoformat())

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
