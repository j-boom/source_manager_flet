"""
Project State Manager - Handles the state of the currently loaded project
"""

import os
import json
from typing import Dict, Any, Optional


class ProjectStateManager:
    """Manages the state of the currently loaded project"""
    
    def __init__(self):
        self.loaded_project_path = None
        self.project_data = None
        self.project_metadata = {}
        self.project_sources = []
        self.project_slide_assignments = []
    
    def load_project(self, project_path: str) -> bool:
        """
        Load a project from a JSON file path
        Returns True if successful, False otherwise
        """
        try:
            if os.path.exists(project_path) and project_path.lower().endswith(".json"):
                with open(project_path, "r") as f:
                    project_data = json.load(f)
                
                self.loaded_project_path = project_path
                self.project_data = project_data
                
                # Extract relevant data from the loaded project
                self.project_metadata = project_data.get("metadata", {})
                self.project_sources = project_data.get("sources", [])
                self.project_slide_assignments = project_data.get("slide_assignments", [])
                
                return True
            else:
                print(f"Invalid project file: {project_path}")
                return False
        except Exception as e:
            print(f"Error loading project: {e}")
            return False
    
    def has_loaded_project(self) -> bool:
        """Check if a project is currently loaded"""
        return self.loaded_project_path is not None and self.project_data is not None
    
    def get_project_title(self) -> str:
        """Get the title/name of the loaded project"""
        if not self.has_loaded_project():
            return "No Project Loaded"
        
        # Try to get title from metadata, or use filename as fallback
        title = self.project_metadata.get("title", "")
        if not title and self.loaded_project_path:
            title = os.path.basename(self.loaded_project_path)
            # Remove extension if present
            title = os.path.splitext(title)[0] 
            
        return title
    
    def get_project_path(self) -> Optional[str]:
        """Get the path of the loaded project file"""
        return self.loaded_project_path
    
    def get_project_metadata(self) -> Dict[str, Any]:
        """Get the metadata of the loaded project"""
        return self.project_metadata
    
    def get_project_sources(self) -> list:
        """Get the sources of the loaded project"""
        return self.project_sources
    
    def get_project_slide_assignments(self) -> list:
        """Get the slide assignments of the loaded project"""
        return self.project_slide_assignments
    
    def update_project_metadata(self, metadata: Dict[str, Any]):
        """Update project metadata"""
        self.project_metadata = metadata
        if self.project_data:
            self.project_data["metadata"] = metadata
    
    def update_project_sources(self, sources: list):
        """Update project sources"""
        self.project_sources = sources
        if self.project_data:
            self.project_data["sources"] = sources
    
    def update_project_slide_assignments(self, assignments: list):
        """Update project slide assignments"""
        self.project_slide_assignments = assignments
        if self.project_data:
            self.project_data["slide_assignments"] = assignments
    
    def save_project(self) -> bool:
        """Save the current project to disk"""
        if not self.has_loaded_project() or not self.loaded_project_path:
            return False
        
        try:
            # Update project data with current state
            self.project_data = {
                "metadata": self.project_metadata,
                "sources": self.project_sources,
                "slide_assignments": self.project_slide_assignments
            }
            
            with open(self.loaded_project_path, "w") as f:
                json.dump(self.project_data, f, indent=4)
            
            return True
        except Exception as e:
            print(f"Error saving project: {e}")
            return False
