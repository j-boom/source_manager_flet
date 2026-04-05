import flet as ft
from src.views.components.user_card import UserCard


class UserManagementTab(ft.Column):
    """
    A UI tab for managing users in the admin panel. It displays a list of UserCards.
    """
    def __init__(self, controller):
        super().__init__(expand=True, scroll=ft.ScrollMode.ADAPTIVE, spacing=10)
        self.controller = controller
        self.users_list = ft.ListView(expand=True, spacing=10)
        self._build_ui()
        self.update_users_list()

    def _build_ui(self):
        """Constructs the static layout of the tab."""
        add_user_button = ft.ElevatedButton(
            "Add New User",
            icon=ft.Icons.ADD,
            on_click=self._on_add_user_clicked
        )

        self.controls.extend([
            ft.Row([
                ft.Text("User Management", theme_style=ft.TextThemeStyle.TITLE_LARGE),
                ft.Container(expand=True),
                add_user_button
            ]),
            ft.Text("Add, edit, or remove users and their permissions.", color=ft.Colors.ON_SURFACE_VARIANT),
            ft.Divider(),
            self.users_list
        ])

    def update_users_list(self):
        """Fetches the latest user list and rebuilds the list view with UserCards."""
        self.users_list.controls.clear()
        users = self.controller.admin_controller.get_all_users()
        for user_data in sorted(users, key=lambda u: u.get('display_name', '')):
            self.users_list.controls.append(UserCard(user_data, self.controller))

    def _on_add_user_clicked(self, e):
        # Open the editor dialog with no user data to indicate creation mode
        self.controller.dialog_controller.open_user_editor_dialog()