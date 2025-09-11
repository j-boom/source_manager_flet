import flet as ft
from typing import List, Dict, Any

class UserManagementTab(ft.Column):
    """A UI component for managing users in the admin panel."""

    def __init__(self, controller):
        super().__init__(expand=True, scroll=ft.ScrollMode.ADAPTIVE, spacing=10)
        self.controller = controller
        self.users_list = ft.ListView(expand=True, spacing=10)
        self._build_ui()
        self.update_users_list()

    def _build_ui(self):
        """Constructs the static parts of the UI."""
        self.controls.extend([
            ft.Row([
                ft.Text("Manage Users", theme_style=ft.TextThemeStyle.TITLE_LARGE),
                ft.Container(expand=True),
                ft.ElevatedButton("Add User", icon=ft.icons.ADD, on_click=self._on_add_user_clicked)
            ]),
            ft.Divider(),
            self.users_list
        ])

    def update_users_list(self):
        """Fetches the latest user list and rebuilds the list view."""
        self.users_list.controls.clear()
        users = self.controller.admin_controller.get_all_users()
        for user in sorted(users, key=lambda u: u.get('display_name', '')):
            self.users_list.controls.append(self._create_user_tile(user))
        if self.page:
            self.page.update()

    def _create_user_tile(self, user_data: Dict[str, Any]) -> ft.Card:
        """Creates a Card with a ListTile for a single user."""
        user_tile = ft.ListTile(
            leading=ft.Icon(ft.icons.PERSON_OUTLINE),
            title=ft.Text(user_data.get("display_name", "Unknown User"), weight=ft.FontWeight.BOLD),
            subtitle=ft.Text(f"Role: {user_data.get('role', 'N/A').replace('_', ' ').title()} | Active: {user_data.get('is_active', False)}"),
            trailing=ft.Row([
                ft.IconButton(ft.icons.EDIT_OUTLINED, on_click=lambda e, u=user_data: self._on_edit_user_clicked(u), tooltip="Edit User"),
                ft.IconButton(ft.icons.DELETE_FOREVER_OUTLINED, on_click=lambda e, u=user_data: self._on_delete_user_clicked(u), tooltip="Delete User", icon_color=ft.colors.ERROR),
            ])
        )
        
        return ft.Card(
            content=ft.Container(user_tile, padding=ft.padding.symmetric(vertical=5))
        )

    def _on_add_user_clicked(self, e):
        self.controller.dialog_controller.open_user_editor_dialog()

    def _on_edit_user_clicked(self, user: Dict[str, Any]):
        self.controller.dialog_controller.open_user_editor_dialog(user_data=user)

    def _on_delete_user_clicked(self, user: Dict[str, Any]):
        self.controller.dialog_controller.open_delete_user_confirmation_dialog(user.get("username"))