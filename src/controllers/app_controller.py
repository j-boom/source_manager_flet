"""
Main Application Controller (Final Refactor)

This controller orchestrates all managers, services, and views. It uses the
DataService for all data operations and the app_config for navigation,
acting as the central hub for all application logic.
"""

from typing import Dict, Optional, Any
from pathlib import Path
import logging

import flet as ft

# --- Configuration ---
from config.app_config import PAGES, SPECIAL_PAGES

# --- Managers: Handle in-memory state ---
from managers import (
    UserConfigManager,
    ThemeManager,
    WindowManager,
    NavigationManager,
    SettingsManager,
    ProjectStateManager,
    ProjectBrowserManager
)

# --- Services: Handle I/O and business logic ---
from src.services.data_service import DataService

# --- Views: Handle UI presentation ---
from src.views import MainView, BaseView
from src.views.pages import (
    HomeView,
    RecentProjectsView,
    NewProjectView,
    ProjectView,
    SettingsView,
    SourcesView,
    ReportsView,
    HelpView,
)

# --- Dialogs: Handle user interactions ---
from src.views.components.dialogs import (
    FirstTimeSetupDialog,
    ProjectCreationDialog,
    FolderCreationDialog,
)


class AppController:
    """The central orchestrator of the application."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing AppController")

        # --- Initialize Core Components ---
        self.data_service = DataService()
        self.user_config_manager = UserConfigManager()
        self.theme_manager = ThemeManager(
            initial_mode=self.user_config_manager.get_theme_mode(),
            initial_color=self.user_config_manager.get_theme_color(),
        )
        self.settings_manager = SettingsManager(
            self.user_config_manager, self.theme_manager
        )
        self.window_manager = WindowManager(page, self.user_config_manager)
        self.navigation_manager = NavigationManager()
        self.project_state_manager = ProjectStateManager()
        self.project_browser_manager = ProjectBrowserManager(self.data_service)

        # --- Views ---
        self.main_view = MainView(page, controller=self)
        self.views: Dict[str, ft.Control] = {}
        self._view_class_map = self._build_view_class_map()

        self._setup_callbacks()
        self.logger.info("AppController initialized successfully")

    def _build_view_class_map(self) -> Dict[str, type]:
        """Creates a mapping from page names to view classes for the factory."""
        # Combine regular and special pages into one map
        all_pages = {p["name"]: p["view_name"] for p in PAGES}
        all_pages.update(
            {name: data["view_name"] for name, data in SPECIAL_PAGES.items()}
        )

        # Map string names to actual class objects
        view_classes = {
            "HomeView": HomeView,
            "NewProjectView": NewProjectView,
            "ProjectView": ProjectView,
            "RecentProjectsView": RecentProjectsView,
            "ReportsView": ReportsView,
            "SettingsView": SettingsView,
            "SourcesView": SourcesView,
            "HelpView": HelpView,
        }
        return {
            name: view_classes[class_name]
            for name, class_name in all_pages.items()
            if class_name in view_classes
        }

    def _setup_callbacks(self):
        """Connects components together using callbacks for loose coupling."""
        self.settings_manager.set_callbacks(
            on_theme_change=self.apply_theme_and_update_views,
            on_display_name_change=self.handle_display_name_change,
        )

    def run(self):
        """Starts the application's main loop."""
        self.window_manager.apply_saved_window_config()
        self.apply_theme_and_update_views()
        self.main_view.show()

        if self.user_config_manager.needs_setup():
            self._show_first_time_setup()
        else:
            self.navigate_to("home")

    def cleanup(self, e=None):
        """
        Saves state before the application exits. This is the single, correct
        cleanup method, designed to be called by Flet's on_disconnect event.
        """
        self.logger.info("Cleanup initiated. Saving window configuration.")
        self.window_manager.save_current_window_config()
        self.logger.info("Application cleanup finished.")

    def apply_theme_and_update_views(self):
        """Applies the current theme to the page and refreshes all visible views."""
        self.logger.debug("Applying theme and updating views.")
        self.page.theme_mode = (
            ft.ThemeMode.DARK
            if self.theme_manager.mode == "dark"
            else ft.ThemeMode.LIGHT
        )
        self.page.theme = self.theme_manager.get_theme_data()

        # 1. Refresh the main application shell (AppBar, Sidebar, etc.)
        self.main_view.refresh_theme()

        # 2. To refresh the current page's content, we force it to be rebuilt.
        current_page_name = self.navigation_manager.get_current_page()

        # Remove the old, stale view from the cache so it's forced to be re-created.
        if current_page_name in self.views:
            self.views.pop(current_page_name, None)
            self.logger.debug(
                f"Removed '{current_page_name}' from view cache to force refresh."
            )

        # 3. Re-run the navigation logic for the current page.
        # This will create a new view instance which will use the updated theme.
        self.navigate_to(current_page_name)

    # --- Business Logic Methods (Called by Views) ---

    def navigate_to(self, page_name: str):
        """Handles navigation requests from any part of the UI."""
        self.navigation_manager.set_current_page(page_name)

        if page_name not in self.views:
            self.views[page_name] = self._create_view_for_page(page_name)

        view_instance = self.views.get(page_name)
        if view_instance:
            # Check if the instance is a custom view class with a .build() method,
            # or if it's already a Flet control (like the error message).
            if hasattr(view_instance, "build") and callable(
                getattr(view_instance, "build")
            ):
                content_to_display = view_instance.build()
            else:
                # It's already a Flet control, so we can use it directly.
                content_to_display = view_instance

            self.main_view.set_content(content_to_display)
            self.main_view.update_navigation(page_name)
        else:
            self.logger.error(f"No view class found for page '{page_name}'")

    def open_project(self, project_path_str: str):
        """Handles the business logic of opening a project."""
        project_path = Path(project_path_str)
        try:
            project_model = self.data_service.load_project(project_path)
            if project_model:
                self.project_state_manager.load_project(project_model)
                self.user_config_manager.add_recent_project(
                    project_model.title, str(project_path)
                )
                self.navigate_to("project_view")
            else:
                self.logger.warning(
                    f"Could not open project at {project_path_str}. File might be empty or corrupt."
                )
        except Exception as e:
            self.logger.error(
                f"Failed to open project at {project_path_str}", exc_info=True
            )

    def handle_display_name_change(self):
        """Handles display name updates from the settings manager."""
        self.main_view.update_greeting()
        if self.navigation_manager.get_current_page() == "settings":
            self.views.pop("settings", None)  # Force re-creation of the view
            self.navigate_to("settings")

    def show_create_project_dialog(self, parent_path: Path):
        """Creates and shows the project creation dialog."""

        def on_dialog_close():
            # This callback could be used to refresh the file list in NewProjectView
            current_view = self.views.get("new_project")
            if current_view and hasattr(current_view, "_update_view"):
                current_view._update_view()

        dialog = ProjectCreationDialog(
            self.page, self, parent_path, on_close=on_dialog_close
        )
        dialog.show()

    def submit_new_project(self, parent_path: Path, form_data: Dict[str, Any]):
        """
        Receives data from the dialog and uses the DataService to create the project.
        This is where all the creation logic now lives.
        """
        self.logger.info(f"Submitting new project data for path: {parent_path}")
        try:
            # The DataService should have a method that accepts this raw form data
            new_project = self.data_service.create_new_project(
                parent_dir=parent_path, form_data=form_data
            )
            if new_project:
                self.logger.info(f"Successfully created project: {new_project.title}")
                # Optionally, auto-open the newly created project
                self.open_project(str(new_project.file_path))
            else:
                # Handle the case where the data service returns None (e.g., validation failed)
                self.logger.error("Project creation failed. DataService returned None.")

        except Exception as e:
            self.logger.error(
                f"An exception occurred during project creation: {e}", exc_info=True
            )
            # Here you would show an error message to the user

    def show_create_folder_dialog(self, parent_path: Path):
        """Creates and shows the folder creation dialog."""

        def on_dialog_close():
            current_view = self.views.get("new_project")
            if current_view and hasattr(current_view, "_update_view"):
                current_view._update_view()

        dialog = FolderCreationDialog(
            self.page, self, parent_path, on_close=on_dialog_close
        )
        dialog.show()

    def submit_new_folder(self, parent_path: Path, folder_name: str, description: str):
        """
        Receives data from the folder dialog and uses the DataService to create the folder.
        """
        self.logger.info(
            f"Submitting new folder '{folder_name}' for path: {parent_path}"
        )
        try:
            success = self.data_service.create_new_folder(
                parent_path=parent_path, folder_name=folder_name, description=description
            )
            if success:
                self.logger.info(f"Successfully created folder: {folder_name}")
                self.project_browser_manager.update_state()
            else:
                self.logger.error(
                    f"Folder creation failed for '{folder_name}'. DataService returned False."
                )
        except Exception as e:
            self.logger.error(
                f"An exception occurred during folder creation: {e}", exc_info=True
            )

    # --- Private Helper Methods ---

    def _create_view_for_page(self, page_name: str) -> Optional[ft.Control]:
        """Factory method to create view instances on demand using the config."""
        view_class = self._view_class_map.get(page_name)
        if view_class:
            return view_class(self.page, self)

        error_view = ft.Text(f"View for '{page_name}' not implemented.", color="red")
        self.logger.error(
            f"Attempted to create a view for '{page_name}', but it was not found in the view map."
        )
        return error_view

    def _show_first_time_setup(self):
        """Shows the initial setup dialog for new users."""

        def on_setup_complete(display_name: str):
            self.settings_manager.save_display_name(display_name)
            self.user_config_manager.mark_setup_completed()
            self.handle_display_name_change()
            self.navigate_to("home")

        dialog = FirstTimeSetupDialog(self.page, on_setup_complete)
        dialog.show()
