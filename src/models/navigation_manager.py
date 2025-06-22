from typing import Dict, Callable, Optional
from .user_config import UserConfigManager


class NavigationManager:
    """Manages application navigation and page routing"""
    
    def __init__(self, user_config: UserConfigManager):
        self.user_config = user_config
        # Always start with home page, ignore saved last page for startup
        self.current_page = "home"
        self.navigation_callback: Optional[Callable[[str], None]] = None
        
        # Define valid pages
        self.valid_pages = ["home", "projects", "sources", "reports", "settings", "help"]
    
    def set_navigation_callback(self, callback: Callable[[str], None]):
        """Set the callback function for navigation changes"""
        self.navigation_callback = callback
    
    def navigate_to(self, page_name: str, trigger_callback: bool = True):
        """Navigate to a specific page"""
        if page_name in self.valid_pages:
            self.current_page = page_name
            self.user_config.save_last_page(page_name)
            
            if trigger_callback and self.navigation_callback:
                self.navigation_callback(page_name)
        else:
            print(f"Warning: Invalid page name: {page_name}")
    
    def get_current_page(self) -> str:
        """Get the current page name"""
        return self.current_page
    
    def get_page_index(self, page_name: str) -> Optional[int]:
        """Get the navigation index for a page"""
        page_mapping = {
            "home": 0,
            "projects": 1,
            "sources": 2,
            "reports": 3
        }
        return page_mapping.get(page_name)
    
    def get_page_from_index(self, index: int) -> Optional[str]:
        """Get page name from navigation index"""
        index_mapping = {
            0: "home",
            1: "projects",
            2: "sources",
            3: "reports"
        }
        return index_mapping.get(index)
    
    def is_valid_page(self, page_name: str) -> bool:
        """Check if a page name is valid"""
        return page_name in self.valid_pages
