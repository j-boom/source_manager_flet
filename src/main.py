"""
Source Manager Application Entry Point
"""
import sys
import logging
from pathlib import Path

# Add parent directory to Python path to access config
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import flet as ft
from config import setup_logging, APP_NAME, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT
from controllers import AppController

def main(page: ft.Page):
    """Main application entry point."""
    # Set up logging
    logger = setup_logging()
    logger.info(f"Starting {APP_NAME}")
    
    # Configure page
    page.title = APP_NAME
    page.window.width = DEFAULT_WINDOW_WIDTH
    page.window.height = DEFAULT_WINDOW_HEIGHT
    page.window.resizable = True
    
    # Set application icon
    icon_path = project_root / "sm_icon.png"
    if icon_path.exists():
        page.window.icon = str(icon_path)
    
    # Initialize and run application
    try:
        controller = AppController(page)
        controller.run()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    ft.app(target=main)
