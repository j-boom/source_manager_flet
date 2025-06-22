#!/usr/bin/env python3
"""
Test database save functionality
"""
import sys
from pathlib import Path

# Add the src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from models.database_manager import DatabaseManager

def test_database_connection():
    """Test database connection and operations"""
    try:
        db = DatabaseManager()
        print("Database manager created successfully")
        
        # Try to get an existing project using UUID from database
        test_uuid = "8916ce6e-be3a-4495-a767-6d7649beb424"  # From the database query
        project = db.get_project(test_uuid)
        
        if project:
            print(f"Found project: {project.title} (UUID: {project.uuid})")
            
            # Try to update the project
            test_data = {
                'description': 'Test update from debug script',
                'status': 'active'
            }
            
            success = db.update_project(project.uuid, test_data)
            print(f"Update result: {success}")
            
            if success:
                print("Database update test passed!")
            else:
                print("Database update test failed!")
        else:
            print(f"Project with UUID {test_uuid} not found")
            
    except Exception as e:
        print(f"Database test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database_connection()
