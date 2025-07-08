import flet as ft
from .base_card import BaseCard
from models.source_models import SourceRecord
from views.components.dialogs.source_citation_dialog import SourceCitationDialog

class OnDeckCard(BaseCard):
    """
    A self-contained card component that can be used in different contexts.
    """
    def __init__(
        self,
        source: SourceRecord,
        controller,
        show_add_button: bool = False,
        context: str = "library" # "library" or "project_tab"
    ):
        self.source = source
        self.show_add_button = show_add_button
        self.context = context
        super().__init__(controller=controller)

    def _build_content(self) -> ft.ListTile:
        trailing_buttons = ft.Row(spacing=0)
        
        trailing_buttons.controls.append(
            ft.IconButton(
                icon=ft.icons.INFO_OUTLINE,
                tooltip="View source details",
                on_click=self._show_citation_dialog
            )
        )

        if self.show_add_button:
            # The tooltip and icon can also be context-dependent
            tooltip = "Add to Project Sources" if self.context == "project_tab" else "Add to On Deck"
            icon = ft.icons.ADD_TASK_ROUNDED if self.context == "project_tab" else ft.icons.ADD_CIRCLE_OUTLINE
            
            trailing_buttons.controls.append(
                ft.IconButton(
                    icon=icon,
                    tooltip=tooltip,
                    on_click=self._handle_add_click
                )
            )
        
        trailing_buttons.width = len(trailing_buttons.controls) * 40

        return ft.ListTile(
            title=ft.Text(self.source.title, size=13, weight=ft.FontWeight.BOLD, overflow=ft.TextOverflow.ELLIPSIS, no_wrap=True),
            subtitle=ft.Text(f"Type: {self.source.source_type.value}", size=11),
            trailing=trailing_buttons,
            dense=True,
        )

    def _handle_add_click(self, e):
        """Calls the correct controller method based on the card's context."""
        if self.context == "project_tab":
            self.controller.promote_source_from_on_deck(self.source.id)
        else: # Default context is "library"
            self.controller.add_source_to_on_deck(self.source.id)

    def _show_citation_dialog(self, e):
        dialog = SourceCitationDialog(self.source)
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()