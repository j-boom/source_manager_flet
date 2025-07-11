"""
Migration Service

Service to migrate legacy project data to the new data structure.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Protocol
from uuid import uuid4

from ..models.project_models import Project, ProjectType, ProjectSourceLink
from ..models.source_models import SourceRecord, SourceType

# Import paths from config
try:
    from config.app_config import OLD_DATA_PATH, MASTER_SOURCES_DIR, USER_PROJECTS_DIR
except ImportError:
    # Fallback if imports fail
    OLD_DATA_PATH = "/Users/jim/Documents/Source Manager/Directory Source Citations"
    MASTER_SOURCES_DIR = Path("/Users/jim/Documents/Source Manager/program_files/master_sources")
    USER_PROJECTS_DIR = Path("/Users/jim/Documents/Source Manager/user_data/projects")

# Migration archive path - safely store old data outside main directory
MIGRATION_ARCHIVE_PATH = Path("/Users/jim/Documents/Source Manager/migration_archive")


# Citation parser protocol
class CitationParser(Protocol):
    """Protocol for citation parsers."""
    def parse(self, citation_string: str) -> SourceRecord:
        """Parse a citation string into a SourceRecord."""
        ...


class MigrationService:
    """Service to migrate legacy project data to new format."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._citation_parser: Optional[CitationParser] = None
        
        # Paths
        self.old_data_path = Path(OLD_DATA_PATH)
        self.master_sources_dir = Path(MASTER_SOURCES_DIR)
        self.user_projects_dir = Path(USER_PROJECTS_DIR)
        
        # Track migrated sources to avoid duplicates
        self._migrated_sources: Dict[str, str] = {}  # old_uuid -> new_source_id
    
    def set_citation_parser(self, parser: CitationParser):
        """Set the citation parser to use for migration."""
        self._citation_parser = parser
    
    def discover_old_project_files(self) -> List[Path]:
        """
        Discover all legacy project JSON files.
        
        Returns:
            List of Path objects to old project files
        """
        if not self.old_data_path.exists():
            self.logger.warning(f"Old data path does not exist: {self.old_data_path}")
            return []
        
        # Find all JSON files recursively
        json_files = list(self.old_data_path.rglob("*.json"))
        
        self.logger.info(f"Found {len(json_files)} JSON files in {self.old_data_path}")
        return json_files
    
    def parse_project_type_from_filename(self, filename: str) -> ProjectType:
        """
        Parse project type from filename.
        
        Expected format: "be_001 - oSuffix - CCR - 2024.json"
        
        Args:
            filename: The filename to parse
            
        Returns:
            ProjectType enum value
        """
        try:
            # Split by " - " and get the third part (index 2)
            parts = filename.split(" - ")
            if len(parts) >= 3:
                type_str = parts[2].strip()
                return ProjectType(type_str)
        except (ValueError, IndexError):
            pass
        
        # Default to OTH if we can't parse
        self.logger.warning(f"Could not parse project type from filename: {filename}")
        return ProjectType.OTH
    
    def derive_region_from_path(self, file_path: Path) -> str:
        """
        Derive region from file path.
        
        Expected path structure: .../Directory Source Citations/ROW/Country/project.json
        
        Args:
            file_path: Path to the project file
            
        Returns:
            Region string (ROW, AMER, EUR, etc.) or "General" if not found
        """
        try:
            # Look for "Directory Source Citations" in the path
            parts = file_path.parts
            
            for i, part in enumerate(parts):
                if "Directory Source Citations" in part:
                    # The next part should be the region
                    if i + 1 < len(parts):
                        return parts[i + 1]
                    break
        except Exception as e:
            self.logger.warning(f"Could not derive region from path {file_path}: {e}")
        
        return "General"
    
    def parse_slide_data(self, old_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Parse slide data from old format.
        
        Combines slide_refs_citation_ordering and slide_refs into new format.
        
        Args:
            old_data: The old project data dictionary
            
        Returns:
            Dictionary mapping slide_id to list of source UUIDs
        """
        slide_citations = {}
        
        # Get the citation ordering
        ordering = old_data.get("slide_refs_citation_ordering", [])
        if not ordering:
            return slide_citations
        
        # Get the slide refs (binary string mapping)
        slide_refs = old_data.get("slide_refs", {})
        
        for slide_id, binary_string in slide_refs.items():
            cited_uuids = []
            
            # Process each bit in the binary string
            for i, bit in enumerate(binary_string):
                if bit == "1" and i < len(ordering):
                    cited_uuids.append(ordering[i])
            
            if cited_uuids:
                slide_citations[slide_id] = cited_uuids
        
        return slide_citations
    
    def migrate_source(self, old_source: Dict[str, Any], region: str) -> Optional[SourceRecord]:
        """
        Migrate a single source from old format to new format.
        
        Args:
            old_source: Old source dictionary
            region: Region for the source
            
        Returns:
            SourceRecord or None if migration fails
        """
        if not self._citation_parser:
            self.logger.error("Citation parser not set. Cannot migrate sources.")
            return None
        
        try:
            # Get the citation string
            citation = old_source.get("citation", "")
            if not citation:
                self.logger.warning("Source has no citation string, skipping")
                return None
            
            # Parse the citation using the citation parser
            source_record = self._citation_parser.parse(citation)
            
            # Override with old UUID and region
            source_record.id = old_source["uuid"]
            source_record.region = region
            
            # Add any additional fields from old data
            if "description" in old_source:
                # Store old description in metadata if needed
                pass
            
            if "comment" in old_source:
                # Store old comment in metadata if needed
                pass
            
            return source_record
            
        except Exception as e:
            self.logger.error(f"Failed to migrate source {old_source.get('uuid', 'unknown')}: {e}")
            return None
    
    def migrate_single_project(self, file_path: Path) -> Optional[Project]:
        """
        Migrate a single project file from old format to new format.
        
        Args:
            file_path: Path to the old project file
            
        Returns:
            Project instance or None if migration fails
        """
        try:
            # Load old data
            with open(file_path, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
            
            # Extract basic project info
            filename = file_path.name
            project_type = self.parse_project_type_from_filename(filename)
            region = self.derive_region_from_path(file_path)
            
            # Generate new project ID
            project_id = str(uuid4())
            
            # Create project title from filename (remove .json)
            title = filename.replace('.json', '')
            
            # Determine new file path
            new_file_path = self.user_projects_dir / f"{project_id}.json"
            
            # Create project metadata
            metadata = {}
            
            # Migrate site properties
            if "site_properties" in old_data:
                metadata["site_properties"] = old_data["site_properties"]
            
            # Migrate characteristics
            if "characteristics" in old_data:
                metadata["characteristics"] = old_data["characteristics"]
            
            # Migrate key citations
            if "key_cites" in old_data:
                metadata["key_cites"] = old_data["key_cites"]
            
            # Migrate slide data
            slide_citations = self.parse_slide_data(old_data)
            if slide_citations:
                metadata["slide_citations"] = slide_citations
            
            # Migrate PowerPoint file info
            if "powerpoint_file" in old_data:
                metadata["powerpoint_file"] = old_data["powerpoint_file"]
            
            if "number_header_citations" in old_data:
                metadata["number_header_citations"] = old_data["number_header_citations"]
            
            # Migrate sources
            project_sources = []
            if "sources" in old_data:
                for i, old_source in enumerate(old_data["sources"]):
                    source_record = self.migrate_source(old_source, region)
                    if source_record:
                        # Track this source
                        self._migrated_sources[old_source["uuid"]] = source_record.id
                        
                        # Create project source link
                        link = ProjectSourceLink(
                            source_id=source_record.id,
                            order=i + 1,
                            notes=old_source.get("comment", "")
                        )
                        project_sources.append(link)
                        
                        # Save the source to master sources
                        self._save_migrated_source(source_record)
            
            # Create the project
            project = Project(
                project_id=project_id,
                project_type=project_type,
                title=title,
                file_path=new_file_path,
                metadata=metadata,
                sources=project_sources
            )
            
            self.logger.info(f"Successfully migrated project: {title}")
            return project
            
        except Exception as e:
            self.logger.error(f"Failed to migrate project {file_path}: {e}")
            return None
    
    def _save_migrated_source(self, source_record: SourceRecord):
        """
        Save a migrated source to the master sources directory.
        
        Args:
            source_record: The source to save
        """
        try:
            # Determine the file path based on region
            region_file = self.master_sources_dir / f"{source_record.region}_sources.json"
            
            # Load existing sources if file exists
            sources = []
            if region_file.exists():
                with open(region_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    sources = [SourceRecord.from_dict(s) for s in data.get("sources", [])]
            
            # Check if source already exists (by ID)
            existing_ids = {s.id for s in sources}
            if source_record.id not in existing_ids:
                sources.append(source_record)
                
                # Save updated sources
                region_file.parent.mkdir(parents=True, exist_ok=True)
                with open(region_file, 'w', encoding='utf-8') as f:
                    data = {
                        "sources": [s.to_dict() for s in sources],
                        "last_updated": source_record.last_modified
                    }
                    json.dump(data, f, indent=4)
                
                self.logger.debug(f"Saved source {source_record.id} to {region_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save source {source_record.id}: {e}")
    
    def migrate_all_projects(self, dry_run: bool = False, archive_first: bool = True) -> Dict[str, Any]:
        """
        Migrate all old projects to new format.
        
        Args:
            dry_run: If True, don't actually save files
            archive_first: If True, archive old data before migration
            
        Returns:
            Dictionary with migration statistics
        """
        if not self._citation_parser:
            raise ValueError("Citation parser not set. Call set_citation_parser() first.")
        
        # Archive old data first if requested
        if archive_first and not dry_run:
            if not self.archive_old_data():
                raise RuntimeError("Failed to archive old data. Migration aborted for safety.")
        
        old_files = self.discover_old_project_files()
        
        stats = {
            "total_files": len(old_files),
            "migrated_projects": 0,
            "migrated_sources": 0,
            "failed_projects": 0,
            "validation_errors": 0,
            "errors": []
        }
        
        self.logger.info(f"Starting migration of {len(old_files)} projects (dry_run={dry_run})")
        
        migrated_files = []  # Track successfully migrated files for testing
        
        for file_path in old_files:
            try:
                project = self.migrate_single_project(file_path)
                if project:
                    # Validate the project before saving
                    validation_errors = self.validate_migrated_project(project)
                    if validation_errors:
                        self.logger.error(f"Validation failed for {project.title}: {validation_errors}")
                        stats["validation_errors"] += 1
                        stats["errors"].extend(validation_errors)
                        continue
                    
                    if not dry_run:
                        project.save()
                        migrated_files.append(project.file_path)
                    
                    stats["migrated_projects"] += 1
                    stats["migrated_sources"] += len(project.sources)
                    
                    self.logger.info(f"✓ Migrated: {project.title}")
                else:
                    stats["failed_projects"] += 1
                    stats["errors"].append(f"Failed to migrate: {file_path}")
                    
            except Exception as e:
                stats["failed_projects"] += 1
                error_msg = f"Error migrating {file_path}: {e}"
                stats["errors"].append(error_msg)
                self.logger.error(error_msg)
        
        # Test loading of migrated projects if not dry run
        if not dry_run and migrated_files:
            self.logger.info("Testing migrated project loading...")
            load_test_failures = 0
            
            for project_file in migrated_files[:3]:  # Test first 3 files
                if not self.test_project_loading(project_file):
                    load_test_failures += 1
            
            if load_test_failures > 0:
                self.logger.warning(f"⚠️  {load_test_failures} projects failed loading tests")
                stats["errors"].append(f"{load_test_failures} projects failed loading tests")
        
        # Log summary
        self.logger.info(f"Migration complete:")
        self.logger.info(f"  - Projects migrated: {stats['migrated_projects']}")
        self.logger.info(f"  - Sources migrated: {stats['migrated_sources']}")
        self.logger.info(f"  - Failed projects: {stats['failed_projects']}")
        self.logger.info(f"  - Validation errors: {stats['validation_errors']}")
        
        if stats["errors"]:
            self.logger.warning(f"  - Errors: {len(stats['errors'])}")
            for error in stats["errors"][:5]:  # Show first 5 errors
                self.logger.warning(f"    {error}")
        
        return stats
    
    def archive_old_data(self) -> bool:
        """
        Archive the old data to a safe location before migration.
        
        Returns:
            True if archiving succeeded, False otherwise
        """
        try:
            if not self.old_data_path.exists():
                self.logger.warning(f"Old data path does not exist: {self.old_data_path}")
                return False
            
            # Create archive directory
            archive_path = MIGRATION_ARCHIVE_PATH
            archive_path.mkdir(parents=True, exist_ok=True)
            
            # Create timestamped archive
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_target = archive_path / f"pre_migration_backup_{timestamp}"
            
            # Copy the entire directory structure
            import shutil
            shutil.copytree(self.old_data_path, archive_target)
            
            self.logger.info(f"Successfully archived old data to: {archive_target}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to archive old data: {e}")
            return False
    
    def validate_migrated_project(self, project: Project) -> List[str]:
        """
        Validate that a migrated project is compatible with the new UI.
        
        Args:
            project: The migrated project to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required fields
        if not project.project_id:
            errors.append("Missing project_id")
        
        if not project.title:
            errors.append("Missing title")
        
        if not project.project_type:
            errors.append("Missing project_type")
        
        if not project.file_path:
            errors.append("Missing file_path")
        
        # Check that file_path is properly structured
        if project.file_path and not project.file_path.suffix == '.json':
            errors.append("Project file_path must end with .json")
        
        # Check sources
        for i, source_link in enumerate(project.sources):
            if not source_link.source_id:
                errors.append(f"Source {i} missing source_id")
            
            if source_link.order is None or source_link.order < 1:
                errors.append(f"Source {i} has invalid order: {source_link.order}")
        
        # Check metadata structure
        if not isinstance(project.metadata, dict):
            errors.append("Metadata must be a dictionary")
        
        return errors
    
    def test_project_loading(self, project_file_path: Path) -> bool:
        """
        Test if a migrated project can be loaded by the new system.
        
        Args:
            project_file_path: Path to the project file to test
            
        Returns:
            True if project loads successfully, False otherwise
        """
        try:
            from ..models.project_models import Project
            project = Project.load(project_file_path)
            
            if project is None:
                self.logger.error(f"Failed to load project: {project_file_path}")
                return False
            
            # Validate the loaded project
            errors = self.validate_migrated_project(project)
            if errors:
                self.logger.error(f"Project validation failed for {project_file_path}: {errors}")
                return False
            
            self.logger.info(f"✓ Project loads successfully: {project.title}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error testing project loading {project_file_path}: {e}")
            return False
