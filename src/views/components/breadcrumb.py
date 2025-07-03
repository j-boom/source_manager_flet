"""
Breadcrumb Component

A reusable component for displaying and handling navigation in a breadcrumb trail.
"""
from typing import List, Callable
import flet as ft

class Breadcrumb(ft.Row):
    """
    A custom breadcrumb component that builds itself dynamically from a list of path parts.
    """
    def __init__(self, crumbs: List[str], on_crumb_click: Callable[[int], None]):
        """
        Initializes the Breadcrumb component.

        Args:
            crumbs: The initial list of strings representing the path parts.
            on_crumb_click: A callback function that is triggered when a breadcrumb
                            part is clicked. It receives the index of the clicked part.
        """
        super().__init__(spacing=5, visible=False)
        self.crumbs = crumbs
        self.on_crumb_click = on_crumb_click
        self._build()

    def _build(self):
        """Builds or rebuilds the breadcrumb controls."""
        self.controls.clear()
        for i, part in enumerate(self.crumbs):
            if i > 0:
                self.controls.append(ft.Text(" / ", color=ft.colors.GREY_500))

            self.controls.append(
                ft.TextButton(
                    text=part,
                    on_click=lambda e, idx=i: self.on_crumb_click(idx),
                    style=ft.ButtonStyle(padding=0)
                )
            )
        self.visible = len(self.crumbs) > 0

    def update_crumbs(self, new_crumbs: List[str]):
        """
        Updates the breadcrumb trail with a new list of path parts.

        Args:
            new_crumbs: The new list of strings for the breadcrumb trail.
        """
        self.crumbs = new_crumbs
        self._build()
        # The view that contains this component is responsible for calling page.update()
