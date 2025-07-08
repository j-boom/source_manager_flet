"""
Project State Manager

Handles the in-memory state of the currently loaded project.
This class does NOT perform any file I/O; that is the responsibility
of the ProjectService.
"""
from typing import Optional, Dict, Any, List
from models import Project, SourceRecord

class ProjectStateManager:
    """Manages the in-memory state of the currently active project."""
    
    def __init__(self):
        """Initializes the manager with no project loaded."""
        self.current_project: Optional[Project] = None
    
    def load_project(self, project_model: Project):
        """
        Loads a project into the application's state.

        Args:
            project_model: A Project model object, typically loaded by the ProjectService.
        """
        self.current_project = project_model
        print(f"Project '{project_model.title}' loaded into state.")

    def unload_project(self):
        """Clears the currently loaded project from the state."""
        if self.current_project:
            print(f"Unloading project '{self.current_project.title}' from state.")
        self.current_project = None

    def has_loaded_project(self) -> bool:
        """Checks if a project is currently loaded in the state."""
        return self.current_project is not None
    
    # --- Accessor Methods ---
    # These methods delegate to the loaded Project model. This provides a stable
    # interface for the rest of the app, even if the Project model changes.

    def get_project_title(self) -> str:
        """Gets the title of the loaded project."""
        if not self.has_loaded_project():
            return "No Project Loaded"
        return self.current_project.title
    
    def get_project_path(self) -> Optional[str]:
        """Gets the file path of the loaded project."""
        # This assumes the project model itself knows its path after being loaded.
        # An alternative is to store the path here alongside the model.
        if not self.has_loaded_project():
            return None
        return getattr(self.current_project, 'file_path', None)

    def get_project_metadata(self) -> Optional[Dict[str, Any]]:
        """Gets the metadata of the loaded project."""
        if not self.has_loaded_project():
            return None
        # In a real model, this might be project.metadata or similar
        return self.current_project.to_dict()

    def get_project_sources(self) -> List[SourceRecord]:
        """Gets the sources of the loaded project."""
        if not self.has_loaded_project():
            return []
        return self.current_project.sources
