#!/usr/bin/env python3
"""
Test Regional Source Management System
Demonstrates the functionality with placeholder data
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.source_types_config import (
    RegionalSourceManager,
    get_region_for_project,
    get_sources_for_project,
    add_source_to_project
)

def test_regional_source_system():
    """Test the regional source management system"""
    print("🧪 TESTING REGIONAL SOURCE MANAGEMENT SYSTEM")
    print("=" * 60)
    
    # Test project paths
    test_projects = [
        ("/network/projects/ROW/Highway_101/project.json", "Highway 101 ROW Acquisition"),
        ("/network/projects/Other_Projects/Building_A/project.json", "Building A Renovation"),
        ("/network/projects/Downtown/Main_Street/project.json", "Main Street Redesign"),
        ("/network/projects/Random/project.json", "Random Project")
    ]
    
    print("\n📍 Testing Regional Mapping:")
    for project_path, title in test_projects:
        region = get_region_for_project(project_path)
        print(f"   {title}")
        print(f"   Path: {project_path}")
        print(f"   Region: {region}")
        print()
    
    print("\n📚 Testing Source Addition:")
    
    # Add some test sources
    test_sources = [
        {
            "project_path": "/network/projects/ROW/Highway_101/project.json",
            "project_title": "Highway 101 ROW Acquisition",
            "source_data": {
                "title": "ROW Acquisition Manual",
                "source_type": "manual",
                "authors": ["State DOT"],
                "year": 2023
            },
            "usage_notes": "Primary reference for acquisition procedures and legal requirements",
            "user_description": "Comprehensive manual covering all aspects of ROW acquisition",
            "added_by": "john.doe"
        },
        {
            "project_path": "/network/projects/ROW/Highway_101/project.json",
            "project_title": "Highway 101 ROW Acquisition",
            "source_data": {
                "title": "Environmental Impact Guidelines",
                "source_type": "standard",
                "authors": ["EPA"],
                "year": 2022
            },
            "usage_notes": "Environmental compliance requirements for ROW projects",
            "user_description": "Guidelines for environmental assessment and mitigation",
            "added_by": "jane.smith"
        },
        {
            "project_path": "/network/projects/Other_Projects/Building_A/project.json",
            "project_title": "Building A Renovation",
            "source_data": {
                "title": "Building Code Standards",
                "source_type": "standard",
                "authors": ["Local Building Dept"],
                "year": 2024
            },
            "usage_notes": "Current building codes for renovation projects",
            "user_description": "Latest building codes and safety requirements",
            "added_by": "bob.wilson"
        }
    ]
    
    for source_info in test_sources:
        success = add_source_to_project(
            source_info["project_path"],
            source_info["project_title"],
            source_info["source_data"],
            source_info["usage_notes"],
            source_info["user_description"],
            source_info["added_by"]
        )
        
        if success:
            print(f"   ✅ Added: {source_info['source_data']['title']}")
            print(f"      To: {source_info['project_title']}")
            print(f"      Region: {get_region_for_project(source_info['project_path'])}")
        else:
            print(f"   ❌ Failed to add: {source_info['source_data']['title']}")
        print()
    
    print("\n📖 Testing Source Retrieval:")
    
    for project_path, title in test_projects:
        region, sources = get_sources_for_project(project_path)
        print(f"   Project: {title}")
        print(f"   Region: {region}")
        print(f"   Sources found: {len(sources)}")
        
        for source in sources:
            print(f"      📚 {source.get('title', 'Unknown Title')}")
            
            # Show project usage for this source
            project_usage = source.get('project_usage', [])
            for usage in project_usage:
                if usage.get('project_path') == project_path:
                    print(f"         Usage: {usage.get('usage_notes', 'No notes')}")
                    print(f"         Description: {usage.get('user_description', 'No description')}")
                    print(f"         Added by: {usage.get('added_by', 'Unknown')}")
                    break
        print()
    
    print("\n🔍 Testing Cross-Region Search:")
    manager = RegionalSourceManager()
    search_results = manager.search_sources_across_regions("Building")
    
    for region, sources in search_results.items():
        print(f"   Region: {region}")
        for source in sources:
            print(f"      📚 {source.get('title', 'Unknown Title')}")
            print(f"         Used by {len(source.get('project_usage', []))} project(s)")
        print()
    
    print("\n🎯 REGIONAL SOURCE SYSTEM FEATURES DEMONSTRATED:")
    print("=" * 60)
    print("✅ Automatic region detection based on project directory")
    print("✅ Regional source files (one JSON per region)")
    print("✅ Project usage tracking with descriptions and notes")
    print("✅ Cross-project source sharing within regions")
    print("✅ Cross-region search capability")
    print("✅ User-generated tagging via usage notes")
    print("✅ Source descriptions per project context")
    print("✅ Professional editing (anyone can add/edit)")
    
    print("\n💡 READY FOR INTEGRATION:")
    print("=" * 60)
    print("🔧 Replace placeholder source datatypes with your actual classes")
    print("🔧 Update regional mappings to match your directory structure")
    print("🔧 Integrate with your UI for source management and citation")
    print("🔧 Add source type configuration similar to project types")
    
    print(f"\n📁 Master sources location: {manager.master_sources_dir}")

if __name__ == "__main__":
    test_regional_source_system()
