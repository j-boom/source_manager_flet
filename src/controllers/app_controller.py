import getpass
import logging
import flet as ft
from typing import Dict, Any

from src.services.data_service import DataService
from src.managers.user_config_manager import UserConfigManager
from src.managers.navigation_manager import NavigationManager
from src.managers.project_state_manager import ProjectStateManager
from src.managers.project_browser_manager import ProjectBrowserManager
from src.managers.theme_manager import ThemeManager
from src.views.main_view import MainView

# Import the specialized controllers
from .project_controller import ProjectController
from .source_controller import SourceController
from .dialog_controller import DialogController
from .powerpoint_controller import PowerPointController
from .navigation_controller import NavigationController

class AppController:
    """
    The main controller for the application.
    Orchestrates interactions between the views, data services, and managers.
    It holds instances of specialized controllers to delegate tasks.
    """

    def __init__(self, page: ft.Page):
        """
        Initializes the AppController.

        Args:
            page (ft.Page): The Flet page object.
        """
        logging.info("Initializing AppController")
        self.page = page
        self.page.title = "Source Manager"

        # Initialize services and managers
        self.data_service = DataService()
        self.user_config_manager = UserConfigManager()
        self.navigation_manager = NavigationManager()
        self.project_state_manager = ProjectStateManager()
        self.theme_manager = ThemeManager()
        self.project_browser_manager = ProjectBrowserManager(data_service=self.data_service)

        # CORRECTED: Reverted controller instance names to match what views expect.
        self.project_controller = ProjectController(self)
        self.source_controller = SourceController(self)
        self.dialog_controller = DialogController(self)
        self.powerpoint_controller = PowerPointController(self)
        self.navigation_controller = NavigationController(self)

        # Initialize views
        self.main_view = MainView(controller=self, page=page)
        self.view_instances: Dict[str, Any] = {}
        self.project_dependent_views = ['project_dashboard', 'project_sources', 'cite_sources', 'project_metadata']

        logging.info("AppController initialized successfully")

    def start(self):
        """
        Starts the application.
        """
        self.page.add(self.main_view.build())
        self.refresh_theme()
        self.navigate_to("home")

    def refresh_theme(self):
        """
        Refreshes the application theme based on user settings.
        """
        self.main_view.refresh_theme()

    def navigate_to(self, page_name: str, force_refresh: bool = False):
        """
        Navigates to a specified page.

        Args:
            page_name (str): The name of the page to navigate to.
            force_refresh (bool): Whether to force a refresh of the view.
        """
        logging.info(f"DIAGNOSTIC: Navigation requested for '{page_name}'...")
        
        if force_refresh and page_name in self.view_instances:
            logging.info(f"DIAGNOSTIC: Popped '{page_name}' from view cache to force refresh.")
            self.view_instances.pop(page_name, None)

        self.navigation_manager.set_current_page(page_name)
        content = self.get_page_content(page_name)

        self.main_view.set_content(content)
        self.page.update()
        logging.info(f"DIAGNOSTIC: Navigation to '{page_name}' complete.")


    def get_page_content(self, page_name: str) -> ft.Control:
        """
        Gets the content for a specified page.

        Args:
            page_name (str): The name of the page.

        Returns:
            ft.Control: The content of the page.
        """
        if page_name not in self.view_instances:
            view_class = self.main_view.get_view_class(page_name)
            if view_class:
                instance = view_class(controller=self, page=self.page)
                self.view_instances[page_name] = instance
            else:
                return ft.Text(f"Unknown page: {page_name}")
        
        return self.view_instances[page_name].build()

    def update_view(self, page_name: str = None):
        """
        Updates the current view or a specified view.

        Args:
            page_name (str, optional): The name of the page to update. Defaults to the current page.
        """
        if page_name is None:
            page_name = self.navigation_manager.get_current_page()
        
        logging.info(f"Calling update_view() on instance for page '{page_name}'.")
        if page_name in self.view_instances:
            self.view_instances[page_name].update_view()
        else:
            logging.warning(f"No view instance found for page '{page_name}' to update.")

        self.main_view.update()

    def clear_project_dependent_view_cache(self):
        """
        Clears the cache for views that depend on project data.
        """
        logging.info("Clearing project-dependent view cache...")
        for view_name in self.project_dependent_views:
            if view_name in self.view_instances:
                del self.view_instances[view_name]

    def show_success_message(self, message):
        """Displays a success message to the user using a SnackBar."""
        logging.info(message)
        snack_bar = ft.SnackBar(ft.Text(message), bgcolor=ft.colors.GREEN)
        self.page.overlay.append(snack_bar)
        snack_bar.open = True
        self.page.update()

    def show_error_message(self, message):
        """Displays an error message to the user using a SnackBar."""
        logging.error(message)
        snack_bar = ft.SnackBar(ft.Text(message), bgcolor=ft.colors.RED)
        self.page.overlay.append(snack_bar)
        snack_bar.open = True
        self.page.update()
