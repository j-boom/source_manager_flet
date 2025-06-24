"""
Regional Source Management Configuration
Maps project directories to regional source files and handles source synchronization
"""

from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json
import os
from dataclasses import dataclass
from enum import Enum


class SourceScope(Enum):
    """Source scope types"""
    REGIONAL = "regional"    # Specific to a region/directory
    GLOBAL = "global"        # Available to all regions
    PROJECT = "project"      # Project-specific only


@dataclass
class RegionalMapping:
    """Configuration for a regional source mapping"""
    region_name: str
    directory_patterns: List[str]  # Patterns to match project directories
    source_file: str              # Master source JSON filename
    display_name: str            # User-friendly region name
    description: str             # Description of the region
    priority: int = 0            # Priority for overlapping patterns


# Regional source mappings configuration
REGIONAL_MAPPINGS = [
    RegionalMapping(
        region_name="ROW",
        directory_patterns=[
            "**/ROW/**",
            "**/Right_of_Way/**", 
            "**/ROW_Projects/**"
        ],
        source_file="ROW_sources.json",
        display_name="Right of Way",
        description="Sources specific to Right of Way projects",
        priority=10
    ),
    RegionalMapping(
        region_name="Other",
        directory_patterns=[
            "**/Other_Projects/**",
            "**/Other/**",
            "**/Miscellaneous/**"
        ],
        source_file="Other_sources.json",
        display_name="Other Projects",
        description="General project sources",
        priority=5
    ),
    RegionalMapping(
        region_name="Downtown",
        directory_patterns=[
            "**/Downtown/**",
            "**/Downtown_Projects/**",
            "**/Urban/**"
        ],
        source_file="Downtown_sources.json",
        display_name="Downtown Projects",
        description="Urban and downtown development sources",
        priority=8
    ),
    RegionalMapping(
        region_name="Regional",
        directory_patterns=[
            "**/Regional/**",
            "**/Regional_Projects/**"
        ],
        source_file="Regional_sources.json",
        display_name="Regional Standards",
        description="Regional standards and specifications",
        priority=7
    ),
    # Fallback for unmatched directories
    RegionalMapping(
        region_name="General",
        directory_patterns=["**"],  # Matches everything
        source_file="General_sources.json",
        display_name="General Sources",
        description="Default sources for unclassified projects",
        priority=1
    )
]


