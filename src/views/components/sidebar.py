"""
Sidebar Component (Refactored)

A self-contained, theme-aware NavigationRail for the main application view.
"""

import flet as ft
from typing import Callable, List, Dict, Any


class Sidebar(ft.NavigationRail):
    """
    A custom NavigationRail that builds its destinations dynamically from config.
    It is initialized without theme-dependent properties, which are applied later.
    """

    def __init__(
        self, pages_config: List[Dict[str, Any]], on_change: Callable[[str], None]
    ):
        """
        Initializes the Sidebar component.

        Args:
            pages_config: A list of dictionaries defining the pages.
            on_change: The callback function to execute when the selection changes.
        """


        # --- Build destinations and set the change handler ---
        self.on_change_handler = on_change
        self.destinations = self._build_destinations(pages_config)
        self._page_names = [p.get("name", "") for p in pages_config]
        
        super().__init__(
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            group_alignment=-0.9,
            destinations=self.destinations,
            on_change=self._handle_change,
        )

    def _build_destinations(
        self, pages_config: List[Dict[str, Any]]
    ) -> List[ft.NavigationRailDestination]:
        """Creates the destination items from the provided configuration."""
        destinations = []
        for page_config in pages_config:
            destinations.append(
                ft.NavigationRailDestination(
                    icon=page_config.get("icon"),
                    selected_icon=page_config.get("selected_icon"),
                    label=page_config.get("label"),
                )
            )
        return destinations

    def _handle_change(self, e: ft.ControlEvent):
        """Internal handler to map the selected index to a page name before calling the callback."""
        selected_index = e.control.selected_index
        if 0 <= selected_index < len(self._page_names):
            page_name = self._page_names[selected_index]
            self.on_change_handler(page_name)

    def update_selection(self, page_name: str):
        """Programmatically updates the selected navigation item based on the page name."""
        if page_name in self._page_names:
            try:
                self.selected_index = self._page_names.index(page_name)
            except ValueError:
                self.selected_index = None  # Deselect if not found
        else:
            self.selected_index = None  # Deselect if page name is not in the list
