"""
Project State Manager - Tracks currently loaded project
"""
from typing import Optional, Dict, Any
from .project_models import Project

class ProjectStateManager:
    """Manages the current project state in the application"""
    
    def __init__(self):
        self.current_project: Optional[Project] = None
        self.current_project_data: Optional[Dict[str, Any]] = None
        self.project_file_path: Optional[str] = None
        
    def load_project(self, project: Project, project_data: Optional[Dict[str, Any]] = None, file_path: Optional[str] = None):
        """Load a project into the application state"""
        self.current_project = project
        self.current_project_data = project_data or {}
        self.project_file_path = file_path
        
    def unload_project(self):
        """Clear the current project state"""
        self.current_project = None
        self.current_project_data = None
        self.project_file_path = None
        
    def has_loaded_project(self) -> bool:
        """Check if a project is currently loaded"""
        return self.current_project is not None
        
    def get_project_title(self) -> str:
        """Get the title of the currently loaded project"""
        if self.current_project and self.current_project.project_title:
            return self.current_project.project_title
        return "No Project Loaded"
        
    def get_project_info(self) -> Dict[str, Any]:
        """Get comprehensive project information"""
        if not self.current_project:
            return {}
            
        return {
            "uuid": self.current_project.uuid,
            "title": self.current_project.project_title,
            "project_type": self.current_project.project_type,
            "project_code": self.current_project.project_code,
            "engineer": self.current_project.engineer,
            "drafter": self.current_project.drafter,
            "reviewer": self.current_project.reviewer,
            "architect": self.current_project.architect,
            "requestor_name": self.current_project.requestor_name,
            "request_date": self.current_project.request_date,
            "relook": self.current_project.relook,
            "file_path": self.project_file_path,
            "data": self.current_project_data
        }
