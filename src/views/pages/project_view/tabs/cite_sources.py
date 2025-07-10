"""
Cite Sources Tab (Refactored)

Provides a dual-select interface for managing source citations. Slides are
selected via a horizontally-scrolling carousel at the bottom.
"""

import flet as ft
from .base_tab import BaseTab
from typing import List, Optional, Tuple
import uuid

from views.components.dialogs.create_source_group_dialog import CreateSourceGroupDialog
from views.components.slide_carousel import SlideCarousel


class CiteSourcesTab(BaseTab):
    """Tab for managing source citations with a dual select interface."""

    def __init__(self, controller):
        super().__init__(controller)
        self.current_slide_id: Optional[str] = None
        self.slide_data: List[Tuple[str, str]] = []

        # --- UI Components ---
        self.slide_carousel = SlideCarousel(on_slide_selected=self._on_slide_selected)
        self.current_slide_title = ft.Text(
            "",
            style=ft.TextThemeStyle.HEADLINE_MEDIUM,
            no_wrap=True,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
        self.change_ppt_btn = ft.ElevatedButton(
            "Sync With PowerPoint",
            icon=ft.icons.SYNC_OUTLINED,
            on_click=lambda e: self.controller.citation.get_slides_for_current_project(
                force_reselect=True
            ),
        )
        self.available_list = ft.ListView(expand=True, spacing=5)
        self.cited_list = ft.ListView(expand=True, spacing=5)
        self.move_to_cited_btn = ft.IconButton(
            icon=ft.icons.ARROW_FORWARD,
            on_click=self._move_to_cited,
            tooltip="Cite selected source(s)",
        )
        self.move_to_available_btn = ft.IconButton(
            icon=ft.icons.ARROW_BACK,
            on_click=self._move_to_available,
            tooltip="Remove citation(s)",
        )
        self.create_group_btn = ft.ElevatedButton(
            "Create Group",
            icon=ft.icons.GROUP_ADD,
            on_click=self._show_create_group_dialog,
        )

        self.main_view = self._build_main_view()
        self.prompt_view = self._build_associate_file_prompt()

    def build(self) -> ft.Control:
        """Builds the tab content, which is a Stack of the main view and prompt."""
        return ft.Stack(controls=[self.prompt_view, self.main_view])

    def _build_associate_file_prompt(self) -> ft.Column:
        """Returns the UI for prompting the user to select a .pptx file."""
        return ft.Column(
            [
                ft.Icon(name=ft.icons.SLIDESHOW_ROUNDED, size=50),
                ft.Text(
                    "PowerPoint File Required", style=ft.TextThemeStyle.HEADLINE_SMALL
                ),
                ft.Text(
                    "To cite sources, you must first associate a .pptx file with this project."
                ),
                ft.Container(height=10),
                ft.FilledButton(
                    "Select Presentation File",
                    icon=ft.icons.ATTACH_FILE,
                    on_click=lambda e: self.controller.citation.get_slides_for_current_project(),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            expand=True,
            visible=False,
        )

    def _build_main_view(self) -> ft.Column:
        """Returns the main dual-list interface for citing sources."""
        return ft.Column(
            [
                ft.Container(
                    content=ft.Stack(
                        [
                            ft.Row(
                                [self.create_group_btn],
                                alignment=ft.MainAxisAlignment.START,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Row(
                                [self.current_slide_title],
                                alignment=ft.MainAxisAlignment.CENTER,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Row(
                                [self.change_ppt_btn],
                                alignment=ft.MainAxisAlignment.END,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        ]
                    ),
                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                ),
                ft.Row(
                    [
                        self._build_source_column(
                            "Project Sources", self.available_list
                        ),
                        ft.Column(
                            [self.move_to_cited_btn, self.move_to_available_btn],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        self._build_source_column(
                            "Cited on this Slide", self.cited_list
                        ),
                    ],
                    expand=True,
                ),
                ft.Divider(height=15),
                ft.Text("Select Slide:", weight=ft.FontWeight.BOLD),
                self.slide_carousel.view,
            ],
            expand=True,
            spacing=10,
            visible=False,
        )

    def _build_source_column(self, title: str, list_view: ft.ListView) -> ft.Column:
        """Helper to build a column for the source lists."""
        return ft.Column(
            [
                ft.Row(
                    [ft.Text(title, weight=ft.FontWeight.BOLD)],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(
                    list_view,
                    border=ft.border.all(1),
                    border_radius=8,
                    padding=10,
                    expand=True,
                ),
            ],
            expand=True,
        )

    def update_project_data(self, project_data: dict, project_path: str):
        """Called by the parent view to show the correct UI and load data."""
        project = self.project_state_manager.current_project
        if not project:
            return

        ppt_path = project.metadata.get("powerpoint_path")
        if ppt_path:
            self.main_view.visible = True
            self.prompt_view.visible = False
            slide_info = self.controller.citation.get_slides_for_current_project()
            if slide_info is not None:
                self.slide_data = slide_info
                self._populate_controls()
        else:
            self.main_view.visible = False
            self.prompt_view.visible = True
        if self.page:
            self.page.update()

    def _populate_controls(self):
        """The core logic to populate all UI controls."""
        project = self.project_state_manager.current_project
        if not self.slide_data:
            self.main_view.visible = False
            self.prompt_view.visible = True
            if self.page:
                self.page.update()
            return

        if self.current_slide_id is None or self.current_slide_id not in [
            s[0] for s in self.slide_data
        ]:
            self.current_slide_id = self.slide_data[0][0]

        self.slide_carousel.update(self.slide_data, self.current_slide_id)
        if hasattr(self.slide_carousel, "scroll_to_key"):
            self.slide_carousel.scroll_to_key(self.current_slide_id)

        for slide_id, title in self.slide_data:
            if slide_id == self.current_slide_id:
                self.current_slide_title.value = title
                break

        all_project_source_ids = {link.source_id for link in project.sources}
        citations = project.metadata.get("citations", {})
        cited_on_this_slide_ids = set(citations.get(str(self.current_slide_id), []))
        source_groups = project.metadata.get("source_groups", [])

        self.available_list.controls.clear()
        self.cited_list.controls.clear()

        # --- REFACTORED LOGIC ---
        # A single loop now correctly populates both lists.
        for source_id in sorted(list(all_project_source_ids)):
            source_record = self.controller.data_service.get_source_by_id(source_id)
            if source_record:
                checkbox = ft.Checkbox(label=source_record.title, data=source_id)
                if source_id in cited_on_this_slide_ids:
                    self.cited_list.controls.append(checkbox)
                else:
                    self.available_list.controls.append(checkbox)

        # Source groups are always considered 'available' for now.
        if source_groups:
            self.available_list.controls.append(ft.Divider())
            for group in source_groups:
                self.available_list.controls.append(
                    ft.Checkbox(
                        label=group.get("name", "Unnamed Group"),
                        data=group,
                        label_style=ft.TextStyle(
                            weight=ft.FontWeight.BOLD, italic=True
                        ),
                    )
                )
        if self.page:
            self.page.update()

    def _on_slide_selected(self, slide_id: str):
        """Callback that runs when a slide is selected in the carousel component."""
        self.current_slide_id = slide_id
        self._populate_controls()

    def _show_create_group_dialog(self, e):
        """Launches the dialog to create a new source group."""
        project = self.project_state_manager.current_project
        if not project:
            return

        all_sources_records = [
            self.controller.data_service.get_source_by_id(link.source_id)
            for link in project.sources
        ]
        source_checkboxes = [
            ft.Checkbox(label=rec.title, data=rec.id)
            for rec in all_sources_records
            if rec
        ]

        dialog = CreateSourceGroupDialog(
            all_sources=source_checkboxes, on_save=self._handle_create_group
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _handle_create_group(self, name: str, source_ids: List[str]):
        """Callback that runs when a group is saved from the dialog."""
        new_group = {
            "id": f"group_{uuid.uuid4()}",
            "name": name,
            "source_ids": source_ids,
        }
        self.controller.citation.add_source_group(new_group)
        self._populate_controls() # ADDED: Refresh the view after creating a group

    def _move_to_cited(self, e):
        """Move selected sources and sources from selected groups to cited."""
        final_ids_to_add = set()
        for cb in self.available_list.controls:
            if isinstance(cb, ft.Checkbox) and cb.value:
                if isinstance(cb.data, dict):
                    final_ids_to_add.update(cb.data.get("source_ids", []))
                else:
                    final_ids_to_add.add(cb.data)
        if final_ids_to_add:
            self.controller.citation.add_citations_to_slide(
                self.current_slide_id, list(final_ids_to_add)
            )
            self._populate_controls() # ADDED: Refresh the view after citing

    def _move_to_available(self, e):
        """Move selected sources from cited to available."""
        selected_ids = [
            cb.data
            for cb in self.cited_list.controls
            if isinstance(cb, ft.Checkbox) and cb.value
        ]
        if selected_ids:
            self.controller.citation.remove_citations_from_slide(
                self.current_slide_id, selected_ids
            )
            self._populate_controls() # ADDED: Refresh the view after un-citing

