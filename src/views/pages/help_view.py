"""
Help View

This view displays help and documentation to the user. It is built using
the modern Material 3 theming system, getting all color information
directly from the page's theme.
"""
import flet as ft
from src.views.base_view import BaseView

class HelpView(BaseView):
    """The UI for the Help & Documentation page."""

    def __init__(self, page: ft.Page, controller):
        super().__init__(page, controller)
        self.controller = controller

        # --- Build the UI upfront ---
        self.view_layout = self.build()

    def build(self) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                [
                    self._build_header(),
                    ft.Divider(),
                    ft.Container(
                        content=self._build_scrollable_content(),
                        expand=True,
                        padding=ft.padding.only(right=10) # Padding for scrollbar
                    ),
                ],
                spacing=0
            ),
            padding=20,
            expand=True,
            bgcolor=ft.colors.SURFACE,
        )

    def _build_header(self) -> ft.Control:
        """Builds the title section of the help page."""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Help & Documentation",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.PRIMARY,
                ),
                ft.Text(
                    "Everything you need to know about Source Manager",
                    size=16,
                    color=ft.colors.ON_SURFACE_VARIANT,
                ),
            ]),
            padding=ft.padding.only(bottom=20)
        )

    def _build_scrollable_content(self) -> ft.Control:
        """Builds the main, scrollable content of the help page."""
        return ft.Column(
            [
                self._create_help_section(
                    "Getting Started",
                    [
                        "1. Create a new project from the Home page.",
                        "2. Import your source files using the Sources section.",
                        "3. Use the navigation menu to explore different sections.",
                        "4. Generate reports to analyze your project structure.",
                    ]
                ),
                self._create_help_section(
                    "Navigation",
                    [
                        "• Home: Start page with quick actions.",
                        "• Recent Projects: Access your recently opened projects.",
                        "• New Project: Create new projects with various templates.",
                        "• Sources: Manage source files and directories.",
                    ]
                ),
                self._create_help_section(
                    "Key Features",
                    [
                        "• Project Management: Organize and track multiple projects.",
                        "• Source File Import: Support for various file types.",
                        "• Citation Management: Track and cite your sources.",
                        "• Theme Customization: Personalize your workspace.",
                    ]
                ),
                ft.Container(
                    content=ft.ElevatedButton(
                        "Back to Home",
                        icon=ft.icons.HOME,
                        on_click=lambda e: self.controller.navigate_to("home"),
                        style=ft.ButtonStyle(
                            color=ft.colors.ON_PRIMARY,
                            bgcolor=ft.colors.PRIMARY,
                        )
                    ),
                    padding=ft.padding.only(top=30),
                    alignment=ft.alignment.center
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
        )

    def _create_help_section(self, title: str, items: list) -> ft.Container:
        """Creates a single help section with a title and a list of items."""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    title,
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.ON_SURFACE,
                ),
                ft.Container(height=10),
                *[
                    ft.Container(
                        content=ft.Text(
                            item,
                            size=14,
                            color=ft.colors.ON_SURFACE_VARIANT
                        ),
                        padding=ft.padding.only(left=10, bottom=5)
                    ) for item in items
                ]
            ]),
            padding=ft.padding.only(bottom=25)
        )

    def refresh_theme(self):
        """
        Rebuilds the view's internal layout control to reflect theme changes.
        The AppController is responsible for displaying this updated layout.
        """
        self.view_layout = self.build()
