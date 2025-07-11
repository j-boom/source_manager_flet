"""
Base Controller for all subcontrollers in the Source Manager application.

This provides common functionality and a reference to the main AppController.
"""

from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from .app_controller import AppController


class BaseController:
    """Base class for all subcontrollers."""
    
    def __init__(self, app_controller: 'AppController'):
        self.app = app_controller
        self.page = app_controller.page
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Quick access to commonly used services and managers
        self.data_service = app_controller.data_service
        self.project_state_manager = app_controller.project_state_manager
        self.navigation_manager = app_controller.navigation_manager
        self.user_config_manager = app_controller.user_config_manager
