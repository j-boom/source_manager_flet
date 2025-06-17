#!/usr/bin/env python3
"""
Test the database integration with project creation
"""

from database_manager import DatabaseManager, Customer, Project
from services.project_creation_service import ProjectCreationService
import uuid

def test_project_creation_integration():
    """Test the complete project creation workflow with database"""
    print("Testing Project Creation with Database Integration...")
    
    # Remove existing test database
    import os
    test_db_path = "test_project_creation.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
        print(f"Removed existing test database: {test_db_path}")
    
    # Initialize components
    db = DatabaseManager(test_db_path)
    project_service = ProjectCreationService()
    
    # Test data
    ten_digit_number = "1001234567"
    customer_key = ten_digit_number[:4]  # "1001"
    
    # Test 1: Create customer
    print("\n1. Testing customer creation...")
    customer_data = {
        'key': customer_key,
        'name': 'Test Corporation',
        'number': customer_key,
        'suffix': 'A'
    }
    
    customer_id = db.get_or_create_customer(customer_data)
    print(f"Customer created/retrieved with ID: {customer_id}")
    
    # Test 2: Create project
    print("\n2. Testing project creation...")
    project_uuid = str(uuid.uuid4())
    project = Project(
        uuid=project_uuid,
        customer_id=customer_id,
        engineer="John Doe",
        drafter="Jane Smith",
        reviewer="Bob Wilson",
        architect="Alice Brown",
        project_code="DC123",
        project_type="CCR",
        title="Test Project Alpha",
        description="A test project for database integration"
    )
    
    project_id = db.create_project(project)
    print(f"Project created with ID: {project_id}")
    
    # Test 3: Retrieve and verify
    print("\n3. Testing data retrieval...")
    retrieved_project = db.get_project(project_uuid)
    if retrieved_project:
        print(f"✅ Retrieved project: {retrieved_project.title}")
        print(f"   Engineer: {retrieved_project.engineer}")
        print(f"   Project Type: {retrieved_project.project_type}")
        print(f"   Customer ID: {retrieved_project.customer_id}")
    else:
        print("❌ Failed to retrieve project")
    
    # Test 4: Get projects by customer
    print("\n4. Testing customer projects query...")
    customer_projects = db.get_projects_by_customer(customer_key)
    print(f"Found {len(customer_projects)} projects for customer {customer_key}")
    for proj in customer_projects:
        print(f"   - {proj.title} ({proj.project_code})")
    
    # Test 5: Test duplicate customer handling
    print("\n5. Testing duplicate customer handling...")
    customer_id_2 = db.get_or_create_customer(customer_data)
    if customer_id == customer_id_2:
        print("✅ Duplicate customer properly handled (same ID returned)")
    else:
        print("❌ Duplicate customer created unexpectedly")
    
    # Test 6: Create second project for same customer
    print("\n6. Testing multiple projects for same customer...")
    project_uuid_2 = str(uuid.uuid4())
    project_2 = Project(
        uuid=project_uuid_2,
        customer_id=customer_id,
        engineer="Mary Johnson",
        project_code="DC124",
        project_type="STD",
        title="Test Project Beta"
    )
    
    project_id_2 = db.create_project(project_2)
    print(f"Second project created with ID: {project_id_2}")
    
    # Final verification
    print("\n7. Final verification...")
    final_projects = db.get_projects_by_customer(customer_key)
    print(f"Customer {customer_key} now has {len(final_projects)} projects")
    
    # Test project service validation
    print("\n8. Testing project service validation...")
    errors = project_service.validate_project_data("CCR", "DC123", "2025", "")
    if not errors:
        print("✅ Project validation passed")
    else:
        print(f"❌ Project validation failed: {errors}")
    
    db.close()
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    test_project_creation_integration()
