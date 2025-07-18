import flet as ft
import logging

class NoPowerPointView(ft.Column):
    """
    A simple view displayed when no PowerPoint file is linked to the project.
    It provides a button to initiate the linking process.
    """
    def __init__(self, controller):
        """
        Initializes the NoPowerPointView.

        Args:
            controller: The ProjectController for handling actions.
        """
        super().__init__()
        self.controller = controller
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 20
        
        self.controls = [
            ft.Icon(name=ft.icons.LINK_OFF, size=50, color=ft.colors.OUTLINE),
            ft.Text("No PowerPoint File Linked", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            ft.Text("Link a .pptx file to this project to begin mapping your sources to slides."),
            ft.ElevatedButton(
                text="Link PowerPoint File",
                icon=ft.icons.ADD_LINK,
                on_click=self._handle_link_file_click
            )
        ]

    def _handle_link_file_click(self, e):
        """
        Delegates the file linking action to the controller.
        """
        self.logger.info("'Link PowerPoint File' button clicked.")
        # The project controller should have a method to handle this
        # e.g., self.controller.prompt_for_powerpoint_file()
        self.controller.powerpoint_controller.handle_link_powerpoint_request()
