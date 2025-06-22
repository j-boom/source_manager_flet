#!/usr/bin/env python3
"""
Database Migration Script
Adds new source_type and source_metadata columns to existing database
"""

import sqlite3
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import DEFAULT_DATABASE


def migrate_database():
    """Migrate database to add new columns for source management"""
    print("🔄 Starting database migration...")
    
    db_path = str(DEFAULT_DATABASE)
    print(f"Database path: {db_path}")
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check current schema
            cursor.execute("PRAGMA table_info(sources)")
            columns = [row[1] for row in cursor.fetchall()]
            print(f"Current columns: {columns}")
            
            # Add source_type column if it doesn't exist
            if 'source_type' not in columns:
                print("Adding source_type column...")
                cursor.execute("""
                    ALTER TABLE sources 
                    ADD COLUMN source_type TEXT NOT NULL DEFAULT 'document'
                """)
                print("✅ Added source_type column")
            else:
                print("ℹ️ source_type column already exists")
            
            # Add source_metadata column if it doesn't exist
            if 'source_metadata' not in columns:
                print("Adding source_metadata column...")
                cursor.execute("""
                    ALTER TABLE sources 
                    ADD COLUMN source_metadata TEXT
                """)
                print("✅ Added source_metadata column")
            else:
                print("ℹ️ source_metadata column already exists")
            
            # Check project_sources table and add usage_notes if needed
            cursor.execute("PRAGMA table_info(project_sources)")
            ps_columns = [row[1] for row in cursor.fetchall()]
            print(f"Project sources columns: {ps_columns}")
            
            if 'usage_notes' not in ps_columns:
                print("Adding usage_notes column to project_sources...")
                cursor.execute("""
                    ALTER TABLE project_sources 
                    ADD COLUMN usage_notes TEXT NOT NULL DEFAULT ''
                """)
                print("✅ Added usage_notes column to project_sources")
            else:
                print("ℹ️ usage_notes column already exists in project_sources")
            
            conn.commit()
            print("✅ Database migration completed successfully!")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    migrate_database()
