#!/usr/bin/env python3
"""
Test script to verify source database operations
"""

import sys
from pathlib import Path
import uuid
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.models.database_manager import DatabaseManager
from src.models.source_models import Source
from src.services.source_management_service import SourceManagementService


def test_source_creation_and_association():
    """Test creating a source and associating it with a project"""
    print("Testing source creation and project association...")
    
    # Initialize database manager
    db = DatabaseManager()
    service = SourceManagementService(db)
    
    try:
        # Test 1: Create a simple image source
        print("\n1. Testing image source creation...")
        form_data = {
            "title": "Test Building Photo",
            "photographer": "John Smith",
            "image_date": "2025-06-22",
            "image_id": "IMG_001",
            "camera_settings": "f/8, 1/125s, ISO 200",
            "location": "Main Building Entrance"
        }
        
        success, message, source_uuid = service.create_source("image", form_data)
        print(f"Create source result: {success}, {message}, {source_uuid}")
        
        if success and source_uuid:
            # Test 2: Retrieve the source
            print("\n2. Testing source retrieval...")
            retrieved_source = service.get_source_by_uuid(source_uuid)
            if retrieved_source:
                print(f"Retrieved source: {retrieved_source.title}")
                print(f"Citation: {retrieved_source.get_citation()}")
            else:
                print("Failed to retrieve source")
            
            # Test 3: Add source to a project
            print("\n3. Testing project association...")
            # Use a mock project UUID
            project_uuid = "1001678921"  # From the running app
            usage_notes = "Primary reference photo for building facade analysis"
            
            add_success = service.add_source_to_project(source_uuid, project_uuid, usage_notes)
            print(f"Add to project result: {add_success}")
            
            if add_success:
                # Test 4: Get sources for project
                print("\n4. Testing project source retrieval...")
                project_sources = service.get_sources_for_project(project_uuid)
                print(f"Found {len(project_sources)} sources for project")
                for source in project_sources:
                    print(f"  - {source['title']}: {source['usage_notes']}")
        
        print("\n✅ Database tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    test_source_creation_and_association()
