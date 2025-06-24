"""
JSON-Only Project Management Service - Handles project creation and management
"""

import uuid
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path


class ProjectManagementService:
    """Service for managing JSON-only project creation and management"""
    
    def __init__(self):
        """Initialize JSON-only project management service"""
        pass
    
    def create_project(self, project_data: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
        """
        Create a new project as JSON file
        Returns: (success, message, project_uuid)
        """
        
        # Generate UUID
        project_uuid = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        # Add metadata to project data
        project_data.update({
            'uuid': project_uuid,
            'created_at': current_time,
            'updated_at': current_time,
            'status': project_data.get('status', 'active')
        })
        
        try:
            # Create JSON file
            success = self._save_project_json(project_data)
            if not success:
                return False, "Failed to create project JSON file", None
            
            return True, "Project created successfully", project_uuid
            
        except Exception as ex:
            return False, f"Error creating project: {str(ex)}", None
    
    def _save_project_json(self, project_data: Dict[str, Any]) -> bool:
        """Save project data to JSON file"""
        try:
            # Determine file path (you can customize this logic)
            project_name = project_data.get('title', project_data.get('name', 'Untitled'))
            safe_filename = self._create_safe_filename(project_name)
            
            # Use project directory if specified, otherwise default location
            project_dir = project_data.get('project_directory')
            if project_dir and os.path.exists(project_dir):
                file_path = os.path.join(project_dir, f"{safe_filename}.json")
            else:
                # Default to projects directory
                projects_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "projects")
                os.makedirs(projects_dir, exist_ok=True)
                file_path = os.path.join(projects_dir, f"{safe_filename}.json")
            
            # Save the JSON file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=4, ensure_ascii=False)
            
            # Store the file path in project data for reference
            project_data['file_path'] = file_path
            
            return True
            
        except Exception as ex:
            print(f"Error saving project JSON: {ex}")
            return False
    
    def _create_safe_filename(self, name: str) -> str:
        """Create a safe filename from project name"""
        # Remove or replace unsafe characters
        safe_chars = []
        for char in name:
            if char.isalnum() or char in [' ', '-', '_']:
                safe_chars.append(char)
            else:
                safe_chars.append('_')
        
        safe_name = ''.join(safe_chars).strip()
        # Replace multiple spaces/underscores with single underscore
        import re
        safe_name = re.sub(r'[_\s]+', '_', safe_name)
        
        return safe_name[:50]  # Limit length
    
    def get_project_by_uuid(self, project_uuid: str) -> Optional[Dict[str, Any]]:
        """Get project by UUID from JSON files (simplified implementation)"""
        # This is a simplified implementation - in practice you might want
        # to maintain an index of UUIDs to file paths
        projects_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "projects")
        
        if not os.path.exists(projects_dir):
            return None
        
        # Search through JSON files to find matching UUID
        for filename in os.listdir(projects_dir):
            if filename.endswith('.json'):
                try:
                    file_path = os.path.join(projects_dir, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        project_data = json.load(f)
                    
                    if project_data.get('uuid') == project_uuid:
                        project_data['file_path'] = file_path
                        return project_data
                        
                except Exception as ex:
                    print(f"Error reading project file {filename}: {ex}")
                    continue
        
        return None
    
    def update_project(self, project_uuid: str, updated_data: Dict[str, Any]) -> bool:
        """Update an existing project"""
        try:
            # Find the project
            project_data = self.get_project_by_uuid(project_uuid)
            if not project_data:
                return False
            
            # Update the data
            project_data.update(updated_data)
            project_data['updated_at'] = datetime.now().isoformat()
            
            # Save back to file
            file_path = project_data.get('file_path')
            if not file_path or not os.path.exists(file_path):
                return False
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=4, ensure_ascii=False)
            
            return True
            
        except Exception as ex:
            print(f"Error updating project: {ex}")
            return False
    
    def list_projects(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List all projects (up to limit)"""
        projects = []
        projects_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "projects")
        
        if not os.path.exists(projects_dir):
            return projects
        
        for filename in os.listdir(projects_dir):
            if filename.endswith('.json') and len(projects) < limit:
                try:
                    file_path = os.path.join(projects_dir, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        project_data = json.load(f)
                    
                    project_data['file_path'] = file_path
                    projects.append(project_data)
                    
                except Exception as ex:
                    print(f"Error reading project file {filename}: {ex}")
                    continue
        
        # Sort by updated_at or created_at, most recent first
        projects.sort(key=lambda p: p.get('updated_at', p.get('created_at', '')), reverse=True)
        
        return projects
    
    def get_recent_projects(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recently updated projects"""
        return self.list_projects(limit)
