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
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

PROJECT_DATA_DIR = DATA_DIR / "Directory_Source_Citations"
MASTER_SOURCES_DIR = DATA_DIR / "master_sources"
USER_DATA_DIR = DATA_DIR / "user_data"

# =============================================================================
# Application Settings
# =============================================================================
APP_NAME = "Source Manager"
APP_VERSION = "1.0.0"
DEFAULT_THEME = "dark"

# =============================================================================
# Window Settings
# =============================================================================
DEFAULT_WINDOW_WIDTH = 1400
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
        "name": "project_view",
        "label": "Project",
        "icon": ft.icons.FOLDER_OUTLINED,
        "selected_icon": ft.icons.FOLDER,
        "view_name": "NewProjectView",
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
    "recent_projects": {"view_name": "RecentProjectsView"},
    "settings": {"view_name": "SettingsView"},
    "help": {"view_name": "HelpView"},
}


# =============================================================================
# Regional Source Mapping Configuration
# =============================================================================
@dataclass
class RegionalMapping:
    """Configuration for a regional source mapping."""

    region_name: str
    directory_patterns: List[str]
    source_file: str
    display_name: str
    description: str
    priority: int = 0


REGIONAL_MAPPINGS = [
    RegionalMapping(
        region_name="ROW",
        directory_patterns=["**/ROW/**", "**/Right_of_Way/**"],
        source_file="ROW_sources.json",
        display_name="Right of Way",
        description="Sources specific to Right of Way projects",
        priority=10,
    ),
    RegionalMapping(
        region_name="Other",
        directory_patterns=["**/Other_Projects/**", "**/Other/**"],
        source_file="Other_sources.json",
        display_name="Other Projects",
        description="General project sources",
        priority=5,
    ),
    RegionalMapping(
        region_name="General",
        directory_patterns=["**"],
        source_file="General_sources.json",
        display_name="General Sources",
        description="Default sources for all other projects",
        priority=1,
    ),
]