class RegionalSourceManager:
    """Manages regional source files and mappings"""
    
    def __init__(self, master_sources_dir: str = None):
        """Initialize with master sources directory
        
        Args:
            master_sources_dir: Path to master sources directory
                               (defaults to Program Files location)
        """
        if master_sources_dir is None:
            # Default to Program Files on Windows, /opt on Linux/Mac
            if os.name == 'nt':  # Windows
                master_sources_dir = r"C:\Program Files\SourceManager\MasterSources"
            else:  # Linux/Mac
                master_sources_dir = "/opt/sourcemanager/master_sources"
        
        self.master_sources_dir = Path(master_sources_dir)
        self.master_sources_dir.mkdir(parents=True, exist_ok=True)
    
    def get_region_for_project(self, project_path: str) -> str:
        """Determine the region for a project based on its directory path
        
        Args:
            project_path: Path to the project file
            
        Returns:
            Region name (e.g., 'ROW', 'Other', 'Downtown')
        """
        project_path = Path(project_path).resolve()
        
        # Sort mappings by priority (higher priority first)
        sorted_mappings = sorted(REGIONAL_MAPPINGS, key=lambda m: m.priority, reverse=True)
        
        for mapping in sorted_mappings:
            for pattern in mapping.directory_patterns:
                if project_path.match(pattern):
                    return mapping.region_name
        
        # Fallback to General if no matches
        return "General"
    
    def get_source_file_path(self, region: str) -> Path:
        """Get the path to the master source file for a region
        
        Args:
            region: Region name
            
        Returns:
            Path to the master source JSON file
        """
        mapping = self._get_mapping_by_region(region)
        if mapping:
            return self.master_sources_dir / mapping.source_file
        
        # Fallback to general sources
        return self.master_sources_dir / "General_sources.json"
    
    def get_sources_for_project(self, project_path: str) -> Tuple[str, List[dict]]:
        """Get all sources available for a project
        
        Args:
            project_path: Path to the project file
            
        Returns:
            Tuple of (region_name, list_of_sources)
        """
        region = self.get_region_for_project(project_path)
        source_file = self.get_source_file_path(region)
        
        sources = []
        if source_file.exists():
            try:
                with open(source_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    sources = data.get('sources', [])
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Warning: Could not load sources from {source_file}: {e}")
        
        return region, sources
    
    def add_source_to_region(self, region: str, source_data: dict) -> bool:
        """Add a source to a regional master file
        
        Args:
            region: Region name
            source_data: Source data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        source_file = self.get_source_file_path(region)
        
        try:
            # Load existing sources
            sources = []
            metadata = {
                "version": "1.0",
                "region": region,
                "last_updated": "",
                "total_sources": 0
            }
            
            if source_file.exists():
                with open(source_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    sources = data.get('sources', [])
                    metadata.update(data.get('metadata', {}))
            
            # Add new source (with unique ID if not provided)
            if 'id' not in source_data:
                source_data['id'] = self._generate_source_id(sources)
            
            sources.append(source_data)
            
            # Update metadata
            from datetime import datetime
            metadata.update({
                "last_updated": datetime.now().isoformat(),
                "total_sources": len(sources),
                "region": region
            })
            
            # Save updated sources
            with open(source_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "sources": sources,
                    "metadata": metadata
                }, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error adding source to {region}: {e}")
            return False
    
    def update_source_in_region(self, region: str, source_id: str, updated_data: dict) -> bool:
        """Update an existing source in a regional master file
        
        Args:
            region: Region name
            source_id: ID of the source to update
            updated_data: Updated source data
            
        Returns:
            True if successful, False otherwise
        """
        source_file = self.get_source_file_path(region)
        
        try:
            if not source_file.exists():
                return False
            
            with open(source_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            sources = data.get('sources', [])
            
            # Find and update the source
            for i, source in enumerate(sources):
                if source.get('id') == source_id:
                    sources[i] = {**source, **updated_data}
                    
                    # Update metadata
                    from datetime import datetime
                    data['metadata']['last_updated'] = datetime.now().isoformat()
                    
                    # Save updated sources
                    with open(source_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    return True
            
            return False  # Source not found
            
        except Exception as e:
            print(f"Error updating source {source_id} in {region}: {e}")
            return False
    
    def get_all_regions(self) -> List[dict]:
        """Get information about all available regions
        
        Returns:
            List of region information dictionaries
        """
        regions = []
        for mapping in REGIONAL_MAPPINGS:
            source_file = self.get_source_file_path(mapping.region_name)
            source_count = 0
            
            if source_file.exists():
                try:
                    with open(source_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        source_count = len(data.get('sources', []))
                except:
                    pass
            
            regions.append({
                'region_name': mapping.region_name,
                'display_name': mapping.display_name,
                'description': mapping.description,
                'source_count': source_count,
                'source_file': mapping.source_file
            })
        
        return regions
    
    def _get_mapping_by_region(self, region: str) -> Optional[RegionalMapping]:
        """Get mapping configuration for a region"""
        for mapping in REGIONAL_MAPPINGS:
            if mapping.region_name == region:
                return mapping
        return None
    
    def _generate_source_id(self, existing_sources: List[dict]) -> str:
        """Generate a unique source ID"""
        existing_ids = {s.get('id', '') for s in existing_sources}
        
        # Try to generate a unique ID
        import uuid
        for _ in range(10):  # Max 10 attempts
            new_id = f"src_{uuid.uuid4().hex[:8]}"
            if new_id not in existing_ids:
                return new_id
        
        # Fallback to timestamp-based ID
        from datetime import datetime
        return f"src_{int(datetime.now().timestamp())}"


# Global instance
regional_source_manager = RegionalSourceManager()


def get_region_for_project(project_path: str) -> str:
    """Convenience function to get region for a project"""
    return regional_source_manager.get_region_for_project(project_path)


def get_sources_for_project(project_path: str) -> Tuple[str, List[dict]]:
    """Convenience function to get sources for a project"""
    return regional_source_manager.get_sources_for_project(project_path)
