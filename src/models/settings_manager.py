import flet as ft
import sys
from pathlib import Path
from typing import Callable, Optional
from .theme_manager import ThemeManager
from .user_config import UserConfigManager

# Import dialog class with lazy loading to avoid circular imports
def get_edit_display_name_dialog():
    """Lazy import to avoid circular imports"""
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    from src.views.components.dialogs.edit_display_name_dialog import EditDisplayNameDialog
    return EditDisplayNameDialog


class SettingsManager:
    """Manages application settings and preferences"""
    
    def __init__(self, user_config: UserConfigManager, theme_manager: ThemeManager):
        self.user_config = user_config
        self.theme_manager = theme_manager
        self.theme_change_callback: Optional[Callable[[str], None]] = None
        self.color_change_callback: Optional[Callable[[str], None]] = None
        self.display_name_change_callback: Optional[Callable[[], None]] = None
        self.current_page: Optional[ft.Page] = None
        self.current_settings_content: Optional[ft.Container] = None
    
    def set_theme_change_callback(self, callback: Callable[[str], None]):
        """Set callback for theme mode changes"""
        self.theme_change_callback = callback
    
    def set_color_change_callback(self, callback: Callable[[str], None]):
        """Set callback for color theme changes"""
        self.color_change_callback = callback
    
    def set_display_name_change_callback(self, callback: Callable[[], None]):
        """Set callback for display name changes"""
        self.display_name_change_callback = callback
    
    def toggle_theme_mode(self, page: ft.Page):
        """Toggle between light and dark theme"""
        current_mode = "dark" if page.theme_mode == ft.ThemeMode.DARK else "light"
        new_mode = "light" if current_mode == "dark" else "dark"
        
        # Apply new theme
        self.theme_manager.apply_theme_to_page(page, new_mode)
        
        # Save to config
        self.user_config.save_theme_mode(new_mode)
        
        # Notify callback
        if self.theme_change_callback:
            self.theme_change_callback(new_mode)
        
        page.update()
    
    def change_theme_color(self, color_name: str):
        """Change the application theme color"""
        if self.theme_manager.is_valid_color(color_name):
            # Save to config
            self.user_config.save_theme_color(color_name)
            
            # Update theme manager
            self.theme_manager.set_color(color_name)
            
            # Notify callback
            if self.color_change_callback:
                self.color_change_callback(color_name)
    
    def get_current_theme_mode(self) -> str:
        """Get current theme mode"""
        return self.user_config.get_theme_mode()
    
    def get_current_theme_color(self) -> str:
        """Get current theme color"""
        return self.user_config.get_theme_color()
    
    def edit_display_name(self):
        """Show dialog to edit display name"""
        if not self.current_page:
            return
            
        current_name = self.user_config.get_display_name() or ""
        
        def on_name_saved(new_name: str):
            self.user_config.save_display_name(new_name)
            if self.display_name_change_callback:
                self.display_name_change_callback()
            # Refresh the settings view to show the updated name
            self._refresh_settings_view()
        
        EditDisplayNameDialog = get_edit_display_name_dialog()
        dialog = EditDisplayNameDialog(self.current_page, current_name, on_name_saved)
        dialog.show()
    
    def _refresh_settings_view(self):
        """Refresh the current settings view"""
        if self.current_page and self.current_settings_content:
            updated_content = self.create_settings_view(self.current_page)
            self.current_settings_content.content = updated_content.content
            self.current_page.update()
    
    def apply_saved_settings(self, page: ft.Page):
        """Apply all saved settings to the page"""
        # Apply theme mode
        theme_mode = self.get_current_theme_mode()
        self.theme_manager.apply_theme_to_page(page, theme_mode)
        
        # Set page title with username
        page.title = f"Source Manager - {self.user_config.get_username()}"
        page.padding = 0
        
        # Update theme manager state
        self.theme_manager.set_mode(theme_mode)
        self.theme_manager.set_color(self.get_current_theme_color())
    
    def create_settings_view(self, page: ft.Page) -> ft.Container:
        """Create the settings view content"""
        self.current_page = page  # Store page reference for dialogs
        
        theme_colors = self.theme_manager.get_available_colors()
        current_color = self.get_current_theme_color()
        
        # Create color theme selection buttons
        color_buttons = []
        for color_name, color_data in theme_colors.items():
            is_selected = color_name == current_color
            
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
                on_click=lambda e, color=color_name: self.change_theme_color(color),
                ink=True,
                border_radius=8,
            )
            color_buttons.append(button)
        
        # Create settings content
        settings_content = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Settings",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=theme_colors[current_color]["primary"]
                ),
                ft.Divider(),
                
                # Personal Settings Section
                ft.Text(
                    "Personal Settings",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.GREY_800
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.PERSON),
                    title=ft.Text("Display Name"),
                    subtitle=ft.Text(self.user_config.get_display_name() or "Not set"),
                    trailing=ft.IconButton(
                        icon=ft.icons.EDIT,
                        tooltip="Edit display name",
                        on_click=lambda e: self.edit_display_name()
                    )
                ),
                
                ft.Container(height=20),
                
                # Theme Mode Setting
                ft.Text(
                    "Appearance",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.GREY_800
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.BRIGHTNESS_6),
                    title=ft.Text("Theme Mode"),
                    subtitle=ft.Text("Choose light or dark theme"),
                    trailing=ft.Switch(
                        value=page.theme_mode == ft.ThemeMode.DARK,
                        on_change=lambda e: self.toggle_theme_mode(page)
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
                ft.ListTile(
                    leading=ft.Icon(ft.icons.COMPUTER),
                    title=ft.Text("System User"),
                    subtitle=ft.Text(self.user_config.get_username()),
                ),
            ]),
            padding=20,
            expand=True,
        )
        
        self.current_settings_content = settings_content  # Store reference for refreshing
        return settings_content
