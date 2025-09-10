"""
Admin Service

Handles loading, modifying, and saving application configurations
such as project types and source types from JSON files.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

from config.app_config import PROJECT_ROOT

class AdminService:
    """Service for managing dynamic application configurations."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config_dir = PROJECT_ROOT / "data" / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.project_types_path = self.config_dir / "project_types.json"
        self.source_types_path = self.config_dir / "source_types.json"

        self.project_types_config = self._load_json(self.project_types_path)
        self.source_types_config = self._load_json(self.source_types_path)
        self.logger.info("AdminService initialized and configurations loaded.")

    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """Loads a JSON file and returns its content."""
        if not file_path.exists():
            self.logger.warning(f"Config file not found: {file_path}. Returning empty dict.")
            return {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            self.logger.error(f"Error reading or parsing {file_path}: {e}")
            return {}

    def _save_json(self, file_path: Path, data: Dict[str, Any]):
        """Saves data to a JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            self.logger.info(f"Configuration saved successfully to {file_path}.")
            return True
        except Exception as e:
            self.logger.error(f"Error saving configuration to {file_path}: {e}")
            return False

    def get_project_types(self) -> Dict[str, Any]:
        """Returns the current project types configuration."""
        return self.project_types_config.get("PROJECT_TYPES_CONFIG", {})
    
    def get_source_types(self) -> Dict[str, Any]:
        """Returns the current source types configuration."""
        return self.source_types_config
        
    def save_project_types(self, new_config: Dict[str, Any]) -> bool:
        """Saves the updated project types configuration."""
        # Wrap in the root key
        data_to_save = {"PROJECT_TYPES_CONFIG": new_config}
        if self._save_json(self.project_types_path, data_to_save):
            # Update in-memory cache
            self.project_types_config = data_to_save
            return True
        return False

    def save_source_types(self, new_config: Dict[str, Any]) -> bool:
        """Saves the updated source types configuration."""
        if self._save_json(self.source_types_path, new_config):
            # Update in-memory cache
            self.source_types_config = new_config
            return True
        return False
