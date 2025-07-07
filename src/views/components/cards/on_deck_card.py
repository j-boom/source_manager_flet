import flet as ft
from .base_card import BaseCard
from models.source_models import SourceRecord

class OnDeckCard(BaseCard):
    """
    A self-contained card component to display a single master source
    that is available to be added to a project ("On Deck").
    """
    def __init__(self, source: SourceRecord, controller):
        """
        Initializes the card.
        Args:
            source: The master SourceRecord object.
            controller: The main AppController instance.
        """
        self.source = source
        super().__init__(controller=controller)

    def _build_content(self) -> ft.ListTile:
        """Builds the ListTile that serves as the card's content."""
        tooltip_text = (
            f"Title: {self.source.title}\n"
            f"Type: {self.source.source_type.value.title()}\n"
            f"Region: {self.source.region}\n"
            f"Authors: {', '.join(self.source.authors) if self.source.authors else 'N/A'}\n"
            f"Year: {self.source.publication_year or 'N/A'}\n"
            f"Publisher: {self.source.publisher or 'N/A'}\n"
            f"URL: {self.source.url or 'N/A'}"
        )

        return ft.ListTile(
            tooltip=tooltip_text,
            title=ft.Text(self.source.title, size=13, weight=ft.FontWeight.BOLD, overflow=ft.TextOverflow.ELLIPSIS, no_wrap=True),
            subtitle=ft.Text(f"Type: {self.source.source_type.value}", size=11),
            trailing=ft.IconButton(
                icon=ft.icons.ADD_CIRCLE_OUTLINE,
                tooltip="Add to project",
                on_click=self._handle_add_to_project,
            ),
            dense=True,
        )

    def _handle_add_to_project(self, e):
        """Handles adding the source to the project via the controller."""
        if hasattr(self.controller, "add_source_to_project"):
            self.controller.add_source_to_project(self.source.id)
        else:
            print(f"Controller is missing 'add_source_to_project' method.")
