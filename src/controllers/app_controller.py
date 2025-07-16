import logging
import flet as ft
from typing import Dict, Optional

from src.services.data_service import DataService
from src.managers.user_config_manager import UserConfigManager
from src.managers.navigation_manager import NavigationManager
from src.managers.project_state_manager import ProjectStateManager
from src.managers.project_browser_manager import ProjectBrowserManager
from src.managers.theme_manager import ThemeManager
from src.managers.settings_manager import SettingsManager
from src.views.main_view import MainView

# Import the specialized controllers
from .project_controller import ProjectController
from .source_controller import SourceController
from .dialog_controller import DialogController
from .powerpoint_controller import PowerPointController
from .navigation_controller import NavigationController
from .settings_controller import SettingsController


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
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing AppController")

        # Initialize services and managers
        self.data_service = DataService()
        self.user_config_manager = UserConfigManager()
        self.navigation_manager = NavigationManager()
        self.project_state_manager = ProjectStateManager()
        self.project_browser_manager = ProjectBrowserManager(
            data_service=self.data_service
        )
        self.theme_manager = ThemeManager()
        self.settings_manager = SettingsManager()
        # Setup sub controllers
        self.project_controller = ProjectController(self)
        self.source_controller = SourceController(self)
        self.dialog_controller = DialogController(self)
        self.powerpoint_controller = PowerPointController(self)
        self.navigation_controller = NavigationController(self)
        self.settings_controller = SettingsController(self)

        # Initialize views
        self.main_view = MainView(controller=self, page=page)
        self.views: Dict[str, ft.Control] = {}
        self._view_class_map = self.navigation_controller.build_view_class_map()
        logging.info("AppController initialized successfully")

    def run(self):
        """Starts the application's main loop."""
        # Apply theme
        theme_mode = self.settings_manager.get_theme_mode()
        theme_color = self.settings_manager.get_theme_color()
        self.theme_manager.set_theme_mode(theme_mode)
        self.theme_manager.set_theme_color(theme_color)
    
        self.settings_controller.apply_theme()
        self.main_view.show()
        if self.settings_manager.needs_setup():
            self.dialog_controller.show_first_time_setup()
        else:
            self.navigate_to("home")

    def navigate_to(self, page_name: str, force_refresh: bool = False):
        """Handles navigation requests from any part of the UI."""
        if force_refresh and page_name in self.views:
            self.logger.info(f"Forcing refresh for view: '{page_name}'")
            del self.views[page_name]

        self.logger.info(f"Navigation requested for '{page_name}'...")
        self.navigation_controller.navigate_to_page(page_name)

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

    def update_view(self, page_name: Optional[str] = None):
        """
        Updates the current view by calling its specific update_view method.

        This method acts as a central dispatcher for UI updates. It finds the
        currently active view and tells it to refresh its own state. This is more
        efficient than a full page redraw.

        Args:
            page_name (str, optional): The name of the page to update.
                                     If None, defaults to the current page.
        """
        if page_name is None:
            page_name = self.navigation_manager.get_current_page()

        self.logger.info(f"Update requested for view: '{page_name}'")

        # Check if the view instance exists in our cache
        if page_name in self.views:
            view_instance = self.views[page_name]

            # Safely check if the view instance has an `update_view` method
            if hasattr(view_instance, "update_view") and callable(
                view_instance.update_view
            ):
                self.logger.debug(
                    f"Calling update_view() on instance of {type(view_instance).__name__}."
                )
                view_instance.update_view()
            else:
                # If the view has no specific update logic, just do a generic page update.
                self.logger.debug(
                    f"View '{page_name}' has no update_view() method. Performing generic page update."
                )
                self.page.update()
        else:
            self.logger.warning(
                f"No view instance found for page '{page_name}' to update. A full navigation might be needed."
            )

    def clear_project_dependent_view_cache(self):
        """
        Clears cached views that depend on a loaded project.

        This is crucial to prevent showing stale data when switching projects.
        It removes views like 'ProjectView' from the cache, forcing them to be
        rebuilt with fresh data on the next navigation.
        """
        self.logger.info("Clearing project-dependent view cache...")
        views_to_clear = ["project_dashboard", "project_view"]
        for view_name in views_to_clear:
            if view_name in self.views:
                del self.views[view_name]
                self.logger.debug(f"Removed '{view_name}' from view cache.")