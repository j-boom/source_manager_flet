"""
User Config Manager

Manages loading, saving, and providing access to user-specific configuration.
This class is the single point of interaction for user settings in the Source Manager application.
Handles window state, theme, display name, setup status, and recent projects.
"""

import getpass
import logging
from typing import Optional, List

# Configuration imports
from config.app_config import (
    USER_DATA_DIR,
    DEFAULT_WINDOW_WIDTH,
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_THEME,
)

# Model imports from our new file
from src.models.user_config_models import (
    UserConfig,
    WindowConfig,
    ThemeConfig,
    RecentProject,
)


class UserConfigManager:
    """
    Manages loading, saving, and accessing user-specific configuration settings.

    This class acts as the interface between the rest of the application and the user's configuration data.
    It provides methods to get and set window state, theme, display name, setup status, and recent projects.
    All persistence is handled via JSON files in the user's data directory.
    """

    def __init__(self):
        """
        Initializes the UserConfigManager for the current user.
        Loads the user's config from disk, or creates a default config if none exists.
        """
        self.logger = logging.getLogger(__name__)
        self.username = getpass.getuser()
        self.config_dir = USER_DATA_DIR
        self.config_file = self.config_dir / f"{self.username}.json"

        # Define the default configuration using our dataclasses
        self.default_config = UserConfig(
            window=WindowConfig(
                width=DEFAULT_WINDOW_WIDTH,
                height=DEFAULT_WINDOW_HEIGHT,
                maximized=False,
            ),
            theme=ThemeConfig(mode=DEFAULT_THEME, color="blue"),
        )

        # Load or create config
        self.config = self._load_config()

    def _load_config(self) -> UserConfig:
        """
        Loads the user configuration from disk, or returns the default config if not found or invalid.
        Returns:
            UserConfig: The loaded or default user configuration.
        """
        self.config_dir.mkdir(parents=True, exist_ok=True)
        config = UserConfig.load_from_json(self.config_file)
        if config:
            self.logger.info(f"Loaded config for user: {self.username}")
            return config
        self.logger.warning(
            f"No config for '{self.username}' found or it was corrupt. Creating new default config."
        )
        return self.default_config

    def save_config(self):
        """
        Saves the current configuration to its JSON file on disk.
        Logs success or error.
        """
        try:
            self.config.save_to_json(self.config_file)
            self.logger.info(f"Config saved for user: {self.username}")
        except Exception as e:
            self.logger.error(f"Error saving config: {e}", exc_info=True)

    # --- Accessor & Mutator Methods ---

    def get_window_config(self) -> WindowConfig:
        """
        Returns the current window configuration (size, position, maximized state).
        Returns:
            WindowConfig: The current window configuration.
        """
        return self.config.window

    def save_window_config(
        self,
        width: int,
        height: int,
        x: Optional[int],
        y: Optional[int],
        maximized: bool,
    ):
        """
        Updates and saves the window configuration.
        Args:
            width (int): Window width in pixels.
            height (int): Window height in pixels.
            x (Optional[int]): X position on screen.
            y (Optional[int]): Y position on screen.
            maximized (bool): Whether the window is maximized.
        """
        self.config.window = WindowConfig(
            width=width, height=height, x=x, y=y, maximized=maximized
        )
        self.save_config()

    def get_theme_mode(self) -> str:
        """
        Returns the current theme mode ("light" or "dark").
        Returns:
            str: The current theme mode.
        """
        return self.config.theme.mode

    def save_theme_mode(self, mode: str):
        """
        Sets and saves the theme mode ("light" or "dark").
        Args:
            mode (str): The theme mode to set.
        """
        if mode in ["light", "dark"]:
            self.config.theme.mode = mode
            self.save_config()

    def get_theme_color(self) -> str:
        """
        Returns the current theme color name.
        Returns:
            str: The current theme color.
        """
        return self.config.theme.color

    def save_theme_color(self, color: str):
        """
        Sets and saves the theme color.
        Args:
            color (str): The color name to set.
        """
        self.config.theme.color = color
        self.save_config()

    def get_display_name(self) -> Optional[str]:
        """
        Returns the user's display name, if set.
        Returns:
            Optional[str]: The display name, or None if not set.
        """
        return self.config.display_name

    def save_display_name(self, display_name: str):
        """
        Sets and saves the user's display name.
        Args:
            display_name (str): The display name to set.
        """
        self.config.display_name = display_name.strip() if display_name else None
        self.save_config()

    def get_greeting(self) -> str:
        """
        Returns a personalized greeting for the user.
        Returns:
            str: Greeting string.
        """
        if self.config.display_name:
            return f"Hi, {self.config.display_name}!"
        return f"Hi, {self.username}!"

    def is_setup_completed(self) -> bool:
        """
        Returns True if the user has completed initial setup.
        Returns:
            bool: True if setup is complete, False otherwise.
        """
        return self.config.setup_completed

    def mark_setup_completed(self):
        """
        Marks the setup as completed and saves the config.
        """
        self.config.setup_completed = True
        self.save_config()

    def needs_setup(self) -> bool:
        """
        Returns True if the user needs to complete setup (not completed or no display name).
        Returns:
            bool: True if setup is needed, False otherwise.
        """
        return not self.is_setup_completed() or not self.get_display_name()

    def get_recent_projects(self) -> List[RecentProject]:
        """
        Returns the list of recently opened projects.
        Returns:
            List[RecentProject]: List of recent projects.
        """
        return self.config.recent_projects

    def add_recent_project(self, display_name: str, path: str):
        """
        Adds a project to the top of the recent projects list.
        If the project already exists, it is moved to the top.
        Only the 10 most recent projects are kept.
        Args:
            display_name (str): The display name of the project.
            path (str): The filesystem path to the project.
        """
        # Remove if already exists to move it to the top
        self.config.recent_projects = [
            p for p in self.config.recent_projects if p.path != path
        ]
        # Add to the beginning of the list
        self.config.recent_projects.insert(
            0, RecentProject(display_name=display_name, path=path)
        )
        # Keep only the 10 most recent
        self.config.recent_projects = self.config.recent_projects[:10]
        self.save_config()

    def clear_recent_projects(self):
        """
        Clears the list of recent projects and saves the config.
        """
        self.config.recent_projects.clear()
        self.save_config()

    def remove_recent_project(self, path_to_remove: str):
        """
        Removes a project from the recent projects list by its path and saves the config.
        Args:
            path_to_remove (str): The path of the project to remove.
        """
        self.config.recent_projects = [
            p for p in self.config.recent_projects if p.path != path_to_remove
        ]
        self.save_config()
