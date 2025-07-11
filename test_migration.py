"""
Migration Test Script

Test script to validate migration functionality and demonstrate usage.
"""
import logging
from pathlib import Path
from src.services.migration_service import MigrationService
from src.models.source_models import SourceRecord, SourceType

# Set up logging to see migration progress
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')


class MockCitationParser:
    """
    Mock citation parser for testing.
    Replace this with your actual citation parser.
    """
    
    def parse(self, citation_string: str) -> SourceRecord:
        """
        Parse a citation string into a SourceRecord.
        
        This is a mock implementation - replace with your actual parser.
        """
        # Extract basic info from citation (very basic parsing)
        title = "Unknown Source"
        authors = []
        
        # Try to extract title (very basic - just use first part before year)
        parts = citation_string.split('.')
        if len(parts) > 1:
            title = parts[0].strip()
        
        # Create a basic SourceRecord
        source_record = SourceRecord(
            id="temp_id",  # Will be overwritten with old UUID
            source_type=SourceType.REPORT,  # Default type
            title=title,
            region="temp_region",  # Will be overwritten
            authors=authors,
            publication_year=2024,  # Default year
        )
        
        return source_record


def test_discovery():
    """Test discovery of old project files."""
    print("=== Testing File Discovery ===")
    migration_service = MigrationService()
    
    old_files = migration_service.discover_old_project_files()
    
    print(f"Found {len(old_files)} old project files:")
    for file_path in old_files[:5]:  # Show first 5
        print(f"  - {file_path}")
    
    if len(old_files) > 5:
        print(f"  ... and {len(old_files) - 5} more")
    
    return old_files


def test_filename_parsing():
    """Test project type parsing from filenames."""
    print("\n=== Testing Filename Parsing ===")
    migration_service = MigrationService()
    
    test_filenames = [
        "be_001 - oSuffix - CCR - 2024.json",
        "be_002 - testSuffix - GSC - 2023.json", 
        "be_003 - another - STD - 2025.json",
        "be_004 - invalid - UNKNOWN - 2024.json",
        "invalid_format.json"
    ]
    
    for filename in test_filenames:
        project_type = migration_service.parse_project_type_from_filename(filename)
        print(f"  {filename} -> {project_type}")


def test_region_parsing():
    """Test region derivation from file paths."""
    print("\n=== Testing Region Parsing ===")
    migration_service = MigrationService()
    
    test_paths = [
        Path("/Users/jim/Source Manager/Directory Source Citations/ROW/Country1/project.json"),
        Path("/Users/jim/Source Manager/Directory Source Citations/AMER/USA/project.json"),
        Path("/Users/jim/Source Manager/Directory Source Citations/EUR/France/project.json"),
        Path("/some/other/path/project.json")
    ]
    
    for path in test_paths:
        region = migration_service.derive_region_from_path(path)
        print(f"  {path} -> {region}")


def test_slide_data_parsing():
    """Test slide data parsing."""
    print("\n=== Testing Slide Data Parsing ===")
    migration_service = MigrationService()
    
    # Mock old data with slide references based on real format
    old_data = {
        "slide_refs_citation_ordering": ["uuid1", "uuid2", "uuid3", "uuid4"],
        "slide_refs": {
            "slide_1": "1010",  # uuid1 and uuid3
            "slide_2": "0110",  # uuid2 and uuid3
            "slide_3": "1111",  # all uuids
            "slide_4": "0000",  # no sources
        }
    }
    
    slide_citations = migration_service.parse_slide_data(old_data)
    
    print("  Input citation ordering:", old_data["slide_refs_citation_ordering"])
    print("  Input slide refs:", old_data["slide_refs"])
    print("  Parsed slide citations:")
    for slide_id, uuids in slide_citations.items():
        print(f"    {slide_id}: {uuids}")


