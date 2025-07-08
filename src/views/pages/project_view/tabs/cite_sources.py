"""
Cite Sources Tab (Refactored)

Provides a dual-select interface for managing which sources are cited
on a per-slide basis. It now requires a PowerPoint file to be associated
before showing the main interface.
"""

import flet as ft
from .base_tab import BaseTab
from typing import List, Optional, Tuple, Callable
from dataclasses import dataclass
import uuid

from views.components.dialogs.create_source_group_dialog import CreateSourceGroupDialog

@dataclass
class TempSourceGroup:
    id: str
    name: str
    source_ids: List[str]


class CiteSourcesTab(BaseTab):
    """Tab for managing source citations with a dual select interface."""
    
    def __init__(self, controller):
        super().__init__(controller)
        self.current_slide_id: Optional[str] = None
        self.slide_data: List[Tuple[str, str]] = []
        self.temp_groups: List[TempSourceGroup] = []
        
        # UI components for the main view
        self.slide_selector = ft.Dropdown(on_change=self._on_slide_change, width=350, hint_text="Select a slide")
        self.available_list = ft.ListView(expand=True, spacing=5)
        self.cited_list = ft.ListView(expand=True, spacing=5)
        self.move_to_cited_btn = ft.IconButton(icon=ft.icons.ARROW_FORWARD, on_click=self._move_to_cited, tooltip="Cite selected source(s)")
        self.move_to_available_btn = ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=self._move_to_available, tooltip="Remove citation(s)")
        self.create_group_btn = ft.ElevatedButton("Create Group", icon=ft.icons.GROUP_ADD, on_click=self._show_create_group_dialog)

        # Define the two possible layouts for this tab
        self.main_view = self._build_main_view()
        self.prompt_view = self._build_associate_file_prompt()

    def build(self) -> ft.Control:
        """
        Builds the tab content, which is a Stack containing both the main view
        and the prompt. The update_project_data method will control which is visible.
        """
        return ft.Stack(controls=[self.prompt_view, self.main_view])

    def _build_associate_file_prompt(self) -> ft.Column:
        """Returns the UI for prompting the user to select a .pptx file."""
        return ft.Column(
            [
                ft.Icon(name=ft.icons.SLIDESHOW_ROUNDED, size=50, color=ft.colors.ON_SURFACE_VARIANT),
                ft.Text("PowerPoint File Required", style=ft.TextThemeStyle.HEADLINE_SMALL),
                ft.Text("To cite sources, you must first associate a .pptx file with this project."),
                ft.Container(height=10),
                ft.FilledButton(
                    "Select Presentation File",
                    icon=ft.icons.ATTACH_FILE,
                    on_click=lambda e: self.controller.get_slides_for_current_project()
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            expand=True,
            visible=False, # Hidden by default
        )

    def _build_main_view(self) -> ft.Column:
        """Returns the main dual-list interface for citing sources."""
        return ft.Column([
            ft.Row([
                ft.Text("Citations for Slide:", style=ft.TextThemeStyle.TITLE_LARGE),
                self.slide_selector
            ]),
            ft.Divider(),
            ft.Row([
                ft.Column([
                    ft.Row([
                        ft.Text("Project Sources", weight=ft.FontWeight.BOLD),
                        self.create_group_btn
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(self.available_list, border=ft.border.all(1, ft.colors.OUTLINE), border_radius=8, padding=10, expand=True)
                ], expand=True),
                ft.Column([self.move_to_cited_btn, self.move_to_available_btn], alignment=ft.MainAxisAlignment.CENTER),
                ft.Column([
                    ft.Text("Cited on this Slide", weight=ft.FontWeight.BOLD),
                    ft.Container(self.cited_list, border=ft.border.all(1, ft.colors.OUTLINE), border_radius=8, padding=10, expand=True)
                ], expand=True),
            ], expand=True)
        ], expand=True, spacing=10, visible=False) # Hidden by default

    def update_project_data(self, project_data: dict, project_path: str):
        """
        Called by the parent view. This is now the main logic controller for the tab.
        It decides whether to show the prompt or the main citation view.
        """
        project = self.project_state_manager.current_project
        if not project: return
        
        ppt_path = project.metadata.get("powerpoint_path")

        if ppt_path:
            self.main_view.visible = True
            self.prompt_view.visible = False
            
            self.slide_data = self.controller.get_slides_for_current_project()
            self._populate_lists()
        else:
            self.main_view.visible = False
            self.prompt_view.visible = True

        if self.page:
            self.page.update()

    def _populate_lists(self):
        """The core logic to populate the available and cited lists."""
        project = self.project_state_manager.current_project
        if not self.slide_data:
            self.available_list.controls = [ft.Text("Could not load slide data. Please re-associate the PowerPoint file.", italic=True)]
            self.cited_list.controls.clear()
            self.slide_selector.options.clear()
            if self.page: self.page.update()
            return
        
        self.slide_selector.options = [
            ft.dropdown.Option(key=slide_id, text=f"{i+1}: {title}") 
            for i, (slide_id, title) in enumerate(self.slide_data)
        ]
        
        if self.current_slide_id is None or self.current_slide_id not in [s[0] for s in self.slide_data]:
             self.current_slide_id = self.slide_data[0][0]
        
        self.slide_selector.value = self.current_slide_id

        all_project_source_ids = {link.source_id for link in project.sources}
        citations = project.metadata.get("citations", {})
        cited_on_this_slide_ids = set(citations.get(str(self.current_slide_id), []))

        self.available_list.controls.clear()
        self.cited_list.controls.clear()

        for source_id in sorted(list(all_project_source_ids)):
            source_record = self.controller.data_service.get_source_by_id(source_id)
            if source_record:
                checkbox = ft.Checkbox(label=source_record.title, data=source_id)
                if source_id in cited_on_this_slide_ids:
                    self.cited_list.controls.append(checkbox)
                else:
                    self.available_list.controls.append(checkbox)
        
        if self.temp_groups:
            self.available_list.controls.append(ft.Divider())
            for group in self.temp_groups:
                self.available_list.controls.append(ft.Checkbox(
                    label=group.name, data=group, label_style=ft.TextStyle(weight=ft.FontWeight.BOLD, italic=True)
                ))
        
        if self.page:
            self.page.update()

    def _show_create_group_dialog(self, e):
        """Launches the dialog to create a new temporary source group."""
        project = self.project_state_manager.current_project
        if not project: return
        
        all_sources_records = [self.controller.data_service.get_source_by_id(link.source_id) for link in project.sources]
        source_checkboxes = [
            ft.Checkbox(label=rec.title, data=rec.id) for rec in all_sources_records if rec
        ]
        
        dialog = CreateSourceGroupDialog(all_sources=source_checkboxes, on_save=self._handle_create_group)
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _handle_create_group(self, name: str, source_ids: List[str]):
        """Callback that runs when a group is saved from the dialog."""
        new_group = TempSourceGroup(id=f"group_{uuid.uuid4()}", name=name, source_ids=source_ids)
        self.temp_groups.append(new_group)
        self._populate_lists()

    def _on_slide_change(self, e):
        """Handle slide selector change."""
        self.current_slide_id = e.control.value
        self._populate_lists()

    def _move_to_cited(self, e):
        """Move selected sources and sources from selected groups to cited."""
        final_ids_to_add = set()
        
        for cb in self.available_list.controls:
            if isinstance(cb, ft.Checkbox) and cb.value:
                if isinstance(cb.data, TempSourceGroup):
                    final_ids_to_add.update(cb.data.source_ids)
                else:
                    final_ids_to_add.add(cb.data)

        if final_ids_to_add:
            if hasattr(self.controller, 'add_citations_to_slide'):
                self.controller.add_citations_to_slide(self.current_slide_id, list(final_ids_to_add))

    def _move_to_available(self, e):
        """Move selected sources from cited to available."""
        selected_ids = [cb.data for cb in self.cited_list.controls if isinstance(cb, ft.Checkbox) and cb.value]
        if selected_ids:
            if hasattr(self.controller, 'remove_citations_from_slide'):
                self.controller.remove_citations_from_slide(self.current_slide_id, selected_ids)