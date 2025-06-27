"""
Edit display name dialog
"""

import flet as ft
from typing import Callable, Optional


class EditDisplayNameDialog:
    """Dialog for editing user display name"""
    
    def __init__(self, page: ft.Page, current_name: str, on_complete: Callable[[str], None]):
        self.page = page
        self.current_name = current_name
        self.on_complete = on_complete
        self.dialog = None
        
        # Form fields
        self.display_name_field = ft.TextField(
            label="Display Name",
            hint_text="How should we address you?",
            width=300,
            value=current_name,
            autofocus=True,
            on_submit=self._on_save
        )
        
        self.error_text = ft.Text(
            color=ft.colors.RED_400,
            size=14,
            visible=False
        )
    
    def show(self):
        """Show the edit dialog"""
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Display Name", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Update how you'd like to be addressed in the app.",
                        size=14,
                        color=ft.colors.GREY_600
                    ),
                    ft.Container(height=15),
                    self.display_name_field,
                    self.error_text,
                    ft.Container(height=10),
                    ft.Text(
                        "This will be used for personalization throughout the app.",
                        size=12,
                        color=ft.colors.GREY_500
                    ),
                ], tight=True),
                width=350,
                padding=20
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=self._on_cancel
                ),
                ft.ElevatedButton(
                    "Save",
                    on_click=self._on_save,
                    style=ft.ButtonStyle(
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.BLUE_700
                    )
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()
    
    def _on_save(self, e=None):
        """Handle save button click"""
        display_name = (self.display_name_field.value or "").strip()
        
        if not display_name:
            self.error_text.value = "Please enter a display name"
            self.error_text.visible = True
            self.page.update()
            return
        
        if len(display_name) > 50:
            self.error_text.value = "Display name must be 50 characters or less"
            self.error_text.visible = True
            self.page.update()
            return
        
        # If name didn't change, just close
        if display_name == self.current_name:
            self._close_dialog()
            return
        
        self._close_dialog()
        self.on_complete(display_name)
    
    def _on_cancel(self, e):
        """Handle cancel button click"""
        self._close_dialog()
    
    def _close_dialog(self):
        """Close the dialog"""
        if self.dialog:
            self.dialog.open = False
            self.page.update()
