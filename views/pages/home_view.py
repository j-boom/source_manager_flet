import flet as ft
from ..base_view import BaseView


class HomeView(BaseView):
    """Home page view"""
    
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
                    self._create_action_card(
                        "Import Sources",
                        "Import existing source files",
                        ft.icons.FILE_UPLOAD,
                        ft.colors.BLUE,
                        self._on_import_sources
                    ),
                    self._create_action_card(
                        "Recent Projects",
                        "View recently accessed projects",
                        ft.icons.HISTORY,
                        ft.colors.ORANGE,
                        self._on_recent_projects
                    ),
                ], spacing=20, wrap=True),
                
                # Statistics Section
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "Statistics",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.GREY_800
                        ),
                        ft.Row([
                            self._create_stat_card("Total Projects", "0", ft.icons.FOLDER),
                            self._create_stat_card("Source Files", "0", ft.icons.CODE),
                            self._create_stat_card("Last Modified", "Never", ft.icons.ACCESS_TIME),
                        ], spacing=20, wrap=True),
                    ]),
                    padding=ft.padding.only(top=30)
                ),
            ]),
            padding=20,
            expand=True,
        )
    
    def _create_action_card(self, title: str, description: str, icon: str, color: str, on_click) -> ft.Container:
        """Create a quick action card"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=40, color=color),
                ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
                ft.Text(description, size=12, color=ft.colors.GREY_600, text_align=ft.TextAlign.CENTER),
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
        if self.page.theme_mode == ft.ThemeMode.DARK:
            return ft.colors.GREY_700
        return ft.colors.WHITE
    
    def _get_card_border_color(self) -> str:
        """Get card border color based on theme"""
        if self.page.theme_mode == ft.ThemeMode.DARK:
            return ft.colors.GREY_600
        return ft.colors.GREY_300

    def _create_stat_card(self, title: str, value: str, icon: str) -> ft.Container:
        """Create a statistics card"""
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=30, color=ft.colors.BLUE_700),
                ft.Column([
                    ft.Text(value, size=20, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700),
                    ft.Text(title, size=12, color=ft.colors.GREY_600),
                ], spacing=2),
            ], spacing=15),
            width=180,
            padding=15,
            bgcolor=ft.colors.BLUE_50,
            border_radius=8,
            border=ft.border.all(1, ft.colors.BLUE_200),
        )
    
    def _on_new_project(self, e):
        """Handle new project action"""
        # This would be handled by the controller
        print("New project clicked")
    
    def _on_import_sources(self, e):
        """Handle import sources action"""
        # This would be handled by the controller
        print("Import sources clicked")
    
    def _on_recent_projects(self, e):
        """Handle recent projects action"""
        # This would be handled by the controller
        print("Recent projects clicked")
