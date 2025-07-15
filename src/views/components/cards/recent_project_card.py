import flet as ft
from pathlib import Path
from models.user_config_models import RecentProject
# Assuming you have a BaseCard component as discussed previously
from .base_card import BaseCard 

class RecentProjectCard(BaseCard):
    """
    A self-contained card component to display a single recent project.
    It uses a robust Row/Column layout to prevent text wrapping issues.
    """
    def __init__(self, project: RecentProject, controller):
        """
        Initializes the card for a specific project.

        Args:
            project: The RecentProject data object to display.
            controller: The main AppController instance.
        """
        self.project = project
        super().__init__(controller=controller)
        # The on_click is now handled by the inner Container to ensure the whole area is clickable
        
    def _build_content(self) -> ft.Container:
        """Builds the card's content using a robust Row/Column layout."""
        
        # --- FIX: Use a Column for title/subtitle that can expand ---
        # This is the core of the fix. This Column will take up all available
        # horizontal space between the leading icon and the trailing buttons.
        text_content = ft.Column(
            [
                ft.Text(self.project.display_name, weight=ft.FontWeight.BOLD, size=14),
                ft.Text(self.project.path, overflow=ft.TextOverflow.ELLIPSIS, italic=True, size=12, color=ft.colors.ON_SURFACE_VARIANT),
            ],
            spacing=2,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        )

        action_buttons = ft.Row(
            [
                ft.IconButton(
                    icon=ft.icons.OPEN_IN_NEW,
                    tooltip="Open project",
                    on_click=self._handle_open_project
                ),
                ft.IconButton(
                    icon=ft.icons.DELETE_OUTLINE,
                    icon_color=ft.colors.ERROR,
                    tooltip="Remove from recent list",
                    on_click=self._handle_remove_project
                )
            ]
        )

        # The main Row that holds all parts of the card
        content_row = ft.Row(
            [
                ft.Icon(ft.icons.FOLDER_OPEN_OUTLINED, color=ft.colors.PRIMARY, size=28),
                text_content,  # The expanding text content
                action_buttons, # The fixed-width buttons
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
        )

        # Wrap everything in a clickable container with padding
        return ft.Container(
            content=content_row,
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            on_click=self._handle_open_project,
            border_radius=ft.border_radius.all(8),
            ink=True,
        )

    def _handle_open_project(self, e):
        """Callback to open the project via the controller."""
        self.controller.project_controller.open_project(Path(self.project.path))

    def _handle_remove_project(self, e):
        """
        Callback to remove the project from the recent list.
        This stops the event from bubbling up to the card's main on_click handler.
        """
        # This is a small but important detail: if we don't handle the event,
        # the click will "pass through" to the parent card and trigger the open_project
        # action. By calling update(), we consume the event here.
        if e.control.page:
            e.control.page.update()
        
        self.controller.navigation_controller.remove_recent_project(self.project.path)
