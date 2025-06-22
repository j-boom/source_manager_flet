import flet as ft
from typing import Dict
from views import MainView, HomeView, RecentProjectsView, NewProjectView
from models import (
    UserConfigManager, 
    ThemeManager, 
    WindowManager, 
    NavigationManager, 
    SettingsManager
)


class AppController:
    """Main application controller - orchestrates all managers and views"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        
        # Initialize managers
        self.user_config = UserConfigManager()
        self.theme_manager = ThemeManager()
        self.window_manager = WindowManager(page, self.user_config)
        self.navigation_manager = NavigationManager(self.user_config)
        self.settings_manager = SettingsManager(self.user_config, self.theme_manager)
        
        # Apply saved configurations
        self.window_manager.apply_saved_window_config()
        self.settings_manager.apply_saved_settings(page)
        
        # Initialize main view
        self.main_view = MainView(page, self.theme_manager)
        
        # Set up callbacks
        self._setup_callbacks()
        
        # Apply saved theme color
        current_color = self.settings_manager.get_current_theme_color()
        if self.theme_manager.is_valid_color(current_color):
            color_data = self.theme_manager.get_color_data(current_color)
            self.main_view.set_theme_color(color_data)
        
        # Initialize views
        self.views = {
            "home": HomeView(page, self.theme_manager, on_navigate=self._handle_navigation),
            "recent_projects": RecentProjectsView(
                page, 
                self.theme_manager, 
                self.user_config,
                on_open_project=self._handle_project_selected,
                on_back=lambda: self._handle_navigation("home"),
                on_navigate=self._handle_navigation
            ),
            "new_project": NewProjectView(
                page,
                self.theme_manager,
                self.user_config,
                on_back=lambda: self._handle_navigation("home"),
                on_project_selected=self._handle_project_selected
            ),
            # Add other views here as you create them
            # "projects": ProjectsView(page, self.theme_manager),
            # "sources": SourcesView(page, self.theme_manager),
            # "reports": ReportsView(page, self.theme_manager),
        }
    
    def _setup_callbacks(self):
        """Set up all manager callbacks"""
        # Navigation callback
        self.navigation_manager.set_navigation_callback(self._handle_navigation)
        self.main_view.set_navigation_callback(self._handle_navigation)
        
        # Settings callbacks
        self.settings_manager.set_theme_change_callback(self._handle_theme_change)
        self.settings_manager.set_color_change_callback(self._handle_color_change)
    
    def _handle_navigation(self, page_name: str):
        """Handle navigation between pages"""
        # Update navigation state without triggering callback to prevent recursion
        self.navigation_manager.current_page = page_name
        self.navigation_manager.user_config.save_last_page(page_name)
        
        # Update main view navigation selection
        page_index = self.navigation_manager.get_page_index(page_name)
        if page_index is not None:
            self.main_view.update_selected_navigation(page_name)
        
        # Load appropriate content
        if page_name == "projects":
            # Special handling for projects route
            # Ensure project state manager exists
            if not hasattr(self, 'project_state_manager'):
                self.project_state_manager = self._create_project_state_manager()
            
            if self.project_state_manager and hasattr(self.project_state_manager, 'loaded_project_path') and self.project_state_manager.loaded_project_path:
                # If a project is loaded, show the project view
                if "project_view" not in self.views:
                    # Initialize project view if not already created
                    from views.pages.project_view import ProjectView
                    from models.database_manager import DatabaseManager
                    
                    db_manager = DatabaseManager()
                    self.views["project_view"] = ProjectView(
                        self.page,
                        self.theme_manager,
                        database_manager=db_manager,
                        project_state_manager=self.project_state_manager,
                        on_navigate=self._handle_navigation
                    )
                else:
                    # Update existing project view with current project data
                    if hasattr(self.views["project_view"], 'refresh_project_data'):
                        self.views["project_view"].refresh_project_data()
                
                content = self.views["project_view"].get_content()
                self.main_view.set_content(content)
            else:
                # No project loaded, redirect to new project view
                self._handle_navigation("new_project")
                return
        elif page_name in self.views:
            # For certain views, we might want to refresh the content
            if page_name == "recent_projects":
                # Refresh the recent projects view to show latest data
                content = self.views[page_name].refresh()
                self.main_view.set_content(content)
            elif page_name == "new_project":
                # Get content first, then refresh theme
                content = self.views[page_name].get_content()
                self.main_view.set_content(content)
                # Refresh theme for new project view after content is loaded
                if hasattr(self.views[page_name], 'refresh_theme'):
                    self.views[page_name].refresh_theme()
            else:
                content = self.views[page_name].get_content()
                self.main_view.set_content(content)
        elif page_name == "settings":
            settings_content = self.settings_manager.create_settings_view(self.page)
            self.main_view.set_content(settings_content)
        elif page_name == "help":
            self._show_help()
        else:
            self._show_not_found(page_name)
    
    def _handle_theme_change(self, new_mode: str):
        """Handle theme mode changes"""
        self.main_view.update_theme_colors()
        
        # Refresh current view to apply theme changes
        current_page = self.navigation_manager.get_current_page()
        if current_page == "new_project" and "new_project" in self.views:
            # Specifically refresh the new project view
            self.views["new_project"].refresh_theme()
        
        # You could add similar refresh calls for other views that need theme updates
        # elif current_page == "recent_projects" and "recent_projects" in self.views:
        #     self.views["recent_projects"].refresh_theme()
        
        self.page.update()
    
    def _handle_color_change(self, new_color: str):
        """Handle color theme changes"""
        color_data = self.theme_manager.get_color_data(new_color)
        self.main_view.set_theme_color(color_data)
        
        # Refresh current page to apply new colors
        current_page = self.navigation_manager.get_current_page()
        self._handle_navigation(current_page)
    
    def add_sample_recent_site(self, display_name: str, path: str):
        """Add a sample recent site (for testing purposes)"""
        self.user_config.add_recent_site(display_name, path)
        
        # If we're currently on the recent projects page, refresh it
        current_page = self.navigation_manager.get_current_page()
        if current_page == "recent_projects":
            content = self.views["recent_projects"].refresh()
            self.main_view.set_content(content)
    
    def _handle_project_selected(self, project_path: str, project_name: str):
        """Handle project selection from new project view"""
        # Add the selected project to recent sites
        self.user_config.add_recent_site(project_name, project_path)
        
        # Log project selection
        print(f"Project selected: {project_name} at {project_path}")
        
        # Initialize the project state manager directly with a simple implementation
        # instead of importing the class that's having issues
        if not hasattr(self, 'project_state_manager'):
            self.project_state_manager = self._create_project_state_manager()
        
        # Load the project data from JSON file
        project_data = self._load_project_json(project_path, project_name)
        
        # Load the selected project
        self.project_state_manager.loaded_project_path = project_path
        self.project_state_manager.project_data = project_data
        
        print(f"Project loaded: {project_path}")
        
        # Check if we need to initialize the project view
        if "project_view" not in self.views:
            # Import here to avoid circular imports
            from views.pages.project_view import ProjectView
            from models.database_manager import DatabaseManager
            
            # Initialize the database manager if needed
            db_manager = DatabaseManager()
            
            # Initialize the project view with the project state manager
            self.views["project_view"] = ProjectView(
                self.page,
                self.theme_manager,
                database_manager=db_manager,
                project_state_manager=self.project_state_manager,
                on_navigate=self._handle_navigation
            )
        else:
            # Update existing project view with new project data
            self.views["project_view"].project_state_manager = self.project_state_manager
            if hasattr(self.views["project_view"], 'refresh_project_data'):
                self.views["project_view"].refresh_project_data()
        
        # Navigate to the project view
        self._handle_navigation("project_view")
    
    def _show_help(self):
        """Show help page"""
        help_content = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Help & Documentation",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=self.theme_manager.get_color_data(
                        self.settings_manager.get_current_theme_color()
                    )["primary"]
                ),
                ft.Divider(),
                ft.Text("Getting Started", size=18, weight=ft.FontWeight.BOLD),
                ft.Text("1. Create a new project from the Home page"),
                ft.Text("2. Import your source files"),
                ft.Text("3. Use the navigation to explore different sections"),
                ft.Container(height=20),
                ft.Text("Support", size=18, weight=ft.FontWeight.BOLD),
                ft.Text("For additional help, please contact support."),
            ]),
            padding=20,
            expand=True,
        )
        self.main_view.set_content(help_content)
    
    def _show_not_found(self, page_name: str):
        """Show not found page"""
        not_found_content = ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.ERROR_OUTLINE, size=64, color=ft.colors.GREY_400),
                ft.Text(
                    f"Page '{page_name}' not found",
                    size=20,
                    color=ft.colors.GREY_600
                ),
                ft.ElevatedButton(
                    "Go to Home",
                    on_click=lambda _: self._handle_navigation("home")
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20),
            alignment=ft.alignment.center,
            expand=True,
        )
        self.main_view.set_content(not_found_content)
    
    def _show_error(self, title: str, message: str):
        """Show an error dialog"""
        error_dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda e: self._close_dialog(error_dialog))
            ]
        )
        self.page.dialog = error_dialog
        error_dialog.open = True
        self.page.update()
    
    def _close_dialog(self, dialog):
        """Close a dialog"""
        dialog.open = False
        self.page.update()

    def _create_project_state_manager(self):
        """Create a simple project state manager"""
        class SimpleProjectStateManager:
            def __init__(self):
                self.loaded_project_path = None
                self.project_data = None
            
            def has_loaded_project(self):
                return self.loaded_project_path is not None
            
            def get_project_title(self):
                if not self.has_loaded_project():
                    return "No Project Loaded"
                if self.project_data and "name" in self.project_data:
                    return self.project_data["name"]
                if self.loaded_project_path:
                    import os
                    return os.path.basename(self.loaded_project_path)
                return "Untitled Project"
        
        return SimpleProjectStateManager()

    def _load_project_json(self, project_path: str, project_name: str) -> Dict:
        """Load project data from JSON file"""
        try:
            # If the project_path is a JSON file, load it directly
            if project_path.endswith('.json'):
                import json
                with open(project_path, 'r') as f:
                    project_data = json.load(f)
                    
                # Flatten nested data for metadata form
                flattened_data = {"path": project_path, "name": project_name}
                
                # Add top-level fields
                for key in ['uuid', 'title', 'project_type', 'description', 'status', 'created_date', 'database_id']:
                    if key in project_data:
                        flattened_data[key] = project_data[key]
                
                # Add customer fields if they exist
                if 'customer' in project_data and isinstance(project_data['customer'], dict):
                    customer = project_data['customer']
                    flattened_data['customer_name'] = customer.get('name', '')
                    flattened_data['customer_number'] = customer.get('number', '')
                    flattened_data['customer_key'] = customer.get('key', '')
                    flattened_data['client'] = customer.get('name', '')  # Map to client field
                
                # Add any other fields that might be in the JSON
                for key, value in project_data.items():
                    if key not in ['customer', 'metadata'] and key not in flattened_data:
                        flattened_data[key] = value
                
                print(f"Loaded project data: {flattened_data}")
                return flattened_data
            else:
                # If it's not a JSON file, return basic data
                return {"path": project_path, "name": project_name}
                
        except Exception as e:
            print(f"Error loading project JSON: {e}")
            return {"path": project_path, "name": project_name}

    def run(self):
        """Start the application"""
        # Show the main view
        self.main_view.show()
        
        # Always navigate to home page on startup (ignore saved last page)
        self._handle_navigation("home")
    
    def cleanup(self):
        """Clean up and save configuration before exit"""
        self.window_manager.save_current_window_config()
