"""Folder creation dialog component"""

import flet as ft
from typing import Callable, Optional
from services import DirectoryService


class FolderCreationDialog:
    """Dialog component for creating new ten-digit folders"""
    
    def __init__(self, page: ft.Page, directory_service: DirectoryService,
                 on_success: Optional[Callable] = None, on_cancel: Optional[Callable] = None):
        self.page = page
        self.directory_service = directory_service
        self.on_success = on_success
        self.on_cancel = on_cancel
        self.dialog = None
        
        # Form fields
        self.ten_digit_field = None
        self.description_field = None
        self.error_text = None
        
        # Data
        self.parent_path = ""
    
    def show_for_specific_number(self, parent_path: str, ten_digit_number: str):
        """Show dialog for creating a specific ten-digit folder"""
        self.parent_path = parent_path
        self._create_specific_folder_dialog(ten_digit_number)
        
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()
    
    def show_for_new_folder(self, parent_path: str):
        """Show dialog for creating a new ten-digit folder"""
        self.parent_path = parent_path
        self._create_new_folder_dialog()
        
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()
    
    def _create_specific_folder_dialog(self, ten_digit_number: str):
        """Create dialog for a specific ten-digit number"""
        description_field = ft.TextField(
            label="Folder Description (optional)",
            hint_text="e.g., Project Description",
            width=300
        )
        
        def create_folder(e):
            description = description_field.value.strip() if description_field.value else ""
            success = self.directory_service.create_ten_digit_folder(
                self.parent_path, ten_digit_number, description
            )
            
            if success:
                self._close_dialog()
                if self.on_success:
                    self.on_success(f"Created folder: {ten_digit_number}")
            else:
                self._show_error("Failed to create folder")
        
        self.dialog = ft.AlertDialog(
            title=ft.Text(f"Create {ten_digit_number} Folder"),
            content=ft.Column([
                ft.Text(f"Create a new ten-digit folder: {ten_digit_number}"),
                ft.Container(height=10),
                description_field
            ], tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self._on_cancel_clicked()),
                ft.ElevatedButton("Create Folder", on_click=create_folder)
            ]
        )
    
    def _create_new_folder_dialog(self):
        """Create dialog for a new ten-digit folder"""
        self.ten_digit_field = ft.TextField(
            label="Ten-Digit Number *",
            hint_text="e.g., 1001234567",
            width=300,
            max_length=10,
            on_change=self._validate_ten_digit
        )
        
        self.description_field = ft.TextField(
            label="Folder Description (optional)",
            hint_text="e.g., Project Description",
            width=300
        )
        
        self.error_text = ft.Text("", color=ft.colors.RED_400, size=12, visible=False)
        
        self.dialog = ft.AlertDialog(
            title=ft.Text("Create New Ten-Digit Folder"),
            content=ft.Column([
                ft.Text("Create a new ten-digit folder in this directory:"),
                ft.Container(height=10),
                self.ten_digit_field,
                ft.Container(height=10),
                self.description_field,
                ft.Container(height=10),
                self.error_text
            ], tight=True, width=400),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self._on_cancel_clicked()),
                ft.ElevatedButton("Create Folder", on_click=self._on_create_clicked)
            ]
        )
    
    def _validate_ten_digit(self, e):
        """Validate ten-digit number format"""
        value = e.control.value.strip() if e.control.value else ""
        
        if value and (not value.isdigit() or len(value) != 10):
            e.control.error_text = "Must be exactly 10 digits"
        else:
            e.control.error_text = None
        self.page.update()
    
    def _on_create_clicked(self, e):
        """Handle create folder button click"""
        ten_digit = self.ten_digit_field.value.strip() if self.ten_digit_field.value else ""
        description = self.description_field.value.strip() if self.description_field.value else ""
        
        # Validate
        if not ten_digit:
            self._show_error("Ten-digit number is required")
            return
        
        if not ten_digit.isdigit() or len(ten_digit) != 10:
            self._show_error("Ten-digit number must be exactly 10 digits")
            return
        
        # Create folder
        success = self.directory_service.create_ten_digit_folder(self.parent_path, ten_digit, description)
        
        if success:
            self._close_dialog()
            if self.on_success:
                folder_name = ten_digit
                if description:
                    folder_name += f" {description}"
                self.on_success(f"Created folder: {folder_name}")
        else:
            self._show_error("Failed to create folder")
    
    def _show_error(self, message: str):
        """Show error message"""
        if self.error_text:
            self.error_text.value = message
            self.error_text.visible = True
            self.page.update()
    
    def _on_cancel_clicked(self):
        """Handle cancel button click"""
        self._close_dialog()
        if self.on_cancel:
            self.on_cancel()
    
    def _close_dialog(self):
        """Close the dialog"""
        if self.dialog:
            self.dialog.open = False
            self.page.update()
