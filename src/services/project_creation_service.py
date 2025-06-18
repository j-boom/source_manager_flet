"""Project creation service for handling project file creation and validation"""

import os
import json
import datetime
import re
from typing import Dict, Any, Optional, List


class ProjectCreationService:
    """Handles project creation logic and validation"""
    
    # Display names for dropdown
    PROJECT_TYPES = [
        "Code Compliance Review",
        "General Site Conditions", 
        "Standard",
        "Field Condition Report",
        "Commercial",
        "Code Review Summary",
        "Other"
    ]
    
    # Mapping from display names to codes for filename
    PROJECT_TYPE_CODES = {
        "Code Compliance Review": "CCR",
        "General Site Conditions": "GSC", 
        "Standard": "STD",
        "Field Condition Report": "FCR",
        "Commercial": "COM",
        "Code Review Summary": "CRS",
        "Other": "OTH"
    }
    
    SUFFIX_PATTERN = r'^[A-Z]{2}\d{3}$'
    
    def __init__(self, user_config=None):
        self.user_config = user_config
    
    def validate_project_data(self, project_type: str, suffix: str, year: str, document_title: str = "") -> List[str]:
        """Validate project creation data and return list of errors"""
        errors = []
        
        if not project_type:
            errors.append("Project type is required")
        elif project_type not in self.PROJECT_TYPES:
            errors.append(f"Invalid project type. Must be one of: {', '.join(self.PROJECT_TYPES)}")
        
        if not year:
            errors.append("Request year is required")
        elif not year.isdigit():
            errors.append("Year must be a valid number")
        
        # Get the project type code for validation
        project_code = self.PROJECT_TYPE_CODES.get(project_type, project_type)
        
        # Suffix validation - required for all except GSC
        if project_code != "GSC" and not suffix:
            errors.append("Suffix is required for this project type")
        
        if suffix and not re.match(self.SUFFIX_PATTERN, suffix):
            errors.append("Suffix must be in format AB123 (2 letters + 3 digits)")
        
        # Document title validation - NO LONGER REQUIRED for OTH projects
        # Removed the requirement that was causing issues
        
        return errors
    
    def generate_filename(self, ten_digit_number: str, project_type: str, suffix: str = "", 
                         year: str = "", document_title: str = "") -> str:
        """Generate the project filename using project type codes"""
        parts = [ten_digit_number]
        
        if suffix:
            parts.append(suffix)
        
        # Convert display name to code for filename
        project_code = self.PROJECT_TYPE_CODES.get(project_type, project_type)
        if project_code:
            parts.append(project_code)
        
        # No longer adding document title to filename for OTH projects
        
        if year:
            parts.append(year)
        
        return " - ".join(parts) + ".json"
    
    def create_project_data(self, ten_digit_number: str, project_type: str, suffix: str = "",
                           year: str = "", document_title: str = "", folder_path: str = "") -> Dict[str, Any]:
        """Create the project data structure"""
        filename = self.generate_filename(ten_digit_number, project_type, suffix, year, document_title)
        
        return {
            "project_id": ten_digit_number,
            "project_type": project_type,
            "suffix": suffix if suffix else None,
            "document_title": document_title if document_title else None,
            "request_year": int(year) if year else None,
            "created_date": datetime.datetime.now().isoformat(),
            "status": "active",
            "metadata": {
                "folder_path": folder_path,
                "filename": filename
            }
        }
    
    def save_project_file(self, project_data: Dict[str, Any], folder_path: str) -> tuple[bool, str]:
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
                display_name = filename.replace(".json", "")
                self.user_config.add_recent_site(display_name, folder_path)
            
            return True, f"Project '{filename}' created successfully!"
            
        except PermissionError:
            return False, f"Permission denied: Cannot write to {folder_path}"
        except Exception as ex:
            return False, f"Error creating file: {str(ex)}"
    
    def is_suffix_required(self, project_type: str) -> bool:
        """Check if suffix is required for the given project type"""
        return project_type != "GSC"
    
    def is_document_title_required(self, project_type: str) -> bool:
        """Check if document title is required for the given project type"""
        # Document title is no longer required for any project type
        return False
    
    def get_current_year_options(self, years_ahead: int = 4) -> List[str]:
        """Get list of year options starting from current year"""
        current_year = datetime.datetime.now().year
        return [str(year) for year in range(current_year, current_year + years_ahead + 1)]
    
    def format_suffix(self, suffix: str) -> str:
        """Format suffix to uppercase"""
        return suffix.strip().upper() if suffix else ""
