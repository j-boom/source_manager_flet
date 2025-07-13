"""
Main Application Controller (Final Refactor)

This controller orchestrates all managers, services, and views. It uses the
DataService for all data operations and the app_config for navigation,
acting as the central hub for all application logic.
"""

from typing import Dict, Optional, Any, List
from pathlib import Path
import logging
import re
import os
from datetime import datetime

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

        # --- Views ---
        self.main_view = MainView(page, controller=self)
        self.views: Dict[str, ft.Control] = {}
        self._view_class_map = self._build_view_class_map()

        # --- Initialize Subcontrollers ---
        from .base_controller import BaseController
        from .navigation_controller import NavigationController
        from .project_controller import ProjectController
        from .source_controller import SourceController
        from .powerpoint_controller import PowerPointController
        from .dialog_controller import DialogController
        
        self.navigation_controller = NavigationController(self)
        self.project_controller = ProjectController(self)
        self.source_controller = SourceController(self)
        self.powerpoint_controller = PowerPointController(self)
        self.dialog_controller = DialogController(self)

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
        self.logger.info(f"Opening project at path: {project_path}")
        try:
            project_model = self.data_service.load_project(project_path)
            if project_model:
                self.project_state_manager.load_project(project_model)
                self.user_config_manager.add_recent_project(
                    project_model.project_title, str(project_path)
                )
                # Clear project-dependent views to refresh their state
                self.logger.info("Clearing project-dependent view cache...")
                self._clear_project_dependent_views()
                self.navigate_to("project_dashboard")
            else:
                self.logger.warning(
                    f"Could not open project at {project_path}. File might be empty or corrupt."
                )
        except ValueError as e:
            # Check if this is an old format file
            if "old format" in str(e):
                self.logger.info(f"Detected old format file: {project_path}")
                self._handle_old_format_file(project_path)
            else:
                self.logger.error(f"ValueError opening project: {e}")
                self._show_error_dialog("Project Error", f"Error opening project: {e}")
        except Exception as e:
            self.logger.error(
                f"Failed to open project at {project_path}", exc_info=True
            )
            self._show_error_dialog("Error", f"Failed to open project: {str(e)}")

    def handle_display_name_change(self):
        """Handles display name updates from the settings manager."""
        self.main_view.update_greeting()
        if self.navigation_manager.get_current_page() == "settings":
            self.views.pop("settings", None)
            self.navigate_to("settings")

    def show_create_project_dialog(self, parent_path: Path):
        """Creates and shows the project creation dialog, pre-filling the BE number if found."""
        return self.project_controller.show_create_project_dialog(parent_path)

    def submit_new_project(self, parent_path: Path, form_data: Dict[str, Any]):
        """Receives data from the dialog and uses the DataService to create the project."""
        return self.project_controller.submit_new_project(parent_path, form_data)

    def show_create_folder_dialog(self, parent_path: Path):
        """Creates and shows the folder creation dialog, pre-filling the parent name."""
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
        )
        dialog.show()

    def submit_new_folder(self, parent_path: Path, folder_name: str, description: str):
        """Receives data from the folder dialog, validates it, and uses the DataService to create the folder."""
        parent_name = parent_path.name

        if not folder_name.strip().startswith(parent_name):
            self.logger.error(
                f"Validation failed: Folder name '{folder_name}' does not start with parent name '{parent_name}'."
            )
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error: Folder name must start with '{parent_name}'."),
                bgcolor=ft.colors.ERROR_CONTAINER,
            )
            self.page.snack_bar.open = True
            self.page.update()
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
                self.logger.info(f"Successfully created folder: {folder_name}")
                self.project_browser_manager.update_state()
                self.navigate_to("new_project")  # Refresh the view
            else:
                self.logger.error(
                    f"Folder creation failed for '{folder_name}': {message}"
                )
        except Exception as e:
            self.logger.error(
                f"An exception occurred during folder creation: {e}", exc_info=True
            )

    def _validate_recent_projects(self):
        """Checks the recent projects list and removes any that no longer exist on disk."""
        self.logger.info("Validating recent projects list...")
        for project in list(self.user_config_manager.get_recent_projects()):
            if not Path(project.path).exists():
                self.logger.warning(
                    f"Recent project file not found, removing from list: {project.path}"
                )
                self.user_config_manager.remove_recent_project(project.path)

    def clear_recent_projects(self):
        """Clears all recent projects from the user's config."""
        self.logger.info("Clearing all recent projects.")
        self.user_config_manager.clear_recent_projects()
        if self.navigation_manager.get_current_page() == "recent_projects":
            self.navigate_to("recent_projects")

    def remove_recent_project(self, path: str):
        """Removes a single recent project from the user's config."""
        self.logger.info(f"Removing recent project: {path}")
        self.user_config_manager.remove_recent_project(path)
        if self.navigation_manager.get_current_page() == "recent_projects":
            self.navigate_to("recent_projects")

    def update_project_metadata(self, updated_data: Dict[str, Any]):
        """Updates the metadata of the currently loaded project."""
        self.logger.info(f"Updating project metadata: {updated_data}")
        project = self.project_state_manager.current_project
        if project:
            project.metadata.update(updated_data)
            self.data_service.save_project(project)
            self.logger.info("Project metadata saved successfully.")
        else:
            self.logger.error("Attempted to update metadata, but no project is loaded.")

    def show_create_source_dialog(self):
        """Shows the dialog to create a new master source."""
        project = self.project_state_manager.current_project
        if not project:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Open a project first to determine the source region."),
                open=True,
            )
            self.page.update()
            return

        def on_dialog_close():
            # Refresh the sources tab
            current_view = self.views.get("project_dashboard")
            if (
                current_view
                and hasattr(current_view, "sources_tab")
                and hasattr(current_view.sources_tab, "_update_view")
            ):
                current_view.sources_tab._update_view()

        dialog = SourceCreationDialog(self.page, self, on_close=on_dialog_close)
        dialog.show()

    def submit_new_source(self, form_data: Dict[str, Any]):
        """Receives data from the source dialog and tells the DataService to create it."""
        project = self.project_state_manager.current_project
        if not project:
            self.logger.error(
                "Attempted to submit new source, but no project is loaded."
            )
            return

        country = self.data_service.get_country_for_project(project.file_path)

        success, message, _ = self.data_service.create_new_source(country, form_data)

        if success:
            self.page.snack_bar = ft.SnackBar(
                ft.Text(message), bgcolor=ft.colors.GREEN
            )
        else:
            self.page.snack_bar = ft.SnackBar(
                ft.Text(message), bgcolor=ft.colors.ERROR_CONTAINER
            )

        self.page.snack_bar.open = True
        self.page.update()

    def show_create_source_dialog_for_country(self, country: str):
        """Shows the dialog to create a new master source for a specific country."""
        def on_dialog_close():
            # Refresh the sources view if it's the current view
            if hasattr(self, 'current_view_name') and self.current_view_name == "sources":
                current_view = self.views.get("sources")
                if current_view and hasattr(current_view, "_load_sources_for_country"):
                    # Refresh the view by reloading sources
                    if hasattr(current_view, "selected_country"):
                        current_view._load_sources_for_country(current_view.selected_country)
                        current_view._clear_all_filters(None)
        
        dialog = SourceCreationDialog(self.page, self, on_close=on_dialog_close, target_country=country)
        dialog.show()

    def submit_new_source_for_country(self, country: str, form_data: Dict[str, Any]):
        """Creates a new source for a specific country (independent of loaded project)."""
        success, message, _ = self.data_service.create_new_source(country, form_data)

        if success:
            self.page.snack_bar = ft.SnackBar(
                ft.Text(message), bgcolor=ft.colors.GREEN
            )
        else:
            self.page.snack_bar = ft.SnackBar(
                ft.Text(message), bgcolor=ft.colors.ERROR_CONTAINER
            )

        if self.page.snack_bar:
            self.page.snack_bar.open = True
            self.page.update()

    def _create_view_for_page(self, page_name: str) -> Optional[ft.Control]:
        """Factory method to create view instances on demand using the config."""
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
        return self.source_controller.add_source_to_on_deck(source_id)

    def add_source_to_project(self, source_id: str):
        """Adds a master source to the currently loaded project and removes it from 'On Deck'."""
        return self.source_controller.add_source_to_project(source_id)

    def reorder_project_sources(self, new_ordered_ids: list):
        """Tells the DataService to reorder the sources for the current project."""
        project = self.project_state_manager.current_project
        if project:
            self.logger.info(f"Reordering sources for project '{project.project_title}'.")
            self.data_service.reorder_sources_in_project(project, new_ordered_ids)
        else:
            self.logger.error("Attempted to reorder sources, but no project is loaded.")

    def show_source_editor_dialog(self, source_id: str):
        """Shows a dialog to view and edit a master source's details."""
        source = self.data_service.get_source_by_id(source_id)
        if not source:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: Could not find source with ID {source_id}."), open=True)
            self.page.update()
            return

        def on_dialog_close():
            # Refresh the sources tab to show any changes
            current_view = self.views.get("project_dashboard")
            if (current_view and hasattr(current_view, 'sources_tab') and 
                hasattr(current_view.sources_tab, "_update_view")):
                current_view.sources_tab._update_view()

        dialog = SourceEditorDialog(self.page, self, source, on_close=on_dialog_close)
        dialog.show()

    def submit_source_update(self, source_id: str, form_data: Dict[str, Any]):
        """Receives updated data from the source editor and tells the DataService to save it."""
        self.logger.info(f"Submitting update for source ID {source_id} with data: {form_data}")
        
        success, message = self.data_service.update_master_source(source_id, form_data)
        
        if success:
            self.page.snack_bar = ft.SnackBar(ft.Text(message), bgcolor=ft.colors.GREEN)
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text(message), bgcolor=ft.colors.ERROR_CONTAINER)
            
        self.page.snack_bar.open = True
        self.page.update()

    def promote_source_from_on_deck(self, source_id: str):
        """
        Moves a source from the "On Deck" list to the main project sources list.
        """
        project = self.project_state_manager.current_project
        if not project:
            logging.warning("Attempted to promote a source with no project loaded.")
            return

        logging.info(f"Promoting source '{source_id}' from On Deck to project sources.")

        # 1. Remove the source from the "On Deck" list in metadata
        try:
            # The user's hunch was correct, we access 'on_deck_sources' via metadata
            project.metadata["on_deck_sources"].remove(source_id)
        except (ValueError, KeyError):
            logging.warning(f"Source ID '{source_id}' not found in On Deck list during promotion.")

        # 2. Add the source to the main project sources list
        if not any(link.source_id == source_id for link in project.sources):
            new_link = ProjectSourceLink(source_id=source_id)
            project.sources.append(new_link)
        
        # 3. Save and refresh
        self.data_service.save_project(project)
        self.refresh_current_view()

    def remove_source_from_project(self, source_id: str):
        """
        Removes a source link from the project AND adds it back to the "On Deck" list.
        """
        project = self.project_state_manager.current_project
        if not project:
            logging.error("Attempted to remove a source, but no project is loaded.")
            return

        logging.info(f"Removing source '{source_id}' from project '{project.project_title}'.")
        
        # --- THIS IS THE FIX FOR THE "DELETE" ISSUE ---
        # 1. Add the source back to the "On Deck" list first.
        if "on_deck_sources" not in project.metadata:
            project.metadata["on_deck_sources"] = []
        
        on_deck_list = project.metadata["on_deck_sources"]
        if source_id not in on_deck_list:
            on_deck_list.append(source_id)
        # --- END FIX ---
        
        # 2. Remove the source from the project (this now just affects the main list)
        self.data_service.remove_source_from_project(project, source_id)
        
        # 3. Refresh the view to show the changes
        self.refresh_current_view()

    def refresh_current_view(self):
        """
        Finds the currently visible view instance from the controller's state
        and calls its update method.
        """
        # Get the name of the current page from your navigation manager
        current_page_name = self.navigation_manager.get_current_page() #
        if not current_page_name:
            logging.warning("refresh_current_view: No current page found in navigation manager.")
            return

        # Get the actual view instance that is currently displayed from the controller's cache
        current_view_instance = self.views.get(current_page_name)
        
        if not current_view_instance:
            logging.warning(f"refresh_current_view: Could not find view instance for page '{current_page_name}'.")
            self.page.update() # Fallback to a simple page update
            return

        # Check if this specific view instance has our update_view method
        if hasattr(current_view_instance, "update_view"):
            logging.info(f"Calling update_view() on instance for page '{current_page_name}'.")
            current_view_instance.update_view()
        else:
            logging.info(f"View for page '{current_page_name}' has no update method, calling page.update().")
            self.page.update()

    def _clear_project_dependent_views(self):
        """Clear views that depend on project state when project is loaded/unloaded"""
        project_dependent_views = ['reports', 'sources', 'project_dashboard']
        for view_name in project_dependent_views:
            if view_name in self.views:
                self.views.pop(view_name)
                self.logger.info(f"Cleared cached view '{view_name}' due to project state change.")

    # --- PowerPoint Integration Methods ---
    
    def get_slides_for_current_project(self, force_reselect: bool = False):
        """
        Shows a file picker to select a PowerPoint file and extracts slide data.
        If force_reselect is True and there's an existing PowerPoint path, reloads that file.
        Stores the slide data in the current project's metadata.
        """
        return self.powerpoint_controller.get_slides_for_current_project(force_reselect)
    
    def _process_powerpoint_file(self, file_path: str):
        """
        Processes the selected PowerPoint file using the PowerPointService
        and stores the slide data in the project metadata.
        """
        return self.powerpoint_controller.process_powerpoint_file(file_path)
    
    def _show_error(self, message: str):
        """Helper method to show error messages to the user"""
        self.page.snack_bar = ft.SnackBar(
            ft.Text(message),
            bgcolor=ft.colors.ERROR_CONTAINER
        )
        self.page.snack_bar.open = True
        self.page.update()

    # --- Citation Management Methods (Placeholders) ---
    
    def add_citations_to_slide(self, slide_id: str, source_ids: list):
        """
        Placeholder method to add source citations to a specific slide.
        Stores citations in project metadata.
        """
        project = self.project_state_manager.current_project
        if not project:
            return
        
        # Initialize citations if not exists
        if "citations" not in project.metadata:
            project.metadata["citations"] = {}
        
        # Get existing citations for this slide
        existing_citations = set(project.metadata["citations"].get(slide_id, []))
        
        # Add new source IDs
        existing_citations.update(source_ids)
        
        # Store back in metadata
        project.metadata["citations"][slide_id] = list(existing_citations)
        
        # Save project
        self.data_service.save_project(project)
        
        self.logger.info(f"Added {len(source_ids)} citations to slide {slide_id}")
    
    def remove_citations_from_slide(self, slide_id: str, source_ids: list):
        """
        Placeholder method to remove source citations from a specific slide.
        Updates citations in project metadata.
        """
        project = self.project_state_manager.current_project
        if not project:
            return
        
        # Check if citations exist
        if "citations" not in project.metadata:
            return
        
        # Get existing citations for this slide
        existing_citations = set(project.metadata["citations"].get(slide_id, []))
        
        # Remove specified source IDs
        existing_citations.difference_update(source_ids)
        
        # Store back in metadata (or remove entry if empty)
        if existing_citations:
            project.metadata["citations"][slide_id] = list(existing_citations)
        else:
            project.metadata["citations"].pop(slide_id, None)
        
        # Save project
        self.data_service.save_project(project)
        
        self.logger.info(f"Removed {len(source_ids)} citations from slide {slide_id}")

    # --- Source Group Management Methods ---
    
    def create_source_group(self, group_name: str, source_ids: list):
        """
        Creates a new source group for the current project.
        
        Args:
            group_name: Name of the group
            source_ids: List of source IDs to include in the group
        """
        project = self.project_state_manager.current_project
        if not project:
            self.logger.warning("Cannot create source group: No project loaded")
            return False
        
        # Initialize source groups if not exists
        if "source_groups" not in project.metadata:
            project.metadata["source_groups"] = {}
        
        # Check if group name already exists
        if group_name in project.metadata["source_groups"]:
            self.logger.warning(f"Source group '{group_name}' already exists")
            return False
        
        # Create the group
        project.metadata["source_groups"][group_name] = {
            "source_ids": source_ids,
            "created_date": datetime.now().isoformat()
        }
        
        # Save project
        self.data_service.save_project(project)
        
        self.logger.info(f"Created source group '{group_name}' with {len(source_ids)} sources")
        return True
    
    def get_source_groups(self):
        """
        Gets all source groups for the current project.
        
        Returns:
            Dict of group_name -> group_data
        """
        project = self.project_state_manager.current_project
        if not project:
            return {}
        
        return project.metadata.get("source_groups", {})
    
    def delete_source_group(self, group_name: str):
        """
        Deletes a source group from the current project.
        
        Args:
            group_name: Name of the group to delete
        """
        project = self.project_state_manager.current_project
        if not project:
            return False
        
        if "source_groups" not in project.metadata:
            return False
        
        if group_name in project.metadata["source_groups"]:
            del project.metadata["source_groups"][group_name]
            self.data_service.save_project(project)
            self.logger.info(f"Deleted source group '{group_name}'")
            return True
        
        return False
    
    def add_source_group_to_slide(self, slide_id: str, group_name: str):
        """
        Adds all sources from a group to a specific slide.
        
        Args:
            slide_id: ID of the slide
            group_name: Name of the source group
        """
        project = self.project_state_manager.current_project
        if not project:
            return False
        
        # Get the group
        source_groups = project.metadata.get("source_groups", {})
        if group_name not in source_groups:
            self.logger.warning(f"Source group '{group_name}' not found")
            return False
        
        # Get source IDs from the group
        source_ids = source_groups[group_name]["source_ids"]
        
        # Add citations to slide using existing method
        self.add_citations_to_slide(slide_id, source_ids)
        
        self.logger.info(f"Added source group '{group_name}' ({len(source_ids)} sources) to slide {slide_id}")
        return True
    
    def show_create_source_group_dialog(self):
        """
        Shows the dialog for creating a new source group.
        """
        project = self.project_state_manager.current_project
        if not project:
            return
        
        # Get all project sources to create checkboxes
        all_source_checkboxes = []
        for source_link in project.sources:
            # Get the actual source record for the title
            source_record = self.data_service.get_source_by_id(source_link.source_id)
            if source_record:
                checkbox = ft.Checkbox(
                    label=source_record.title,
                    value=False,
                    data=source_link.source_id
                )
                all_source_checkboxes.append(checkbox)
        
        # Import and create the dialog
        from views.components.dialogs.create_source_group_dialog import CreateSourceGroupDialog
        
        def on_group_save(group_name: str, selected_ids: list):
            """Callback when group is saved"""
            success = self.create_source_group(group_name, selected_ids)
            if success:
                if self.page:
                    self.page.show_snack_bar(
                        ft.SnackBar(
                            ft.Text(f"Source group '{group_name}' created successfully!"),
                            bgcolor=ft.colors.GREEN
                        )
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                
                # Refresh the current view to show updated groups
                self.refresh_current_view()
            else:
                if self.page:
                    self.page.show_snack_bar(
                        ft.SnackBar(
                            ft.Text(f"Failed to create group '{group_name}'. Name may already exist."),
                            bgcolor=ft.colors.RED
                        )
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        
        dialog = CreateSourceGroupDialog(
            all_sources=all_source_checkboxes,
            on_save=on_group_save
        )
        
        if self.page:
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()

    # --- Export Methods ---
    
    def export_bibliography_to_word(self, export_path: str) -> bool:
        """Export bibliography as Word document"""
        try:
            project = self.project_state_manager.current_project
            if not project:
                self.logger.warning("No project loaded for bibliography export")
                return False
            
            # Get project sources - use the existing country approach from data service
            from config.app_config import get_country_from_project_path
            country = get_country_from_project_path(project.file_path)
            sources = self.data_service.get_master_sources_for_country(country)
            
            if not sources:
                self.logger.warning("No sources found for bibliography export")
                return False
            
            # TODO: Implement actual Word document creation
            # For now, just create a simple text file with bibliography
            from utils.citation_generator import generate_citation
            
            bibliography_lines = []
            for source in sources:
                citation = generate_citation(source)
                bibliography_lines.append(citation)
            
            bibliography_content = "\n\n".join(bibliography_lines)
            
            # Write to file (for now as text, replace with Word generation later)
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(f"Bibliography - {project.metadata.get('title', 'Untitled Project')}\n")
                f.write("=" * 60 + "\n\n")
                f.write(bibliography_content)
            
            self.logger.info(f"Bibliography exported to: {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting bibliography to Word: {e}")
            return False
    
    def get_project_sources_for_bibliography(self) -> List:
        """Get sources for the current project for bibliography generation"""
        project = self.project_state_manager.current_project
        if not project:
            return []
        
        try:
            from config.app_config import get_country_from_project_path
            country = get_country_from_project_path(project.file_path)
            return self.data_service.get_master_sources_for_country(country)
        except Exception as e:
            self.logger.error(f"Error getting project sources: {e}")
            return []
    
    def get_bibliography_preview(self) -> str:
        """Generate a preview of the bibliography"""
        sources = self.get_project_sources_for_bibliography()
        if not sources:
            return "No sources found for the current project."
        
        try:
            from utils.citation_generator import generate_citation
            
            bibliography_lines = []
            for source in sources:
                citation = generate_citation(source)
                bibliography_lines.append(citation)
            
            return "\n\n".join(bibliography_lines)
            
        except Exception as e:
            self.logger.error(f"Error generating bibliography preview: {e}")
            return "Error generating bibliography preview."
    
    def _show_error_dialog(self, title: str, message: str):
        """Show an error dialog to the user."""
        import flet as ft
        
        def close_dialog(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=close_dialog)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _handle_old_format_file(self, project_path: Path):
        """Handle opening an old format project file by offering migration."""
        return self.project_controller.handle_old_format_file(project_path)
    
    def _show_migration_progress_dialog(self):
        """Show a progress dialog during migration."""
        import flet as ft
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Migrating Project..."),
            content=ft.Column([
                ft.ProgressRing(),
                ft.Text("Please wait while we update your project to the new format."),
                ft.Text("This may take a moment...")
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
        
        return dialog
    
    def _show_success_dialog(self, title: str, message: str):
        """Show a success dialog to the user."""
        import flet as ft
        
        def close_dialog(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=close_dialog)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()