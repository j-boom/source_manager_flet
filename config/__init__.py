"""
Configuration package initialization.
"""
from .app_config import *
from .logging_config import setup_logging

__all__ = [
    'PROJECT_ROOT', 'SRC_DIR', 'DATA_DIR', 'LOGS_DIR', 'TEMP_DIR',
    'USER_DATA_DIR', 'PROJECTS_DIR',
    'APP_NAME', 'APP_VERSION', 'DEFAULT_THEME',
    'LOG_LEVEL', 'LOG_FORMAT',
    'DEFAULT_WINDOW_WIDTH', 'DEFAULT_WINDOW_HEIGHT',
    'MIN_WINDOW_WIDTH', 'MIN_WINDOW_HEIGHT',
    'RECENT_PROJECTS_LIMIT', 'RECENT_SITES_LIMIT',
    'setup_logging'
]
