import flet as ft
from typing import Dict
from views import MainView, HomeView
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
            "home": HomeView(page, self.theme_manager),
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
        if page_name in self.views:
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
    
    def _handle_color_change(self, new_color: str):
        """Handle color theme changes"""
        color_data = self.theme_manager.get_color_data(new_color)
        self.main_view.set_theme_color(color_data)
        
        # Refresh current page to apply new colors
        current_page = self.navigation_manager.get_current_page()
        self._handle_navigation(current_page)
    
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
    
    def run(self):
        """Start the application"""
        # Show the main view
        self.main_view.show()
        
        # Navigate to the last opened page
        last_page = self.navigation_manager.get_current_page()
        self._handle_navigation(last_page)
    
    def cleanup(self):
        """Clean up and save configuration before exit"""
        self.window_manager.save_current_window_config()
