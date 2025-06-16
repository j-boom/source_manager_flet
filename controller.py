import flet as ft
from views import MainView, HomeView
from models import UserConfigManager


class AppController:
    """Main application controller that coordinates between models and views"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        
        # Initialize user configuration manager
        self.user_config = UserConfigManager()
        
        # Apply saved window configuration
        self._apply_window_config()
        
        # Apply saved theme configuration
        self._apply_theme_config()
        
        self.main_view = MainView(page)
        self.current_page = self.user_config.get_last_page()
        
        # Theme color options
        self.theme_colors = {
            "blue": {"primary": ft.colors.BLUE_700, "accent": ft.colors.BLUE_50},
            "red": {"primary": ft.colors.RED_700, "accent": ft.colors.RED_50},
            "orange": {"primary": ft.colors.ORANGE_700, "accent": ft.colors.ORANGE_50},
            "green": {"primary": ft.colors.GREEN_700, "accent": ft.colors.GREEN_50},
            "yellow": {"primary": ft.colors.YELLOW_700, "accent": ft.colors.YELLOW_50},
            "purple": {"primary": ft.colors.PURPLE_700, "accent": ft.colors.PURPLE_50},
            "indigo": {"primary": ft.colors.INDIGO_700, "accent": ft.colors.INDIGO_50},
        }
        self.current_theme_color = self.user_config.get_theme_color()
        
        # Apply the saved theme color
        if self.current_theme_color in self.theme_colors:
            self.main_view.set_theme_color(self.theme_colors[self.current_theme_color])
        
        # Set up navigation callback
        self.main_view.set_navigation_callback(self.navigate_to_page)
        
        # Initialize views
        self.views = {
            "home": HomeView(page),
            # Add other views here as you create them
            # "projects": ProjectsView(page),
            # "sources": SourcesView(page),
            # "reports": ReportsView(page),
        }

    def _apply_window_config(self):
        """Apply saved window configuration"""
        window_config = self.user_config.get_window_config()
        
        self.page.window_width = window_config["width"]
        self.page.window_height = window_config["height"]
        self.page.window_min_width = 800
        self.page.window_min_height = 600
        
        if window_config["x"] is not None and window_config["y"] is not None:
            self.page.window_left = window_config["x"]
            self.page.window_top = window_config["y"]
        
        if window_config["maximized"]:
            self.page.window_maximized = True

    def _apply_theme_config(self):
        """Apply saved theme configuration"""
        theme_mode = self.user_config.get_theme_mode()
        
        if theme_mode == "dark":
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
        
        self.page.title = f"Source Manager - {self.user_config.get_username()}"
        self.page.padding = 0

    def _on_window_event(self, e):
        """Handle window events to save configuration"""
        if e.event_type == "close":
            self._save_current_window_config()

    def _save_current_window_config(self):
        """Save current window configuration"""
        try:
            self.user_config.save_window_config(
                width=int(self.page.window_width or 1200),
                height=int(self.page.window_height or 800),
                x=int(self.page.window_left) if self.page.window_left is not None else None,
                y=int(self.page.window_top) if self.page.window_top is not None else None,
                maximized=self.page.window_maximized or False
            )
            self.user_config.save_last_page(self.current_page)
        except Exception as e:
            print(f"Error saving window config: {e}")

    def run(self):
        """Start the application"""
        # Show the main view
        self.main_view.show()
        
        # Load the default page (home)
        self.navigate_to_page("home")
    
    def navigate_to_page(self, page_name: str):
        """Navigate to a specific page"""
        self.current_page = page_name
        
        # Update the navigation selection
        self.main_view.update_selected_navigation(page_name)
        
        # Load the appropriate view
        if page_name in self.views:
            content = self.views[page_name].get_content()
            self.main_view.set_content(content)
        else:
            # Handle unknown pages or special cases
            if page_name == "settings":
                self._show_settings()
            elif page_name == "help":
                self._show_help()
            else:
                self._show_not_found(page_name)
    
    def _show_settings(self):
        """Show settings page"""
        # Create color theme selection buttons
        color_buttons = []
        for color_name in self.theme_colors.keys():
            color_data = self.theme_colors[color_name]
            is_selected = color_name == self.current_theme_color
            
            button = ft.Container(
                content=ft.Column([
                    ft.Container(
                        width=40,
                        height=40,
                        bgcolor=color_data["primary"],
                        border_radius=20,
                        border=ft.border.all(3, ft.colors.WHITE if is_selected else ft.colors.TRANSPARENT),
                        shadow=ft.BoxShadow(
                            spread_radius=1,
                            blur_radius=3,
                            color=ft.colors.BLACK26,
                            offset=ft.Offset(0, 2),
                        ) if is_selected else None,
                    ),
                    ft.Text(
                        color_name.title(),
                        size=12,
                        weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL,
                        color=color_data["primary"] if is_selected else ft.colors.GREY_600
                    )
                ], 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8),
                padding=10,
                on_click=lambda e, color=color_name: self._change_theme_color(color),
                ink=True,
                border_radius=8,
            )
            color_buttons.append(button)
        
        settings_content = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Settings",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=self.theme_colors[self.current_theme_color]["primary"]
                ),
                ft.Divider(),
                
                # Theme Mode Setting
                ft.ListTile(
                    leading=ft.Icon(ft.icons.BRIGHTNESS_6),
                    title=ft.Text("Theme Mode"),
                    subtitle=ft.Text("Choose light or dark theme"),
                    trailing=ft.Switch(
                        value=self.page.theme_mode == ft.ThemeMode.DARK,
                        on_change=self._toggle_theme
                    )
                ),
                
                ft.Container(height=20),
                
                # Theme Color Setting
                ft.Text(
                    "Theme Color",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.GREY_800
                ),
                ft.Text(
                    "Choose your preferred color theme",
                    size=14,
                    color=ft.colors.GREY_600
                ),
                ft.Container(height=10),
                ft.Row(
                    color_buttons,
                    spacing=15,
                    wrap=True,
                ),
                
                ft.Container(height=30),
                
                # Application Info
                ft.Divider(),
                ft.Text(
                    "Application Info",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.GREY_800
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.INFO_OUTLINE),
                    title=ft.Text("Version"),
                    subtitle=ft.Text("Source Manager v1.0.0"),
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.DEVELOPER_MODE),
                    title=ft.Text("Built with"),
                    subtitle=ft.Text("Python & Flet Framework"),
                ),
            ]),
            padding=20,
            expand=True,
        )
        self.main_view.set_content(settings_content)
    
    def _show_help(self):
        """Show help page"""
        help_content = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Help & Documentation",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.BLUE_700
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
                    on_click=lambda _: self.navigate_to_page("home")
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20),
            alignment=ft.alignment.center,
            expand=True,
        )
        self.main_view.set_content(not_found_content)
    
    def _change_theme_color(self, color_name: str):
        """Change the application theme color"""
        if color_name in self.theme_colors:
            self.current_theme_color = color_name
            
            # Save to user config
            self.user_config.save_theme_color(color_name)
            
            # Update the main view with new colors
            self.main_view.set_theme_color(self.theme_colors[color_name])
            
            # Refresh the current page to apply new colors
            self.navigate_to_page(self.current_page)
            
            # If we're on settings page, refresh it to show the updated selection
            if self.current_page == "settings":
                self._show_settings()

    def _toggle_theme(self, e):
        """Toggle between light and dark theme"""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.user_config.save_theme_mode("dark")
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.user_config.save_theme_mode("light")
        
        # Update the main view colors
        self.main_view.update_theme_colors()
        self.page.update()
