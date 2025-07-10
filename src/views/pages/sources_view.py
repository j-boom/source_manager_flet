import flet as ft
from typing import Dict, Any, List
from functools import partial
from views import BaseView
from models import SourceRecord
from views.components import OnDeckCard, AppFAB
from config.source_types_config import get_filterable_fields, ALL_SOURCE_FIELDS

class SourcesView(BaseView):
    """A dedicated page for Browse, searching, and filtering all master sources."""

    def __init__(self, page: ft.Page, controller):
        super().__init__(page, controller)
        self.all_sources: List[SourceRecord] = []
        self.current_sources: List[SourceRecord] = []
        
        # UI for showing current project title
        self.project_title_header = ft.Text(visible=False, weight=ft.FontWeight.BOLD, color=ft.colors.PRIMARY)

        # UI Components
        self.filter_controls: Dict[str, ft.TextField] = {}
        self.active_filter_chips = ft.Row(wrap=True)
        self.filter_controls_column = ft.Column(spacing=10)
        self.results_list = ft.ListView(expand=True, spacing=10, padding=ft.padding.only(top=10))

    def build(self) -> ft.Control:
        """Builds the UI for the sources browser page."""
        self._initialize_view()

        filters_panel = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Filters", style=ft.TextThemeStyle.TITLE_MEDIUM),
                    ft.Divider(),
                    self.filter_controls_column,
                    ft.Container(height=10),
                    ft.Row(
                        [
                            ft.ElevatedButton("Clear", on_click=self._clear_all_filters, expand=True),
                            ft.FilledButton("Apply", on_click=self._apply_all_filters, expand=True),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    )
                ],
                spacing=10,
            ),
            width=280,
            padding=15,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=8,
        )

        results_panel = ft.Column(
            [
                ft.Row([
                    ft.Text("Master Source Library", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                    self.project_title_header,
                ], spacing=10),
                ft.Text("Use the filters on the left to search the library.", color=ft.colors.ON_SURFACE_VARIANT),
                ft.Divider(),
                self.active_filter_chips,
                ft.Container(self.results_list, expand=True),
            ],
            expand=True,
            spacing=10,
        )

        main_content = ft.Container(
            content=ft.Row([filters_panel, results_panel], expand=True, spacing=20),
            padding=20,
            expand=True,
        )

        # Add floating action button using AppFAB component
        fab = AppFAB.create_add_source_fab(self.controller)

        return ft.Stack(
            [
                main_content,
                ft.Container(
                    fab,
                    right=20,
                    bottom=20,
                    alignment=ft.alignment.bottom_right,
                )
            ],
            expand=True,
        )

    def _initialize_view(self):
        """Fetches data and builds the dynamic filter controls. Called once."""
        if not self.all_sources:
            self.all_sources = self.controller.data_service.get_all_master_sources()
            self.current_sources = self.all_sources
            self._build_filter_controls()
            # Initial UI update based on project state
            self.update_view_for_project_state()

    def update_view_for_project_state(self):
        """Updates the view based on the current project state."""
        project = self.controller.project_state_manager.current_project
        if project:
            self.project_title_header.value = f"| Adding to: {project.title}"
            self.project_title_header.visible = True
        else:
            self.project_title_header.visible = False
        
        # Re-render the list of sources to show/hide add buttons
        self._update_results_list(self.current_sources)
        if self.page:
            self.page.update()

    def _build_filter_controls(self):
        """Dynamically creates filter TextFields based on config and source data."""
        self.filter_controls_column.controls.clear()
        self.filter_controls = {}
        
        # Create a TextField for each filterable field
        # Add a text field for the title first
        title_field = ft.TextField(label="Title", border_radius=8, dense=True)
        self.filter_controls["title"] = title_field
        self.filter_controls_column.controls.append(title_field)
        
        # Add one for authors
        authors_field = ft.TextField(label="Authors", border_radius=8, dense=True)
        self.filter_controls["authors"] = authors_field
        self.filter_controls_column.controls.append(authors_field)
        
        # Add fields from the config
        for field_config in get_filterable_fields():
            field = ft.TextField(label=field_config.label, border_radius=8, dense=True)
            self.filter_controls[field_config.name] = field
            self.filter_controls_column.controls.append(field)

    def _apply_all_filters(self, e):
        """Applies all active filters from the text fields."""
        filtered_sources = self.all_sources
        self.active_filter_chips.controls.clear()

        for field_name, control in self.filter_controls.items():
            search_term = control.value.lower().strip()
            if not search_term: continue
                
            chip = ft.Chip(
                label=ft.Text(f"{control.label}: '{search_term}'"),
                data=field_name,
                on_delete=self._remove_filter_chip,
            )
            self.active_filter_chips.controls.append(chip)

            if field_name == "authors":
                 filtered_sources = [s for s in filtered_sources if s.authors and any(search_term in author.lower() for author in s.authors)]
            else:
                filtered_sources = [s for s in filtered_sources if search_term in str(getattr(s, field_name, '')).lower()]

        self.current_sources = filtered_sources # Store the current filtered list
        self._update_results_list(self.current_sources)
        self.page.update()
        
    def _remove_filter_chip(self, e):
        """Removes a filter when a chip's delete icon is clicked."""
        field_to_remove = e.control.data
        # Clear the corresponding text field
        if field_to_remove in self.filter_controls:
            self.filter_controls[field_to_remove].value = ""
        # Re-apply all filters
        self._apply_all_filters(e)
            
    def _clear_all_filters(self, e):
        """Resets all filter text fields and clears results."""
        for control in self.filter_controls.values():
            control.value = ""
        
        self.active_filter_chips.controls.clear()
        self.current_sources = self.all_sources
        self._update_results_list(self.current_sources)
        self.page.update()

    def _update_results_list(self, sources: List[SourceRecord]):
        """Clears and repopulates the results list."""
        project = self.controller.project_state_manager.current_project
        self.results_list.controls.clear()
        if sources:
            for source in sorted(sources, key=lambda s: s.title):
                # We just create the card. Its default context is "library",
                # which correctly calls 'add_source_to_on_deck'.
                self.results_list.controls.append(
                    OnDeckCard(
                        source=source,
                        controller=self.controller,
                        show_add_button=bool(project)
                        # No context needed, it defaults to "library"
                    )
                )
        else:
            self.results_list.controls.append(ft.Text("No sources match your criteria.", italic=True, text_align=ft.TextAlign.CENTER))