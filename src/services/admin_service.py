"""
Admin Service

Handles loading, modifying, and saving application configurations
such as project types and source types from JSON files.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

from config.app_config import PROJECT_TYPES_PATH, SOURCE_TYPES_PATH

class AdminService:
    """Service for managing dynamic application configurations."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        self.project_types_path = PROJECT_TYPES_PATH
        self.source_types_path = SOURCE_TYPES_PATH

        # Ensure parent directories exist before loading
        self.project_types_path.parent.mkdir(parents=True, exist_ok=True)
        self.source_types_path.parent.mkdir(parents=True, exist_ok=True)

        # Define default structures for the config files
        default_project_config = {"PROJECT_TYPES_CONFIG": {}}
        default_source_config = {"SOURCE_TYPES_CONFIG": {}}

        # Load configs, creating them if they don't exist
        self.project_types_config = self._load_or_create_config(self.project_types_path, default_project_config)
        self.source_types_config = self._load_or_create_config(self.source_types_path, default_source_config)
        self.logger.info("AdminService initialized and configurations loaded.")

    def _load_or_create_config(self, file_path: Path, default_data: Dict[str, Any]) -> Dict[str, Any]:
        """Loads a JSON file, or creates it with default data if it doesn't exist."""
        if not file_path.exists():
            self.logger.warning(f"Config file not found: {file_path}. Creating a new one.")
            self._save_json(file_path, default_data)
            return default_data
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            self.logger.error(f"Error reading or parsing {file_path}: {e}. Returning default data.")
            return default_data

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
        # The new standard format expects all project types to be nested under this key.
        # The backward-compatibility layer has been removed to enforce the new structure.
        return self.project_types_config.get("PROJECT_TYPES_CONFIG", {})
    
    def get_source_types(self) -> Dict[str, Any]:
        """Returns the current source types configuration."""
        # The new standard format expects all source types to be nested under this key.
        return self.source_types_config.get("SOURCE_TYPES_CONFIG", {})
        
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
        # Wrap in the root key
        data_to_save = {"SOURCE_TYPES_CONFIG": new_config}
        if self._save_json(self.source_types_path, data_to_save):
            # Update in-memory cache
            self.source_types_config = data_to_save
            return True
        return False
