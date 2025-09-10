"""
Configuration package initialization.
"""

from .app_config import *
from .logging_config import setup_logging

__all__ = [
    "PROJECT_ROOT",
    "SRC_DIR",
    "LOGS_DIR",
    "USER_DATA_DIR",
    "APP_NAME",
    "APP_VERSION",
    "DEFAULT_THEME",
    "DEFAULT_WINDOW_WIDTH",
    "DEFAULT_WINDOW_HEIGHT",
    "MIN_WINDOW_WIDTH",
    "MIN_WINDOW_HEIGHT",
    "setup_logging",
]