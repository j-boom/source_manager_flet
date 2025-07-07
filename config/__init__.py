"""
Configuration package initialization.
"""

from .app_config import *
from .logging_config import setup_logging
from .project_types_config import get_dialog_fields, get_project_type_display_names, get_project_type_config, create_field_widget

__all__ = [
    "PROJECT_ROOT",
    "SRC_DIR",
    "DATA_DIR",
    "LOGS_DIR",
    "TEMP_DIR",
    "USER_DATA_DIR",
    "PROJECTS_DIR",
    "APP_NAME",
    "APP_VERSION",
    "DEFAULT_THEME",
    "LOG_LEVEL",
    "LOG_FORMAT",
    "DEFAULT_WINDOW_WIDTH",
    "DEFAULT_WINDOW_HEIGHT",
    "MIN_WINDOW_WIDTH",
    "MIN_WINDOW_HEIGHT",
    "RECENT_PROJECTS_LIMIT",
    "RECENT_SITES_LIMIT",
    "setup_logging",
    "get_dialog_fields",
    "get_project_type_display_names",
    "get_project_type_config",
    "create_field_widget",
]
