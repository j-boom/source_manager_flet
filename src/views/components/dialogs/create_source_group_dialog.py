import flet as ft
from typing import List, Callable, Optional
from .base_dialog import BaseDialog

class CreateSourceGroupDialog(BaseDialog):
    def __init__(
        self,
        page: ft.Page,
        all_sources: List[ft.Checkbox],
        on_save: Callable[[str, List[str]], None]
    ):
        self.on_save = on_save
        
        self.group_name_field = ft.TextField(label="Group Name", autofocus=True)
        self.sources_checklist = ft.ListView(controls=all_sources, expand=True, spacing=5)

        super().__init__(page=page, title="Create New Source Group", width=400, height=400)

    def _build_content(self) -> List[ft.Control]:
        return [
            self.group_name_field,
            ft.Text("Select sources to include:"),
            ft.Container(self.sources_checklist, expand=True, height=300, border=ft.border.all(1, ft.Colors.OUTLINE), padding=10)
        ]

    def _build_actions(self) -> List[ft.Control]:
        return [
            ft.TextButton("Cancel", on_click=self._close_dialog),
            ft.FilledButton("Save Group", on_click=self._save),
        ]

    def _save(self, e):
        group_name = self.group_name_field.value.strip()
        selected_ids = [cb.data for cb in self.sources_checklist.controls if cb.value]

        if not group_name:
            self.group_name_field.error_text = "Group name cannot be empty."
            self.dialog.content.update() # Update just the dialog content
            return
            
        if not selected_ids:
            self.group_name_field.error_text = ""
            # Let the controller show the message for consistency
            self.page.snack_bar = ft.SnackBar(ft.Text("You must select at least one source."), open=True) # This is a temporary message, better to use controller
            self.dialog.content.update()
            return

        self.on_save(group_name, selected_ids)
        self._close_dialog(e)