import flet as ft
from typing import Dict
from views import MainView, HomeView, RecentProjectsView, NewProjectView, ProjectView
from models import (
    UserConfigManager, 
    ThemeManager, 
    WindowManager, 
    NavigationManager, 
    SettingsManager,
    ProjectStateManager,
    DatabaseManager
)
from models.database_manager import Project


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
        self.project_state_manager = ProjectStateManager()
        self.database_manager = DatabaseManager()
        
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
            "project_view": ProjectView(
                page,
                self.theme_manager,
                self.database_manager,
                self.project_state_manager,
                on_navigate=self._handle_navigation
            ),
            "recent_projects": RecentProjectsView(
                page, 
                self.theme_manager, 
                self.user_config,
                on_open_project=self._handle_open_project,
                on_back=lambda: self._handle_navigation("home"),
                on_navigate=self._handle_navigation
            ),
            "new_project": NewProjectView(
                page,
                self.theme_manager,
                self.user_config,
                on_back=lambda: self._handle_navigation("home"),
                on_project_selected=self._handle_project_selected,
                project_state_manager=self.project_state_manager,
                on_navigate=self._handle_navigation
            ),
            # Add other views here as you create them
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
        # Special handling for "projects" destination - context-aware
        if page_name == "projects":
            if self.project_state_manager.has_loaded_project():
                # If a project is loaded, go to project view (to be implemented)
                page_name = "current_project"
            else:
                # If no project is loaded, go to new project view
                page_name = "new_project"
        
        # Update navigation state without triggering callback to prevent recursion
        self.navigation_manager.current_page = page_name
        self.navigation_manager.user_config.save_last_page(page_name)
        
        # Update main view navigation selection
        page_index = self.navigation_manager.get_page_index(page_name)
        if page_index is not None:
            self.main_view.update_selected_navigation(page_name)
        
        # Load appropriate content
        if page_name in self.views:
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
            elif page_name == "project_view":
                # Check if a project is loaded
                if self.project_state_manager.has_loaded_project():
                    content = self.views[page_name].get_content()
                    self.main_view.set_content(content)
                else:
                    # No project loaded, redirect to new project view
                    self._handle_navigation("new_project")
                    return
            else:
                content = self.views[page_name].get_content()
                self.main_view.set_content(content)
        elif page_name == "settings":
            settings_content = self.settings_manager.create_settings_view(self.page)
            self.main_view.set_content(settings_content)
        elif page_name == "current_project":
            # Show current project view
            self._show_current_project()
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
    
    def _handle_open_project(self, path: str, display_name: str):
        """Handle opening a project from recent projects"""
        # Add the project to recent sites (moves it to top if already exists)
        self.user_config.add_recent_site(display_name, path)
        
        # Load the project into the project state manager
        # For now, we'll create a simple project object from the display name
        # In a real implementation, you'd load from the JSON file or database
        import uuid
        project = Project(
            uuid=str(uuid.uuid4()),
            customer_id=1,  # Default customer ID
            title=display_name,
            project_code=display_name.split(' - ')[0] if ' - ' in display_name else display_name
        )
        self.project_state_manager.load_project(project)
        
        print(f"Opening project: {display_name} at {path}")
        
        # Navigate to the project view
        self._handle_navigation("project_view")
    
    def _handle_project_selected(self, project_path: str, project_name: str):
        """Handle project selection from new project view"""
        # Add the selected project to recent sites
        self.user_config.add_recent_site(project_name, project_path)
        
        # Load the project into the project state manager
        # For now, we'll create a simple project object from the name
        # In a real implementation, you'd load from the JSON file or database
        import uuid
        project = Project(
            uuid=str(uuid.uuid4()),
            customer_id=1,  # Default customer ID
            title=project_name,
            project_code=project_name.split(' - ')[0] if ' - ' in project_name else project_name
        )
        self.project_state_manager.load_project(project)
        
        print(f"Project loaded: {project_name} at {project_path}")
        
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
    
    def _show_current_project(self):
        """Show the current project view"""
        if self.project_state_manager.has_loaded_project():
            # Create a simple current project view
            project_info = self.project_state_manager.get_project_info()
            
            # Build project view content
            project_content = ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.ElevatedButton(
                            "Back to Home",
                            icon=ft.icons.HOME,
                            on_click=lambda e: self._handle_navigation("home")
                        ),
                        ft.Container(expand=True),
                        ft.Text("Current Project", size=20, weight=ft.FontWeight.BOLD)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.all(20),
                    bgcolor=ft.colors.GREY_800 if self.page.theme_mode == ft.ThemeMode.DARK else ft.colors.WHITE,
                    border=ft.border.only(bottom=ft.BorderSide(1, ft.colors.GREY_600 if self.page.theme_mode == ft.ThemeMode.DARK else ft.colors.GREY_300))
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"Project: {project_info.get('title', 'Unknown')}", size=18, weight=ft.FontWeight.BOLD),
                        ft.Container(height=10),
                        ft.Text(f"Type: {project_info.get('project_type', 'Unknown')}"),
                        ft.Text(f"Code: {project_info.get('project_code', 'Unknown')}"),
                        ft.Text(f"Engineer: {project_info.get('engineer', 'Not assigned')}"),
                        ft.Text(f"Drafter: {project_info.get('drafter', 'Not assigned')}"),
                        ft.Text(f"Reviewer: {project_info.get('reviewer', 'Not assigned')}"),
                        ft.Text(f"Architect: {project_info.get('architect', 'Not assigned')}"),
                        ft.Container(height=20),
                        ft.ElevatedButton(
                            "Close Project",
                            icon=ft.icons.CLOSE,
                            on_click=lambda e: self._close_current_project(),
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.RED_600,
                                color=ft.colors.WHITE
                            )
                        )
                    ], spacing=5),
                    padding=ft.padding.all(20)
                )
            ])
            
            self.main_view.set_content(project_content)
        else:
            # No project loaded, redirect to new project
            self._handle_navigation("new_project")
    
    def _close_current_project(self):
        """Close the current project and return to home"""
        self.project_state_manager.unload_project()
        self._handle_navigation("home")
    
    def run(self):
        """Start the application"""
        # Show the main view
        self.main_view.show()
        
        # Always navigate to home page on startup
        self._handle_navigation("home")
    
    def cleanup(self):
        """Clean up and save configuration before exit"""
        self.window_manager.save_current_window_config()
