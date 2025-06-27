"""
Data Models Configuration - Defines all dataclasses for JSON serialization
All JSON data structures should be defined here as dataclasses
"""

from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any, List
import json
import uuid
from datetime import datetime
from pathlib import Path


@dataclass
class ProjectMetadata:
    """Metadata section of project JSON files"""
    folder_path: str
    filename: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectMetadata':
        """Create instance from dictionary"""
        return cls(**data)


@dataclass
class CustomerInfo:
    """Customer information section of project JSON files"""
    key: str
    name: str
    number: str
    suffix: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CustomerInfo':
        """Create instance from dictionary"""
        return cls(**data)


@dataclass
class ProjectSource:
    """Source reference within a project"""
    source_id: str  # Reference to the master source ID
    usage_notes: str  # How this source is used in this project
    user_description: str  # User's description for this project context
    date_added: str  # When added to this project
    added_by: str  # Who added it to this project
    citation_format: Optional[str] = None  # Custom citation format for this project
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectSource':
        """Create instance from dictionary"""
        return cls(**data)


@dataclass
class ProjectCitation:
    """Citation/slide reference within a project"""
    citation_id: str  # Unique citation ID within this project
    title: str  # Citation/slide title
    content: Optional[str] = None  # Citation content or slide notes
    source_references: Optional[List[str]] = None  # List of source IDs this citation references
    slide_number: Optional[int] = None  # Slide number if this is a presentation citation
    date_created: str = ""  # When citation was created
    created_by: str = ""  # Who created the citation
    last_modified: str = ""  # Last modification date
    modified_by: str = ""  # Who last modified
    
    def __post_init__(self):
        """Initialize source_references list if None"""
        if self.source_references is None:
            self.source_references = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectCitation':
        """Create instance from dictionary"""
        return cls(**data)


