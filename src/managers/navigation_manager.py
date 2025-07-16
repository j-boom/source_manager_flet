"""
Navigation Manager

A simple state machine that holds the name of the currently active page.
It does not contain any navigation logic or hardcoded page data.
"""
from typing import Optional
import logging

class NavigationManager:
    """Manages the application's current navigation state."""
    
    def __init__(self):
        """Initializes the navigation manager, starting at the home page."""
        self.current_page: str = "home"
        self.previous_page: Optional[str] = None
        self.logger = logging.getLogger(__name__)
        self.logger.info("NavigationManager initialized with home page")

    def set_current_page(self, page_name: str):
        """
        Updates the current page state.

        Args:
            page_name: The name of the page to set as current (e.g., "home", "settings").
        """
        self.previous_page = self.current_page
        self.current_page = page_name
        self.logger.info(f"Navigation: {self.previous_page} -> {self.current_page}")
    
    def get_current_page(self) -> str:
        """
        Gets the name of the currently active page.
        
        Returns:
            The name of the current page.
        """
        return self.current_page

    def get_previous_page(self) -> Optional[str]:
        """
        Gets the name of the previously active page.
        
        Returns:
            The name of the previous page, or None if there is no previous page.
        """
        return self.previous_page