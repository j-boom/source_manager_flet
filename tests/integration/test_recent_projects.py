#!/usr/bin/env python3
"""Test script for recent projects functionality"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.user_config import UserConfigManager

def test_recent_projects_uniqueness():
    """Test that recent projects are unique by path"""
    print("Testing recent projects uniqueness...")
    
    # Create a test config manager
    config = UserConfigManager()
    
    # Clear existing recent sites for clean test
    config.clear_recent_sites()
    print(f"Initial recent sites: {len(config.get_recent_sites())}")
    
    # Add some test projects
    test_projects = [
        ("Project A", "/path/to/project/a"),
        ("Project B", "/path/to/project/b"),
        ("Project C", "/path/to/project/c"),
        ("Project A Updated", "/path/to/project/a"),  # Same path, should update
        ("Project D", "/path/to/project/d"),
    ]
    
    for display_name, path in test_projects:
        config.add_recent_site(display_name, path)
        print(f"Added: {display_name} -> {path}")
    
    recent_sites = config.get_recent_sites()
    print(f"\nFinal recent sites count: {len(recent_sites)}")
    
    # Check uniqueness by path
    paths = [site["path"] for site in recent_sites]
    unique_paths = set(paths)
    
    print(f"Total paths: {len(paths)}")
    print(f"Unique paths: {len(unique_paths)}")
    print(f"Are all paths unique? {len(paths) == len(unique_paths)}")
    
    # Print all recent sites
    print("\nCurrent recent sites:")
    for i, site in enumerate(recent_sites, 1):
        print(f"{i}. {site['display_name']} -> {site['path']}")
    
    # Test display name update
    print("\nTesting display name update...")
    config.update_recent_site_display_name("/path/to/project/a", "Project A - Modified")
    
    updated_sites = config.get_recent_sites()
    for site in updated_sites:
        if site["path"] == "/path/to/project/a":
            print(f"Updated display name: {site['display_name']}")
            break
    
    return len(paths) == len(unique_paths)

def test_max_recent_projects():
    """Test that recent projects are limited to 10 items"""
    print("\nTesting max recent projects limit...")
    
    config = UserConfigManager()
    config.clear_recent_sites()
    
    # Add 15 projects
    for i in range(15):
        config.add_recent_site(f"Project {i}", f"/path/to/project/{i}")
    
    recent_sites = config.get_recent_sites()
    print(f"Added 15 projects, actual count: {len(recent_sites)}")
    print(f"Max limit respected? {len(recent_sites) <= 10}")
    
    # Check that the most recent ones are kept
    first_project = recent_sites[0]
    last_project = recent_sites[-1]
    print(f"First (most recent): {first_project['display_name']}")
    print(f"Last (oldest): {last_project['display_name']}")
    
    return len(recent_sites) <= 10

if __name__ == "__main__":
    print("Testing Recent Projects Functionality")
    print("=" * 50)
    
    uniqueness_test = test_recent_projects_uniqueness()
    limit_test = test_max_recent_projects()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Uniqueness test: {'PASS' if uniqueness_test else 'FAIL'}")
    print(f"Limit test: {'PASS' if limit_test else 'FAIL'}")
    print(f"Overall: {'PASS' if all([uniqueness_test, limit_test]) else 'FAIL'}")
