"""
Base Dialog

Provides a base class for all dialogs in the application to ensure
consistency and reduce code duplication.
"""

import flet as ft
from abc import ABC, abstractmethod
from typing import List, Callable, Optional, Union


class BaseDialog(ABC):
    """An abstract base class for creating Flet AlertDialogs."""

    def __init__(
        self,
        page: ft.Page,
        title: Union[str, ft.Control],
        on_close: Optional[Callable] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ):
        """
        Initializes the BaseDialog.

        Args:
            page: The Flet Page object.
            title: The text or Control for the dialog's title.
            on_close: An optional callback function to execute when the dialog is closed.
            width: Optional width for the dialog content area.
            height: Optional height for the dialog content area.
        """
        self.page = page
        self.on_close = on_close
        self.width = width
        self.height = height

        # The main dialog control, constructed by the _build method.
        self.dialog = self._build(title)

    @abstractmethod
    def _build_content(self) -> List[ft.Control]:
        """
        Abstract method for building the main content of the dialog.
        Subclasses MUST implement this.
        """
        pass

    @abstractmethod
    def _build_actions(self) -> List[ft.Control]:
        """
        Abstract method for building the action buttons of the dialog.
        Subclasses MUST implement this.
        """
        pass

    def _build(self, title: Union[str, ft.Control]) -> ft.AlertDialog:
        """Constructs the main AlertDialog using the abstract methods."""
        title_control = (
            ft.Text(title, size=20, weight=ft.FontWeight.BOLD)
            if isinstance(title, str)
            else title
        )
        # The content is wrapped in a column that can scroll.
        # It takes its size from the constructor, which is essential for scrolling.
        scrollable_content = ft.Column(
            controls=self._build_content(),
            width=self.width,
            height=self.height,
            scroll=ft.ScrollMode.ADAPTIVE,
            spacing=15,
            tight=True,
        )

        return ft.AlertDialog(
            modal=True,
            title=title_control,
            content=scrollable_content,
            actions=self._build_actions(),
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: self._close_dialog(), # Ensure close on outside click
        )

    def show(self):
        """Opens the dialog on the page."""
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()

    def _close_dialog(self, e=None):
        """Closes the dialog and calls the on_close callback if it exists."""
        if self.dialog.open:
            self.dialog.open = False
            self.page.update()
            if self.on_close:
                self.on_close()

