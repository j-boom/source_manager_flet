#!/usr/bin/env python3
"""
Test script to verify project metadata configuration
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.project_types_config import get_project_type_config
import json

def test_project_metadata():
    """Test project metadata configuration"""
    
    # Load the sample project JSON
    project_file = project_root / "data/Directory_Source_Citations/ROW/1234/1234567890 Sample Project Folder/1234567890 - 2025 - STD - 2025.json"
    
    if project_file.exists():
        with open(project_file, 'r') as f:
            project_data = json.load(f)
        
        print("📁 LOADED PROJECT DATA:")
        print(f"   Project Type: {project_data.get('project_type', 'Unknown')}")
        print(f"   Title: {project_data.get('title', 'No title')}")
        print(f"   Keys in JSON: {list(project_data.keys())}")
        
        # Check if old database fields are present
        old_fields = ['engineer', 'drafter', 'reviewer', 'architect', 'geologist']
        found_old_fields = [field for field in old_fields if field in project_data]
        
        if found_old_fields:
            print(f"   ⚠️  OLD DATABASE FIELDS FOUND: {found_old_fields}")
        else:
            print("   ✅ No old database fields found")
        
        # Get the configuration for this project type
        project_type = project_data.get('project_type', 'STD')
        config = get_project_type_config(project_type)
        
        if config:
            print(f"\n🔧 PROJECT TYPE CONFIGURATION ({project_type}):")
            print(f"   Display Name: {config.display_name}")
            print(f"   Description: {config.description}")
            print(f"   Total Fields: {len(config.fields)}")
            
            print("\n📋 CONFIGURED FIELDS:")
            for field in config.fields:
                has_data = field.name in project_data
                status = "✅" if has_data else "❌"
                value = project_data.get(field.name, 'No data')
                print(f"   {status} {field.name}: {field.label} = '{value}'")
        else:
            print(f"\n❌ No configuration found for project type: {project_type}")
    
    else:
        print(f"❌ Project file not found: {project_file}")

if __name__ == "__main__":
    test_project_metadata()
