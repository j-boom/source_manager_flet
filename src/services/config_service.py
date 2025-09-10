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
        print(f"DEBUG: Attempting to read source types from: {self.source_types_path}")
        if not self.source_types_path.exists():
            print(f"DEBUG: Source types file not found: {self.source_types_path}")
            return {}
        try:
            with open(self.source_types_path, "r") as f:
                data = json.load(f)
                print(f"DEBUG: Successfully loaded source types: {data}")
                return data
        except json.JSONDecodeError as e:
            print(f"ERROR: JSON decoding error in {self.source_types_path}: {e}")
            return {}
        except IOError as e:
            print(f"ERROR: IO error reading {self.source_types_path}: {e}")
            return {}

    def get_project_types(self) -> Dict[str, Any]:
        """Reads the project types from the JSON file."""
        print(f"DEBUG: Attempting to read project types from: {self.project_types_path}")
        if not self.project_types_path.exists():
            print(f"DEBUG: Project types file not found: {self.project_types_path}")
            return {}
        try:
            with open(self.project_types_path, "r") as f:
                data = json.load(f)
                print(f"DEBUG: Successfully loaded project types: {data}")
                return data
        except json.JSONDecodeError as e:
            print(f"ERROR: JSON decoding error in {self.project_types_path}: {e}")
            return {}
        except IOError as e:
            print(f"ERROR: IO error reading {self.project_types_path}: {e}")
            return {}

    def save_source_types(self, data: Dict[str, Any]):
        """Saves the source types to the JSON file."""
        with open(self.source_types_path, "w") as f:
            json.dump(data, f, indent=4)

    def save_project_types(self, data: Dict[str, Any]):
        """Saves the project types to the JSON file."""
        with open(self.project_types_path, "w") as f:
            json.dump(data, f, indent=4)
