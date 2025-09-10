import json
from pathlib import Path
from typing import Dict, Any
from config.app_config import SOURCE_TYPES_PATH, PROJECT_TYPES_PATH

class ConfigService:
    """Service for managing configuration files."""

    def __init__(self):
        """Initializes the ConfigService."""
        self.source_types_path = SOURCE_TYPES_PATH
        self.project_types_path = PROJECT_TYPES_PATH

    def get_source_types(self) -> Dict[str, Any]:
        """Reads the source types from the JSON file."""
        if not self.source_types_path.exists():
            return {}
        with open(self.source_types_path, "r") as f:
            return json.load(f)

    def get_project_types(self) -> Dict[str, Any]:
        """Reads the project types from the JSON file."""
        if not self.project_types_path.exists():
            return {}
        with open(self.project_types_path, "r") as f:
            return json.load(f)

    def save_source_types(self, data: Dict[str, Any]):
        """Saves the source types to the JSON file."""
        with open(self.source_types_path, "w") as f:
            json.dump(data, f, indent=4)

    def save_project_types(self, data: Dict[str, Any]):
        """Saves the project types to the JSON file."""
        with open(self.project_types_path, "w") as f:
            json.dump(data, f, indent=4)
