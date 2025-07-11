"""
Project Data Models

This file defines the authoritative data structures for projects and their
relationship to sources.
"""
from __future__ import annotations
import json
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, field, asdict, fields
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import the master SourceRecord for type hinting
from .source_models import SourceRecord

# =============================================================================
# Core Enumerations
# =============================================================================

class ProjectType(Enum):
    """Defines the type of a project."""
    CCR = "CCR"
    GSC = "GSC"
    STD = "STD"
    FCR = "FCR"
    COM = "COM"
    CRS = "CRS"
    OTH = "OTH"

# =============================================================================
# Linking Model
# =============================================================================

@dataclass
class ProjectSourceLink:
    """
    This is the key to the solution. It links a Project to a master SourceRecord.
    It stores the project-specific ordering and notes.
    """
    source_id: str  # The ID of the master SourceRecord
    order: int      # The display order of this source within the project
    notes: str = "" # User's notes about this source for this specific project

# =============================================================================
# Project Model
# =============================================================================

@dataclass
class Project:
    """
    Represents a single project file. It contains the project's metadata
    and a list of links to the master sources it uses.
    """
    project_id: str # Unique ID for this project
    project_type: ProjectType
    title: str
    file_path: Path # The location where this project file is saved

    # A dictionary to hold all dynamic metadata based on the project type
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # The ordered list of sources used by this project
    sources: List[ProjectSourceLink] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the project to a dictionary for saving."""
        data = asdict(self)
        data['project_type'] = self.project_type.value
        data['file_path'] = str(self.file_path.as_posix()) # Use as_posix for cross-platform compatibility
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Project:
        """Creates a Project instance from a dictionary."""
        # Check if this is an old format file (missing required new format fields)
        if 'project_type' not in data:
            raise ValueError("This appears to be an old format project file. Please run migration first.")
        
        # Handle project_type conversion safely
        if isinstance(data['project_type'], str):
            data['project_type'] = ProjectType(data['project_type'])
        elif not isinstance(data['project_type'], ProjectType):
            raise ValueError(f"Invalid project_type: {data['project_type']}")
        
        # Handle file_path safely
        if 'file_path' in data:
            data['file_path'] = Path(data['file_path'])
        else:
            raise ValueError("Missing required field: file_path")
        
        if 'sources' in data and data['sources']:
            data['sources'] = [ProjectSourceLink(**s) for s in data['sources']]
        
        field_names = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in field_names}
        return cls(**filtered_data)

    def save(self):
        """Saves the project data to its file_path."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load(cls, file_path: Path) -> Optional[Project]:
        """Loads a project from a JSON file."""
        if not file_path.exists():
            return None
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error loading project from {file_path}: {e}")
            return None

    def add_source(self, source_id: str, notes: str = ""):
        """Adds a source to the project, maintaining order."""
        if source_id not in [s.source_id for s in self.sources]:
            new_order = (max(s.order for s in self.sources) + 1) if self.sources else 1
            link = ProjectSourceLink(source_id=source_id, order=new_order, notes=notes)
            self.sources.append(link)
            self.sources.sort(key=lambda s: s.order)

    def remove_source(self, source_id: str):
        """Removes a source link from the project."""
        self.sources = [s for s in self.sources if s.source_id != source_id]
