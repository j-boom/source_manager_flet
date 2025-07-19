"""
The project models module.
This module defines the data structures for managing projects and their
relationship to source records.
"""

from .project_models import Project,  ProjectType, ProjectSourceLink
from .source_models import SourceRecord, SourceRecordFactory, SourceType
from .user_config_models import UserConfig, WindowConfig, ThemeConfig, RecentProject

__all__ = [
    # Project Models
    "Project",
    "ProjectType",
    # Source Models
    "ProjectSourceLink",
    "SourceRecord",
    "SourceRecordFactory",
    "SourceType",
    # User Config Models
    "UserConfig",
    "WindowConfig",
    "ThemeConfig",
    "RecentProject",
]
