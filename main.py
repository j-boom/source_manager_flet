"""
Source Manager Application Entry Point
"""
import flet as ft
import sys
import logging
from pathlib import Path

# --- 1. Add Project Root to Python Path ---
# This ensures that imports work correctly regardless of how the script is run.
# It assumes main.py is in the project's root directory.
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# --- 2. Set up Logging (Crucial First Step) ---
# Import directly from the logging_config module and run setup immediately.
# This prevents circular dependencies.
from config.logging_config import setup_logging
setup_logging()

# --- 3. Import Application Components ---
# Now that logging is configured, it's safe to import the rest of the app.
from src.controllers.app_controller import AppController
from config.app_config import (
    APP_NAME, 
    MIN_WINDOW_WIDTH, 
    MIN_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    DEFAULT_WINDOW_HEIGHT
)

def main(page: ft.Page):
    """Main application entry point."""
    logger = logging.getLogger(__name__)
    logger.info(f"--- Starting {APP_NAME} ---")

    # --- Page and Window Configuration ---
    page.title = APP_NAME
    page.window.width = DEFAULT_WINDOW_WIDTH
    page.window.height = DEFAULT_WINDOW_HEIGHT
    page.window.min_width = MIN_WINDOW_WIDTH
    page.window.min_height = MIN_WINDOW_HEIGHT
    
    # Set application icon
    try:
        icon_path = project_root / "assets/sm_icon.png" # Assuming icon is in an assets folder
        if icon_path.exists():
            page.window.icon = str(icon_path)
            logger.info(f"Application icon loaded from {icon_path}")
    except Exception as e:
        logger.error(f"Could not load application icon: {e}", exc_info=True)

    # --- Initialize and Run Application ---
    try:
        controller = AppController(page)
        
        # Set up the cleanup handler for graceful shutdown
        page.on_disconnect = controller.cleanup
        
        controller.run()

    except Exception as e:
        logger.critical(f"A critical error occurred during application startup: {e}", exc_info=True)
        # To display a fatal error, first completely clean the page of all elements
        # to avoid a broken UI state.
        page.appbar = None
        page.clean() # Use page.clean() to remove all controls. It's a shortcut for page.controls.clear()
        
        # Add a more user-friendly error message
        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.icons.ERROR_OUTLINE, color="red", size=48),
                        ft.Text("Application Startup Failed", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            f"A critical error occurred. Please check the logs for details:\n{project_root / 'logs'}",
                            text_align=ft.TextAlign.CENTER,
                            color=ft.colors.ON_SURFACE_VARIANT
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
    ft.app(
        target=main,
        assets_dir="assets" # Tell Flet where to find assets like the icon
    )
