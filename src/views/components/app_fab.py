import flet as ft
from typing import Callable

def AppFab(
    icon: str,
    text: str,
    on_click: Callable,
    tooltip: str = None
) -> ft.FloatingActionButton:
    """
    Creates a standardized FloatingActionButton for the application.
    """
    return ft.FloatingActionButton(
        icon=icon,
        text=text,
        on_click=on_click,
        tooltip=tooltip,
        # You can add consistent styling here if you wish
    )