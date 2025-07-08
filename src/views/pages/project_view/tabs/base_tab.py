"""
Base Tab

Provides a base class for all tabs within the ProjectView to ensure
a consistent interface for initialization and data updates.
"""

import flet as ft
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTab(ABC):
    """An abstract base class for creating tabs in the ProjectView."""

    def __init__(self, controller):
        """
        Initializes the BaseTab.

        Args:
            controller: The main AppController instance, providing access to managers and services.
        """
        self.controller = controller
        self.page = controller.page
        self.project_state_manager = controller.project_state_manager

    @abstractmethod
    def build(self) -> ft.Control:
        """
        Abstract method for building the main content of the tab.
        Subclasses MUST implement this.
        """
        pass

    def update_project_data(self, project_data: Dict[str, Any], project_path: str):
        """
        An optional method for tabs to implement if they need to react to
        project data changes after initialization.
        """
        pass

