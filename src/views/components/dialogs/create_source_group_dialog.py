import flet as ft
from typing import List, Callable

class CreateSourceGroupDialog(ft.AlertDialog):
    def __init__(
        self,
        all_sources: List[ft.Checkbox],
        on_save: Callable[[str, List[str]], None]
    ):
        super().__init__()
        self.modal = True
        self.title = ft.Text("Create New Source Group")
        self.on_save = on_save
        
        self.group_name_field = ft.TextField(label="Group Name", autofocus=True)
        self.sources_checklist = ft.ListView(controls=all_sources, expand=True, spacing=5)

        self.content = ft.Column([
            self.group_name_field,
            ft.Text("Select sources to include:"),
            ft.Container(self.sources_checklist, expand=True, height=300, border=ft.border.all(1, ft.colors.OUTLINE), padding=10)
        ], spacing=10, width=400, height=400)
        
        self.actions = [
            ft.TextButton("Cancel", on_click=self._close),
            ft.FilledButton("Save Group", on_click=self._save),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def _save(self, e):
        group_name = self.group_name_field.value.strip()
        selected_ids = [cb.data for cb in self.sources_checklist.controls if cb.value]

        if not group_name:
            self.group_name_field.error_text = "Group name cannot be empty."
            self.page.update()
            return
            
        if not selected_ids:
            self.group_name_field.error_text = ""
            self.page.snack_bar = ft.SnackBar(ft.Text("You must select at least one source."), open=True)
            self.page.update()
            return

        self.on_save(group_name, selected_ids)
        self._close(e)

    def _close(self, e):
        self.open = False
        self.page.update()