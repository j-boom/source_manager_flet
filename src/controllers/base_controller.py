import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app_controller import AppController


class BaseController:
    """
    A base class for all other controllers.
    Provides access to the main AppController instance.
    """
    def __init__(self, controller: "AppController"):
        """
        Initializes the BaseController.

        Args:
            controller (AppController): The main application controller instance.
        """
        self.controller = controller
        self.logger = logging.getLogger(self.__class__.__name__)
