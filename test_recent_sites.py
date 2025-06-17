#!/usr/bin/env python3
"""
Test the recent projects functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.user_config import UserConfigManager

def test_recent_sites():
    """Test the recent sites functionality"""
    config_manager = UserConfigManager()
    
    print("=== Testing Recent Sites Functionality ===")
    
    # Test getting current recent sites
    current_sites = config_manager.get_recent_sites()
    print(f"\nCurrent recent sites ({len(current_sites)}):")
    for i, site in enumerate(current_sites, 1):
        print(f"  {i}. {site['display_name']} -> {site['path']}")
    
    # Test adding a new site
    print("\n=== Adding new site ===")
    config_manager.add_recent_site("Test Project", "/path/to/test/project")
    
    updated_sites = config_manager.get_recent_sites()
    print(f"\nAfter adding new site ({len(updated_sites)}):")
    for i, site in enumerate(updated_sites, 1):
        print(f"  {i}. {site['display_name']} -> {site['path']}")
    
    # Test adding duplicate (should move to top)
    print("\n=== Adding duplicate site (should move to top) ===")
    config_manager.add_recent_site("React Dashboard", "/Users/jim/Documents/Projects/react-dashboard")
    
    final_sites = config_manager.get_recent_sites()
    print(f"\nAfter adding duplicate ({len(final_sites)}):")
    for i, site in enumerate(final_sites, 1):
        print(f"  {i}. {site['display_name']} -> {site['path']}")
    
    # Test removing a site
    print("\n=== Removing a site ===")
    config_manager.remove_recent_site("/path/to/test/project")
    
    after_removal = config_manager.get_recent_sites()
    print(f"\nAfter removal ({len(after_removal)}):")
    for i, site in enumerate(after_removal, 1):
        print(f"  {i}. {site['display_name']} -> {site['path']}")
    
    print("\n=== Test completed successfully! ===")

if __name__ == "__main__":
    test_recent_sites()
