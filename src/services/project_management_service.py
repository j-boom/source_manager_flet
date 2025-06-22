"""
Project Management Service - Handles project creation and management
"""

import uuid
import json
import os
from typing import List, Dict, Any, Optional, Tuple, TYPE_CHECKING
from datetime import datetime
from pathlib import Path

if TYPE_CHECKING:
    from src.models.database_manager import DatabaseManager


class ProjectManagementService:
    """Service for managing project creation and database operations"""
    
    def __init__(self, database_manager: Optional['DatabaseManager'] = None):
        self.database_manager = database_manager
    
    def create_project(self, project_data: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
        """
        Create a new project in database and JSON file
        Returns: (success, message, project_uuid)
        """
        if not self.database_manager:
            return False, "No database manager available", None
        
        # Generate UUID
        project_uuid = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        try:
            # Add to database first
            success = self._save_project_to_database(project_uuid, project_data, current_time)
            if not success:
                return False, "Failed to save project to database", None
            
            # Create JSON file
            json_success = self._create_project_json(project_uuid, project_data, current_time)
            if not json_success:
                # Rollback database if JSON creation fails
                self._remove_project_from_database(project_uuid)
                return False, "Failed to create project JSON file", None
            
            return True, "Project created successfully", project_uuid
            
        except Exception as e:
            return False, f"Error creating project: {e}", None
    
    def _save_project_to_database(self, project_uuid: str, project_data: Dict[str, Any], created_at: str) -> bool:
        """Save project to database"""
        try:
            if not self.database_manager or not hasattr(self.database_manager, 'connection'):
                return False
                
            # Find or create customer (simplified - assume customer ID 1 for now)
            customer_id = 1
            
            # Insert project
            cursor = self.database_manager.connection.cursor()
            cursor.execute("""
                INSERT INTO projects (
                    uuid, customer_id, title, description, project_type, 
                    engineer, drafter, reviewer, architect, geologist,
                    project_code, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_uuid,
                customer_id,
                project_data.get('title', ''),
                project_data.get('description', ''),
                project_data.get('project_type', ''),
                project_data.get('engineer', ''),
                project_data.get('drafter', ''),
                project_data.get('reviewer', ''),
                project_data.get('architect', ''),
                project_data.get('geologist', ''),
                project_data.get('project_code', ''),
                'active',
                created_at,
                created_at
            ))
            
            self.database_manager.connection.commit()
            return True
            
        except Exception as e:
            print(f"Error saving project to database: {e}")
            if self.database_manager and hasattr(self.database_manager, 'connection') and self.database_manager.connection:
                self.database_manager.connection.rollback()
            return False
    
    def _create_project_json(self, project_uuid: str, project_data: Dict[str, Any], created_at: str) -> bool:
        """Create JSON file for project with source ordering"""
        try:
            # Create project directory structure
            project_dir = self._get_project_directory(project_uuid, project_data)
            os.makedirs(project_dir, exist_ok=True)
            
            # Create JSON filename
            project_code = project_data.get('project_code', 'PROJ')
            project_type = project_data.get('project_type', 'STD')
            year = datetime.now().year
            filename = f"{project_uuid} - {project_code} - {project_type} - {year}.json"
            
            json_path = os.path.join(project_dir, filename)
            
            # Create JSON content
            json_data = {
                "project_uuid": project_uuid,
                "project_code": project_data.get('project_code', ''),
                "project_type": project_data.get('project_type', ''),
                "title": project_data.get('title', ''),
                "description": project_data.get('description', ''),
                "engineer": project_data.get('engineer', ''),
                "drafter": project_data.get('drafter', ''),
                "reviewer": project_data.get('reviewer', ''),
                "architect": project_data.get('architect', ''),
                "geologist": project_data.get('geologist', ''),
                "location": project_data.get('location', ''),
                "client": project_data.get('client', ''),
                "status": "active",
                "created_at": created_at,
                "updated_at": created_at,
                "source_order": []  # For ordering project sources
            }
            
            # Save JSON file
            with open(json_path, 'w') as f:
                json.dump(json_data, f, indent=4)
            
            return True
            
        except Exception as e:
            print(f"Error creating project JSON: {e}")
            return False
    
    def _get_project_directory(self, project_uuid: str, project_data: Dict[str, Any]) -> str:
        """Get the directory path for project files"""
        # Create directory structure based on project type
        base_dir = "/Users/jim/Documents/Development/source_manager_flet/data/projects"
        
        project_type = project_data.get('project_type', 'General')
        client = project_data.get('client', 'Unknown')
        title = project_data.get('title', 'Untitled')[:50]  # Limit length
        
        # Clean filename components
        safe_client = "".join(c for c in client if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        
        return os.path.join(base_dir, project_type, safe_client, f"{project_uuid} {safe_title}")
    
    def _remove_project_from_database(self, project_uuid: str) -> bool:
        """Remove project from database (rollback)"""
        try:
            if not self.database_manager or not hasattr(self.database_manager, 'connection'):
                return False
                
            cursor = self.database_manager.connection.cursor()
            cursor.execute("DELETE FROM projects WHERE uuid = ?", (project_uuid,))
            self.database_manager.connection.commit()
            return True
        except Exception as e:
            print(f"Error removing project from database: {e}")
            return False
    
    def get_project_by_uuid(self, project_uuid: str) -> Optional[Dict[str, Any]]:
        """Get project by UUID from database"""
        if not self.database_manager or not hasattr(self.database_manager, 'connection'):
            return None
        
        try:
            cursor = self.database_manager.connection.cursor()
            cursor.execute("SELECT * FROM projects WHERE uuid = ?", (project_uuid,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            print(f"Error getting project: {e}")
            return None
    
    def update_project_source_order(self, project_uuid: str, source_uuids: List[str]) -> bool:
        """Update the source order in project JSON file"""
        try:
            # Find the project JSON file
            json_path = self._find_project_json_path(project_uuid)
            if not json_path:
                print(f"Could not find JSON file for project {project_uuid}")
                return False
            
            # Load, update, and save JSON
            with open(json_path, 'r') as f:
                project_data = json.load(f)
            
            project_data['source_order'] = source_uuids
            project_data['updated_at'] = datetime.now().isoformat()
            
            with open(json_path, 'w') as f:
                json.dump(project_data, f, indent=4)
            
            return True
            
        except Exception as e:
            print(f"Error updating project source order: {e}")
            return False
    
    def get_project_source_order(self, project_uuid: str) -> List[str]:
        """Get source order from project JSON file"""
        try:
            json_path = self._find_project_json_path(project_uuid)
            if not json_path:
                return []
            
            with open(json_path, 'r') as f:
                project_data = json.load(f)
            
            return project_data.get('source_order', [])
            
        except Exception as e:
            print(f"Error getting project source order: {e}")
            return []
    
    def _find_project_json_path(self, project_uuid: str) -> Optional[str]:
        """Find the JSON file path for a project"""
        # Search in the projects directory
        base_dir = "/Users/jim/Documents/Development/source_manager_flet/data/projects"
        
        if not os.path.exists(base_dir):
            return None
        
        # Walk through all subdirectories looking for JSON files with matching UUID
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.endswith('.json') and file.startswith(project_uuid):
                    return os.path.join(root, file)
        
        return None
