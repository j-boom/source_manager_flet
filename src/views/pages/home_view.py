"""
Home View (Refactored)

The main landing page for the application, providing quick actions and a welcome message.
This view has been refactored to align with the application's MVC-like architecture.
"""

import flet as ft
from src.views.base_view import BaseView


class HomeView(BaseView):
    """The Home page view."""

    def __init__(self, page: ft.Page, controller):
        """
        Initializes the HomeView.

        Args:
            page: The Flet Page object.
            controller: The main AppController instance.
        """
        super().__init__(page, controller)

    def build(self) -> ft.Control:
        """Builds the UI for the home page content."""
        # The view now simply uses the 'self.colors' property from BaseView.
        # It's guaranteed to be safe and always return a valid color object.
        colors = self.colors

        # The root control is a Container to handle padding and alignment.
        return ft.Container(
            content=ft.Column(
                [
                    # Welcome Section
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "Welcome to Source Manager",
                                    theme_style=ft.TextThemeStyle.DISPLAY_SMALL,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.colors.INVERSE_PRIMARY,
                                ),
                                ft.Text(
                                    "Manage your source code projects efficiently",
                                    theme_style=ft.TextThemeStyle.TITLE_LARGE,
                                    color=ft.colors.SECONDARY,
                                ),
                            ],
                            spacing=5,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.only(bottom=40, top=20),
                    ),
                    # Quick Actions Cards
                    ft.Text(
                        "Quick Actions", theme_style=ft.TextThemeStyle.HEADLINE_SMALL
                    ),
                    ft.Row(
                        [
                            self._create_action_card(
                                "New Project",
                                "Create a new project or folder.",
                                ft.icons.ADD_CIRCLE_OUTLINE,
                                lambda e: self.controller.navigate_to("new_project"),
                            ),
                            self._create_action_card(
                                "Recent Projects",
                                "View and open recent projects.",
                                ft.icons.HISTORY,
                                lambda e: self.controller.navigate_to(
                                    "recent_projects"
                                ),
                            ),
                            self._create_action_card(
                                "Sources",
                                "Search for Sources to add, or create a new one.",
                                ft.icons.SOURCE_OUTLINED,
                                lambda e: self.controller.navigate_to("sources"),
                            ),
                        ],
                        # Center the action cards
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=20,
                    ),
                ],
                spacing=20,
                scroll=ft.ScrollMode.ADAPTIVE,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.all(30),
            expand=True,
        )

    def _create_action_card(
        self, title: str, description: str, icon: str, on_click
    ) -> ft.Container:
        """Helper method to create a consistent action card."""
        colors = self.colors

        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=40, color=ft.colors.ON_SECONDARY_CONTAINER),
                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SECONDARY_CONTAINER),
                    ft.Text(
                        description,
                        size=12,
                        color=ft.colors.ON_SECONDARY_CONTAINER,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            width=220,
            height=180,
            padding=20,
            bgcolor=ft.colors.SECONDARY_CONTAINER,
            border_radius=ft.border_radius.all(12),
            ink=True,
            on_click=on_click,
        )
