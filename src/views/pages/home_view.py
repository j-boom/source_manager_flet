import flet as ft
from ..base_view import BaseView


class HomeView(BaseView):
    """Home page view"""
    
    def __init__(self, page: ft.Page, theme_manager=None, on_navigate=None):
        super().__init__(page)
        self.theme_manager = theme_manager
        self.on_navigate = on_navigate
    
    def build(self) -> ft.Control:
        """Build the home page content"""
        return ft.Container(
            content=ft.Column([
                # Welcome Section
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "Welcome to Source Manager",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.BLUE_700
                        ),
                        ft.Text(
                            "Manage your source code projects efficiently",
                            size=16,
                            color=ft.colors.GREY_600
                        ),
                    ]),
                    padding=ft.padding.only(bottom=30)
                ),
                
                # Quick Actions Cards
                ft.Text(
                    "Quick Actions",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.GREY_800
                ),
                
                ft.Row([
                    self._create_action_card(
                        "New Project",
                        "Create a new source code project",
                        ft.icons.ADD_CIRCLE_OUTLINE,
                        ft.colors.GREEN,
                        self._on_new_project
                    ),
                    ft.Container(width=50),  # 50px spacing
                    self._create_action_card(
                        "Import Sources",
                        "Import existing source files",
                        ft.icons.UPLOAD_FILE,
                        ft.colors.BLUE,
                        self._on_import_sources
                    ),
                    ft.Container(width=50),  # 50px spacing
                    self._create_action_card(
                        "Recent Projects",
                        "View recently accessed projects",
                        ft.icons.HISTORY,
                        ft.colors.ORANGE,
                        self._on_recent_projects
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER),
            ]),
            padding=20,
            expand=True,
        )
    
    def _create_action_card(self, title: str, description: str, icon: str, color: str, on_click) -> ft.Container:
        """Create a quick action card"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=40, color=color),
                ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=self._get_card_title_color()),
                ft.Text(description, size=12, color=self._get_card_description_color(), text_align=ft.TextAlign.CENTER),
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10),
            width=200,
            height=150,
            padding=20,
            bgcolor=self._get_card_bg_color(),
            border=ft.border.all(1, self._get_card_border_color()),
            border_radius=8,
            ink=True,
            on_click=on_click,
        )
    
    def _get_card_bg_color(self) -> str:
        """Get card background color based on theme"""
        if self.theme_manager:
            current_mode = "dark" if self.page.theme_mode == ft.ThemeMode.DARK else "light"
            return self.theme_manager.get_card_bg_color(current_mode)
        # Fallback
        if self.page.theme_mode == ft.ThemeMode.DARK:
            return ft.colors.GREY_700
        return ft.colors.WHITE
    
    def _get_card_border_color(self) -> str:
        """Get card border color based on theme"""
        if self.theme_manager:
            current_mode = "dark" if self.page.theme_mode == ft.ThemeMode.DARK else "light"
            return self.theme_manager.get_card_border_color(current_mode)
        # Fallback
        if self.page.theme_mode == ft.ThemeMode.DARK:
            return ft.colors.GREY_600
        return ft.colors.GREY_300

    def _get_card_title_color(self) -> str:
        """Get card title text color based on theme"""
        if self.page.theme_mode == ft.ThemeMode.DARK:
            return ft.colors.WHITE
        return ft.colors.BLACK
    
    def _get_card_description_color(self) -> str:
        """Get card description text color based on theme"""
        if self.page.theme_mode == ft.ThemeMode.DARK:
            return ft.colors.GREY_400
        return ft.colors.GREY_700

    def _on_new_project(self, e):
        """Handle new project action"""
        if self.on_navigate:
            self.on_navigate("new_project")
        else:
            print("New project clicked")
    
    def _on_import_sources(self, e):
        """Handle import sources action (placeholder)"""
        print("Import sources clicked - functionality to be implemented")

    def _on_recent_projects(self, e):
        """Handle recent projects action"""
        if self.on_navigate:
            self.on_navigate("recent_projects")
        else:
            print("Recent projects clicked")