@dataclass
class ProjectData:
    """Complete project data structure for JSON persistence"""
    project_id: str
    project_suffix: str
    project_type: str
    created_date: str
    metadata: ProjectMetadata
    uuid: str
    customer: CustomerInfo
    title: str
    document_title: Optional[str] = None
    description: Optional[str] = None
    sources: Optional[List[ProjectSource]] = None  # Project-specific sources
    citations: Optional[List[ProjectCitation]] = None  # Project-specific citations/slides
    
    def __post_init__(self):
        """Ensure nested objects are dataclass instances"""
        if isinstance(self.metadata, dict):
            self.metadata = ProjectMetadata.from_dict(self.metadata)
        if isinstance(self.customer, dict):
            self.customer = CustomerInfo.from_dict(self.customer)
        
        # Initialize sources list if None
        if self.sources is None:
            self.sources = []
        elif self.sources and len(self.sources) > 0 and isinstance(self.sources[0], dict):
            self.sources = [ProjectSource.from_dict(source) for source in self.sources if isinstance(source, dict)]
        
        # Initialize citations list if None
        if self.citations is None:
            self.citations = []
        elif self.citations and len(self.citations) > 0 and isinstance(self.citations[0], dict):
            self.citations = [ProjectCitation.from_dict(citation) for citation in self.citations if isinstance(citation, dict)]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectData':
        """Create instance from dictionary"""
        return cls(**data)
    
    def save_to_json(self, file_path: Path) -> bool:
        """Save project data to JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)
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
    
    # Helper methods for managing sources
    def add_source(self, source_id: str, usage_notes: str, user_description: str, 
                   added_by: str, citation_format: Optional[str] = None) -> None:
        """Add a source to this project"""
        if self.sources is None:
            self.sources = []
        
        # Remove existing source if it exists (to update it)
        self.sources = [s for s in self.sources if s.source_id != source_id]
        
        # Add new source
        new_source = ProjectSource(
            source_id=source_id,
            usage_notes=usage_notes,
            user_description=user_description,
            date_added=datetime.now().isoformat(),
            added_by=added_by,
            citation_format=citation_format
        )
        self.sources.append(new_source)
    
    def remove_source(self, source_id: str) -> bool:
        """Remove a source from this project"""
        if self.sources is None:
            return False
        
        original_count = len(self.sources)
        self.sources = [s for s in self.sources if s.source_id != source_id]
        return len(self.sources) < original_count
    
    def get_source(self, source_id: str) -> Optional[ProjectSource]:
        """Get a specific source from this project"""
        if self.sources is None:
            return None
        
        for source in self.sources:
            if source.source_id == source_id:
                return source
        return None
    
    # Helper methods for managing citations
    def add_citation(self, citation_id: str, title: str, content: Optional[str] = None,
                     source_references: Optional[List[str]] = None, slide_number: Optional[int] = None,
                     created_by: str = "") -> None:
        """Add a citation to this project"""
        if self.citations is None:
            self.citations = []
        
        # Remove existing citation if it exists (to update it)
        self.citations = [c for c in self.citations if c.citation_id != citation_id]
        
        # Add new citation
        new_citation = ProjectCitation(
            citation_id=citation_id,
            title=title,
            content=content,
            source_references=source_references or [],
            slide_number=slide_number,
            date_created=datetime.now().isoformat(),
            created_by=created_by,
            last_modified=datetime.now().isoformat(),
            modified_by=created_by
        )
        self.citations.append(new_citation)
    
    def remove_citation(self, citation_id: str) -> bool:
        """Remove a citation from this project"""
        if self.citations is None:
            return False
        
        original_count = len(self.citations)
        self.citations = [c for c in self.citations if c.citation_id != citation_id]
        return len(self.citations) < original_count
    
    def get_citation(self, citation_id: str) -> Optional[ProjectCitation]:
        """Get a specific citation from this project"""
        if self.citations is None:
            return None
        
        for citation in self.citations:
            if citation.citation_id == citation_id:
                return citation
        return None
    
    def get_citations_by_source(self, source_id: str) -> List[ProjectCitation]:
        """Get all citations that reference a specific source"""
        if self.citations is None:
            return []
        
        matching_citations = []
        for citation in self.citations:
            if citation.source_references and source_id in citation.source_references:
                matching_citations.append(citation)
        return matching_citations


@dataclass
class WindowConfig:
    """Window configuration for user settings"""
    width: int
    height: int
    x: Optional[int] = None
    y: Optional[int] = None
    maximized: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WindowConfig':
        """Create instance from dictionary"""
        return cls(**data)


@dataclass
class ThemeConfig:
    """Theme configuration for user settings"""
    mode: str = "light"  # "light" or "dark"
    color: str = "blue"  # "red", "blue", "orange", "green", "yellow", "purple", "indigo"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThemeConfig':
        """Create instance from dictionary"""
        return cls(**data)


@dataclass
class RecentSite:
    """Recent site entry for user config"""
    display_name: str
    path: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RecentSite':
        """Create instance from dictionary"""
        return cls(**data)


@dataclass
class UserConfig:
    """Complete user configuration data structure"""
    window: WindowConfig
    theme: ThemeConfig
    last_page: str = "home"
    recent_sites: List[RecentSite] = field(default_factory=list)
    display_name: Optional[str] = None  # User's display name for personalization
    setup_completed: bool = False  # Whether initial setup is complete
    
    def __post_init__(self):
        """Ensure nested objects are dataclass instances"""
        if isinstance(self.window, dict):
            self.window = WindowConfig.from_dict(self.window)
        if isinstance(self.theme, dict):
            self.theme = ThemeConfig.from_dict(self.theme)
        if self.recent_sites and len(self.recent_sites) > 0 and isinstance(self.recent_sites[0], dict):
            self.recent_sites = [RecentSite.from_dict(site) for site in self.recent_sites if isinstance(site, dict)]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserConfig':
        """Create instance from dictionary"""
        return cls(**data)
    
    def save_to_json(self, file_path: Path) -> bool:
        """Save user config to JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving user config to {file_path}: {e}")
            return False
    
    @classmethod
    def load_from_json(cls, file_path: Path) -> Optional['UserConfig']:
        """Load user config from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            print(f"Error loading user config from {file_path}: {e}")
            return None


# Helper functions for working with dataclasses and JSON
def dataclass_to_json(obj, file_path: Path) -> bool:
    """Save any dataclass to JSON file"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(obj), f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving dataclass to {file_path}: {e}")
        return False


def json_to_dataclass(cls, file_path: Path):
    """Load JSON file as dataclass"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
    except Exception as e:
        print(f"Error loading JSON as dataclass from {file_path}: {e}")
        return None
