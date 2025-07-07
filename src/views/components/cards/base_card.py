import flet as ft
from abc import ABC, abstractmethod

class BaseCard(ft.Card, ABC):
    """
    An abstract base class for all card components in the application.
    It provides a consistent structure, styling, and interface.
    """
    def __init__(self, controller):
        """
        Initializes the BaseCard.

        Args:
            controller: The main AppController instance.
        """
        super().__init__()
        self.controller = controller
        
        # --- Unified Styling ---
        # All cards will share these visual properties.
        self.elevation = 2
        self.margin = ft.margin.symmetric(vertical=4)
        
        # --- Content Structure ---
        # The content of the card must be built by the subclass.
        self.content = self._build_content()

    @abstractmethod
    def _build_content(self) -> ft.Control:
        """
        Abstract method for building the main content of the card.
        Subclasses MUST implement this to define the card's specific layout.
        """
        pass
