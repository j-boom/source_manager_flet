import flet as ft
from ..base_view import BaseView
from typing import List, Dict, Any


class RecentProjectsView(BaseView):
    """Recent projects view - displays list of recent sites"""
    
    def __init__(self, page: ft.Page, theme_manager=None, user_config=None, on_open_project=None, on_back=None):
        super().__init__(page)
        self.theme_manager = theme_manager
        self.user_config = user_config
        self.on_open_project = on_open_project
        self.on_back = on_back
    
    def build(self) -> ft.Control:
        """Build the recent projects page content"""
        recent_sites = self.user_config.get_recent_sites() if self.user_config else []
        
        return ft.Container(
            content=ft.Column([
                # Header Section
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.IconButton(
                                icon=ft.icons.ARROW_BACK,
                                icon_color=ft.colors.BLUE_700,
                                on_click=self._on_back_clicked,
                                tooltip="Back to Home"
                            ),
                            ft.Text(
                                "Recent Projects",
                                size=28,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.BLUE_700
                            ),
                        ], alignment=ft.MainAxisAlignment.START),
                        ft.Text(
                            f"Your {len(recent_sites)} most recently accessed projects",
                            size=16,
                            color=ft.colors.GREY_600
                        ),
                    ]),
                    padding=ft.padding.only(bottom=30)
                ),
                
                # Content based on whether there are recent sites
                self._build_content(recent_sites),
                
            ]),
            padding=20,
            expand=True,
        )
    
    def _build_content(self, recent_sites: List[Dict[str, str]]) -> ft.Control:
        """Build content based on whether there are recent sites"""
        if not recent_sites:
            return self._build_empty_state()
        else:
            return self._build_recent_sites_list(recent_sites)
    
    def _build_empty_state(self) -> ft.Control:
        """Build empty state when no recent sites exist"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(
                    ft.icons.HISTORY,
                    size=80,
                    color=ft.colors.GREY_400
                ),
                ft.Text(
                    "No Recent Projects",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.GREY_600
                ),
                ft.Text(
                    "You haven't opened any projects yet. Start by creating a new project or importing existing sources.",
                    size=16,
                    color=ft.colors.GREY_500,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=30),
                ft.ElevatedButton(
                    text="Create New Project",
                    icon=ft.icons.ADD_CIRCLE_OUTLINE,
                    on_click=self._on_new_project_clicked,
                    style=ft.ButtonStyle(
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.BLUE_700,
                        padding=ft.padding.symmetric(horizontal=30, vertical=15)
                    )
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20),
            alignment=ft.alignment.center,
            expand=True
        )
    
    def _build_recent_sites_list(self, recent_sites: List[Dict[str, str]]) -> ft.Control:
        """Build list of recent sites as cards"""
        return ft.Container(
            content=ft.Column([
                # Action buttons row
                ft.Row([
                    ft.ElevatedButton(
                        text="New Project",
                        icon=ft.icons.ADD_CIRCLE_OUTLINE,
                        on_click=self._on_new_project_clicked,
                        style=ft.ButtonStyle(
                            color=ft.colors.WHITE,
                            bgcolor=ft.colors.GREEN_700
                        )
                    ),
                    ft.OutlinedButton(
                        text="Clear All",
                        icon=ft.icons.CLEAR_ALL,
                        on_click=self._on_clear_all_clicked,
                        style=ft.ButtonStyle(
                            color=ft.colors.RED_700,
                        )
                    ),
                ], spacing=10),
                
                ft.Container(height=20),
                
                # Recent sites grid
                ft.GridView(
                    controls=[
                        self._create_project_card(site) for site in recent_sites
                    ],
                    runs_count=3,  # 3 cards per row
                    max_extent=300,
                    child_aspect_ratio=1.2,
                    spacing=15,
                    run_spacing=15,
                    expand=True
                )
            ]),
            expand=True
        )
    
    def _create_project_card(self, site: Dict[str, str]) -> ft.Container:
        """Create a card for a recent project"""
        display_name = site.get("display_name", "Unknown Project")
        path = site.get("path", "")
        
        # Extract directory name from path for additional context
        import os
        dir_name = os.path.basename(path) if path else ""
        
        return ft.Container(
            content=ft.Column([
                # Project icon and name
                ft.Row([
                    ft.Icon(
                        ft.icons.FOLDER,
                        size=24,
                        color=ft.colors.BLUE_700
                    ),
                    ft.Text(
                        display_name,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.GREY_800,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        expand=True
                    )
                ], spacing=10),
                
                # Path info
                ft.Text(
                    dir_name,
                    size=12,
                    color=ft.colors.GREY_600,
                    overflow=ft.TextOverflow.ELLIPSIS
                ),
                ft.Text(
                    path,
                    size=10,
                    color=ft.colors.GREY_500,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    max_lines=2
                ),
                
                ft.Container(expand=True),
                
                # Action buttons
                ft.Row([
                    ft.TextButton(
                        text="Open",
                        icon=ft.icons.OPEN_IN_NEW,
                        on_click=lambda e, p=path, n=display_name: self._on_open_project_clicked(p, n)
                    ),
                    ft.IconButton(
                        icon=ft.icons.DELETE_OUTLINE,
                        icon_color=ft.colors.RED_400,
                        tooltip="Remove from recent",
                        on_click=lambda e, p=path: self._on_remove_project_clicked(p)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ], spacing=8),
            width=280,
            height=150,
            padding=15,
            bgcolor=self._get_card_bg_color(),
            border=ft.border.all(1, self._get_card_border_color()),
            border_radius=8,
            ink=True,
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
    
    def _on_back_clicked(self, e):
        """Handle back button click"""
        if self.on_back:
            self.on_back()
        else:
            print("Back to home clicked")
    
    def _on_new_project_clicked(self, e):
        """Handle new project button click"""
        print("New project clicked from recent projects view")
    
    def _on_clear_all_clicked(self, e):
        """Handle clear all button click"""
        if self.user_config:
            self.user_config.clear_recent_sites()
            print("All recent projects cleared")
    
    def _on_open_project_clicked(self, path: str, display_name: str):
        """Handle opening a project"""
        if self.on_open_project:
            self.on_open_project(path, display_name)
        else:
            print(f"Open project: {display_name} at {path}")
    
    def _on_remove_project_clicked(self, path: str):
        """Handle removing a project from recent list"""
        if self.user_config:
            self.user_config.remove_recent_site(path)
            print(f"Removed project from recent: {path}")
    
    def refresh(self):
        """Refresh the view content"""
        # This would rebuild the view with updated data
        return self.build()
