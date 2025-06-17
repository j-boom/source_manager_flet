import flet as ft
from abc import ABC, abstractmethod
from typing import Optional


class BaseView(ABC):
    """Base class for all views in the application"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self._content: Optional[ft.Control] = None
    
    @abstractmethod
    def build(self) -> ft.Control:
        """Build and return the view's content"""
        pass
    
    def get_content(self) -> ft.Control:
        """Get the view's content, building it if necessary"""
        if self._content is None:
            self._content = self.build()
        return self._content
    
    def refresh(self):
        """Refresh the view by rebuilding its content"""
        self._content = None
        return self.get_content()
    
    def show_loading(self, message: str = "Loading...") -> ft.Control:
        """Show a loading indicator"""
        return ft.Container(
            content=ft.Column([
                ft.ProgressRing(),
                ft.Text(message, size=16, color=ft.colors.GREY_600)
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20),
            alignment=ft.alignment.center,
            expand=True
        )
    
    def show_error(self, message: str, details: str = "") -> ft.Control:
        """Show an error message"""
        content = [
            ft.Icon(ft.icons.ERROR, color=ft.colors.RED, size=48),
            ft.Text("Error", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.RED),
            ft.Text(message, size=16, color=ft.colors.GREY_700),
        ]
        
        if details:
            content.append(
                ft.Text(details, size=12, color=ft.colors.GREY_500)
            )
        
        return ft.Container(
            content=ft.Column(
                content,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            alignment=ft.alignment.center,
            expand=True,
            padding=20
        )
    
    def show_empty_state(self, 
                        message: str = "No data available", 
                        icon: str = ft.icons.INBOX,
                        action_text: str = "",
                        on_action=None) -> ft.Control:
        """Show an empty state message"""
        content = [
            ft.Icon(icon, color=ft.colors.GREY_400, size=64),
            ft.Text(message, size=18, color=ft.colors.GREY_600),
        ]
        
        if action_text and on_action:
            content.append(
                ft.ElevatedButton(
                    text=action_text,
                    on_click=on_action,
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.BLUE_700,
                        color=ft.colors.WHITE
                    )
                )
            )
        
        return ft.Container(
            content=ft.Column(
                content,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            ),
            alignment=ft.alignment.center,
            expand=True,
            padding=40
        )
