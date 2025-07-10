"""
App Floating Action Button Component

A reusable floating action button component that can be used across different views.
"""

import flet as ft
from typing import Callable, Optional


class AppFAB:
    """
    A reusable floating action button component.
    """
    
    def __init__(
        self,
        icon: str = ft.icons.ADD,
        tooltip: str = "Add",
        on_click: Optional[Callable] = None,
        bgcolor: Optional[str] = None,
        foreground_color: Optional[str] = None,
    ):
        """
        Initialize the FAB component.
        
        Args:
            icon: The icon to display in the FAB
            tooltip: Tooltip text for the FAB
            on_click: Callback function when FAB is clicked
            bgcolor: Background color of the FAB
            foreground_color: Foreground/icon color of the FAB
        """
        self.icon = icon
        self.tooltip = tooltip
        self.on_click = on_click
        self.bgcolor = bgcolor
        self.foreground_color = foreground_color
    
    def build(self) -> ft.FloatingActionButton:
        """
        Build and return the FloatingActionButton control.
        
        Returns:
            A configured FloatingActionButton control
        """
        return ft.FloatingActionButton(
            icon=self.icon,
            tooltip=self.tooltip,
            on_click=self.on_click,
            bgcolor=self.bgcolor,
            foreground_color=self.foreground_color,
        )
    
    @staticmethod
    def create_add_source_fab(controller) -> ft.FloatingActionButton:
        """
        Create a pre-configured FAB for adding sources.
        
        Args:
            controller: The app controller instance
            
        Returns:
            A FloatingActionButton configured for adding sources
        """
        fab = AppFAB(
            icon=ft.icons.ADD,
            tooltip="Add Source",
            on_click=lambda e: controller.show_create_source_dialog(),
            bgcolor=ft.colors.PRIMARY,
            foreground_color=ft.colors.ON_PRIMARY,
        )
        return fab.build()
    
    @staticmethod
    def create_custom_fab(
        icon: str,
        tooltip: str,
        on_click: Callable,
        bgcolor: Optional[str] = None,
        foreground_color: Optional[str] = None,
    ) -> ft.FloatingActionButton:
        """
        Create a custom FAB with specified parameters.
        
        Args:
            icon: The icon to display
            tooltip: Tooltip text
            on_click: Click handler
            bgcolor: Background color
            foreground_color: Foreground color
            
        Returns:
            A configured FloatingActionButton
        """
        fab = AppFAB(
            icon=icon,
            tooltip=tooltip,
            on_click=on_click,
            bgcolor=bgcolor,
            foreground_color=foreground_color,
        )
        return fab.build()
