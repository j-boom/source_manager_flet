"""
Base class for Project View tabs
"""

import flet as ft
from abc import ABC, abstractmethod
from typing import Optional
from services.project_creation_service import ProjectCreationService


class BaseProjectTab(ABC):
    """Abstract base class for all project view tabs"""
    
    def __init__(self, page: ft.Page, theme_manager=None, database_manager=None, project_state_manager=None):
        self.page = page
        self.theme_manager = theme_manager
        self.database_manager = database_manager
        self.project_state_manager = project_state_manager
        
        # Edit mode state
        self.edit_mode = False
        
    @abstractmethod
    def build(self) -> ft.Control:
        """Build the tab content"""
        pass
        
    def _get_theme_color(self) -> str:
        """Get the current theme color"""
        if self.theme_manager:
            return self.theme_manager.get_current_color()
        return ft.colors.BLUE_600
        
    def _get_project_info(self) -> dict:
        """Get current project information"""
        if self.project_state_manager and self.project_state_manager.has_loaded_project():
            return self.project_state_manager.get_project_info()
        return {}
        
    def _create_text_field(self, key: str, label: str, value: str, width: int = 300, hint_text: Optional[str] = None) -> ft.TextField:
        """Create a text field with edit mode support"""
        # Get theme-appropriate colors for edit mode
        if self.edit_mode:
            theme_color = self._get_theme_color()
            border_color = theme_color
            bgcolor = None
        else:
            bgcolor = None
            border_color = ft.colors.GREY_400
            
        field = ft.TextField(
            label=label,
            value=value,
            width=width,
            hint_text=hint_text,
            read_only=not self.edit_mode,
            bgcolor=bgcolor,
            border_color=border_color,
            focused_border_color=self._get_theme_color() if self.edit_mode else None
        )
        
        return field
        
    def _create_checkbox_field(self, key: str, label: str, value: bool) -> ft.Checkbox:
        """Create a checkbox field with edit mode support"""
        field = ft.Checkbox(
            label=label,
            value=value,
            disabled=not self.edit_mode
        )
        
        return field
        
    def refresh(self):
        """Refresh the tab content"""
        # Override in subclasses if needed
        pass
