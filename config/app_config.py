
"""
Application Configuration

This file is the single source of truth for all application-level configuration,
including paths, constants, and navigation structure.
"""

from pathlib import Path

import flet as ft


# =============================================================================
# Core Path Definitions
# =============================================================================
# Root directory of the project (one level above this config file)
PROJECT_ROOT = Path(__file__).parent.parent
# Source code directory
SRC_DIR = PROJECT_ROOT / "src"

# Base directory for all application data (user, project, and master sources)
BASE_DATA_DIR = Path("/Users/jim/Documents/Source Manager")

# Directory for application logs (kept with source code for development)
LOGS_DIR = PROJECT_ROOT / "logs"

# Directory containing all project data, organized by region/country/project
PROJECT_DATA_DIR = BASE_DATA_DIR / "Directory_Source_Citations"

# Directory containing master source files (used for reference or templates)
MASTER_SOURCES_DIR = BASE_DATA_DIR / "program_files" / "master_sources"

# Directory for user-specific data (e.g., user config, user projects)
USER_DATA_DIR = BASE_DATA_DIR / "user_data"

# Path to legacy data (used for migration from older versions)
OLD_DATA_PATH = "/Users/jim/Documents/Source Manager/Directory Source Citations"
# Directory for user project files
USER_PROJECTS_DIR = USER_DATA_DIR / "projects"

# Path to the target folder
DEFAULT_SAVE_DIR = "/Users/jim/Documents"


# =============================================================================
# Application Settings
# =============================================================================
# Application display name
APP_NAME = "Source Manager 2.0"
# Application version string
APP_VERSION = "2.0.0"
# Default theme mode ("light" or "dark")
DEFAULT_THEME = "dark"


# =============================================================================
# Window Settings
# =============================================================================
# Default window size (pixels)
DEFAULT_WINDOW_WIDTH = 1900
DEFAULT_WINDOW_HEIGHT = 900
# Minimum window size (pixels)
MIN_WINDOW_WIDTH = 1000
MIN_WINDOW_HEIGHT = 700


# =============================================================================
# Navigation and Page Configuration
# =============================================================================
# List of main navigation pages for the application sidebar
PAGES = [
    {
        "name": "home",
        "label": "Home",
        "icon": ft.icons.HOME_OUTLINED,
        "selected_icon": ft.icons.HOME,
        "view_name": "HomeView",
    },
    {
        "name": "project_view",  # Route for project view (dynamic)
        "label": "Project",
        "icon": ft.icons.FOLDER_OUTLINED,
        "selected_icon": ft.icons.FOLDER,
        "view_name": "NewProjectView",  # Default project view
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

# Dictionary of special pages (not in main navigation)
SPECIAL_PAGES = {
    "new_project": {"view_name": "NewProjectView"},
    "project_dashboard": {"view_name": "ProjectView"},
    "recent_projects": {"view_name": "RecentProjectsView"},
    "settings": {"view_name": "SettingsView"},
    "help": {"view_name": "HelpView"},
}



# =============================================================================
# Country-Based Source Mapping Configuration
# =============================================================================

def get_country_from_project_path(project_path: Path) -> str:
    """
    Extract the country name from a project path structure.

    The expected structure is:
        {BASE_DIR}/Directory_Source_Citations/{REGION}/{COUNTRY}/{BE_PREFIX}/{BE_FOLDER}/{PROJECT}/...

    Args:
        project_path (Path): Path to the project file or directory.

    Returns:
        str: Country name if found in the expected structure, otherwise "General".
    """
    try:
        # Normalize to relative path from PROJECT_DATA_DIR
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
    Return the source filename for a given country.

    Args:
        country (str): Country name.

    Returns:
        str: Filename for the country's source file.
    """
    return f"{country}_sources.json"
