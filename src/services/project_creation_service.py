"""Project creation service for handling project file creation and validation"""

import os
import json
import datetime
import re
from typing import Dict, Any, Optional, List
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.project_types_config import get_all_project_types, get_project_type_display_names, get_project_type_config


class ProjectCreationService:
    """Handles project creation logic and validation"""
    
    def __init__(self, user_config=None):
        self.user_config = user_config
        # Load project types from the new configuration
        self.project_type_display_names = get_project_type_display_names()
        self.project_type_codes = {v: k for k, v in self.project_type_display_names.items()}
        self.project_types = get_all_project_types()
    
    def validate_project_data(self, project_type: str, document_title: str = "") -> List[str]:
        """Validate project creation data and return list of errors"""
        errors = []
        
        # Convert display name to code if needed
        if project_type in self.project_type_codes:
            project_type = self.project_type_codes[project_type]
        
        if not project_type:
            errors.append("Project type is required")
        elif project_type not in self.project_types:
            errors.append(f"Invalid project type. Must be one of: {', '.join(self.get_project_type_options())}")
        
        # Document title validation - required for OTH
        if project_type == "OTH" and not document_title.strip():
            errors.append("Document title is required for OTH projects")
        
        return errors
    
    def generate_filename(self, ten_digit_number: str, project_type: str, suffix: str, 
                         document_title: str = "") -> str:
        """Generate the project filename"""
        parts = [ten_digit_number, suffix]
        
        if project_type == "OTH" and document_title:
            parts = [document_title]
        
        else:
            parts.append(project_type)

        year = str(datetime.datetime.now().year)
        parts.append(year)
        
        return " - ".join(parts) + ".json"
    
    def create_project_data(self, ten_digit_number: str, project_type: str, suffix: str,
                           document_title: str = "", folder_path: str = "") -> Dict[str, Any]:
        """Create the project data structure"""
        filename = self.generate_filename(ten_digit_number, project_type, suffix, document_title)
        
        return {
            "project_id": ten_digit_number,
            "project_suffix": suffix,
            "project_type": project_type,
            "document_title": document_title if document_title else None,
            "created_date": datetime.datetime.now().isoformat(),
            "metadata": {
                "folder_path": folder_path,
                "filename": filename
            }
        }
    
    def save_project_file(self, project_data: Dict[str, Any], folder_path: str, project_title: str = "") -> tuple[bool, str]:
        """Save the project file and return (success, message)"""
        try:
            # Ensure the folder path exists
            if not os.path.exists(folder_path):
                return False, f"Folder path does not exist: {folder_path}"
            
            if not os.path.isdir(folder_path):
                return False, f"Path is not a directory: {folder_path}"
            
            filename = project_data["metadata"]["filename"]
            file_path = os.path.join(folder_path, filename)
            
            # Check if file already exists
            if os.path.exists(file_path):
                return False, f"File already exists: {filename}"
            
            # Create the file
            with open(file_path, 'w') as f:
                json.dump(project_data, f, indent=4)
            
            # Verify the file was created
            if not os.path.exists(file_path):
                return False, f"File creation failed: {filename}"
            
            # Add to recent projects if user_config is available
            if self.user_config:
                # Use project title if provided, otherwise fall back to filename
                display_name = project_title if project_title.strip() else filename.replace(".json", "")
                self.user_config.add_recent_site(display_name, folder_path)
            
            return True, f"Project '{filename}' created successfully!"
            
        except PermissionError:
            return False, f"Permission denied: Cannot write to {folder_path}"
        except Exception as ex:
            return False, f"Error creating file: {str(ex)}"
    
    def is_document_title_required(self, project_type: str) -> bool:
        """Check if document title is required for the given project type"""
        return project_type == "OTH"
    
    def get_current_year_options(self, years_ahead: int = 4) -> List[str]:
        """Get list of year options starting from current year"""
        current_year = datetime.datetime.now().year
        return [str(year) for year in range(current_year, current_year + years_ahead + 1)]

    def get_project_type_options(self) -> List[str]:
        """Get list of project type display names for dropdown"""
        return list(self.project_type_display_names.values())
    
    def get_project_type_code(self, display_name: str) -> str:
        """Get project type code from display name"""
        return self.project_type_codes.get(display_name, display_name)
    
    def get_project_type_display_name(self, code: str) -> str:
        """Get project type display name from code"""
        return self.project_type_display_names.get(code, code)
