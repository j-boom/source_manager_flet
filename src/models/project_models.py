# File: src/models/project_models.py

"""
Project Data Models

This file defines the authoritative data structures for projects and their
relationship to sources.
"""
from __future__ import annotations
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict, fields
from typing import List, Dict, Any, Optional
from enum import Enum


class FieldType(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    CHECKBOX = "checkbox"
    DROPDOWN = "dropdown"
    DATE = "date"
    BOOLEAN = "boolean"
    TEXTAREA = "textarea"


class ValidationRule(str, Enum):
    PATTERN = "pattern"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"


@dataclass
class FieldConfig:
    name: str
    label: str
    field_type: FieldType
    required: bool = False
    is_filterable: bool = False
    is_title_part: bool = False
    hint_text: Optional[str] = None
    options: Optional[List[str]] = None
    width: Optional[int] = None
    validation_rules: Dict[ValidationRule, Any] = field(default_factory=dict)


@dataclass
class ProjectSourceLink:
    """
    Represents the link between a master SourceRecord and a specific project.
    This object is stored within the project's .json file and holds all
    project-specific context about the source.
    """

    source_id: str  # The ID of the master SourceRecord
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the dataclass to a dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ProjectSourceLink:
        """
        Deserializes a dictionary into a dataclass instance.
        Handles backward compatibility for old format with 'notes' and 'declassify'.
        """
        if 'notes' in data or 'declassify' in data:
            metadata = data.get('metadata', {})
            if 'notes' in data and data['notes'] is not None:
                metadata.setdefault('usage_notes', data.get('notes'))
            if 'declassify' in data and data['declassify'] is not None:
                metadata.setdefault('declassify_info', data.get('declassify'))
            
            data['metadata'] = metadata
            data.pop('notes', None)
            data.pop('declassify', None)
            
        return cls(**{k: v for k, v in data.items() if k in [f.name for f in fields(cls)]})


@dataclass
class Project:
    """
    Represents a single project file. It contains the project's metadata
    and a list of links to the master sources it uses.
    """

    project_id: str  # Unique ID for this project
    project_type: str
    project_title: str
    file_path: Path  # The location where this project file is saved

    # A dictionary to hold all dynamic metadata based on the project type
    metadata: Dict[str, Any] = field(default_factory=dict)

    # The ordered list of sources used by this project
    sources: List[ProjectSourceLink] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the project to a dictionary for saving."""
        return {
            "project_id": self.project_id,
            "project_type": self.project_type,
            "project_title": self.project_title,
            "file_path": str(self.file_path.as_posix()),
            "metadata": self.metadata,
            "sources": [s.to_dict() for s in self.sources],
        }

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], file_path: Optional[Path] = None
    ) -> Project:
        """Creates a Project instance from a dictionary."""
        return cls(
            project_id=data.get("project_id", ""),
            project_type=data.get("project_type", ""),
            project_title=data.get("project_title", ""),
            file_path=Path(data.get("file_path", "")),
            metadata=data.get("metadata", {}),
            sources=[ProjectSourceLink.from_dict(s) for s in data.get("sources", [])],
        )

    def save(self):
        """Saves the project data to its file_path."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load(cls, file_path: Path) -> Optional[Project]:
        """Loads a project from a JSON file."""
        if not file_path.exists():
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data, file_path)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error loading project from {file_path}: {e}")
            return None

    def add_source(self, source_id: str, metadata: Dict[str, Any] = None):
        """Adds a source to the project. Sources are ordered by their position in the list."""
        if source_id not in [s.source_id for s in self.sources]:
            link = ProjectSourceLink(source_id=source_id, metadata=metadata or {})
            self.sources.append(link)

    def remove_source(self, source_id: str):
        """Removes a source link from the project."""
        self.sources = [s for s in self.sources if s.source_id != source_id]

    def associate_powerpoint_file(self, powerpoint_file: str):
        """
        Associates a PowerPoint file with the project.

        Args:
            powerpoint_file: The file path of the PowerPoint file to associate.
        """
        self.metadata["powerpoint_file"] = powerpoint_file
