"""
User Configuration Data Models

Defines the authoritative data structures for user-specific settings in the Source Manager application.
Includes window state, theme preferences, recent projects, and serialization logic for saving/loading user config.
"""

from __future__ import annotations
import json
import logging
from pathlib import Path
from dataclasses import dataclass, field, asdict, fields
from typing import List, Optional, Dict, Any


@dataclass
class WindowConfig:
    """
    Stores the state of the application window.

    Attributes:
        width (int): Window width in pixels.
        height (int): Window height in pixels.
        x (Optional[int]): X position of the window (screen coordinates).
        y (Optional[int]): Y position of the window (screen coordinates).
        maximized (bool): Whether the window is maximized.
    """
    width: int
    height: int
    x: Optional[int] = None
    y: Optional[int] = None
    maximized: bool = False


@dataclass
class ThemeConfig:
    """
    Stores the user's selected theme.

    Attributes:
        mode (str): Theme mode, e.g., "light" or "dark".
        color (str): Theme accent color, e.g., "blue".
    """
    mode: str  # e.g., "light" or "dark"
    color: str # e.g., "blue"


@dataclass
class RecentProject:
    """
    Stores a reference to a recently opened project.

    Attributes:
        display_name (str): The user-friendly name of the project.
        path (str): Filesystem path to the project.
    """
    display_name: str
    path: str


@dataclass
class UserConfig:
    """
    The main container for all user-specific settings.

    Attributes:
        window (WindowConfig): Window state and position.
        theme (ThemeConfig): User's theme preferences.
        display_name (Optional[str]): User's display name (optional).
        setup_completed (bool): Whether the initial setup has been completed.
        recent_projects (List[RecentProject]): List of recently opened projects.
        last_page (str): The last page/view visited by the user.
    """
    window: WindowConfig
    theme: ThemeConfig
    display_name: Optional[str] = None
    setup_completed: bool = False
    recent_projects: List[RecentProject] = field(default_factory=list)
    last_page: str = "home"

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the entire config into a dictionary suitable for JSON export.
        Returns:
            dict: Dictionary representation of the user config.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UserConfig:
        """
        Creates a UserConfig instance from a dictionary, handling nested dataclasses.
        Args:
            data (dict): Dictionary containing user config data.
        Returns:
            UserConfig: Instantiated UserConfig object.
        """
        # Handle nested dataclasses
        data['window'] = WindowConfig(**data.get('window', {}))
        data['theme'] = ThemeConfig(**data.get('theme', {}))
        data['recent_projects'] = [RecentProject(**rp) for rp in data.get('recent_projects', [])]
        # Only pass valid fields to the constructor
        field_names = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in field_names}
        return cls(**filtered_data)

    def save_to_json(self, file_path: Path):
        """
        Saves the current config state to a JSON file.
        Args:
            file_path (Path): Path to the JSON file to write.
        """
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load_from_json(cls, file_path: Path) -> Optional[UserConfig]:
        """
        Loads a UserConfig from a JSON file, returning None if loading fails.
        Args:
            file_path (Path): Path to the JSON file to read.
        Returns:
            Optional[UserConfig]: Loaded UserConfig object, or None if loading fails.
        """
        if not file_path.exists():
            return None
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            logging.getLogger(__name__).error(f"Error loading user config from {file_path}: {e}")
            return None