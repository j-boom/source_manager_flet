"""
Base tab class for New Project View tabs
"""

import flet as ft
from typing import Optional, Callable, Any
from abc import ABC, abstractmethod


class BaseTab(ABC):
    """Base class for tabs in the New Project View"""
    
    def __init__(self, page: ft.Page, theme_manager=None, **kwargs):
        self.page = page
        self.theme_manager = theme_manager
        self.tab_content: Optional[ft.Control] = None
        
        # Store any additional kwargs for subclasses
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @abstractmethod
    def build(self) -> ft.Control:
        """Build and return the tab content"""
        pass
    
    @abstractmethod
    def get_tab_text(self) -> str:
        """Return the text for this tab"""
        pass
    
    def get_tab_icon(self) -> Optional[str]:
        """Return the icon for this tab (optional)"""
        return None
    
    def on_tab_selected(self):
        """Called when this tab is selected"""
        pass
    
    def on_tab_deselected(self):
        """Called when this tab is deselected"""
        pass
    
    def refresh(self):
        """Refresh the tab content"""
        if hasattr(self, 'build'):
            self.tab_content = self.build()
    
    def _get_theme_color(self) -> str:
        """Get the theme primary color"""
        if self.theme_manager:
            return self.theme_manager.get_accent_color()
        return ft.colors.BLUE_600
    
    def _get_icon_color(self) -> str:
        """Get appropriate icon color for current theme"""
        if self.page.theme_mode == ft.ThemeMode.DARK:
            return ft.colors.GREY_400
        else:
            return ft.colors.GREY_600


class TabManager:
    """Manages tab switching and state for the New Project View"""
    
    def __init__(self, page: ft.Page, theme_manager=None):
        self.page = page
        self.theme_manager = theme_manager
        self.tabs: list[BaseTab] = []
        self.current_tab_index = 0
        self.tabs_container: Optional[ft.Control] = None
        self.content_container: Optional[ft.Container] = None
    
    def add_tab(self, tab: BaseTab):
        """Add a tab to the manager"""
        self.tabs.append(tab)
    
    def build_tabs(self) -> ft.Control:
        """Build the tab bar"""
        tab_buttons = []
        
        for i, tab in enumerate(self.tabs):
            # Theme-aware tab styling
            if i == self.current_tab_index:
                # Active tab
                if self.page.theme_mode == ft.ThemeMode.DARK:
                    bg_color = ft.colors.GREY_700
                    text_color = ft.colors.WHITE
                else:
                    bg_color = ft.colors.BLUE_50
                    text_color = ft.colors.BLUE_700
            else:
                # Inactive tab
                if self.page.theme_mode == ft.ThemeMode.DARK:
                    bg_color = ft.colors.GREY_800
                    text_color = ft.colors.GREY_400
                else:
                    bg_color = ft.colors.GREY_100
                    text_color = ft.colors.GREY_700
            
            tab_button = ft.Container(
                content=ft.Row([
                    ft.Icon(tab.get_tab_icon(), size=16, color=text_color) if tab.get_tab_icon() else ft.Container(),
                    ft.Text(tab.get_tab_text(), color=text_color, weight=ft.FontWeight.BOLD if i == self.current_tab_index else ft.FontWeight.NORMAL)
                ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
                bgcolor=bg_color,
                border_radius=ft.border_radius.only(top_left=8, top_right=8),
                on_click=lambda e, index=i: self.switch_to_tab(index),
                ink=True
            )
            tab_buttons.append(tab_button)
        
        self.tabs_container = ft.Row(tab_buttons, spacing=2)
        return self.tabs_container
    
    def build_content(self) -> ft.Control:
        """Build the content area for the current tab"""
        if not self.tabs or self.current_tab_index >= len(self.tabs):
            return ft.Container()
        
        current_tab = self.tabs[self.current_tab_index]
        tab_content = current_tab.build()
        
        # Theme-aware content container
        if self.page.theme_mode == ft.ThemeMode.DARK:
            content_bg = ft.colors.GREY_900
            border_color = ft.colors.GREY_700
        else:
            content_bg = ft.colors.WHITE
            border_color = ft.colors.GREY_300
        
        self.content_container = ft.Container(
            content=tab_content,
            bgcolor=content_bg,
            border=ft.border.all(1, border_color),
            border_radius=ft.border_radius.only(
                top_right=8, bottom_left=8, bottom_right=8
            ),
            padding=ft.padding.all(20),
            expand=True
        )
        
        return self.content_container
    
    def switch_to_tab(self, index: int):
        """Switch to the specified tab"""
        if index < 0 or index >= len(self.tabs):
            return
        
        # Deselect current tab
        if self.current_tab_index < len(self.tabs):
            self.tabs[self.current_tab_index].on_tab_deselected()
        
        # Switch to new tab
        self.current_tab_index = index
        self.tabs[self.current_tab_index].on_tab_selected()
        
        # Rebuild UI
        self._refresh_ui()
    
    def _refresh_ui(self):
        """Refresh the tab UI"""
        if self.tabs_container and self.content_container:
            # Rebuild tabs
            new_tabs = self.build_tabs()
            if hasattr(self.tabs_container, 'controls'):
                self.tabs_container.controls = new_tabs.controls
            
            # Rebuild content
            new_content = self.build_content()
            if hasattr(self.content_container, 'content'):
                self.content_container.content = new_content.content
                self.content_container.bgcolor = new_content.bgcolor
                self.content_container.border = new_content.border
            
            self.page.update()
    
    def get_current_tab(self) -> Optional[BaseTab]:
        """Get the currently selected tab"""
        if 0 <= self.current_tab_index < len(self.tabs):
            return self.tabs[self.current_tab_index]
        return None
