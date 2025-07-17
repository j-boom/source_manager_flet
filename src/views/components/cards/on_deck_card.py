import flet as ft
from .base_card import BaseCard
from models.source_models import SourceRecord
from views.components.dialogs.source_citation_dialog import SourceCitationDialog


class OnDeckCard(BaseCard):
    """
    A self-contained card component that can be used in different contexts.
    Represents a source that is "On Deck" for a project.
    """

    def __init__(
        self,
        source: SourceRecord,
        controller,
        show_add_button: bool = False,
        show_remove_button: bool = False,  # New parameter to control remove button visibility
        context: str = "library",  # "library" or "project_tab"
    ):
        """
        Initializes the OnDeckCard.

        Args:
            source (SourceRecord): The source data to display.
            controller: The application controller for handling actions.
            show_add_button (bool): If True, shows the 'add' button.
            show_remove_button (bool): If True, shows the 'remove' button.
            context (str): The context in which the card is used ('library' or 'project_tab').
        """
        self.source = source
        self.show_add_button = show_add_button
        self.show_remove_button = show_remove_button  # Store the new parameter
        self.context = context
        super().__init__(controller=controller)

    def _build_content(self) -> ft.ListTile:
        """Builds the content of the card."""
        trailing_buttons = ft.Row(spacing=0)

        # Always show the info button
        trailing_buttons.controls.append(
            ft.IconButton(
                icon=ft.icons.INFO_OUTLINE,
                tooltip="View source details",
                on_click=self._show_citation_dialog,
            )
        )

        # Conditionally show the add button
        if self.show_add_button:
            tooltip = (
                "Add to Project Sources"
                if self.context == "project_tab"
                else "Add to On Deck"
            )
            icon = (
                ft.icons.ADD_TASK_ROUNDED
                if self.context == "project_tab"
                else ft.icons.ADD_CIRCLE_OUTLINE
            )

            trailing_buttons.controls.append(
                ft.IconButton(
                    icon=icon, tooltip=tooltip, on_click=self._handle_add_click
                )
            )

        # Conditionally show the remove button
        if self.show_remove_button:
            trailing_buttons.controls.append(
                ft.IconButton(
                    icon=ft.icons.REMOVE_CIRCLE_OUTLINE,
                    tooltip="Remove from On Deck",
                    on_click=self._handle_remove_click,
                )
            )

        # Adjust width based on number of buttons
        trailing_buttons.width = len(trailing_buttons.controls) * 40

        return ft.ListTile(
            title=ft.Text(
                self.source.title,
                size=13,
                weight=ft.FontWeight.BOLD,
                overflow=ft.TextOverflow.ELLIPSIS,
                no_wrap=True,
            ),
            subtitle=ft.Text(f"Type: {self.source.source_type.value}", size=11),
            trailing=trailing_buttons,
            dense=True,
        )

    def _handle_add_click(self, e):
        """Calls the correct controller method based on the card's context."""
        if self.context == "project_tab":
            self.controller.source_controller.add_source_to_project(self.source.id, {})
        else:  # Default context is "library"
            self.controller.project_controller.add_source_to_on_deck(self.source.id)

    def _handle_remove_click(self, e):
        """Calls the controller to remove the source from the On Deck list."""
        if hasattr(self.controller.project_controller, "remove_source_from_on_deck"):
            self.controller.project_controller.remove_source_from_on_deck(self.source.id)

    def _show_citation_dialog(self, e):
        """Shows the source citation dialog."""
        dialog = SourceCitationDialog(self.source)
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()