"""
Project Data Models for Source Management System
Handles both JSON persistence and database integration
"""

from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any, List
import json
import uuid
from datetime import datetime
from pathlib import Path


@dataclass
class ProjectMetadata:
    """Core project metadata that goes into both JSON and database"""
    project_uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_type: str = ""
    display_name: str = ""
    facility_number: str = ""
    suffix: str = ""
    year: str = ""
    created_by: str = ""  # OS login
    created_by_display: str = ""  # User's display name
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Dynamic fields based on project type (stored as JSON)
    type_specific_data: Dict[str, Any] = field(default_factory=dict)
    
    # PowerPoint integration
    powerpoint_path: Optional[str] = None
    powerpoint_last_read: Optional[str] = None
    
    def generate_filename(self) -> str:
        """Generate JSON filename: facility_number-suffix-type-year.json"""
        return f"{self.facility_number}-{self.suffix}-{self.project_type}-{self.year}.json"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectMetadata':
        """Create instance from dictionary"""
        return cls(**data)


@dataclass
class SlideData:
    """Individual slide information for PowerPoint projects"""
    slide_id: str
    title: str = ""
    sources: List[str] = field(default_factory=list)  # List of source UUIDs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


@dataclass
class ProjectData:
    """Complete project data structure for JSON persistence"""
    metadata: ProjectMetadata
    slides: Dict[str, SlideData] = field(default_factory=dict)  # slide_id -> SlideData
    source_assignments: List[str] = field(default_factory=list)  # Ordered list of source UUIDs
    project_settings: Dict[str, Any] = field(default_factory=dict)  # Project-specific settings
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "metadata": self.metadata.to_dict(),
            "slides": {k: v.to_dict() for k, v in self.slides.items()},
            "source_assignments": self.source_assignments,
            "project_settings": self.project_settings
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectData':
        """Create instance from dictionary"""
        metadata = ProjectMetadata.from_dict(data.get("metadata", {}))
        slides = {k: SlideData(**v) for k, v in data.get("slides", {}).items()}
        
        return cls(
            metadata=metadata,
            slides=slides,
            source_assignments=data.get("source_assignments", []),
            project_settings=data.get("project_settings", {})
        )
    
    def save_to_json(self, file_path: Path) -> bool:
        """Save project data to JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving project to {file_path}: {e}")
            return False
    
    @classmethod
    def load_from_json(cls, file_path: Path) -> Optional['ProjectData']:
        """Load project data from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            print(f"Error loading project from {file_path}: {e}")
            return None


@dataclass
class ProjectRegistryEntry:
    """Database entry for project registry (for discovery and analytics)"""
    project_uuid: str
    project_type: str
    display_name: str
    facility_number: str
    file_path: str
    created_by: str
    created_by_display: str
    created_at: str
    updated_at: str
    is_active: bool = True
    
    # Database fields
    id: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
