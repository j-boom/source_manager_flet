#!/usr/bin/env python3
"""
Migration Service for converting old format project files to new format.
"""

import json
import uuid
import re
from pathlib import Path
from typing import Dict, Any, List
import logging

# Set up logging
logger = logging.getLogger(__name__)


class MigrationService:
    """Service for migrating project data from old format to new format."""
    
    def __init__(self):
        """Initialize the migration service."""
        self.logger = logger
    
    def migrate_project_data(self, old_data: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """
        Migrate project data from old format to new format.
        
        Args:
            old_data: The old format project data
            filename: The original filename (used for deriving metadata)
            
        Returns:
            Dict containing the new format project data
        """
        self.logger.info(f"Starting migration for file: {filename}")
        
        # Extract information from filename
        file_info = self._parse_filename(filename)
        
        # Build new format structure
        new_data = {
            "project_metadata": self._build_project_metadata(old_data, file_info, filename),
            "team": self._migrate_team(old_data),
            "key_cites": self._migrate_key_cites(old_data),
            "facility_information": self._migrate_facility_information(old_data, file_info),
            "slide_data": self._migrate_slide_data(old_data),
            "sources": self._migrate_sources(old_data),
            "powerpoint_file": old_data.get("powerpoint_file", ""),
            "number_header_citations": old_data.get("number_header_citations", 0)
        }
        
        self.logger.info(f"Migration completed for file: {filename}")
        return new_data
    
    def _parse_filename(self, filename: str) -> Dict[str, str]:
        """
        Parse filename to extract component information.
        Expected format: "2023123001 - CA123 - STD - 2023.json"
        
        Args:
            filename: The filename to parse
            
        Returns:
            Dict with parsed components
        """
        # Remove .json extension
        name_without_ext = filename.replace('.json', '')
        
        # Split by " - " delimiter
        parts = name_without_ext.split(' - ')
        
        if len(parts) >= 4:
            benjamin = parts[0]  # 10-digit number
            oscar = parts[1]     # CA123
            project_type = parts[2]  # STD, FCR, etc.
            year = parts[3]      # 2023, 2024, etc.
        else:
            # Fallback parsing if format is different
            self.logger.warning(f"Unexpected filename format: {filename}")
            benjamin = ""
            oscar = ""
            project_type = ""
            year = ""
        
        return {
            "benjamin": benjamin,
            "oscar": oscar,
            "project_type": project_type,
            "year": year
        }
    
    def _build_project_metadata(self, old_data: Dict[str, Any], file_info: Dict[str, str], filename: str) -> Dict[str, Any]:
        """Build the project_metadata section."""
        
        # Generate new UUID for project
        project_id = str(uuid.uuid4())
        
        # Build file path (derived from filename structure)
        benjamin = file_info["benjamin"]
        year = file_info["year"]
        file_path = f"/Users/jim/Documents/Source Manager/Directory Source Citations/ROW/{year}/{benjamin}/{filename}"
        
        # Remove .json extension from filename for title
        title = filename.replace('.json', '')
        
        return {
            "project_id": project_id,
            "project_type": file_info["project_type"],
            "title": title,
            "file_path": file_path,
            "requestor": "",
            "request_year": "",
            "relook": False
        }
    
    def _migrate_team(self, old_data: Dict[str, Any]) -> Dict[str, str]:
        """Migrate team section (preserve as-is)."""
        return old_data.get("team", {})
    
    def _migrate_key_cites(self, old_data: Dict[str, Any]) -> Dict[str, str]:
        """Migrate key_cites section (preserve as-is)."""
        return old_data.get("key_cites", {})
    
    def _migrate_facility_information(self, old_data: Dict[str, Any], file_info: Dict[str, str]) -> Dict[str, str]:
        """
        Migrate site_properties to facility_information with transformations.
        """
        site_props = old_data.get("site_properties", {})
        
        facility_info = {
            "benjamin": file_info["benjamin"],  # Derived from filename
            "oscar": file_info["oscar"],        # Derived from filename
            "Facility Name": site_props.get("Facility Name", ""),
            "Facility Surrogate Key": site_props.get("Facility Surrogate Key", "")
        }
        
        # Note: We're dropping 'm_class' and 'Date Accessed' as they're not in the new format
        
        return facility_info
    
    def _migrate_slide_data(self, old_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate slide_data section (preserve as-is)."""
        return old_data.get("slide_data", {})
    
    def _migrate_sources(self, old_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Migrate sources section with transformation.
        Convert from full source objects to simplified format with order.
        """
        old_sources = old_data.get("sources", [])
        new_sources = []
        
        for i, source in enumerate(old_sources):
            new_source = {
                "uuid": source.get("uuid", ""),
                "order": i + 1,  # 1-based ordering
                "usage_notes": source.get("comment", "")  # comment -> usage_notes
            }
            new_sources.append(new_source)
        
        return new_sources
    
    def migrate_file(self, input_file_path: str, output_file_path: str | None = None) -> bool:
        """
        Migrate a single file from old format to new format.
        
        Args:
            input_file_path: Path to the old format file
            output_file_path: Path for the new format file (optional)
            
        Returns:
            bool: True if migration successful, False otherwise
        """
        try:
            input_path = Path(input_file_path)
            
            # Read old format file
            with open(input_path, 'r') as f:
                old_data = json.load(f)
            
            # Perform migration
            new_data = self.migrate_project_data(old_data, input_path.name)
            
            # Determine output path
            if output_file_path is None:
                output_path = input_path.parent / f"{input_path.stem}_migrated.json"
            else:
                output_path = Path(output_file_path)
            
            # Write new format file
            with open(output_path, 'w') as f:
                json.dump(new_data, f, indent=4)
            
            self.logger.info(f"Successfully migrated {input_path} to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error migrating file {input_file_path}: {e}")
            return False
    
    def migrate_directory(self, directory_path: str, backup: bool = True) -> Dict[str, bool]:
        """
        Migrate all JSON files in a directory.
        
        Args:
            directory_path: Path to directory containing old format files
            backup: Whether to create backup copies of original files
            
        Returns:
            Dict mapping filename to migration success status
        """
        results = {}
        directory = Path(directory_path)
        
        if not directory.exists():
            self.logger.error(f"Directory does not exist: {directory_path}")
            return results
        
        # Find all JSON files
        json_files = list(directory.glob("*.json"))
        
        if not json_files:
            self.logger.warning(f"No JSON files found in {directory_path}")
            return results
        
        self.logger.info(f"Found {len(json_files)} JSON files to migrate")
        
        for json_file in json_files:
            try:
                # Create backup if requested
                if backup:
                    backup_path = json_file.parent / f"{json_file.stem}_backup.json"
                    json_file.rename(backup_path)
                    source_file = backup_path
                else:
                    source_file = json_file
                
                # Migrate file
                success = self.migrate_file(str(source_file), str(json_file))
                results[json_file.name] = success
                
            except Exception as e:
                self.logger.error(f"Error processing {json_file}: {e}")
                results[json_file.name] = False
        
        return results


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate project files from old format to new format")
    parser.add_argument("input", help="Input file or directory path")
    parser.add_argument("-o", "--output", help="Output file path (for single file migration)")
    parser.add_argument("--no-backup", action="store_true", help="Don't create backup files")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
    
    # Create migration service
    migration_service = MigrationService()
    
    input_path = Path(args.input)
    
    if input_path.is_file():
        # Migrate single file
        success = migration_service.migrate_file(str(input_path), args.output)
        if success:
            print(f"✅ Successfully migrated {input_path}")
        else:
            print(f"❌ Failed to migrate {input_path}")
    elif input_path.is_dir():
        # Migrate directory
        results = migration_service.migrate_directory(str(input_path), backup=not args.no_backup)
        
        # Print summary
        successful = sum(results.values())
        total = len(results)
        print(f"Migration complete: {successful}/{total} files migrated successfully")
        
        for filename, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {filename}")
    else:
        print(f"❌ Input path does not exist: {input_path}")


if __name__ == "__main__":
    main()
