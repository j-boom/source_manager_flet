"""
Source Manager Application Entry Point
"""
import flet as ft
import logging
from config.logging_config import setup_logging

from typing import Optional

setup_logging()
# --- Import Application Components ---
from src.controllers.app_controller import AppController
from config.app_config import (
    APP_NAME,
    DEFAULT_WINDOW_WIDTH,
    DEFAULT_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT
)

def main(page: ft.Page):
    """Main application entry point."""
    logger = logging.getLogger(__name__)
    logger.info(f"--- Starting {APP_NAME} ---")

    # --- Window Configuration ---
    page.title = APP_NAME
    page.window.width = DEFAULT_WINDOW_WIDTH
    page.window.height = DEFAULT_WINDOW_HEIGHT
    page.window.min_width = MIN_WINDOW_WIDTH
    page.window.min_height = MIN_WINDOW_HEIGHT
    page.window.center()

    # This will be assigned after the controller is initialized
    app_controller_instance: Optional[AppController] = None

    def on_window_event(e):
        if e.data == "close":
            if app_controller_instance:
                app_controller_instance.shutdown()
            page.window_destroy()

    # --- Initialize and Run Application ---
    try:
        app_controller_instance = AppController(page)
        page.window.on_event = on_window_event
        app_controller_instance.run()
    except Exception as e:
        logger.critical(f"A critical error occurred during application startup: {e}", exc_info=True)
        # Display a simple error message
        page.clean()
        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.ERROR_OUTLINE, color="red", size=48),
                        ft.Text("Application Startup Failed", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            "A critical error occurred. Please check the logs for details.",
                            text_align=ft.TextAlign.CENTER,
                            color=ft.Colors.ON_SURFACE_VARIANT
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                ),
                alignment=ft.alignment.center,
                expand=True,
                padding=20
            )
        )
        page.update()

if __name__ == "__main__":
    ft.app(target=main)
