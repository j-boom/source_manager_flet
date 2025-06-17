import flet as ft
from ..base_view import BaseView
from typing import List, Dict, Any


class RecentProjectsView(BaseView):
    """Recent projects view - displays list of recent sites"""
    
    def __init__(self, page: ft.Page, theme_manager=None, user_config=None, on_open_project=None, on_back=None, on_navigate=None):
        super().__init__(page)
        self.theme_manager = theme_manager
        self.user_config = user_config
        self.on_open_project = on_open_project
        self.on_back = on_back
        self.on_navigate = on_navigate
    
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
                                icon_color=self._get_accent_color(),
                                on_click=self._on_back_clicked,
                                tooltip="Back to Home"
                            ),
                            ft.Text(
                                "Recent Projects",
                                size=28,
                                weight=ft.FontWeight.BOLD,
                                color=self._get_accent_color()
                            ),
                        ], alignment=ft.MainAxisAlignment.START),
                        ft.Text(
                            f"Your {len(recent_sites)} most recently accessed projects",
                            size=16,
                            color=self._get_secondary_text_color()
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
                    color=self._get_secondary_text_color()
                ),
                ft.Text(
                    "No Recent Projects",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=self._get_text_color()
                ),
                ft.Text(
                    "You haven't opened any projects yet. Start by creating a new project or importing existing sources.",
                    size=16,
                    color=self._get_secondary_text_color(),
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=30),
                ft.ElevatedButton(
                    text="Create New Project",
                    icon=ft.icons.ADD_CIRCLE_OUTLINE,
                    on_click=self._on_new_project_clicked,
                    style=ft.ButtonStyle(
                        color=ft.colors.WHITE,
                        bgcolor=self._get_accent_color(),
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
        """Build list of recent sites as vertical list"""
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
                
                # Recent sites vertical list
                ft.ListView(
                    controls=[
                        self._create_project_list_item(site) for site in recent_sites
                    ],
                    spacing=10,
                    expand=True
                )
            ]),
            expand=True
        )
    
    def _create_project_list_item(self, site: Dict[str, str]) -> ft.Container:
        """Create a list item for a recent project with editable display name"""
        display_name = site.get("display_name", "Unknown Project")
        path = site.get("path", "")
        
        # Extract directory name from path for additional context
        import os
        dir_name = os.path.basename(path) if path else ""
        
        # Create the display name text field for editing
        display_name_field = ft.TextField(
            value=display_name,
            text_size=16,
            border=ft.InputBorder.NONE,
            content_padding=ft.padding.symmetric(horizontal=5, vertical=0),
            on_submit=lambda e, p=path: self._on_display_name_updated(p, e.control.value),
            on_blur=lambda e, p=path: self._on_display_name_updated(p, e.control.value),
            text_style=ft.TextStyle(
                weight=ft.FontWeight.BOLD,
                color=self._get_text_color()
            ),
            cursor_color=self._get_accent_color(),
            selection_color=self._get_accent_color() + "40",  # Semi-transparent
            visible=False  # Start hidden
        )
        
        # Create the display name text (shown by default)
        display_name_text = ft.Text(
            display_name,
            size=16,
            weight=ft.FontWeight.BOLD,
            color=self._get_text_color(),
            overflow=ft.TextOverflow.ELLIPSIS,
            expand=True
        )
        
        return ft.Container(
            content=ft.Row([
                # Project icon
                ft.Icon(
                    ft.icons.FOLDER,
                    size=24,
                    color=self._get_accent_color()
                ),
                
                # Project info column
                ft.Column([
                    # Display name (either text or editable field)
                    ft.Stack([
                        display_name_text,
                        display_name_field
                    ]),
                    # Path info
                    ft.Row([
                        ft.Text(
                            dir_name,
                            size=12,
                            color=self._get_secondary_text_color(),
                            weight=ft.FontWeight.W_500
                        ),
                        ft.Text(" • ", size=12, color=self._get_secondary_text_color()),
                        ft.Text(
                            path,
                            size=12,
                            color=self._get_secondary_text_color(),
                            overflow=ft.TextOverflow.ELLIPSIS,
                            expand=True
                        )
                    ], spacing=0)
                ], spacing=4, expand=True),
                
                # Action buttons
                ft.Row([
                    ft.IconButton(
                        icon=ft.icons.EDIT,
                        icon_color=self._get_secondary_text_color(),
                        icon_size=18,
                        tooltip="Edit display name",
                        on_click=lambda e, txt=display_name_text, fld=display_name_field: self._toggle_edit_mode(txt, fld)
                    ),
                    ft.IconButton(
                        icon=ft.icons.OPEN_IN_NEW,
                        icon_color=self._get_accent_color(),
                        icon_size=18,
                        tooltip="Open project",
                        on_click=lambda e, p=path, n=display_name: self._on_open_project_clicked(p, n)
                    ),
                    ft.IconButton(
                        icon=ft.icons.DELETE_OUTLINE,
                        icon_color=ft.colors.RED_400,
                        icon_size=18,
                        tooltip="Remove from recent",
                        on_click=lambda e, p=path: self._on_remove_project_clicked(p)
                    )
                ], spacing=0)
            ], spacing=8, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=15, vertical=12),
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
    
    def _get_text_color(self) -> str:
        """Get primary text color based on theme"""
        if self.theme_manager:
            current_mode = "dark" if self.page.theme_mode == ft.ThemeMode.DARK else "light"
            return self.theme_manager.get_text_color(current_mode)
        # Fallback
        if self.page.theme_mode == ft.ThemeMode.DARK:
            return ft.colors.WHITE
        return ft.colors.GREY_800
    
    def _get_secondary_text_color(self) -> str:
        """Get secondary text color based on theme"""
        if self.theme_manager:
            current_mode = "dark" if self.page.theme_mode == ft.ThemeMode.DARK else "light"
            return self.theme_manager.get_secondary_text_color(current_mode)
        # Fallback
        if self.page.theme_mode == ft.ThemeMode.DARK:
            return ft.colors.GREY_400
        return ft.colors.GREY_600
    
    def _get_accent_color(self) -> str:
        """Get accent color based on theme"""
        if self.theme_manager:
            return self.theme_manager.get_accent_color()
        # Fallback
        return ft.colors.BLUE_700
    
    def _toggle_edit_mode(self, text_control: ft.Text, field_control: ft.TextField):
        """Toggle between display and edit mode for project name"""
        text_control.visible = not text_control.visible
        field_control.visible = not field_control.visible
        if field_control.visible:
            field_control.focus()
        self.page.update()
    
    def _on_display_name_updated(self, path: str, new_display_name: str):
        """Handle display name update"""
        if self.user_config and new_display_name.strip():
            old_display_name = None
            # Find the old display name for comparison
            recent_sites = self.user_config.get_recent_sites()
            for site in recent_sites:
                if site["path"] == path:
                    old_display_name = site.get("display_name", "")
                    break
            
            # Only update if the name actually changed
            if old_display_name != new_display_name.strip():
                self.user_config.update_recent_site_display_name(path, new_display_name.strip())
                print(f"Updated display name for {path} to: {new_display_name.strip()}")
                # Call the controller to refresh the view
                if hasattr(self, 'on_navigate') and self.on_navigate:
                    self.on_navigate("recent_projects")  # This will rebuild the view
    
    def refresh_theme(self):
        """Refresh the view when theme changes"""
        if hasattr(self, 'page') and self.page:
            self.page.update()
    
    def _on_back_clicked(self, e):
        """Handle back button click"""
        if self.on_back:
            self.on_back()
        else:
            print("Back to home clicked")
    
    def _on_new_project_clicked(self, e):
        """Handle new project button click"""
        if self.on_navigate:
            self.on_navigate("new_project")
        else:
            print("New project clicked from recent projects view")
    
    def _on_clear_all_clicked(self, e):
        """Handle clear all button click"""
        if self.user_config:
            self.user_config.clear_recent_sites()
            print("All recent projects cleared")
            # Call the controller to refresh the view
            if hasattr(self, 'on_navigate') and self.on_navigate:
                self.on_navigate("recent_projects")  # This will rebuild the view
    
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
            # Call the controller to refresh the view
            if hasattr(self, 'on_navigate') and self.on_navigate:
                self.on_navigate("recent_projects")  # This will rebuild the view
    
    def refresh(self):
        """Refresh the view content"""
        # This would rebuild the view with updated data
        return self.build()
