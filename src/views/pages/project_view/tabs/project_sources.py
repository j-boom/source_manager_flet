import flet as ft
from typing import Dict, Any
from .base_tab import BaseTab
from views.components import ProjectSourceCard, OnDeckCard
from views.components.dialogs import AddSourceToProjectDialog

class ProjectSourcesTab(BaseTab):
    """A tab for managing project sources with a user-curated 'On Deck' list."""

    def __init__(self, controller):
        super().__init__(controller)
        self.on_deck_list = ft.ListView(expand=True, spacing=5, padding=ft.padding.only(top=10))
        self.project_sources_list = ft.Column(expand=True, spacing=5, scroll=ft.ScrollMode.ADAPTIVE)

    def build(self) -> ft.Control:
        """Builds the UI for the project sources tab."""
        on_deck_column = ft.Column(
            [
                ft.Text("On Deck", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.Text("Sources selected for this project.", italic=True, size=12, color=ft.colors.ON_SURFACE_VARIANT),
                ft.Divider(),
                ft.Container(self.on_deck_list, expand=True, border_radius=ft.border_radius.all(8)),
            ],
            width=350,
            spacing=5,
        )

        project_sources_header = ft.Row(
            controls=[
                ft.Text("Project Sources", theme_style=ft.TextThemeStyle.TITLE_MEDIUM, expand=True),
                ft.ElevatedButton(
                    text="Add Source",
                    icon=ft.icons.ADD_ROUNDED,
                    on_click=lambda _: self.controller.show_create_source_dialog(),
                    tooltip="Add a new source to the master list",
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        project_sources_column = ft.Column(
            [
                project_sources_header,
                ft.Text("Sources currently included in this project. (Drag to Reorder)", italic=True, size=12, color=ft.colors.ON_SURFACE_VARIANT),
                ft.Divider(),
                ft.Container(self.project_sources_list, expand=True),
            ],
            expand=True,
            spacing=5,
        )

        main_content = ft.Row(
            [
                ft.Container(on_deck_column, padding=10, bgcolor=ft.colors.SURFACE_VARIANT, border_radius=8),
                project_sources_column,
            ],
            expand=True,
            spacing=20,
        )

        return main_content

    def _update_view(self):
        """Refreshes both lists based on the current project's state."""
        project = self.controller.project_state_manager.current_project
        if not project: return

        self.on_deck_list.controls.clear()
        self.project_sources_list.controls.clear()

        on_deck_ids = project.metadata.get("on_deck_sources", [])
        project_source_ids = {link.source_id for link in project.sources}

        for source_id in on_deck_ids:
            if source_id not in project_source_ids:
                source = self.controller.data_service.get_source_by_id(source_id)
                if source:
                    # The OnDeckCard now gets a `show_remove_button` argument
                    card = OnDeckCard(
                        source=source,
                        controller=self.controller,
                        show_add_button=True,
                        show_remove_button=True, # This enables the remove button
                        context="project_tab"
                    )
                    add_button = next((c for c in card.content.trailing.controls if isinstance(c, ft.IconButton) and c.icon == ft.icons.ADD_TASK_ROUNDED), None)
                    if add_button:
                        add_button.on_click = lambda e, s_id=source_id: self._show_add_to_project_dialog(s_id)
                    self.on_deck_list.controls.append(card)
        
        for link in project.sources:
            source = self.controller.data_service.get_source_by_id(link.source_id)
            if source:
                card = ProjectSourceCard(source=source, link=link, controller=self.controller)
                self.project_sources_list.controls.append(
                    ft.DragTarget(
                        group="project_sources",
                        content=ft.Draggable(
                            group="project_sources",
                            content=card,
                            data=link.source_id
                        ),
                        data=link.source_id,
                        on_will_accept=self._drag_will_accept,
                        on_accept=self._drag_accept,
                        on_leave=self._drag_leave,
                    )
                )

        if not self.project_sources_list.controls:
            self.project_sources_list.controls.append(ft.Text("No sources added yet.", italic=True, text_align=ft.TextAlign.CENTER))
        if not self.on_deck_list.controls:
            self.on_deck_list.controls.append(ft.Text("Add sources from the main 'Sources' page.", italic=True, text_align=ft.TextAlign.CENTER))

        if self.page: self.page.update()

    def _drag_will_accept(self, e: ft.DragTargetAcceptEvent):
        """Provides visual feedback by modifying the target control's appearance."""
        e.control.content.content.opacity = 0.5
        e.control.update()

    def _drag_leave(self, e: ft.DragTargetAcceptEvent):
        """Resets the appearance of the target control when the draggable leaves."""
        e.control.content.content.opacity = 1
        e.control.update()

    def _drag_accept(self, e: ft.DragTargetAcceptEvent):
        """Handles the logic for reordering sources when a drop occurs."""
        e.control.content.content.opacity = 1
        
        project = self.controller.project_state_manager.current_project
        if not project:
            e.control.update()
            return

        src_id_being_dragged = self.page.get_control(e.src_id).data
        target_id = e.control.data

        if src_id_being_dragged == target_id:
            e.control.update()
            return

        source_links = project.sources
        dragged_link = next((link for link in source_links if link.source_id == src_id_being_dragged), None)
        
        target_index = -1
        for i, link in enumerate(source_links):
            if link.source_id == target_id:
                target_index = i
                break

        if dragged_link and target_index != -1:
            source_links.remove(dragged_link)
            source_links.insert(target_index, dragged_link)
            self.controller.data_service.save_project(project)
            self._update_view()
        else:
            e.control.update()

    def update_project_data(self, project_data: Dict[str, Any], project_path: str):
        """Called by the parent view to refresh the data."""
        self._update_view()

    def _show_add_to_project_dialog(self, source_id: str):
        def on_save(notes: str, declassify: str):
            self.controller.add_source_to_project(source_id, notes, declassify)
            self._update_view()

        dialog = AddSourceToProjectDialog(on_save=on_save)
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    