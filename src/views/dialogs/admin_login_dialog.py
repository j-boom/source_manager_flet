"""
Admin Login Dialog

A dialog for admin authentication and user role management.
"""
import flet as ft
from typing import Callable, List, Dict, Optional
from src.services.admin_service import AdminService


class AdminLoginDialog(ft.AlertDialog):
    """Dialog for admin login and user management."""
    
    def __init__(self, page: ft.Page, admin_service: AdminService, on_close: Optional[Callable] = None):
        self.page = page
        self.admin_service = admin_service
        self.on_close = on_close
        self.is_authenticated = False
        
        # Password field
        self.password_field = ft.TextField(
            label="Master Admin Password",
            password=True,
            can_reveal_password=True,
            width=300,
            on_submit=self._handle_login,
            autofocus=True
        )
        
        # Login content
        self.login_content = ft.Column([
            ft.Text("Admin Login", size=20, weight=ft.FontWeight.BOLD),
            ft.Text("Enter master admin password to access user management", size=14),
            self.password_field,
            ft.Row([
                ft.ElevatedButton("Login", on_click=self._handle_login),
                ft.TextButton("Cancel", on_click=self._handle_close)
            ], alignment=ft.MainAxisAlignment.END)
        ], width=400, spacing=20)
        
        # User management content (shown after login)
        self.management_content = self._build_management_content()
        
        super().__init__(
            modal=True,
            title=ft.Text("Admin Access"),
            content=self.login_content,
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=self._handle_close,  # Handle close when clicking outside or pressing escape
        )
    
    def _build_management_content(self) -> ft.Column:
        """Build the user management interface."""
        self.users_container = ft.Column(spacing=5)
        
        return ft.Column([
            ft.Text("User Management", size=20, weight=ft.FontWeight.BOLD),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Users", weight=ft.FontWeight.W_500),
                        # Header row
                        ft.Container(
                            content=ft.Row([
                                ft.Container(ft.Text("User", weight=ft.FontWeight.BOLD), width=200),
                                ft.Container(ft.Text("Can save to local drive", weight=ft.FontWeight.BOLD), width=150),
                                ft.Container(ft.Text("Admin", weight=ft.FontWeight.BOLD), width=100),
                                ft.Container(ft.Text("Actions", weight=ft.FontWeight.BOLD), width=80),
                            ], alignment=ft.MainAxisAlignment.START),
                            bgcolor=ft.colors.SURFACE_VARIANT,
                            padding=10,
                            border_radius=5
                        ),
                        ft.Container(
                            content=self.users_container,
                            height=400,
                        )
                    ]),
                    padding=15
                )
            ),
            
            ft.Row([
                ft.ElevatedButton("Refresh", on_click=self._refresh_users),
                ft.TextButton("Close", on_click=self._handle_close)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ], width=700, spacing=15)
    
    def _handle_login(self, e=None):
        """Handle admin login attempt."""
        password = self.password_field.value
        
        if not password:
            self._show_error("Please enter a password")
            return
        
        if self.admin_service.authenticate_admin(password):
            self.is_authenticated = True
            self.content = self.management_content
            self.title = ft.Text("User Management")
            self._refresh_users()
            if self.page:
                self.page.update()
        else:
            self._show_error("Invalid admin password")
    
    def _refresh_users(self, e=None):
        """Refresh the users list display."""
        self.users_container.controls.clear()
        
        users = self.admin_service.get_all_users()
        
        if not users:
            self.users_container.controls.append(
                ft.Container(
                    content=ft.Text("No users found", color=ft.colors.GREY),
                    padding=20,
                    alignment=ft.alignment.center
                )
            )
        else:
            for user in users:
                user_row = self._build_user_row(user)
                self.users_container.controls.append(user_row)
        
        if self.page:
            self.page.update()
    
    def _build_user_row(self, user: Dict) -> ft.Container:
        """Build a row for displaying a user."""
        local_saver_checkbox = ft.Checkbox(
            value=user["is_local_saver"],
            on_change=lambda e, uid=user["user_id"]: self._update_local_saver(uid, e.control.value)
        )
        
        admin_checkbox = ft.Checkbox(
            value=user["is_admin"],
            on_change=lambda e, uid=user["user_id"]: self._update_admin_status(uid, e.control.value)
        )
        
        delete_button = ft.IconButton(
            ft.icons.DELETE,
            tooltip="Delete User",
            on_click=lambda e, uid=user["user_id"], name=user["display_name"]: self._confirm_delete_user(uid, name)
        )
        
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text(user["display_name"], weight=ft.FontWeight.W_500),
                        ft.Text(f"ID: {user['user_id']}", size=12, color=ft.colors.GREY)
                    ], spacing=2),
                    width=200
                ),
                ft.Container(content=local_saver_checkbox, width=150, alignment=ft.alignment.center),
                ft.Container(content=admin_checkbox, width=100, alignment=ft.alignment.center),
                ft.Container(content=delete_button, width=80, alignment=ft.alignment.center),
            ], alignment=ft.MainAxisAlignment.START),
            padding=10,
            border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
            border_radius=5
        )
    
    def _update_local_saver(self, user_id: str, is_local_saver: bool):
        """Update a user's local saver status."""
        if self.admin_service.update_user_local_saver_status(user_id, is_local_saver):
            self._show_success(f"Updated local saver status for {user_id}")
        else:
            self._show_error(f"Failed to update local saver status for {user_id}")
            self._refresh_users()  # Refresh to revert changes
    
    def _update_admin_status(self, user_id: str, is_admin: bool):
        """Update a user's admin status."""
        if self.admin_service.update_user_admin_status(user_id, is_admin):
            self._show_success(f"Updated admin status for {user_id}")
        else:
            self._show_error(f"Failed to update admin status for {user_id}")
            self._refresh_users()  # Refresh to revert changes
    
    def _confirm_delete_user(self, user_id: str, display_name: str):
        """Show confirmation dialog before deleting a user."""
        def confirm_delete(e):
            if self.admin_service.delete_user(user_id):
                self._refresh_users()
                self._show_success(f"User '{display_name}' deleted")
            else:
                self._show_error(f"Failed to delete user '{display_name}'")
            # Close dialog
            if hasattr(e, 'control') and hasattr(e.control, 'page'):
                e.control.page.dialog.open = False
                e.control.page.update()
        
        def cancel_delete(e):
            if hasattr(e, 'control') and hasattr(e.control, 'page'):
                e.control.page.dialog.open = False
                e.control.page.update()
        
        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm User Deletion"),
            content=ft.Text(f"Are you sure you want to delete user '{display_name}' (ID: {user_id})?\n\nThis will permanently remove their profile and all settings."),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_delete),
                ft.ElevatedButton("Delete", on_click=confirm_delete, color=ft.colors.ERROR),
            ],
        )
        
        if self.page:
            self.page.dialog = confirm_dialog
            confirm_dialog.open = True
            self.page.update()
    
    def _show_error(self, message: str):
        """Show error message."""
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                ft.Text(message),
                bgcolor=ft.colors.ERROR_CONTAINER
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _show_success(self, message: str):
        """Show success message."""
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                ft.Text(message),
                bgcolor=ft.colors.GREEN
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _handle_close(self, e=None):
        """Handle dialog close."""
        self.open = False
        if e and hasattr(e, 'page'):
            e.page.update()
        elif self.page:
            self.page.update()
        if self.on_close:
            self.on_close()
