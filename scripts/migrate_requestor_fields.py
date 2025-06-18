#!/usr/bin/env python3
"""
Database Migration: Add Requestor Fields

Adds the new requestor fields to the projects table:
- requestor_name
- request_date 
- relook
"""

import sqlite3
import os
import sys

def migrate_database(db_path: str):
    """Add requestor fields to projects table"""
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(projects)")
        columns = [col[1] for col in cursor.fetchall()]
        
        migrations_needed = []
        if 'requestor_name' not in columns:
            migrations_needed.append("ALTER TABLE projects ADD COLUMN requestor_name TEXT")
        
        if 'request_date' not in columns:
            migrations_needed.append("ALTER TABLE projects ADD COLUMN request_date TEXT")
            
        if 'relook' not in columns:
            migrations_needed.append("ALTER TABLE projects ADD COLUMN relook BOOLEAN DEFAULT 0")
        
        if not migrations_needed:
            print(f"✓ {db_path} - No migration needed, all columns exist")
            return True
        
        # Apply migrations
        for migration in migrations_needed:
            print(f"  Applying: {migration}")
            cursor.execute(migration)
        
        conn.commit()
        conn.close()
        
        print(f"✓ {db_path} - Migration completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ {db_path} - Migration failed: {e}")
        return False

def main():
    """Migrate all database files"""
    print("Database Migration: Adding Requestor Fields")
    print("=" * 50)
    
    # Find all database files
    db_dir = "data/databases"
    if not os.path.exists(db_dir):
        print(f"Database directory not found: {db_dir}")
        return False
    
    db_files = []
    for file in os.listdir(db_dir):
        if file.endswith('.db'):
            db_files.append(os.path.join(db_dir, file))
    
    if not db_files:
        print("No database files found to migrate")
        return True
    
    print(f"Found {len(db_files)} database files to migrate:")
    for db_file in db_files:
        print(f"  - {db_file}")
    
    print("\nStarting migration...")
    
    success_count = 0
    for db_file in db_files:
        if migrate_database(db_file):
            success_count += 1
    
    print(f"\nMigration Summary:")
    print(f"  Total databases: {len(db_files)}")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {len(db_files) - success_count}")
    
    if success_count == len(db_files):
        print("\n🎉 All databases migrated successfully!")
        return True
    else:
        print(f"\n❌ {len(db_files) - success_count} database(s) failed to migrate")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
