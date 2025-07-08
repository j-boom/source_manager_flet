"""
Cite Sources Tab (Refactored)

Provides a dual-select interface for managing which sources are cited
on a per-slide basis within the project.
"""

import flet as ft
from .base_tab import BaseTab
from typing import List

class CiteSourcesTab(BaseTab):
    """Tab for managing source citations with a dual select interface."""
    
    def __init__(self, controller):
        super().__init__(controller)
        self.current_slide_index = 1
        
        # UI Components
        self.slide_selector = ft.Dropdown(on_change=self._on_slide_change, width=250, hint_text="Select a slide")
        self.available_list = ft.ListView(expand=True, spacing=5)
        self.cited_list = ft.ListView(expand=True, spacing=5)
        self.move_to_cited_btn = ft.IconButton(icon=ft.icons.ARROW_FORWARD, on_click=self._move_to_cited, tooltip="Cite selected source(s)")
        self.move_to_available_btn = ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=self._move_to_available, tooltip="Remove citation(s)")

    def build(self) -> ft.Control:
        """Build the cite sources tab content."""
        return ft.Column([
            ft.Row([
                ft.Text("Citations for Slide:", style=ft.TextThemeStyle.TITLE_LARGE),
                self.slide_selector
            ]),
            ft.Divider(),
            ft.Row([
                ft.Column([
                    ft.Text("Project Sources", weight=ft.FontWeight.BOLD),
                    ft.Container(self.available_list, border=ft.border.all(1, ft.colors.OUTLINE), border_radius=8, padding=10, expand=True)
                ], expand=True),
                ft.Column([self.move_to_cited_btn, self.move_to_available_btn], alignment=ft.MainAxisAlignment.CENTER),
                ft.Column([
                    ft.Text("Cited on this Slide", weight=ft.FontWeight.BOLD),
                    ft.Container(self.cited_list, border=ft.border.all(1, ft.colors.OUTLINE), border_radius=8, padding=10, expand=True)
                ], expand=True),
            ], expand=True)
        ], expand=True, spacing=10)

    def _update_view(self):
        """Refreshes the entire view based on the current project and slide."""
        # --- FIX: Access the .current_project attribute directly ---
        project = self.project_state_manager.current_project
        # --- END FIX ---

        if not project:
            self.slide_selector.options.clear()
            self.slide_selector.value = None
            self.available_list.controls.clear()
            self.cited_list.controls.clear()
            if self.page:
                self.page.update()
            return

        slide_count = project.metadata.get("slide_count", 10)
        self.slide_selector.options = [ft.dropdown.Option(str(i + 1)) for i in range(slide_count)]
        if self.slide_selector.value is None:
             self.slide_selector.value = "1"
        self.current_slide_index = int(self.slide_selector.value)

        all_project_source_ids = {link.source_id for link in project.sources}
        
        citations = project.metadata.get("citations", {})
        cited_on_this_slide_ids = set(citations.get(str(self.current_slide_index), []))

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
        
        if self.page:
            self.page.update()

    def _on_slide_change(self, e):
        """Handle slide selector change."""
        self.current_slide_index = int(e.control.value)
        self._update_view()

    def _move_to_cited(self, e):
        """Move selected sources from available to cited."""
        selected_ids = [cb.data for cb in self.available_list.controls if isinstance(cb, ft.Checkbox) and cb.value]
        if selected_ids:
            if hasattr(self.controller, 'add_citations_to_slide'):
                self.controller.add_citations_to_slide(self.current_slide_index, selected_ids)

    def _move_to_available(self, e):
        """Move selected sources from cited to available."""
        selected_ids = [cb.data for cb in self.cited_list.controls if isinstance(cb, ft.Checkbox) and cb.value]
        if selected_ids:
            if hasattr(self.controller, 'remove_citations_from_slide'):
                self.controller.remove_citations_from_slide(self.current_slide_index, selected_ids)

    def update_project_data(self, project_data: dict, project_path: str):
        """Called by the parent view to refresh the data."""
        self._update_view()
