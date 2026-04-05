import flet as ft
from typing import Dict, Any


class UserCard(ft.Card):
    """
    A card component to display user information with edit and delete actions.
    """

    def __init__(self, user_data: Dict[str, Any], controller):
        super().__init__(elevation=2, margin=ft.margin.only(bottom=5))
        self.user_data = user_data
        self.controller = controller
        self.original_name = user_data.get("display_name")

        # Determine icon and color based on active status
        active_status = user_data.get("is_active", False)
        status_icon = ft.Icons.CHECK_CIRCLE if active_status else ft.Icons.CANCEL
        status_color = ft.Colors.GREEN if active_status else ft.Colors.RED
        status_text = "Active" if active_status else "Inactive"

        # Manually build the layout with Row and Column for better control, as ListTile
        # can have wrapping issues with complex trailing controls.
        info_column = ft.Column(
            [
                ft.Text(self.original_name, weight=ft.FontWeight.BOLD),
                ft.Text(f"Role: {user_data.get('role', 'N/A').title()}", size=12),
            ],
            spacing=2,
        )

        actions_row = ft.Row([
                ft.Icon(name=status_icon, color=status_color, tooltip=status_text),
                ft.IconButton(
                    icon=ft.Icons.EDIT_OUTLINED,
                    tooltip="Edit User",
                    on_click=self._on_edit_clicked,
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    tooltip="Delete User",
                    icon_color=ft.Colors.RED,
                    on_click=self._on_delete_clicked,
                ),
            ], spacing=5, vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        self.content = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.PERSON_OUTLINE, size=32, color=ft.Colors.ON_SURFACE_VARIANT),
                    info_column,
                    ft.Container(expand=True),  # Spacer to push actions to the right
                    actions_row,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
            ),
            padding=ft.padding.symmetric(vertical=8, horizontal=15)
        )

    def _on_edit_clicked(self, e):
        self.controller.dialog_controller.open_user_editor_dialog(self.user_data)

    def _on_delete_clicked(self, e):
        self.controller.dialog_controller.open_delete_user_confirmation_dialog(self.original_name)