def test_real_file_structure():
    """Test if we can access real files and examine structure."""
    print("\n=== Testing Real File Structure ===")
    migration_service = MigrationService()
    
    old_files = migration_service.discover_old_project_files()
    
    if not old_files:
        print("  No old project files found.")
        print("  Expected location: /Users/jim/Source Manager/Directory Source Citations")
        return
    
    # Examine first file
    test_file = old_files[0]
    print(f"  Examining: {test_file}")
    
    try:
        import json
        with open(test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("  File structure:")
        for key in data.keys():
            value = data[key]
            if isinstance(value, list):
                print(f"    {key}: list with {len(value)} items")
            elif isinstance(value, dict):
                print(f"    {key}: dict with keys: {list(value.keys())}")
            else:
                print(f"    {key}: {type(value).__name__}")
        
        # Check for sources
        if "sources" in data and data["sources"]:
            print(f"  First source structure:")
            first_source = data["sources"][0]
            for key, value in first_source.items():
                print(f"    {key}: {type(value).__name__}")
                
        # Check slide data
        if "slide_refs_citation_ordering" in data:
            ordering = data["slide_refs_citation_ordering"]
            print(f"  Citation ordering: {len(ordering)} UUIDs")
            if ordering:
                print(f"    First UUID: {ordering[0]}")
        
        if "slide_refs" in data:
            slide_refs = data["slide_refs"]
            print(f"  Slide refs: {len(slide_refs)} slides")
            for slide_id, binary_str in slide_refs.items():
                print(f"    {slide_id}: {binary_str}")
                break  # Just show first one
                
    except Exception as e:
        print(f"  Error reading file: {e}")


def test_migration_dry_run():
    """Test migration without actually saving files."""
    print("\n=== Testing Migration (Dry Run) ===")
    
    migration_service = MigrationService()
    migration_service.set_citation_parser(MockCitationParser())
    
    # Get a few files to test
    old_files = migration_service.discover_old_project_files()
    
    if not old_files:
        print("  No old project files found for testing")
        return
    
    # Test migration of first file
    test_file = old_files[0]
    print(f"  Testing migration of: {test_file}")
    
    project = migration_service.migrate_single_project(test_file)
    
    if project:
        print(f"  ✓ Successfully migrated project:")
        print(f"    - Title: {project.title}")
        print(f"    - Type: {project.project_type}")
        print(f"    - Project ID: {project.project_id}")
        print(f"    - Sources: {len(project.sources)}")
        print(f"    - Metadata keys: {list(project.metadata.keys())}")
        
        # Validate the project
        validation_errors = migration_service.validate_migrated_project(project)
        if validation_errors:
            print(f"    ⚠️  Validation errors: {validation_errors}")
        else:
            print(f"    ✓ Project validation passed")
        
        # Show slide citations if present
        if 'slide_citations' in project.metadata:
            slide_count = len(project.metadata['slide_citations'])
            print(f"    - Slide citations: {slide_count} slides")
            
        # Show first few sources
        if project.sources:
            print(f"    - First source: {project.sources[0].source_id}")
            print(f"    - Source notes: '{project.sources[0].notes}'")
            
        # Show key metadata
        if 'site_properties' in project.metadata:
            props = project.metadata['site_properties']
            print(f"    - Site properties: {list(props.keys())}")
            
    else:
        print("  ✗ Migration failed")


def test_archiving():
    """Test the archiving functionality."""
    print("\n=== Testing Data Archiving ===")
    
    migration_service = MigrationService()
    
    # Test archiving (this will actually create an archive)
    print("  Testing archive functionality...")
    success = migration_service.archive_old_data()
    
    if success:
        print("  ✓ Archiving test passed")
        print("  Note: Archive created in /Users/jim/Documents/Source Manager/migration_archive/")
    else:
        print("  ✗ Archiving test failed")


def test_safe_migration():
    """Test the complete safe migration workflow."""
    print("\n=== Testing Safe Migration Workflow ===")
    
    migration_service = MigrationService()
    migration_service.set_citation_parser(MockCitationParser())
    
    print("  Running migration with validation and archiving (dry run)...")
    
    # Run a safe dry run migration
    stats = migration_service.migrate_all_projects(dry_run=True, archive_first=False)
    
    print(f"  Migration results:")
    print(f"    - Total files found: {stats['total_files']}")
    print(f"    - Successfully migrated: {stats['migrated_projects']}")
    print(f"    - Failed migrations: {stats['failed_projects']}")
    print(f"    - Validation errors: {stats['validation_errors']}")
    print(f"    - Total sources: {stats['migrated_sources']}")
    
    if stats['errors']:
        print(f"    - Errors encountered: {len(stats['errors'])}")
        for error in stats['errors'][:3]:  # Show first 3 errors
            print(f"      * {error}")


if __name__ == "__main__":
    print("Migration Service Test")
    print("=" * 50)
    
    # Run tests
    test_discovery()
    test_filename_parsing()
    test_region_parsing()
    test_slide_data_parsing()
    test_real_file_structure()
    test_migration_dry_run()
    test_archiving()
    test_safe_migration()
    
    print("\n" + "=" * 50)
    print("Test complete!")
    print("\nNext steps:")
    print("1. Replace MockCitationParser with your actual citation parser")
    print("2. Review the migration results")
    print("3. Test with: migration_service.migrate_all_projects(dry_run=True)")
    print("4. When ready, run: migration_service.migrate_all_projects(dry_run=False)")
    print("5. The old data will be automatically archived before migration")
