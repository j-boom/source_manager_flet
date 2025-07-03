"""
The project models module.
This module defines the data structures for managing projects and their
relationship to source records.
"""

from .project_models import Project, ProjectSourceLink, ProjectType
from .source_models import SourceRecord
from .user_config_models import UserConfig, WindowConfig, ThemeConfig, RecentProject

__all__ = [
    # Project Models
    "Project",
    "ProjectSourceLink",
    "ProjectType",
    # Source Models
    "SourceRecord",
    # User Config Models
    "UserConfig",
    "WindowConfig",
    "ThemeConfig",
    "RecentProject",
]
