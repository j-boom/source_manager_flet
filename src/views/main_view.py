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
        Initializes the MainView, which contains the app bar, sidebar, and content area.
        Args:
            controller: The main application controller.
            page (ft.Page): The Flet page object.
        """
        super().__init__(page=page, controller=controller)
        # This is the crucial part: ensuring the controller and page are assigned correctly.
        self.controller = controller
        self.page = page
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

    def build(self) -> ft.Control:
        """
        Builds the entire main view as a single Flet control.
        Returns:
            ft.Control: The root UI control for the main view.
        """
        return ft.Column([self.main_layout], spacing=0, expand=True)

    def _build_app_bar(self) -> SourceManagerAppBar:
        """
        Builds the AppBar component, including the greeting and navigation callbacks.
        Returns:
            SourceManagerAppBar: The app bar control.
        """
        try:
            app_greeting = self.controller.user_config_manager.get_greeting()
        except AttributeError:
            app_greeting = "Welcome"

        return SourceManagerAppBar(
            greeting=(app_greeting),
            on_settings_click=lambda e: self.controller.navigate_to("settings"),
            on_help_click=lambda e: self.controller.navigate_to("help"),
        )

    def _build_sidebar(self) -> Sidebar:
        """
        Builds the Sidebar component dynamically from config.
        Returns:
            Sidebar: The sidebar control.
        """
        return Sidebar(
            pages_config=PAGES,
            on_change=self.controller.navigation_controller.navigate_to_page,
        )

    def _build_content_area(self) -> ft.Container:
        """
        Creates the container that will hold the current page's content.
        Returns:
            ft.Container: The content area container.
        """
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
            type: The view class corresponding to the page name, or None if not found.
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
        """
        Refreshes the theme of the application by applying the current mode and color from ThemeManager.
        This should be called after any theme change to update the UI.
        """
        self.page.theme_mode = (
            ft.ThemeMode.DARK
            if self.controller.theme_manager.mode == "dark"
            else ft.ThemeMode.LIGHT
        )
        self.page.theme = self.controller.theme_manager.get_theme_data()
        self.page.update()

    def update_greeting(self):
        """
        Refreshes the greeting message in the app bar to reflect the current display name.
        """
        new_greeting = self.controller.settings_manager.get_greeting()
        self.app_bar.update_greeting(new_greeting)

    def show(self):
        """
        Clears the page and displays the main application layout (app bar, sidebar, content area).
        """
        self.page.appbar = self.app_bar
        self.page.controls.clear()
        self.page.add(self.main_layout)
        self.page.update()

    def update_navigation(self, page_name: str):
        """
        Updates the sidebar's selected item to reflect the current page.
        Args:
            page_name (str): The name of the page to select in the sidebar.
        """
        self.sidebar.update_selection(page_name)
