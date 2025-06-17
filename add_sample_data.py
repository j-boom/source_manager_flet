#!/usr/bin/env python3
"""
Test script to add sample recent sites to the user config
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.user_config import UserConfigManager

def add_sample_data():
    """Add sample recent sites for testing"""
    config_manager = UserConfigManager()
    
    # Add some sample recent sites
    sample_sites = [
        {"display_name": "My Website Project", "path": "/Users/jim/Documents/Projects/website"},
        {"display_name": "Python API Server", "path": "/Users/jim/Documents/Projects/api-server"},
        {"display_name": "React Dashboard", "path": "/Users/jim/Documents/Projects/react-dashboard"},
        {"display_name": "Mobile App Backend", "path": "/Users/jim/Documents/Projects/mobile-backend"},
        {"display_name": "Data Analysis Scripts", "path": "/Users/jim/Documents/Projects/data-analysis"},
    ]
    
    for site in sample_sites:
        config_manager.add_recent_site(site["display_name"], site["path"])
    
    print(f"Added {len(sample_sites)} sample recent sites")
    print("Recent sites:")
    for site in config_manager.get_recent_sites():
        print(f"  - {site['display_name']}: {site['path']}")

if __name__ == "__main__":
    add_sample_data()
