"""
Source Types Configuration
Defines source types and their specific fields for the regional source management system

TODO: Replace placeholder source types with your actual dataclasses from local machine
Place your existing source dataclasses in the section marked "SOURCE TYPE DEFINITIONS"
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


# =============================================================================
# SOURCE TYPE DEFINITIONS - REPLACE WITH YOUR ACTUAL DATACLASSES
# =============================================================================

class SourceType(Enum):
    """Source types - replace with your actual source types"""
    BOOK = "book"
    ARTICLE = "article"
    STANDARD = "standard"
    WEBSITE = "website"
    REPORT = "report"
    MANUAL = "manual"
    # TODO: Add your actual source types here


@dataclass
class ProjectUsage:
    """Tracks how a source is used in a specific project"""
    project_path: str              # Full path to the project JSON file
    project_title: str             # Human-readable project title
    usage_notes: str               # Why this source was added to this project
    user_description: str          # User's description for this project context
    date_added: str                # When added to this project
    added_by: str                  # Who added it to this project
    citation_format: Optional[str] = None  # Custom citation format for this project


@dataclass
class SourceRecord:
    """
    Base source record structure
    TODO: Replace this with your actual source dataclass structure
    """
    # Core identification
    id: str                        # Unique source ID
    source_type: SourceType        # Type of source
    title: str                     # Source title
    
    # Regional management
    region: str                    # Primary region (ROW, Other, Downtown, etc.)
    
    # Project usage tracking
    project_usage: Optional[List[ProjectUsage]] = None  # Which projects use this source
    
    # Master record metadata
    date_created: str = ""         # When first added to master
    created_by: str = ""           # Who first added to master
    last_modified: str = ""        # Last modification date
    modified_by: str = ""          # Who last modified
    
    # TODO: Add your actual source fields here
    # Common fields might include:
    # authors: List[str]
    # year: Optional[int]
    # publisher: Optional[str]
    # isbn: Optional[str]
    # doi: Optional[str]
    # url: Optional[str]
    # etc.
    
    def __post_init__(self):
        if self.project_usage is None:
            self.project_usage = []
    
    def add_project_usage(self, project_path: str, project_title: str, 
                         usage_notes: str, user_description: str, added_by: str) -> None:
        """Add usage tracking for a project"""
        if self.project_usage is None:
            self.project_usage = []
            
        # Remove existing usage for this project (if any)
        self.project_usage = [u for u in self.project_usage if u.project_path != project_path]
        
        # Add new usage record
        usage = ProjectUsage(
            project_path=project_path,
            project_title=project_title,
            usage_notes=usage_notes,
            user_description=user_description,
            date_added=datetime.now().isoformat(),
            added_by=added_by
        )
        self.project_usage.append(usage)
        
        # Update master record metadata
        self.last_modified = datetime.now().isoformat()
        self.modified_by = added_by
    
    def remove_project_usage(self, project_path: str) -> bool:
        """Remove usage tracking for a project"""
        if self.project_usage is None:
            return False
            
        initial_count = len(self.project_usage)
        self.project_usage = [u for u in self.project_usage if u.project_path != project_path]
        return len(self.project_usage) < initial_count
    
    def get_project_usage(self, project_path: str) -> Optional[ProjectUsage]:
        """Get usage record for a specific project"""
        if self.project_usage is None:
            return None
            
        for usage in self.project_usage:
            if usage.project_path == project_path:
                return usage
        return None
    
    def is_used_by_project(self, project_path: str) -> bool:
        """Check if this source is used by a specific project"""
        if self.project_usage is None:
            return False
            
        return any(u.project_path == project_path for u in self.project_usage)


# =============================================================================
# REGIONAL MAPPING CONFIGURATION
# =============================================================================

@dataclass
class RegionalMapping:
    """Maps project directory patterns to regional source files"""
    region_name: str
    directory_patterns: List[str]  # Glob patterns to match project directories
    display_name: str             # User-friendly region name
    description: str              # Description of the region
    priority: int = 0             # Priority for overlapping patterns (higher = first match)


# Regional source mappings - based on your existing directory structure
REGIONAL_MAPPINGS = [
    RegionalMapping(
        region_name="ROW",
        directory_patterns=[
            "**/ROW/**",
            "**/Right_of_Way/**", 
            "**/ROW_Projects/**",
            "**/Directory_Source_Citations/ROW/**"
        ],
        display_name="Right of Way",
        description="Sources specific to Right of Way projects",
        priority=10
    ),
    RegionalMapping(
        region_name="Other_Projects",
        directory_patterns=[
            "**/Other_Projects/**",
            "**/Other/**",
            "**/Directory_Source_Citations/Other Projects/**"
        ],
        display_name="Other Projects",
        description="General and miscellaneous project sources",
        priority=8
    ),
    # Fallback for unmatched directories
    RegionalMapping(
        region_name="General",
        directory_patterns=["**"],  # Matches everything
        display_name="General Sources",
        description="Default sources for unclassified projects",
        priority=1
    )
]


# =============================================================================
# REGIONAL SOURCE MANAGER
# =============================================================================

class RegionalSourceManager:
    """Manages regional source files and project usage tracking"""
    
    def __init__(self, master_sources_dir: Optional[str] = None):
        """Initialize with master sources directory"""
        import os
        from pathlib import Path
        
        if master_sources_dir is None:
            # Default to a subdirectory in the app's data directory
            # This can be changed to Program Files or another location
            master_sources_dir = os.path.join(os.path.dirname(__file__), "..", "data", "master_sources")
        
        self.master_sources_dir = Path(master_sources_dir)
        self.master_sources_dir.mkdir(parents=True, exist_ok=True)
    
    def get_region_for_project(self, project_path: str) -> str:
        """Determine the region for a project based on its directory path"""
        from pathlib import Path
        import fnmatch
        
        project_path_obj = Path(project_path).resolve()
        project_str = str(project_path_obj)
        
        # Sort mappings by priority (higher priority first)
        sorted_mappings = sorted(REGIONAL_MAPPINGS, key=lambda m: m.priority, reverse=True)
        
        for mapping in sorted_mappings:
            for pattern in mapping.directory_patterns:
                if fnmatch.fnmatch(project_str, pattern) or fnmatch.fnmatch(project_str.replace('\\', '/'), pattern):
                    return mapping.region_name
        
        # Fallback to General if no matches
        return "General"
    
    def get_master_sources_file(self, region: str) -> str:
        """Get the path to the master sources JSON file for a region"""
        return str(self.master_sources_dir / f"{region}_sources.json")
    
    def load_sources_for_region(self, region: str) -> List[Dict[str, Any]]:
        """Load all sources for a specific region"""
        import json
        
        sources_file = self.get_master_sources_file(region)
        
        try:
            with open(sources_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('sources', [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_sources_for_region(self, region: str, sources: List[Dict[str, Any]]) -> bool:
        """Save sources for a specific region"""
        import json
        
        sources_file = self.get_master_sources_file(region)
        
        try:
            data = {
                "metadata": {
                    "region": region,
                    "total_sources": len(sources),
                    "last_updated": datetime.now().isoformat(),
                    "version": "1.0"
                },
                "sources": sources
            }
            
            with open(sources_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving sources for region {region}: {e}")
            return False
    
    def get_sources_for_project(self, project_path: str) -> tuple[str, List[Dict[str, Any]]]:
        """Get all sources available for a project (region-specific)"""
        region = self.get_region_for_project(project_path)
        sources = self.load_sources_for_region(region)
        return region, sources
    
    def add_source_to_project(self, project_path: str, project_title: str, 
                            source_data: Dict[str, Any], usage_notes: str, 
                            user_description: str, added_by: str) -> bool:
        """
        Add a source to a project and update the master regional file
        
        Args:
            project_path: Path to the project JSON file
            project_title: Human-readable project title
            source_data: Source data dictionary
            usage_notes: Why this source was added (for tagging)
            user_description: User's description of the source
            added_by: Username of person adding the source
            
        Returns:
            True if successful, False otherwise
        """
        region = self.get_region_for_project(project_path)
        sources = self.load_sources_for_region(region)
        
        # Generate unique ID if not provided
        if 'id' not in source_data:
            import uuid
            source_data['id'] = f"src_{uuid.uuid4().hex[:8]}"
        
        source_id = source_data['id']
        
        # Find existing source or create new
        existing_source = None
        for i, source in enumerate(sources):
            if source.get('id') == source_id:
                existing_source = i
                break
        
        if existing_source is not None:
            # Update existing source
            source = sources[existing_source]
        else:
            # Create new source
            source = source_data.copy()
            source['region'] = region
            source['date_created'] = datetime.now().isoformat()
            source['created_by'] = added_by
            source['project_usage'] = []
            sources.append(source)
            existing_source = len(sources) - 1
        
        # Add/update project usage
        project_usage = source.get('project_usage', [])
        
        # Remove existing usage for this project
        project_usage = [u for u in project_usage if u.get('project_path') != project_path]
        
        # Add new usage record
        project_usage.append({
            'project_path': project_path,
            'project_title': project_title,
            'usage_notes': usage_notes,
            'user_description': user_description,
            'date_added': datetime.now().isoformat(),
            'added_by': added_by
        })
        
        # Update source
        sources[existing_source]['project_usage'] = project_usage
        sources[existing_source]['last_modified'] = datetime.now().isoformat()
        sources[existing_source]['modified_by'] = added_by
        
        # Save updated sources
        return self.save_sources_for_region(region, sources)
    
    def remove_source_from_project(self, project_path: str, source_id: str) -> bool:
        """Remove a source from a project (but keep it in master if used elsewhere)"""
        region = self.get_region_for_project(project_path)
        sources = self.load_sources_for_region(region)
        
        for source in sources:
            if source.get('id') == source_id:
                # Remove project usage
                project_usage = source.get('project_usage', [])
                project_usage = [u for u in project_usage if u.get('project_path') != project_path]
                source['project_usage'] = project_usage
                source['last_modified'] = datetime.now().isoformat()
                
                # Save updated sources
                return self.save_sources_for_region(region, sources)
        
        return False
    
    def search_sources_across_regions(self, search_term: str, 
                                    regions: Optional[List[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for sources across multiple regions (for explicit cross-region search)
        
        Args:
            search_term: Text to search for in titles, descriptions, etc.
            regions: List of regions to search (None = all regions)
            
        Returns:
            Dict mapping region names to matching sources
        """
        if regions is None:
            regions = [m.region_name for m in REGIONAL_MAPPINGS if m.region_name != "General"]
        
        results = {}
        search_lower = search_term.lower()
        
        for region in regions:
            sources = self.load_sources_for_region(region)
            matching_sources = []
            
            for source in sources:
                # Search in title, descriptions from project usage, and usage notes
                title = source.get('title', '').lower()
                if search_lower in title:
                    matching_sources.append(source)
                    continue
                
                # Search in project usage descriptions and notes
                for usage in source.get('project_usage', []):
                    desc = usage.get('user_description', '').lower()
                    notes = usage.get('usage_notes', '').lower()
                    if search_lower in desc or search_lower in notes:
                        matching_sources.append(source)
                        break
            
            if matching_sources:
                results[region] = matching_sources
        
        return results


