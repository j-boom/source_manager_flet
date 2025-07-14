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
    Display order is determined by position in the sources list.
    """
    source_id: str  # The ID of the master SourceRecord
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
    project_title: str
    file_path: Path # The location where this project file is saved

    # A dictionary to hold all dynamic metadata based on the project type
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # The ordered list of sources used by this project
    sources: List[ProjectSourceLink] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the project to a dictionary for saving in the desired format."""
        # Extract metadata fields for restructuring
        metadata = self.metadata or {}
        
        # Build project_metadata section
        project_metadata = {
            "project_id": self.project_id,
            "project_type": self.project_type.value,
            "title": self.project_title,
            "file_path": str(self.file_path.as_posix()),
            "requestor": metadata.get("requestor", ""),
            "request_year": metadata.get("request_year", ""),
            "relook": metadata.get("relook", False)
        }
        
        # Build team section
        team = {
            "engineer": metadata.get("engineer", ""),
            "all-source analyst": metadata.get("analyst", ""),
            "imagery analyst": metadata.get("imagery", ""),
            "geologist": metadata.get("geologist", ""),
            "engineer senior reviewer": metadata.get("reviewer", "")
        }
        
        # Build facility_information section
        facility_information = {
            "benjamin": metadata.get("be_number", ""),
            "oscar": metadata.get("osuffix", ""),
            "Facility Name": metadata.get("facility_name", ""),
            "Facility Surrogate Key": metadata.get("facility_number", "")
        }
        
        # Build slide_data section (initialize empty for new projects)
        slide_data = metadata.get("slide_data", {})
        
        # Build sources with new field names
        sources = []
        for i, source_link in enumerate(self.sources):
            sources.append({
                "uuid": source_link.source_id,
                "order": i + 1,  # Use 1-based index for order
                "usage_notes": source_link.notes or ""
            })
        
        return {
            "project_metadata": project_metadata,
            "team": team,
            "facility_information": facility_information,
            "slide_data": slide_data,
            "sources": sources,
            "powerpoint_file": metadata.get("powerpoint_file", ""),
            "number_header_citations": metadata.get("number_header_citations", 0)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], file_path: Optional[Path] = None) -> Project:
        """Creates a Project instance from a dictionary, handling both old and new formats."""
        
        # Check if this is the new format (has project_metadata)
        if 'project_metadata' in data:
            # New format - extract from nested structure
            project_metadata = data.get('project_metadata', {})
            team = data.get('team', {})
            facility_info = data.get('facility_information', {})
            slide_data = data.get('slide_data', {})
            
            # Rebuild metadata from the separate sections
            metadata = {
                # Team information
                "engineer": team.get("engineer", ""),
                "analyst": team.get("all-source analyst", ""),
                "imagery": team.get("imagery analyst", ""),
                "geologist": team.get("geologist", ""),
                "reviewer": team.get("engineer senior reviewer", ""),
                
                # Facility information
                "be_number": facility_info.get("benjamin", ""),
                "osuffix": facility_info.get("oscar", ""),
                "facility_name": facility_info.get("Facility Name", ""),
                "facility_number": facility_info.get("Facility Surrogate Key", ""),
                
                # Project metadata
                "requestor": project_metadata.get("requestor", ""),
                "request_year": project_metadata.get("request_year", ""),
                "relook": project_metadata.get("relook", False),
                
                # Additional data
                "slide_data": slide_data,
                "powerpoint_file": data.get("powerpoint_file", ""),
                "number_header_citations": data.get("number_header_citations", 0)
            }
            
            # Convert sources from new format
            sources = []
            for source_data in data.get('sources', []):
                sources.append(ProjectSourceLink(
                    source_id=source_data.get('uuid', ''),
                    notes=source_data.get('usage_notes', '')
                ))
            
            return cls(
                project_id=project_metadata.get('project_id', ''),
                project_type=ProjectType(project_metadata.get('project_type', 'STD')),
                project_title=project_metadata.get('title', ''),
                file_path=Path(project_metadata.get('file_path', '')),
                metadata=metadata,
                sources=sources
            )
        else:
            # Old format - use existing logic with better error handling
            if 'project_type' not in data:
                # Try to extract project type from filename if not in data
                file_path = data.get('file_path', '')
                if ' - STD - ' in str(file_path):
                    data['project_type'] = 'STD'
                elif ' - COM - ' in str(file_path):
                    data['project_type'] = 'COM'
                elif ' - FCR - ' in str(file_path):
                    data['project_type'] = 'FCR'
                elif ' - GSC - ' in str(file_path):
                    data['project_type'] = 'GSC'
                elif ' - CCR - ' in str(file_path):
                    data['project_type'] = 'CCR'
                elif ' - CRS - ' in str(file_path):
                    data['project_type'] = 'CRS'
                else:
                    data['project_type'] = 'STD'  # Default fallback
                    
            data['project_type'] = ProjectType(data['project_type'])
            
            # Handle missing file_path - use the file path from the load method
            if 'file_path' not in data:
                if file_path:
                    data['file_path'] = str(file_path)
                else:
                    data['file_path'] = str(Path.cwd())  # Fallback
            data['file_path'] = Path(data['file_path'])
            
            # Handle missing project_id - generate from filename or use fallback
            if 'project_id' not in data:
                if file_path:
                    # Extract project ID from filename (e.g., "2023123002 - CA123 - FCR - 2023.json" -> "2023123002")
                    filename = file_path.stem
                    project_id = filename.split(' - ')[0] if ' - ' in filename else filename
                    data['project_id'] = project_id
                else:
                    data['project_id'] = 'LEGACY_PROJECT'
            
            # Handle missing title - generate from filename or use fallback
            if 'project_title' not in data:
                if file_path:
                    # Use filename without extension as title
                    data['project_title'] = file_path.stem
                else:
                    data['project_title'] = 'Legacy Project'
            
            # Handle missing metadata - ensure it exists
            if 'metadata' not in data:
                data['metadata'] = {}
            
            # Handle missing sources - ensure it exists
            if 'sources' not in data:
                data['sources'] = []
            
            if 'sources' in data and data['sources']:
                # Handle old format sources - map fields to new structure
                converted_sources = []
                for source_data in data['sources']:
                    # Create new format source link (order field removed, using list position)
                    new_source = {
                        'source_id': source_data.get('source_id', ''),
                        'notes': source_data.get('notes', '')
                    }
                    converted_sources.append(ProjectSourceLink(**new_source))
                data['sources'] = converted_sources
            
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
            return cls.from_dict(data, file_path)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error loading project from {file_path}: {e}")
            return None

    def add_source(self, source_id: str, notes: str = ""):
        """Adds a source to the project. Sources are ordered by their position in the list."""
        if source_id not in [s.source_id for s in self.sources]:
            link = ProjectSourceLink(source_id=source_id, notes=notes)
            self.sources.append(link)

    def remove_source(self, source_id: str):
        """Removes a source link from the project."""
        self.sources = [s for s in self.sources if s.source_id != source_id]
