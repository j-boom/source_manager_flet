"""
Navigation Controller - Handles navigation-related operations.

This controller could manage navigation history, breadcrumbs, etc.
"""

from .base_controller import BaseController


class NavigationController(BaseController):
    """Handles navigation-related operations."""
    
    def __init__(self, app_controller):
        super().__init__(app_controller)
        # Navigation-specific initialization could go here
        pass
    
    # Future navigation methods could be added here
    # For now, most navigation is handled directly in AppController
