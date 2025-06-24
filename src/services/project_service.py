"""
Project Management Service
Handles JSON persistence for projects
"""

import os
import json
import getpass
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from models.project_data_models import ProjectData, ProjectMetadata, ProjectRegistryEntry


class ProjectService:
    """Service for managing project data in JSON files"""
    
    def __init__(self):
        self.current_user = getpass.getuser()  # Get OS login
        
    def create_project(self, 
                      project_type: str,
                      display_name: str,
                      facility_number: str,
                      suffix: str,
                      year: str,
                      save_directory: Path,
                      type_specific_data: Optional[Dict[str, Any]] = None,
                      user_display_name: str = "") -> Optional[ProjectData]:
        """Create a new project with JSON file"""
        try:
            # Create project data
            current_time = datetime.now().isoformat()
            
            metadata = ProjectMetadata(
                project_type=project_type,
                display_name=display_name,
                facility_number=facility_number,
                suffix=suffix,
                year=year,
                date_created=current_time,
                created_by=user_display_name or self.current_user,
                date_modified=current_time,
                modified_by=user_display_name or self.current_user
            )
            
            project_data = ProjectData(
                metadata=metadata,
                type_specific_data=type_specific_data or {}
            )
            
            # Save to JSON file
            json_file_path = save_directory / f"{display_name}.json"
            self.save_project_json(project_data, json_file_path)
            
            return project_data
            
        except Exception as e:
            print(f"Error creating project: {e}")
            return None
    
    def save_project_json(self, project: ProjectData, file_path: Path):
        """Save project to JSON file"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(project.to_dict(), f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving project JSON: {e}")
            raise
    
    def load_project_json(self, file_path: Path) -> Optional[ProjectData]:
        """Load project from JSON file"""
        try:
            if not file_path.exists():
                return None
                
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            return ProjectData.from_dict(data)
            
        except Exception as e:
            print(f"Error loading project JSON: {e}")
            return None
    
    def update_project(self, project: ProjectData, file_path: Path):
        """Update project metadata and save to JSON"""
        try:
            # Update modification timestamp
            project.metadata.date_modified = datetime.now().isoformat()
            project.metadata.modified_by = self.current_user
            
            # Save to JSON file
            self.save_project_json(project, file_path)
            
        except Exception as e:
            print(f"Error updating project: {e}")
            raise
    
    def get_project_title(self, project_path: str) -> str:
        """Get project title from JSON file for display purposes"""
        try:
            project_data = self.load_project_json(Path(project_path))
            if project_data and project_data.metadata:
                return project_data.metadata.display_name
            return Path(project_path).stem  # Fallback to filename
        except:
            return Path(project_path).stem  # Fallback to filename
    
    def project_exists(self, file_path: Path) -> bool:
        """Check if project JSON file exists"""
        return file_path.exists() and file_path.is_file()
    
    def get_recent_projects(self, max_count: int = 10) -> List[Dict[str, Any]]:
        """
        Get recently accessed projects, filtering out missing JSON files
        Note: Without database, this returns empty list. 
        UI should maintain recent projects list in user config.
        """
        # Since we removed database functionality, return empty list
        # The UI layer should maintain recent projects in user configuration
        return []
    
    def delete_project(self, file_path: Path) -> bool:
        """Delete project JSON file"""
        try:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting project: {e}")
            return False
