#!/usr/bin/env python3
"""
Batch Migration Script

This script processes all project files from the old format directory
and migrates them to the new format, saving them in the reformatted directory.
"""

import json
import uuid
from pathlib import Path
from src.services.migration_service import MigrationService
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main migration function"""
    # Define source and destination directories
    source_dir = Path("/Users/jim/Documents/data/Directory_Source_Citations/ROW/old")
    destination_dir = Path("/Users/jim/Documents/data/Directory_Source_Citations/ROW/reformatted")
    
    # Create destination directory if it doesn't exist
    destination_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize migration service
    migration_service = MigrationService()
    
    # Find all JSON files in the source directory
    json_files = list(source_dir.glob("*.json"))
    
    logger.info(f"Found {len(json_files)} JSON files to migrate")
    
    success_count = 0
    error_count = 0
    
    for json_file in json_files:
        try:
            logger.info(f"Processing: {json_file.name}")
            
            # Generate project_title from filename (without extension)
            project_title = json_file.stem
            
            # Generate a UUID for project_id
            project_id = str(uuid.uuid4())
            
            # Migrate the file
            success, message = migration_service.migrate_project_file(
                source_file=json_file,
                destination_file=destination_dir / json_file.name,
                project_id=project_id,
                project_title=project_title
            )
            
            if success:
                logger.info(f"✅ Successfully migrated: {json_file.name}")
                success_count += 1
            else:
                logger.error(f"❌ Failed to migrate {json_file.name}: {message}")
                error_count += 1
                
        except Exception as e:
            logger.error(f"❌ Error processing {json_file.name}: {e}")
            error_count += 1
    
    # Summary
    logger.info(f"Migration complete!")
    logger.info(f"✅ Successfully migrated: {success_count} files")
    logger.info(f"❌ Failed migrations: {error_count} files")
    logger.info(f"📁 Migrated files saved to: {destination_dir}")

if __name__ == "__main__":
    main()
