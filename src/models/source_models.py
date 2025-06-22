"""
Database Models for Source Management System
Updated to support dynamic source types and usage notes
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import json
from datetime import datetime


@dataclass
class Source:
    """Database model for sources - single source of truth"""
    uuid: str
    source_type: str  # image, document, etc.
    title: str
    source_metadata: Optional[str] = None  # JSON blob for dynamic fields
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    # Legacy fields for backward compatibility
    originator: Optional[str] = None
    identifier: Optional[str] = None
    url: Optional[str] = None
    date_created: Optional[str] = None
    content_type: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    checksum: Optional[str] = None
    
    # Database fields
    id: Optional[int] = None
    
    def get_metadata_dict(self) -> Dict[str, Any]:
        """Get source metadata as dictionary"""
        if self.source_metadata:
            try:
                return json.loads(self.source_metadata)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_metadata_dict(self, metadata: Dict[str, Any]):
        """Set source metadata from dictionary"""
        self.source_metadata = json.dumps(metadata, indent=2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


@dataclass
class ProjectSource:
    """Database model for project-source associations"""
    project_id: int
    source_id: int
    usage_notes: str  # Required field describing how source is used in project
    assignment_order: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    # Database fields
    id: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


@dataclass
class ProjectSourceDetails:
    """Combined view of project-source association with source details"""
    # From project_sources table
    association_id: int
    project_id: int
    source_id: int
    usage_notes: str
    assignment_order: Optional[int] = None
    association_created_at: Optional[str] = None
    
    # From sources table
    source_uuid: str = ""
    source_type: str = ""
    title: str = ""
    source_metadata: Optional[str] = None
    source_created_at: Optional[str] = None
    
    def get_metadata_dict(self) -> Dict[str, Any]:
        """Get source metadata as dictionary"""
        if self.source_metadata:
            try:
                return json.loads(self.source_metadata)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
