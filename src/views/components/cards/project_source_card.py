from typing import List
import flet as ft
from .base_card import BaseCard
from src.models.source_models import SourceRecord
from src.models.project_models import ProjectSourceLink


class ProjectSourceCard(BaseCard):
    """
    A self-contained card component to display a single source that is part
    of the current project. It inherits from BaseCard for consistent styling.
    """

    def __init__(self, source: SourceRecord, link: ProjectSourceLink, controller, used_on_slides: List[str]):
        """
        Initializes the card.

        Args:
            source: The master SourceRecord object.
            link: The ProjectSourceLink object that connects the source to the project.
            controller: The main AppController instance.
        """
        self.source = source
        self.link = link
        self.used_on_slides = used_on_slides or []
        super().__init__(controller=controller)

    def _build_content(self) -> ft.Container:
        """Builds the card's content using a robust Row/Column layout."""
        # --- Section to display slide usage ---
        usage_section = ft.Column(spacing=2, visible=bool(self.used_on_slides))
        if self.used_on_slides:
            usage_section.controls.append(
                ft.Text("Used on:", weight=ft.FontWeight.BOLD, size=11, color=ft.Colors.ON_SECONDARY_CONTAINER)
            )
            for slide_title in self.used_on_slides:
                usage_section.controls.append(
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.SLIDESHOW_OUTLINED, size=12, opacity=0.7),
                            ft.Text(f"{slide_title}", size=11, italic=True, color=ft.Colors.ON_SECONDARY_CONTAINER),
                        ],
                        spacing=5,
                    )
                )
        text_content = ft.Column(
            [
                ft.Text(
                    self.source.get_title(),
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.ON_SECONDARY_CONTAINER,
                ),
                ft.Text(
                    f"Notes: {self.link.metadata.get('usage_notes') or 'N/A'}",
                    overflow=ft.TextOverflow.ELLIPSIS,
                    italic=True,
                    size=12,
                    color=ft.Colors.ON_SECONDARY_CONTAINER,
                ),
                ft.Text(
                    f"Declassify: {self.link.metadata.get('declassify_info') or 'N/A'}",
                    overflow=ft.TextOverflow.ELLIPSIS,
                    italic=True,
                    size=12,
                    color=ft.Colors.ON_SECONDARY_CONTAINER,
                ),
            ],
            spacing=2,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        )

        action_buttons = ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.EDIT_DOCUMENT,
                    tooltip="View / Edit Source Details",
                    on_click=self._handle_view_edit_source,
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color=ft.Colors.ERROR,
                    tooltip="Remove from project",
                    on_click=self._handle_remove_from_project,
                ),
            ]
        )

        content_row = ft.Row(
            [
                ft.Icon(ft.Icons.DRAG_HANDLE, color=ft.Colors.PRIMARY, size=28),
                text_content,
                action_buttons,
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
        )

        return ft.Container(
            content=content_row,
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            bgcolor=ft.Colors.SECONDARY_CONTAINER,
        )

    def _handle_view_edit_source(self, e):
        """Handles the view/edit source action."""
        if hasattr(self.controller.dialog_controller, "open_source_editor_dialog"):
            self.controller.dialog_controller.open_source_editor_dialog(self.source.id)
        if e.control.page:
            e.control.page.update()

    def _handle_remove_from_project(self, e):
        """Handles removing the source from the project via the controller."""
        self.logger.info(f"Removing source '{self.source.id}' from project.")
        if hasattr(self.controller.project_controller, "remove_source_from_project"):
            self.controller.project_controller.remove_source_from_project(self.source.id)
        if e.control.page:
            e.control.page.update()