# =============================================================================
# GLOBAL INSTANCE AND CONVENIENCE FUNCTIONS
# =============================================================================

# Global instance for easy access
regional_source_manager = RegionalSourceManager()


def get_region_for_project(project_path: str) -> str:
    """Convenience function to get region for a project"""
    return regional_source_manager.get_region_for_project(project_path)


def get_sources_for_project(project_path: str) -> tuple[str, List[Dict[str, Any]]]:
    """Convenience function to get sources for a project"""
    return regional_source_manager.get_sources_for_project(project_path)


def add_source_to_project(project_path: str, project_title: str, source_data: Dict[str, Any], 
                         usage_notes: str, user_description: str, added_by: str) -> bool:
    """Convenience function to add a source to a project"""
    return regional_source_manager.add_source_to_project(
        project_path, project_title, source_data, usage_notes, user_description, added_by
    )


# =============================================================================
# DOCUMENTATION AND INTEGRATION NOTES
# =============================================================================

"""
INTEGRATION GUIDE:

1. REPLACE SOURCE DATATYPES:
   - Replace the placeholder SourceRecord class with your actual source dataclasses
   - Update the SourceType enum with your actual source types
   - Ensure your dataclasses include the required fields for project usage tracking

2. DIRECTORY PATTERNS:
   - Update REGIONAL_MAPPINGS to match your actual project directory structure
   - Add new regions as needed
   - Adjust priority values for proper matching

3. MASTER SOURCES LOCATION:
   - Update the default master_sources_dir in RegionalSourceManager.__init__()
   - Consider using Program Files or another shared location

4. INTEGRATION WITH UI:
   - Use get_sources_for_project(project_path) to load sources for current project
   - Use add_source_to_project() when user adds a source
   - Use search_sources_across_regions() for cross-region search functionality

5. USAGE TRACKING:
   - Each source tracks which projects use it via the project_usage list
   - Each project usage includes the user's description and usage notes
   - This enables rich display cards showing source context per project

EXAMPLE USAGE:

# Get sources for current project (region-specific)
region, sources = get_sources_for_project("/path/to/ROW_project.json")

# Add a source to a project
success = add_source_to_project(
    project_path="/path/to/project.json",
    project_title="My ROW Project",
    source_data={"title": "ROW Design Manual", "type": "manual"},
    usage_notes="Standards and specifications for ROW design",
    user_description="Primary reference for design requirements",
    added_by="john.doe"
)

# Search across regions (explicit cross-region search)
results = regional_source_manager.search_sources_across_regions("foundation design")
"""
