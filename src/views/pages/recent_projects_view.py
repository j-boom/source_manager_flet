import flet as ft
from ..base_view import BaseView
from models.user_config_models import RecentProject
from typing import List
import logging

# --- FIX: Import the new component ---
from ..components.cards.recent_project_card import RecentProjectCard


class RecentProjectsView(BaseView):
    """A view to display and manage recently opened projects."""

    def __init__(self, page: ft.Page, controller):
        super().__init__(page, controller)
        self.user_config_manager = self.controller.user_config_manager
        self.logger = logging.getLogger(__name__)

    def build(self) -> ft.Control:
        """Builds the UI for the recent projects view."""
        recent_projects = self.user_config_manager.get_recent_projects()

        return ft.Container(
            content=ft.Column(
                controls=[
                    self._build_header(len(recent_projects)),
                    self._build_content(recent_projects),
                ],
                expand=True,
                spacing=0,
            ),
            padding=ft.padding.all(20),
            expand=True,
        )
        # --- END FIX ---

    def _build_header(self, count: int) -> ft.Container:
        """Builds the header section of the view."""
        return ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.icons.ARROW_BACK,
                        on_click=lambda e: self.controller.navigate_to("home"),
                        tooltip="Back to Home",
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                "Recent Projects",
                                theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                            ),
                            ft.Text(
                                f"Your {count} most recently accessed projects",
                                color=ft.colors.ON_SURFACE_VARIANT,
                            ),
                        ]
                    ),
                ],
                spacing=20,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            padding=ft.padding.only(bottom=20),
            border=ft.border.only(bottom=ft.BorderSide(1, ft.colors.OUTLINE_VARIANT)),
        )

    def _build_content(self, recent_projects: List[RecentProject]) -> ft.Control:
        """Builds the main content area, showing either the list or an empty state."""
        if not recent_projects:
            return self.show_empty_state(
                message="You haven't opened any projects yet.",
                icon=ft.icons.HISTORY,
                action_text="Browse for a Project",
                on_action=lambda e: self.controller.navigate_to("new_project"),
            )
        else:
            return ft.Column(
                controls=[
                    ft.Row(
                        [
                            ft.Container(expand=True),  # Spacer
                            ft.OutlinedButton(
                                text="Clear All",
                                icon=ft.icons.DELETE_SWEEP_OUTLINED,
                                on_click=self._on_clear_all_clicked,
                                style=ft.ButtonStyle(color=self.colors.error),
                            ),
                        ]
                    ),
                    # --- FIX: Use the new RecentProjectCard component in a loop ---
                    ft.ListView(
                        controls=[
                            RecentProjectCard(
                                project=project, controller=self.controller
                            )
                            for project in recent_projects
                        ],
                        spacing=10,
                        expand=True,
                        padding=ft.padding.only(top=20),
                    ),
                ],
                expand=True,
                spacing=20,
            )

    # --- The _create_project_list_item method has been removed ---

    def _on_clear_all_clicked(self, e):
        """Handles the clear all button click by delegating to the controller."""
        self.controller.navigation_controller.clear_recent_projects()
