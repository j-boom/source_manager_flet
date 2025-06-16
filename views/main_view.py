import flet as ft
from typing import Optional, Callable


class MainView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Source Manager"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window_min_width = 800
        self.page.window_min_height = 600
        
        # Callbacks for navigation
        self.on_navigation_change: Optional[Callable[[str], None]] = None
        
        # UI Components
        self.sidebar = self._create_sidebar()
        self.app_bar = self._create_app_bar()
        self.content_area = self._create_content_area()
        self.main_layout = self._create_main_layout()
        
    def _create_app_bar(self) -> ft.AppBar:
        """Create the application bar"""
        return ft.AppBar(
            title=ft.Text("Source Manager", size=20, weight=ft.FontWeight.BOLD),
            bgcolor=ft.colors.BLUE_700,
            color=ft.colors.WHITE,
            actions=[
                ft.IconButton(
                    icon=ft.icons.SETTINGS,
                    icon_color=ft.colors.WHITE,
                    tooltip="Settings",
                    on_click=self._on_settings_click
                ),
                ft.IconButton(
                    icon=ft.icons.HELP,
                    icon_color=ft.colors.WHITE,
                    tooltip="Help",
                    on_click=self._on_help_click
                ),
            ]
        )
    
    def _create_sidebar(self) -> ft.NavigationRail:
        """Create the sidebar navigation"""
        return ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.HOME_OUTLINED,
                    selected_icon=ft.icons.HOME,
                    label="Home"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.FOLDER_OUTLINED,
                    selected_icon=ft.icons.FOLDER,
                    label="Projects"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.CODE_OUTLINED,
                    selected_icon=ft.icons.CODE,
                    label="Sources"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.ANALYTICS_OUTLINED,
                    selected_icon=ft.icons.ANALYTICS,
                    label="Reports"
                ),
            ],
            on_change=self._on_navigation_change,
            bgcolor=self._get_sidebar_color(),
        )
    
    def _create_content_area(self) -> ft.Container:
        """Create the main content area"""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Welcome to Source Manager",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.BLUE_700
                ),
                ft.Text(
                    "Select an option from the sidebar to get started.",
                    size=16,
                    color=ft.colors.GREY_700
                ),
                ft.Divider(height=20, thickness=1),
                ft.Container(
                    content=ft.Text(
                        "Content will be loaded here based on your selection.",
                        size=14,
                        color=ft.colors.GREY_600
                    ),
                    padding=20,
                    bgcolor=self._get_secondary_bg_color(),
                    border_radius=8,
                    margin=ft.margin.only(top=20)
                )
            ]),
            padding=20,
            expand=True,
            bgcolor=self._get_content_bg_color(),
        )
    
    def _create_main_layout(self) -> ft.Row:
        """Create the main layout combining sidebar and content"""
        return ft.Row(
            [
                self.sidebar,
                ft.VerticalDivider(width=1),
                self.content_area,
            ],
            spacing=0,
            expand=True,
        )
    
    def _on_navigation_change(self, e: ft.ControlEvent):
        """Handle navigation rail selection changes"""
        selected_index = e.control.selected_index
        
        # Map indices to page names
        pages = ["home", "projects", "sources", "reports"]
        if 0 <= selected_index < len(pages):
            page_name = pages[selected_index]
            if self.on_navigation_change:
                self.on_navigation_change(page_name)
    
    def _on_settings_click(self, e: ft.ControlEvent):
        """Handle settings button click"""
        if self.on_navigation_change:
            self.on_navigation_change("settings")
    
    def _on_help_click(self, e: ft.ControlEvent):
        """Handle help button click"""
        if self.on_navigation_change:
            self.on_navigation_change("help")
    
    def set_content(self, content: ft.Control):
        """Update the content area with new content"""
        self.content_area.content = content
        self.page.update()
    
    def set_navigation_callback(self, callback: Callable[[str], None]):
        """Set the callback function for navigation changes"""
        self.on_navigation_change = callback
    
    def show(self):
        """Display the main view on the page"""
        self.page.appbar = self.app_bar
        self.page.add(self.main_layout)
        self.page.update()
    
    def update_selected_navigation(self, page_name: str):
        """Update the selected navigation item"""
        page_mapping = {
            "home": 0,
            "projects": 1,
            "sources": 2,
            "reports": 3
        }
        
        if page_name in page_mapping:
            self.sidebar.selected_index = page_mapping[page_name]
            self.page.update()
    
    def _get_sidebar_color(self) -> str:
        """Get sidebar background color based on theme"""
        if self.page.theme_mode == ft.ThemeMode.DARK:
            return ft.colors.GREY_900
        return ft.colors.GREY_100
    
    def _get_content_bg_color(self) -> str:
        """Get content area background color based on theme"""
        if self.page.theme_mode == ft.ThemeMode.DARK:
            return ft.colors.GREY_800
        return ft.colors.WHITE
    
    def _get_secondary_bg_color(self) -> str:
        """Get secondary background color based on theme"""
        if self.page.theme_mode == ft.ThemeMode.DARK:
            return ft.colors.GREY_700
        return ft.colors.GREY_50
    
    def set_theme_color(self, color_data: dict):
        """Set the theme color for the application"""
        self.current_theme_color = color_data
        # Update app bar color
        if self.app_bar:
            self.app_bar.bgcolor = color_data["primary"]
        self.page.update()

    def update_theme_colors(self):
        """Update colors when theme changes"""
        self.sidebar.bgcolor = self._get_sidebar_color()
        self.content_area.bgcolor = self._get_content_bg_color()
        # Update the nested container's background color if it exists
        if (self.content_area.content and 
            hasattr(self.content_area.content, 'controls') and 
            len(self.content_area.content.controls) > 3):
            nested_container = self.content_area.content.controls[3]
            if hasattr(nested_container, 'bgcolor'):
                nested_container.bgcolor = self._get_secondary_bg_color()
        self.page.update()
