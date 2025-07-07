"""
Project Sources Tab (Refactored)

Manages the sources linked to the current project, interacting with the 
DataService via the controller for all operations.
"""

import flet as ft
from typing import List
from .base_tab import BaseTab
from models.project_models import ProjectSourceLink
from models.source_models import SourceRecord

class ProjectSourcesTab(BaseTab):
    """A tab for adding, removing, and reordering project sources."""

    def __init__(self, controller):
        super().__init__(controller)
        self.project_sources_list = ft.ListView(expand=True, spacing=10)
        self.available_sources_list = ft.ListView(expand=True, spacing=5)

    def build(self) -> ft.Control:
        """Builds the UI for the project sources tab."""
        add_source_button = ft.ElevatedButton(
            "Add Source from Master List",
            icon=ft.icons.ADD,
            on_click=self._on_add_source_click
        )

        return ft.Column(
            controls=[
                ft.Row([ft.Text("Project Sources", style=ft.TextThemeStyle.TITLE_LARGE), ft.Container(expand=True), add_source_button]),
                ft.Text("Click the trash icon to remove a source from the project.", italic=True),
                ft.Divider(),
                ft.Container(
                    content=self.project_sources_list,
                    expand=True,
                )
            ],
            expand=True,
            spacing=10
        )

    def _update_view(self):
        """Refreshes the list of project sources from the current project state."""
        self.project_sources_list.controls.clear()
        
        # --- FIX: Access the .current_project attribute directly ---
        project = self.project_state_manager.current_project
        # --- END FIX ---

        if not project or not project.sources:
            self.project_sources_list.controls.append(ft.Text("No sources have been added to this project yet."))
        else:
            source_links = sorted(project.sources, key=lambda s: s.order)
            for link in source_links:
                source_record = self.controller.data_service.get_source_by_id(link.source_id)
                if source_record:
                    self.project_sources_list.controls.append(
                        self._create_source_card(source_record, link)
                    )
        if self.page:
            self.page.update()
            
    def _create_source_card(self, source: SourceRecord, link: ProjectSourceLink) -> ft.Card:
        """Creates a UI card for a single project source."""
        return ft.Card(
            content=ft.ListTile(
                leading=ft.Icon(ft.icons.SOURCE_OUTLINED),
                title=ft.Text(source.title, weight=ft.FontWeight.BOLD),
                subtitle=ft.Text(f"Type: {source.source_type.name} | Region: {source.region}"),
                trailing=ft.IconButton(
                    icon=ft.icons.DELETE_OUTLINE,
                    icon_color=ft.colors.RED_400,
                    tooltip="Remove from project",
                    data=link.source_id,
                    on_click=self._on_remove_source_click,
                ),
            )
        )

    def _on_add_source_click(self, e):
        """Opens a dialog to select sources from the master list."""
        self.available_sources_list.controls.clear()
        
        # --- FIX: Access the .current_project attribute directly ---
        project = self.project_state_manager.current_project
        # --- END FIX ---

        if not project:
            return

        all_sources = self.controller.data_service.get_all_master_sources()
        project_source_ids = {s.source_id for s in project.sources}

        for source in all_sources:
            if source.id not in project_source_ids:
                self.available_sources_list.controls.append(
                    ft.Checkbox(
                        label=f"{source.title} ({source.region})",
                        data=source.id
                    )
                )

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Add Sources to Project"),
            content=ft.Container(
                ft.Column(
                    controls=[self.available_sources_list],
                    scroll=ft.ScrollMode.AUTO,
                ), 
                width=600, 
                height=400
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self._close_dialog(e.page)),
                ft.ElevatedButton("Add Selected", on_click=lambda e: self._add_selected_sources(e.page)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _add_selected_sources(self, page: ft.Page):
        """Adds the sources selected in the dialog to the project."""
        selected_ids = [
            cb.data for cb in self.available_sources_list.controls if isinstance(cb, ft.Checkbox) and cb.value
        ]
        if selected_ids:
            if hasattr(self.controller, 'add_sources_to_project'):
                self.controller.add_sources_to_project(selected_ids)
        self._close_dialog(page)

    def _on_remove_source_click(self, e):
        """Handles the click event to remove a source."""
        source_id_to_remove = e.control.data
        if hasattr(self.controller, 'remove_source_from_project'):
            self.controller.remove_source_from_project(source_id_to_remove)

    def _close_dialog(self, page: ft.Page):
        if page.dialog:
            page.dialog.open = False
            page.update()

    def update_project_data(self, project_data: dict, project_path: str):
        """Called by the parent view to refresh the data."""
        self._update_view()
