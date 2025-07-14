"""
Application Configuration (Updated)

This file is the single source of truth for all application-level configuration,
including paths, constants, and navigation structure.
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import List
import flet as ft

# =============================================================================
# Core Path Definitions
# =============================================================================
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"

# Updated for production environment - data now lives in separate directory
BASE_DATA_DIR = Path("/Users/jim/Documents/Source Manager")
DATA_DIR = BASE_DATA_DIR  # For compatibility with existing code
LOGS_DIR = PROJECT_ROOT / "logs"  # Keep logs with source code for development

PROJECT_DATA_DIR = BASE_DATA_DIR / "Directory Source Citations"
MASTER_SOURCES_DIR = BASE_DATA_DIR / "program_files" / "master_sources"
USER_DATA_DIR = BASE_DATA_DIR / "user_data"

# Migration paths
OLD_DATA_PATH = "/Users/jim/Documents/Source Manager/Directory Source Citations"
USER_PROJECTS_DIR = USER_DATA_DIR / "projects"

# =============================================================================
# Application Settings
# =============================================================================
APP_NAME = "Source Manager"
APP_VERSION = "1.0.0"
DEFAULT_THEME = "dark"

# =============================================================================
# Window Settings
# =============================================================================
DEFAULT_WINDOW_WIDTH = 1900
DEFAULT_WINDOW_HEIGHT = 900
MIN_WINDOW_WIDTH = 1000
MIN_WINDOW_HEIGHT = 700

# =============================================================================
# Navigation and Page Configuration
# =============================================================================
PAGES = [
    {
        "name": "home",
        "label": "Home",
        "icon": ft.icons.HOME_OUTLINED,
        "selected_icon": ft.icons.HOME,
        "view_name": "HomeView",
    },
    {
        "name": "project_view", # This is the "smart route"
        "label": "Project",
        "icon": ft.icons.FOLDER_OUTLINED,
        "selected_icon": ft.icons.FOLDER,
        "view_name": "NewProjectView", # This is a default
    },
    {
        "name": "sources",
        "label": "Sources",
        "icon": ft.icons.SOURCE_OUTLINED,
        "selected_icon": ft.icons.SOURCE,
        "view_name": "SourcesView",
    },
    {
        "name": "reports",
        "label": "Reports",
        "icon": ft.icons.ANALYTICS_OUTLINED,
        "selected_icon": ft.icons.ANALYTICS,
        "view_name": "ReportsView",
    },
]

# --- CHANGE: Settings and Help are now defined as special pages ---
SPECIAL_PAGES = {
    "new_project": {"view_name": "NewProjectView"},
    "project_dashboard": {"view_name": "ProjectView"}, # <-- Crucial for this fix
    "recent_projects": {"view_name": "RecentProjectsView"},
    "settings": {"view_name": "SettingsView"},
    "help": {"view_name": "HelpView"},
}


# =============================================================================
# Country-Based Source Mapping Configuration
# =============================================================================

def get_country_from_project_path(project_path: Path) -> str:
    """
    Extracts the country name from a project path structure.
    
    Expected structure: {BASE_DIR}/Directory Source Citations/{REGION}/{COUNTRY}/{PROJECT}/...
    
    Args:
        project_path: Path to the project file or directory
        
    Returns:
        Country name if found in the expected structure, otherwise "General"
    """
    try:
        # Convert to relative path from PROJECT_DATA_DIR to normalize
        if PROJECT_DATA_DIR in project_path.parents:
            relative_path = project_path.relative_to(PROJECT_DATA_DIR)
            path_parts = relative_path.parts
            
            # Expected structure: REGION/COUNTRY/PROJECT/...
            if len(path_parts) >= 2:
                country = path_parts[1]  # Second level is country
                return country
                
    except (ValueError, IndexError):
        pass
    
    # Fallback to "General" if structure doesn't match
    return "General"


def get_source_file_for_country(country: str) -> str:
    """
    Returns the source filename for a given country.
    
    Args:
        country: Country name
        
    Returns:
        Filename for the country's source file
    """
    return f"{country}_sources.json"
