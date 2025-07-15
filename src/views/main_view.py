import flet as ft
from typing import TYPE_CHECKING

from .components.app_bar import AppBar as SourceManagerAppBar
from .components.sidebar import Sidebar
from .pages import (
    HomeView,
    RecentProjectsView,
    NewProjectView,
    ProjectView,
    SourcesView,
    ReportsView,
    SettingsView,
    HelpView,
)
from .base_view import BaseView

from config.app_config import PAGES
if TYPE_CHECKING:
    from src.controllers.app_controller import AppController


class MainView(BaseView):
    """
    The main view of the application, containing the app bar, sidebar, and content area.
    This version is a Flet control and is compatible with the refactored AppController.
    """

    def __init__(self, controller: "AppController", page: ft.Page):
        """
        Initializes the MainView.

        Args:
            controller: The main application controller.
            page (ft.Page): The Flet page object.
        """
        super().__init__(page=page, controller=controller)
        # This is the crucial part: ensuring the controller and page are assigned correctly.
        self.controller = controller
        self.page = page
         # --- Initialize UI Components ---
        self.page.appbar = self._build_app_bar()
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

    def build(self) -> ft.Control:
        """
        Builds the entire main view as a single Flet control.
        This method overrides the one in BaseView and returns the
        actual UI to be added to the page.
        """
        return ft.Column(
            [
                self.main_layout
            ],
            spacing=0,
            expand=True
        )

    def _build_app_bar(self) -> SourceManagerAppBar:
        """Builds the AppBar component."""
        return SourceManagerAppBar(
            greeting=self.controller.user_config_manager.get_greeting(),
            on_settings_click=lambda e: self.controller.navigate_to("settings"),
            on_help_click=lambda e: self.controller.navigate_to("help"),
        )

    def _build_sidebar(self) -> Sidebar:
        """Builds the Sidebar component dynamically from config."""
        return Sidebar(pages_config=PAGES, on_change=self.controller.navigation_controller.navigate_to_page)

    def _build_content_area(self) -> ft.Container:
        """Creates the container that will hold the current page's content."""
        return ft.Container(
            content=ft.ProgressRing(),  # Show a loading ring initially
            alignment=ft.alignment.center,
            expand=True,
        )

    def set_content(self, content: ft.Control):
        """
        Sets the content of the main content area.

        Args:
            content (ft.Control): The control to display in the content area.
        """
        self.content_area.content = content

    def get_view_class(self, page_name: str):
        """
        Maps a page name to its corresponding view class.

        Args:
            page_name (str): The name of the page.

        Returns:
            The view class corresponding to the page name.
        """
        view_map = {
            "home": HomeView,
            "recent_projects": RecentProjectsView,
            "new_project": NewProjectView,
            "project_dashboard": ProjectView,
            "sources": SourcesView,
            "reports": ReportsView,
            "settings": SettingsView,
            "help": HelpView,
        }
        return view_map.get(page_name)

    def refresh_theme(self):
        """Refreshes the theme of the application."""
        theme = self.controller.theme_manager.get_theme_data()
        self.page.theme_mode = theme
        self.page.update()

    def on_keyboard(self, e: ft.KeyboardEvent):
        """Handles global keyboard events."""
        if e.key == "N" and e.ctrl:
            self.controller.dialog_controller.open_new_project_dialog(e)
        self.page.update()
