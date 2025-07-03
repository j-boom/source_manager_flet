import flet as ft
from typing import Callable

# --- Component Imports ---
from components import AppBar, Sidebar

# --- Configuration ---
from config.app_config import PAGES


class MainView:
    """The main application shell."""

    def __init__(self, page: ft.Page, controller):
        self.page = page
        self.controller = controller

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

    def _build_app_bar(self) -> AppBar:
        """Builds the AppBar component."""
        return AppBar(
            greeting=self.controller.user_config_manager.get_greeting(),
            on_settings_click=lambda e: self.controller.navigate_to("settings"),
            on_help_click=lambda e: self.controller.navigate_to("help"),
        )

    def _build_sidebar(self) -> Sidebar:
        """Builds the Sidebar component dynamically from config."""
        return Sidebar(pages_config=PAGES, on_change=self.controller.navigate_to)

    def _build_content_area(self) -> ft.Container:
        """Creates the container that will hold the current page's content."""
        return ft.Container(
            content=ft.ProgressRing(),  # Show a loading ring initially
            alignment=ft.alignment.center,
            expand=True,
        )

    def show(self):
        """Clears the page and displays the main application layout."""
        self.page.appbar = self.app_bar
        self.page.controls.clear()
        self.page.add(self.main_layout)
        self.page.update()

    def set_content(self, content: ft.Control):
        """Updates the content area with a new view/page."""
        self.content_area.content = content
        self.page.update()

    def update_navigation(self, page_name: str):
        """Updates the sidebar's selected item."""
        self.sidebar.update_selection(page_name)

    def update_greeting(self):
        """Refreshes the greeting message in the app bar."""
        new_greeting = self.controller.user_config_manager.get_greeting()
        self.app_bar.update_greeting(new_greeting)

    def refresh_theme(self):
        """
        Updates the colors of all components when the theme changes.
        The AppBar is now styled automatically by the page.theme.
        """
        if not self.page.theme or not self.page.theme.color_scheme:
            return

        colors = self.page.theme.color_scheme

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
