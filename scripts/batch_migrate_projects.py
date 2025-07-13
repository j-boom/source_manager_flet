#!/usr/bin/env python3
"""
Batch migration script for processing 150 projects from old format to new format.
Processes files from the old directory and saves them to the reformatted directory.
"""

import json
import sys
from pathlib import Path
import logging

# Add the root directory to Python path so we can import our services
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.migration_service import MigrationService


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('migration.log'),
            logging.StreamHandler()
        ]
    )


def batch_migrate_projects():
    """
    Batch migrate all projects from old directory to reformatted directory.
    """
    # Set up paths
    old_dir = Path("/Users/jim/Documents/data/Directory_Source_Citations/ROW/old")
    reformatted_dir = Path("/Users/jim/Documents/data/Directory_Source_Citations/ROW/reformatted")
    
    # Create reformatted directory if it doesn't exist
    reformatted_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize migration service
    migration_service = MigrationService()
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting batch migration from {old_dir} to {reformatted_dir}")
    
    if not old_dir.exists():
        logger.error(f"Source directory does not exist: {old_dir}")
        return False
    
    # Find all JSON files in old directory
    json_files = list(old_dir.glob("*.json"))
    
    if not json_files:
        logger.warning(f"No JSON files found in {old_dir}")
        return False
    
    logger.info(f"Found {len(json_files)} JSON files to migrate")
    
    # Track results
    successful_migrations = 0
    failed_migrations = 0
    migration_results = {}
    
    for json_file in json_files:
        try:
            logger.info(f"Processing: {json_file.name}")
            
            # Read old format file
            with open(json_file, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
            
            # Perform migration
            new_data = migration_service.migrate_project_data(old_data, json_file.name)
            
            # Define output path in reformatted directory
            output_path = reformatted_dir / json_file.name
            
            # Write new format file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, indent=4)
            
            logger.info(f"✅ Successfully migrated {json_file.name}")
            successful_migrations += 1
            migration_results[json_file.name] = True
            
        except Exception as e:
            logger.error(f"❌ Failed to migrate {json_file.name}: {e}")
            failed_migrations += 1
            migration_results[json_file.name] = False
    
    # Print summary
    total_files = len(json_files)
    logger.info("=" * 60)
    logger.info("MIGRATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total files processed: {total_files}")
    logger.info(f"Successful migrations: {successful_migrations}")
    logger.info(f"Failed migrations: {failed_migrations}")
    logger.info(f"Success rate: {(successful_migrations/total_files)*100:.1f}%")
    
    if failed_migrations > 0:
        logger.info("\nFailed files:")
        for filename, success in migration_results.items():
            if not success:
                logger.info(f"  ❌ {filename}")
    
    logger.info(f"\nMigrated files saved to: {reformatted_dir}")
    
    return successful_migrations == total_files


def main():
    """Main function."""
    setup_logging()
    
    logger = logging.getLogger(__name__)
    logger.info("Starting batch project migration...")
    
    success = batch_migrate_projects()
    
    if success:
        logger.info("🎉 All projects migrated successfully!")
        sys.exit(0)
    else:
        logger.error("⚠️  Some projects failed to migrate. Check the log for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
