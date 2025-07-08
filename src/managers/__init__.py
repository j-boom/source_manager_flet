"""
Managers package for the source manager application.

This package provides various manager classes that handle different aspects
of the application's functionality including navigation, project state,
settings, themes, user configuration, window management, and project browsing.

Modules:
    navigation_manager: Handles application navigation and routing
    project_state_manager: Manages project state and data persistence
    settings_manager: Handles application settings and preferences
    theme_manager: Manages UI themes and styling
    user_config_manager: Handles user-specific configuration
    window_manager: Manages application window properties and behavior
    project_browser_manager: Handles project browsing and file system operations

Classes:
    NavigationManager: Main navigation controller
    ProjectStateManager: Project state management controller
    SettingsManager: Application settings controller
    ThemeManager: Theme and styling controller
    UserConfigManager: User configuration controller
    WindowManager: Window management controller
    ProjectBrowserManager: Project browsing controller
"""

from .navigation_manager import NavigationManager
from .navigation_manager import NavigationManager
from .project_state_manager import ProjectStateManager
from .settings_manager import SettingsManager
from .theme_manager import ThemeManager
from .user_config_manager import UserConfigManager
from .window_manager import WindowManager
from .project_browser_manager import ProjectBrowserManager

__all__ = [
    "NavigationManager",
    "ProjectStateManager",
    "SettingsManager",
    "ThemeManager",
    "UserConfigManager",
    "WindowManager",
    "ProjectBrowserManager",
]
