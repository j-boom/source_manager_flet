"""
Base class for Project View tabs
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import flet as ft


class BaseTab(ABC):
    """Abstract base class for all project view tabs"""
    
    def __init__(self, project_state_manager, database_manager):
        self.project_state_manager = project_state_manager
        self.database_manager = database_manager
        self.edit_mode = False
        self.controls = {}
        
    @abstractmethod
    def create_content(self) -> ft.Container:
        """Create the tab content"""
        pass
        
    @abstractmethod
    def load_data(self, project_info: Optional[Dict[str, Any]] = None) -> None:
        """Load data into the tab"""
        pass
        
    @abstractmethod
    def save_data(self) -> bool:
        """Save tab data, return True if successful"""
        pass
        
    def toggle_edit_mode(self) -> None:
        """Toggle between edit and view mode"""
        self.edit_mode = not self.edit_mode
        self._update_controls_state()
        
    def _update_controls_state(self) -> None:
        """Update control states based on edit mode"""
        for control in self.controls.values():
            if hasattr(control, 'disabled'):
                control.disabled = not self.edit_mode
        if hasattr(self, 'page') and self.page:
            self.page.update()
