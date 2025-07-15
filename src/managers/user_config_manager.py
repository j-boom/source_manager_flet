"""
User Config Manager (Restructured)

Manages loading, saving, and providing access to user-specific configuration.
This class is the single point of interaction for user settings.
"""
import getpass
import logging
from pathlib import Path
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
    """Manages loading, saving, and accessing user-specific configuration settings."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.username = getpass.getuser()
        self.config_dir = USER_DATA_DIR / "users"
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
        """Load configuration from file or return defaults."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        config = UserConfig.load_from_json(self.config_file)
        if config:
            self.logger.info(f"Loaded config for user: {self.username}")
            return config
        
        self.logger.warning(f"No config for '{self.username}' found or it was corrupt. Creating new default config.")
        return self.default_config

    def save_config(self):
        """Save current configuration to its JSON file."""
        try:
            self.config.save_to_json(self.config_file)
            self.logger.info(f"Config saved for user: {self.username}")
        except Exception as e:
            self.logger.error(f"Error saving config: {e}", exc_info=True)

    # --- Accessor & Mutator Methods ---

    def get_window_config(self) -> WindowConfig:
        return self.config.window

    def save_window_config(self, width: int, height: int, x: Optional[int], y: Optional[int], maximized: bool):
        self.config.window = WindowConfig(width=width, height=height, x=x, y=y, maximized=maximized)
        self.save_config()

    def get_theme_mode(self) -> str:
        return self.config.theme.mode

    def save_theme_mode(self, mode: str):
        if mode in ["light", "dark"]:
            self.config.theme.mode = mode
            self.save_config()

    def get_theme_color(self) -> str:
        return self.config.theme.color

    def save_theme_color(self, color: str):
        self.config.theme.color = color
        self.save_config()

    def get_display_name(self) -> Optional[str]:
        return self.config.display_name

    def save_display_name(self, display_name: str):
        self.config.display_name = display_name.strip() if display_name else None
        self.save_config()

    def get_greeting(self) -> str:
        if self.config.display_name:
            return f"Hi, {self.config.display_name}!"
        return f"Hi, {self.username}!"

    def is_setup_completed(self) -> bool:
        return self.config.setup_completed

    def mark_setup_completed(self):
        self.config.setup_completed = True
        self.save_config()
    
    def needs_setup(self) -> bool:
        return not self.is_setup_completed() or not self.get_display_name()

    def get_recent_projects(self) -> List[RecentProject]:
        return self.config.recent_projects

    def add_recent_project(self, display_name: str, path: str):
        """Adds a project to the top of the recent projects list."""
        # Remove if already exists to move it to the top
        self.config.recent_projects = [p for p in self.config.recent_projects if p.path != path]
        # Add to the beginning of the list
        self.config.recent_projects.insert(0, RecentProject(display_name=display_name, path=path))
        # Keep only the 10 most recent
        self.config.recent_projects = self.config.recent_projects[:10]
        self.save_config()

    def clear_recent_projects(self):
        """Clears the list of recent projects."""
        self.config.recent_projects.clear()
        self.save_config()

    def remove_recent_project(self, path_to_remove: str):
        """Removes a project from the recent projects list by its path."""
        self.config.recent_projects = [
            p for p in self.config.recent_projects if p.path != path_to_remove
        ]
        self.save_config()

    def validate_recent_projects(self):
        """Validates the list of recent projects, removing any that no longer exist."""
        self.logger.info("Validating recent projects list...")
        self.config.recent_projects = [
            p for p in self.config.recent_projects if Path(p).exists()
        ]
        self.save_config()
