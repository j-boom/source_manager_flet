"""
Base View (Simplified)

A simple base class for all page views in the application. It provides
common helper methods and a safe 'colors' property for consistent theming.
"""
import flet as ft

class BaseView:
    """Base class for all views in the application."""
    
    def __init__(self, page: ft.Page, controller):
        self.page = page
        self.controller = controller

    @property
    def colors(self) -> ft.ColorScheme:
        """
        A safe property to access the application's color scheme.
        It returns the current page's color scheme if it exists, otherwise,
        it returns a failsafe default ColorScheme from the ThemeManager.
        """
        if self.page.theme and self.page.theme.color_scheme:
            return self.page.theme.color_scheme
        
        # This is now much simpler. It just asks the ThemeManager for a default
        # ColorScheme object, removing all complex logic from the view.
        return self.controller.theme_manager.get_default_color_scheme()

    def build(self) -> ft.Control:
        """
        Builds and returns the view's root Flet control.
        This method must be implemented by all subclasses.
        """
        raise NotImplementedError("Each view must implement the build method.")

    def show_error(self, message: str, details: str = "") -> ft.Control:
        """Returns a standardized error message control using the safe colors property."""
        colors = self.colors # This is now guaranteed to be a valid ColorScheme
        
        content = [
            ft.Icon(ft.icons.ERROR, color=colors.error, size=48),
            ft.Text("Error", size=20, weight=ft.FontWeight.BOLD, color=colors.error),
            ft.Text(message, size=16, color=ft.colors.ON_SURFACE_VARIANT),
        ]
        
        if details:
            content.append(ft.Text(details, size=12, color=ft.colors.ON_SURFACE_VARIANT))
        
        return ft.Container(
            content=ft.Column(content, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            alignment=ft.alignment.center,
            expand=True,
            padding=20,
            bgcolor=colors.error_container,
            border_radius=8
        )
    
    def show_empty_state(self, message: str, icon: str = ft.icons.INBOX, action_text: str = "", on_action=None) -> ft.Control:
        """Returns a standardized empty state control using the safe colors property."""
        colors = self.colors # This is now guaranteed to be a valid ColorScheme

        content = [
            ft.Icon(icon, color=ft.colors.ON_SURFACE_VARIANT, size=64),
            ft.Text(message, size=18, color=ft.colors.ON_SURFACE_VARIANT),
        ]
        
        if action_text and on_action:
            content.append(
                ft.ElevatedButton(
                    text=action_text,
                    on_click=on_action,
                    style=ft.ButtonStyle(
                        bgcolor=colors.primary,
                        color=colors.on_primary
                    )
                )
            )
        
        return ft.Container(
            content=ft.Column(content, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
            alignment=ft.alignment.center,
            expand=True,
            padding=40
        )

    def update_view(self):
        """Refreshes the view by calling page.update(). Subclasses can override for specific logic."""
        if self.page:
            self.page.update()
