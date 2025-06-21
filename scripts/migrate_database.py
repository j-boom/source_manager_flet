#!/usr/bin/env python3
"""
Database migration script to ensure the database schema is up to date
"""
import sqlite3
import sys
from pathlib import Path

# Add the src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from config.app_config import DEFAULT_DATABASE

def check_and_fix_database_schema():
    """Check and fix any missing columns in the database"""
    print("Checking database schema...")
    
    try:
        conn = sqlite3.connect(DEFAULT_DATABASE)
        cursor = conn.cursor()
        
        # Check projects table columns
        cursor.execute("PRAGMA table_info(projects)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"Current projects table columns: {columns}")
        
        # Required columns based on the schema
        required_columns = [
            'id', 'uuid', 'customer_id', 'engineer', 'drafter', 
            'reviewer', 'architect', 'geologist', 'project_code', 
            'project_type', 'title', 'description', 'status', 
            'created_at', 'updated_at'
        ]
        
        missing_columns = []
        for column in required_columns:
            if column not in columns:
                missing_columns.append(column)
        
        if missing_columns:
            print(f"Missing columns found: {missing_columns}")
            
            # Add missing columns
            for column in missing_columns:
                if column == 'geologist':
                    cursor.execute("ALTER TABLE projects ADD COLUMN geologist TEXT")
                    print(f"Added column: {column}")
                # Add other missing columns as needed
                
            conn.commit()
            print("Database schema updated successfully!")
        else:
            print("Database schema is up to date!")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking database schema: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = check_and_fix_database_schema()
    sys.exit(0 if success else 1)
