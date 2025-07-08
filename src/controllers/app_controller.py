"""
Main Application Controller (Final Refactor)

This controller orchestrates all managers, services, and views. It uses the
DataService for all data operations and the app_config for navigation,
acting as the central hub for all application logic.
"""

from typing import Dict, Optional, Any
from pathlib import Path
import logging
import re

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
    ProjectBrowserManager,
)

# --- Services: Handle I/O and business logic ---
from services import DataService, PowerPointService

# --- Views: Handle UI presentation ---
from views import MainView

# --- Dialogs: Handle user interactions ---
from views.components.dialogs import (
    FirstTimeSetupDialog,
    ProjectCreationDialog,
    FolderCreationDialog,
    SourceCreationDialog,
    SourceEditorDialog
)

# --- Models: Define data structures ---
from models import ProjectSourceLink


class AppController:
    """The central orchestrator of the application."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing AppController")

        # --- Initialize Core Components ---
        self.data_service = DataService()
        self.powerpoint_service = PowerPointService()
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

        # --- UI Components ---
        self.main_view = MainView(page, controller=self)
        self.views: Dict[str, ft.Control] = {}
        self._view_class_map = self._build_view_class_map()
        self.powerpoint_file_picker = ft.FilePicker(on_result=self._on_powerpoint_selected)
        self.page.overlay.append(self.powerpoint_file_picker)

        # --- State Flags ---
        self._add_new_source_to_project_context: bool = False

        self._setup_callbacks()
        self.logger.info("AppController initialized successfully")

    def _build_view_class_map(self) -> Dict[str, type]:
        """Creates a mapping from page names to view classes for the factory."""
        from views.pages import (
            HomeView,
            RecentProjectsView,
            NewProjectView,
            ProjectView,
            SettingsView,
            SourcesView,
            ReportsView,
            HelpView,
        )

        all_pages = {p["name"]: p["view_name"] for p in PAGES}
        all_pages.update(
            {name: data["view_name"] for name, data in SPECIAL_PAGES.items()}
        )

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
        """Saves state before the application exits."""
        self.window_manager.save_current_window_config()

    def apply_theme_and_update_views(self):
        """Applies the current theme to the page and refreshes all visible views."""
        self.page.theme_mode = (
            ft.ThemeMode.DARK
            if self.theme_manager.mode == "dark"
            else ft.ThemeMode.LIGHT
        )
        self.page.theme = self.theme_manager.get_theme_data()
        self.main_view.refresh_theme()
        current_page_name = self.navigation_manager.get_current_page()
        if current_page_name in self.views:
            self.views.pop(current_page_name, None)
        self.navigate_to(current_page_name)

    def navigate_to(self, page_name: str):
        """Handles navigation requests from any part of the UI."""
        self.logger.info(f"Navigation requested for '{page_name}'...")
        sidebar_page_name = page_name
        self.page.floating_action_button = None # Clear FAB on all navigation

        if page_name == "project_view":
            if self.project_state_manager.has_loaded_project():
                page_name = "project_dashboard"
                self.logger.info(f"Project is loaded. Redirecting to '{page_name}'.")
            else:
                page_name = "new_project"
                self.logger.info(f"No project loaded. Redirecting to '{page_name}'.")

        if page_name == "recent_projects":
            self._validate_recent_projects()

        self.navigation_manager.set_current_page(page_name)

        if page_name in self.views:
            self.views.pop(page_name)
            self.logger.info(f"Popped '{page_name}' from view cache to force refresh.")

        self.views[page_name] = self._create_view_for_page(page_name)

        view_instance = self.views.get(page_name)
        if view_instance:
            content_to_display = (
                view_instance.build()
                if hasattr(view_instance, "build")
                and callable(getattr(view_instance, "build"))
                else view_instance
            )
            self.main_view.set_content(content_to_display)
            self.main_view.update_navigation(sidebar_page_name)
            self.logger.info(f"Navigation to '{page_name}' complete.")
        else:
            self.logger.error(
                f"Could not navigate to '{page_name}' because view instance is null."
            )

    def open_project(self, project_path: Path):
        """Handles the business logic of opening a project."""
        try:
            project_model = self.data_service.load_project(project_path)
            if project_model:
                self.project_state_manager.load_project(project_model)
                self.user_config_manager.add_recent_project(
                    project_model.title, str(project_path)
                )
                self.navigate_to("project_dashboard")
            else:
                self.logger.warning(
                    f"Could not open project at {project_path}. File might be empty or corrupt."
                )
        except Exception as e:
            self.logger.error(
                f"Failed to open project at {project_path}", exc_info=True
            )

    def handle_display_name_change(self):
        """Handles display name updates from the settings manager."""
        self.main_view.update_greeting()
        if self.navigation_manager.get_current_page() == "settings":
            self.views.pop("settings", None)
            self.navigate_to("settings")

    def show_create_project_dialog(self, parent_path: Path):
        """Creates and shows the project creation dialog."""
        initial_be_number = None
        match = re.search(r"^(\d{4}[A-Z]{2}\d{4}|\d{10})", parent_path.name)
        if match:
            initial_be_number = match.group(1)

        def on_dialog_close():
            current_view = self.views.get("new_project")
            if current_view and hasattr(current_view, "_update_view"):
                current_view._update_view()

        dialog = ProjectCreationDialog(
            self.page,
            self,
            parent_path,
            on_close=on_dialog_close,
            initial_be_number=initial_be_number,
        )
        dialog.show()

    def submit_new_project(self, parent_path: Path, form_data: Dict[str, Any]):
        """Receives data from the dialog and uses the DataService to create the project."""
        try:
            success, message, new_project = self.data_service.create_new_project(
                parent_dir=parent_path, form_data=form_data
            )
            if success and new_project:
                self.open_project(new_project.file_path)
            else:
                self.logger.error(f"Project creation failed: {message}")
        except Exception as e:
            self.logger.error(
                f"An exception occurred during project creation: {e}", exc_info=True
            )

    def show_create_folder_dialog(self, parent_path: Path):
        """Creates and shows the folder creation dialog."""
        parent_name_prefix = f"{parent_path.name} "
        self.logger.info(
            f"Showing create folder dialog for parent: {parent_path} with prefix: {parent_name_prefix}"
        )

        def on_dialog_close():
            current_view = self.views.get("new_project")
            if current_view and hasattr(current_view, "_update_view"):
                current_view._update_view()

        dialog = FolderCreationDialog(
            self.page,
            self,
            parent_path,
            on_close=on_dialog_close,
            initial_prefix=parent_name_prefix,
        )
        dialog.show()

    def submit_new_folder(self, parent_path: Path, folder_name: str, description: str):
        """Receives data from the folder dialog and creates the folder."""
        parent_name = parent_path.name

        if not folder_name.strip().startswith(parent_name):
            self.logger.error(
                f"Validation failed: Folder name '{folder_name}' does not start with parent name '{parent_name}'."
            )
            return

        self.logger.info(
            f"Submitting new folder '{folder_name}' for path: {parent_path}"
        )
        try:
            success, message = self.data_service.create_new_folder(
                parent_path=parent_path,
                folder_name=folder_name.strip(),
                description=description,
            )
            if success:
                self.project_browser_manager.update_state()
                self.navigate_to("new_project")
            else:
                self.logger.error(
                    f"Folder creation failed for '{folder_name}': {message}"
                )
        except Exception as e:
            self.logger.error(
                f"An exception occurred during folder creation: {e}", exc_info=True
            )

    def _validate_recent_projects(self):
        """Checks the recent projects list and removes any that no longer exist."""
        self.logger.info("Validating recent projects list...")
        for project in list(self.user_config_manager.get_recent_projects()):
            if not Path(project.path).exists():
                self.logger.warning(
                    f"Recent project file not found, removing from list: {project.path}"
                )
                self.user_config_manager.remove_recent_project(project.path)

    def clear_recent_projects(self):
        """Clears all recent projects."""
        self.user_config_manager.clear_recent_projects()
        if self.navigation_manager.get_current_page() == "recent_projects":
            self.navigate_to("recent_projects")

    def remove_recent_project(self, path: str):
        """Removes a single recent project."""
        self.user_config_manager.remove_recent_project(path)
        if self.navigation_manager.get_current_page() == "recent_projects":
            self.navigate_to("recent_projects")

    def update_project_metadata(self, updated_data: Dict[str, Any]):
        """Updates the metadata of the currently loaded project."""
        project = self.project_state_manager.current_project
        if project:
            project.metadata.update(updated_data)
            self.data_service.save_project(project)
        else:
            self.logger.error("Attempted to update metadata, but no project is loaded.")

    def show_create_source_dialog(self, add_to_project_on_create: bool = False):
        """
        Shows the dialog to create a new master source.
        Sets a flag to determine if the new source should be added to the current project.
        """
        self._add_new_source_to_project_context = add_to_project_on_create

        project = self.project_state_manager.current_project
        if not project and add_to_project_on_create:
            self.page.snack_bar = ft.SnackBar(ft.Text("Open a project first to create and add a source."), open=True)
            self.page.update()
            return

        def on_dialog_close():
            self.refresh_current_view()

        dialog = SourceCreationDialog(self.page, self, on_close=on_dialog_close)
        dialog.show()

    def submit_new_source(self, form_data: Dict[str, Any]):
        """
        Receives data from the source dialog, creates it, and adds it to the project if context is set.
        """
        project = self.project_state_manager.current_project
        region = "General" # Default region
        if project:
            region = self.data_service.get_region_for_project(project.file_path)

        success, message, new_source = self.data_service.create_new_source(region, form_data)

        if success:
            self.page.snack_bar = ft.SnackBar(ft.Text(message), bgcolor=ft.colors.GREEN)
            if new_source and self._add_new_source_to_project_context:
                self.logger.info(f"Automatically adding new source '{new_source.id}' to project due to context.")
                self.add_source_to_project(new_source.id)
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text(message), bgcolor=ft.colors.ERROR_CONTAINER)

        self._add_new_source_to_project_context = False
        self.page.snack_bar.open = True
        self.page.update()

    def _create_view_for_page(self, page_name: str) -> Optional[ft.Control]:
        """Factory method to create view instances on demand."""
        view_class = self._view_class_map.get(page_name)
        if view_class:
            return view_class(self.page, self)
        return ft.Text(f"View for '{page_name}' not implemented.", color="red")

    def _show_first_time_setup(self):
        """Shows the initial setup dialog for new users."""
        def on_setup_complete(display_name: str):
            self.settings_manager.save_display_name(display_name)
            self.user_config_manager.mark_setup_completed()
            self.handle_display_name_change()
            self.navigate_to("home")

        dialog = FirstTimeSetupDialog(self.page, on_setup_complete)
        dialog.show()

    def add_source_to_on_deck(self, source_id: str):
        """Adds a source ID to the on_deck_sources list in the current project's metadata."""
        project = self.project_state_manager.current_project
        if not project:
            return

        if "on_deck_sources" not in project.metadata:
            project.metadata["on_deck_sources"] = []
        
        on_deck_list = project.metadata["on_deck_sources"]
        
        if source_id not in on_deck_list:
            on_deck_list.append(source_id)
            self.data_service.save_project(project)
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Source added to On Deck for '{project.title}'."), open=True)
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text("This source is already on deck."), open=True)
            
        self.page.update()

    def add_source_to_project(self, source_id: str):
        """Adds a master source to the currently loaded project."""
        project = self.project_state_manager.current_project
        if not project:
            return

        self.data_service.add_source_to_project(project, source_id)
        self.refresh_current_view()

    def reorder_project_sources(self, new_ordered_ids: list):
        """Tells the DataService to reorder the sources for the current project."""
        project = self.project_state_manager.current_project
        if project:
            self.data_service.reorder_sources_in_project(project, new_ordered_ids)

    def remove_source_from_project(self, source_id: str):
        """Removes a source link from the project and adds it back to the 'On Deck' list."""
        project = self.project_state_manager.current_project
        if not project:
            return

        if "on_deck_sources" not in project.metadata:
            project.metadata["on_deck_sources"] = []
        
        on_deck_list = project.metadata["on_deck_sources"]
        if source_id not in on_deck_list:
            on_deck_list.append(source_id)
        
        self.data_service.remove_source_from_project(project, source_id)
        self.refresh_current_view()

    def show_source_editor_dialog(self, source_id: str):
        """Shows a dialog to view and edit a master source's details."""
        source = self.data_service.get_source_by_id(source_id)
        if not source:
            return

        def on_dialog_close():
            self.refresh_current_view()

        dialog = SourceEditorDialog(self.page, self, source, on_close=on_dialog_close)
        dialog.show()

    def submit_source_update(self, source_id: str, form_data: Dict[str, Any]):
        """Receives updated data from the source editor and saves it."""
        success, message = self.data_service.update_master_source(source_id, form_data)
        
        if success:
            self.page.snack_bar = ft.SnackBar(ft.Text(message), bgcolor=ft.colors.GREEN)
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text(message), bgcolor=ft.colors.ERROR_CONTAINER)
            
        self.page.snack_bar.open = True
        self.page.update()

    def refresh_current_view(self):
        """Finds the currently visible view instance and calls its update method."""
        current_page_name = self.navigation_manager.get_current_page()
        if not current_page_name:
            return

        current_view_instance = self.views.get(current_page_name)
        
        if not current_view_instance:
            self.page.update()
            return

        if hasattr(current_view_instance, "update_view"):
            current_view_instance.update_view()
        else:
            self.page.update()

    def promote_source_from_on_deck(self, source_id: str):
        """Moves a source from the "On Deck" list to the main project sources list."""
        project = self.project_state_manager.current_project
        if not project:
            return

        try:
            project.metadata["on_deck_sources"].remove(source_id)
        except (ValueError, KeyError):
            logging.warning(f"Source ID '{source_id}' not found in On Deck list during promotion.")

        if not any(link.source_id == source_id for link in project.sources):
            new_order = len(project.sources)
            new_link = ProjectSourceLink(source_id=source_id, order=new_order)
            project.sources.append(new_link)
        
        self.data_service.save_project(project)
        self.refresh_current_view()

    def _on_powerpoint_selected(self, e: ft.FilePickerResultEvent):
        """Callback that runs after the user selects a .pptx file."""
        if not e.files:
            return

        selected_file_path = e.files[0].path
        project = self.project_state_manager.current_project
        if project:
            project.metadata["powerpoint_path"] = selected_file_path
            self.data_service.save_project(project)
            self.refresh_current_view()

    def get_slides_for_current_project(self) -> Optional[list[tuple[str, str]]]:
        """Gets slide data for the current project, prompting for a file if needed."""
        project = self.project_state_manager.current_project
        if not project:
            return None

        ppt_path = project.metadata.get("powerpoint_path")
        
        if not ppt_path:
            self.powerpoint_file_picker.pick_files(
                dialog_title="Select Presentation for this Project",
                file_type="custom",
                allowed_extensions=["pptx"],
            )
            return None

        presentation = self.powerpoint_service.load_presentation(ppt_path)
        if not presentation:
            project.metadata["powerpoint_path"] = None
            self.data_service.save_project(project)
            return None

        return self.powerpoint_service.get_slide_data(presentation)

    def add_citations_to_slide(self, slide_id: str, source_ids: list[str]):
        """Adds a list of source IDs as citations for a specific slide."""
        project = self.project_state_manager.current_project
        if not project or not slide_id:
            return

        if "citations" not in project.metadata:
            project.metadata["citations"] = {}
        
        slide_citations = set(project.metadata["citations"].get(str(slide_id), []))
        slide_citations.update(source_ids)
        project.metadata["citations"][str(slide_id)] = sorted(list(slide_citations))
        
        self.data_service.save_project(project)
        self.refresh_current_view()

    def remove_citations_from_slide(self, slide_id: str, source_ids: list[str]):
        """Removes a list of source IDs from a specific slide's citations."""
        project = self.project_state_manager.current_project
        if not project or not slide_id or "citations" not in project.metadata:
            return

        slide_citations = set(project.metadata["citations"].get(str(slide_id), []))
        slide_citations.difference_update(source_ids)
        project.metadata["citations"][str(slide_id)] = sorted(list(slide_citations))

        self.data_service.save_project(project)
        self.refresh_current_view()
