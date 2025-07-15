import flet as ft
from .base_card import BaseCard
from models.source_models import SourceRecord
from models.project_models import ProjectSourceLink


class ProjectSourceCard(BaseCard):
    """
    A self-contained card component to display a single source that is part
    of the current project. It inherits from BaseCard for consistent styling.
    """

    def __init__(self, source: SourceRecord, link: ProjectSourceLink, controller):
        """
        Initializes the card.

        Args:
            source: The master SourceRecord object.
            link: The ProjectSourceLink object that connects the source to the project.
            controller: The main AppController instance.
        """
        self.source = source
        self.link = link
        super().__init__(controller=controller)

    def _build_content(self) -> ft.Container:
        """Builds the card's content using a robust Row/Column layout."""

        # --- FIX: Display both notes and declassify info ---
        text_content = ft.Column(
            [
                ft.Text(
                    self.source.title,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.ON_SECONDARY_CONTAINER,
                ),
                ft.Text(
                    f"Notes: {self.link.notes or 'N/A'}",
                    overflow=ft.TextOverflow.ELLIPSIS,
                    italic=True,
                    size=12,
                    color=ft.colors.ON_SECONDARY_CONTAINER,
                ),
                ft.Text(
                    f"Declassify: {self.link.declassify or 'N/A'}",
                    overflow=ft.TextOverflow.ELLIPSIS,
                    italic=True,
                    size=12,
                    color=ft.colors.ON_SECONDARY_CONTAINER,
                ),
            ],
            spacing=2,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        )
        # --- END FIX ---

        action_buttons = ft.Row(
            [
                ft.IconButton(
                    icon=ft.icons.EDIT_DOCUMENT,
                    tooltip="View / Edit Source Details",
                    on_click=self._handle_view_edit_source,
                ),
                ft.IconButton(
                    icon=ft.icons.DELETE_OUTLINE,
                    icon_color=ft.colors.ERROR,
                    tooltip="Remove from project",
                    on_click=self._handle_remove_from_project,
                ),
            ]
        )

        content_row = ft.Row(
            [
                ft.Icon(ft.icons.DRAG_HANDLE, color=ft.colors.PRIMARY, size=28),
                text_content,
                action_buttons,
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
        )

        return ft.Container(
            content=content_row,
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            bgcolor=ft.colors.SECONDARY_CONTAINER,
        )

    def _handle_view_edit_source(self, e):
        """Handles the view/edit source action."""
        if hasattr(self.controller, "show_source_editor_dialog"):
            self.controller.dialog_controller.show_source_editor_dialog(self.source.id)
        if e.control.page:
            e.control.page.update()

    def _handle_remove_from_project(self, e):
        """Handles removing the source from the project via the controller."""
        if hasattr(self.controller, "remove_source_from_project"):
            self.controller.project_controller.remove_source_from_project(self.source.id)
        if e.control.page:
            e.control.page.update()