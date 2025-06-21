"""
Application configuration settings.
"""
import os
from pathlib import Path

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
TEMP_DIR = PROJECT_ROOT / "temp"

# Database configuration
DATABASE_DIR = DATA_DIR / "databases"
DEFAULT_DATABASE = DATABASE_DIR / "source_manager.db"
DATABASE_SCHEMA = DATABASE_DIR / "database_schema.sql"

# User data paths
USER_DATA_DIR = DATA_DIR / "user_data"
PROJECTS_DIR = DATA_DIR / "projects"

# Application settings
APP_NAME = "Source Manager"
APP_VERSION = "1.0.0"
DEFAULT_THEME = "dark"

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Window settings
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600

# Directory management
RECENT_PROJECTS_LIMIT = 10
RECENT_SITES_LIMIT = 10

# Project type mappings (code -> display name)
PROJECT_TYPE_DISPLAY_NAMES = {
    "CCR": "Change Control Request",
    "GSC": "Government Specification Check", 
    "STD": "Standard Drawing",
    "FCR": "Field Change Request",
    "COM": "Commissioning",
    "CRS": "Correspondence",
    "OTH": "Other"
}

# Reverse mapping for getting codes from display names
PROJECT_TYPE_CODES = {v: k for k, v in PROJECT_TYPE_DISPLAY_NAMES.items()}

# Create directories if they don't exist
for directory in [DATA_DIR, LOGS_DIR, TEMP_DIR, DATABASE_DIR, USER_DATA_DIR, PROJECTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
