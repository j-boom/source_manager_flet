import flet as ft
import logging
from typing import Callable

# --- Component Imports ---
from .components import AppBar, Sidebar
# --- Configuration ---
from config.app_config import PAGES


class MainView:
    """The main application shell."""

    def __init__(self, page: ft.Page, controller):
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing MainView")
        
        self.page = page
        self.controller = controller

        self.logger.debug("Building main UI components")
        
        # --- Initialize UI Components ---
        self.app_bar = self._build_app_bar()
        self.sidebar = self._build_sidebar()
        self.content_area = self._build_content_area()

        # --- Main Layout ---
        self.main_layout = ft.Row(
            [
                self.sidebar,
                ft.VerticalDivider(width=1),
                self.content_area,
            ],
            spacing=0,
            expand=True,
        )
        
        self.logger.info("MainView initialization complete")

    def _build_app_bar(self) -> AppBar:
        """Builds the AppBar component."""
        self.logger.debug("Building AppBar component")
        return AppBar(
            greeting=self.controller.user_config_manager.get_greeting(),
            on_settings_click=lambda e: self.controller.navigate_to("settings"),
            on_help_click=lambda e: self.controller.navigate_to("help"),
        )

    def _build_sidebar(self) -> Sidebar:
        """Builds the Sidebar component dynamically from config."""
        self.logger.debug("Building Sidebar component")
        return Sidebar(pages_config=PAGES, on_change=self.controller.navigate_to)

    def _build_content_area(self) -> ft.Container:
        """Creates the container that will hold the current page's content."""
        self.logger.debug("Building content area container")
        return ft.Container(
            content=ft.ProgressRing(),  # Show a loading ring initially
            alignment=ft.alignment.center,
            expand=True,
        )
    
    def show(self):
        """Clears the page and displays the main application layout."""
        self.logger.info("Showing main layout")
        self.page.appbar = self.app_bar
        if self.page.controls:
            self.page.controls.clear()
        self.page.add(self.main_layout)
        self.page.update()

    def set_content(self, content: ft.Control):
        """Updates the content area with a new view/page."""
        self.logger.debug(f"Setting new content: {type(content).__name__}")
        self.content_area.content = content
        self.page.update()

    def update_navigation(self, page_name: str):
        """Updates the sidebar's selected item."""
        self.logger.debug(f"Updating navigation to: {page_name}")
        self.sidebar.update_selection(page_name)

    def update_greeting(self):
        """Refreshes the greeting message in the app bar."""
        new_greeting = self.controller.user_config_manager.get_greeting()
        self.logger.debug(f"Updating greeting to: {new_greeting}")
        self.app_bar.update_greeting(new_greeting)
        
    def refresh_theme(self):
        """
        Updates the colors of all components when the theme changes.
        The AppBar is now styled automatically by the page.theme.
        """
        self.logger.debug("Refreshing theme colors")
        if not self.page.theme or not self.page.theme.color_scheme:
            self.logger.warning("No theme or color scheme available for refresh")
            return

        colors = self.page.theme.color_scheme
        self.logger.debug(f"Using color scheme: {type(colors).__name__}")
        self.logger.debug("Refreshing theme colors")

        # --- SIMPLIFIED: No manual AppBar styling needed ---
        # The AppBar's theme is now defined in the ThemeManager.
        # We only need to style the components MainView directly owns.

        # We do, however, need to update the greeting text color manually
        # as it's a child control inside the custom AppBar.
        self.app_bar.greeting_text.color = colors.on_primary

        self.sidebar.bgcolor = colors.surface
        self.content_area.bgcolor = colors.background

        # Refresh the components themselves to apply internal color changes
        self.sidebar.refresh_theme()
        self.page.update()
