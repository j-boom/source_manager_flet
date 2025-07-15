import flet as ft
from typing import Dict, List
from ..base_view import BaseView
from models.source_models import SourceRecord
from ..components.cards.on_deck_card import OnDeckCard
from config.source_types_config import get_filterable_fields

class SourcesView(BaseView):
    """
    A view for browsing, searching, and filtering the master source library.
    Allows users to add sources to the "On Deck" list of an active project.
    """

    def __init__(self, controller):
        super().__init__(controller)
        self.all_sources: List[SourceRecord] = []
        self.current_sources: List[SourceRecord] = []
        self.selected_country: str = "All"

        # UI Components
        self.project_title_header = ft.Text(visible=False, weight=ft.FontWeight.BOLD, color=ft.colors.PRIMARY)
        self.country_dropdown = ft.Dropdown(
            label="Country/Region",
            width=200,
            on_change=self._on_country_changed,
            border_radius=8,
        )
        self.filter_controls: Dict[str, ft.TextField] = {}
        self.active_filter_chips = ft.Row(wrap=True)
        self.filter_controls_column = ft.Column(spacing=10, scroll=ft.ScrollMode.ADAPTIVE)
        self.results_list = ft.ListView(expand=True, spacing=10, padding=ft.padding.only(top=10))

    def get_content(self) -> ft.Control:
        """Builds the UI for the sources browser page."""
        self._initialize_view_data()

        filters_panel = self._build_filters_panel()
        results_panel = self._build_results_panel()

        return ft.Container(
            content=ft.Row([filters_panel, results_panel], expand=True, spacing=20),
            padding=20,
            expand=True,
        )

    def _build_filters_panel(self) -> ft.Container:
        """Builds the left-hand panel containing filter controls."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Filters", style=ft.TextThemeStyle.TITLE_MEDIUM),
                    ft.Divider(),
                    ft.Container(self.filter_controls_column, expand=True),
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

    def _build_results_panel(self) -> ft.Column:
        """Builds the main content panel for displaying source results."""
        add_source_button = ft.ElevatedButton(
            text="Add New Source",
            icon=ft.icons.ADD,
            on_click=self._on_add_source_clicked,
        )

        return ft.Column(
            [
                ft.Row([
                    ft.Text("Master Source Library", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                    self.project_title_header,
                    ft.Container(expand=True),
                    self.country_dropdown,
                    add_source_button,
                ], spacing=10, alignment=ft.MainAxisAlignment.START),
                ft.Text("Use the filters on the left to search the library.", color=ft.colors.ON_SURFACE_VARIANT),
                ft.Divider(),
                self.active_filter_chips,
                ft.Container(self.results_list, expand=True),
            ],
            expand=True,
            spacing=10,
        )

    def _initialize_view_data(self):
        """Fetches initial data and builds dynamic controls. Called once per view load."""
        self._populate_country_dropdown()
        self._load_sources_for_country(self.selected_country)
        self._build_filter_controls()
        self.update_view()

    def update_view(self):
        """Updates the view based on the current project state."""
        project = self.controller.project_controller.get_current_project()
        if project:
            self.project_title_header.value = f"| Adding to: {project.name}"
            self.project_title_header.visible = True
        else:
            self.project_title_header.visible = False
        
        self._update_results_list()
        if self.page:
            self.page.update()

    def _populate_country_dropdown(self):
        """Populates the country dropdown using data from the SourceController."""
        available_countries = self.controller.source_controller.get_available_countries()
        self.country_dropdown.options = [ft.dropdown.Option("All", "All Countries")]
        for country in sorted(available_countries):
            self.country_dropdown.options.append(ft.dropdown.Option(country, country))
        self.country_dropdown.value = self.selected_country

    def _on_country_changed(self, e):
        """Handles country dropdown selection change."""
        self.selected_country = e.control.value
        self._load_sources_for_country(self.selected_country)
        self._clear_all_filters(e)

    def _load_sources_for_country(self, country: str):
        """Loads sources for the selected country via the SourceController."""
        if country == "All":
            self.all_sources = self.controller.source_controller.get_all_source_records()
        else:
            self.all_sources = self.controller.source_controller.get_sources_by_country(country)
        self.current_sources = self.all_sources

    def _on_add_source_clicked(self, e):
        """Handles the 'Add New Source' button click, delegating to the DialogController."""
        initial_data = {}
        if self.selected_country != "All":
            initial_data['region'] = self.selected_country

        self.controller.dialog_controller.open_new_source_dialog(e, initial_data=initial_data)

    def _build_filter_controls(self):
        """Dynamically creates filter TextFields based on config."""
        self.filter_controls_column.controls.clear()
        self.filter_controls = {}
        
        # Add a text field for the title first
        title_field = ft.TextField(label="Title", border_radius=8, dense=True)
        self.filter_controls["title"] = title_field
        self.filter_controls_column.controls.append(title_field)
        
        # Add one for authors
        authors_field = ft.TextField(label="Authors (comma-separated)", border_radius=8, dense=True)
        self.filter_controls["authors"] = authors_field
        self.filter_controls_column.controls.append(authors_field)
        
        for field_config in get_filterable_fields():
            field = ft.TextField(label=field_config.label, border_radius=8, dense=True)
            self.filter_controls[field_config.name] = field
            self.filter_controls_column.controls.append(field)

    def _apply_all_filters(self, e):
        """Applies all active filters from the text fields."""
        filtered_sources = self.all_sources
        self.active_filter_chips.controls.clear()

        for field_name, control in self.filter_controls.items():
            search_term = (control.value or "").lower().strip()
            if not search_term:
                continue

            self.active_filter_chips.controls.append(
                ft.Chip(
                    label=ft.Text(f"{control.label}: '{control.value.strip()}'"),
                    data=field_name,
                    on_delete=self._remove_filter_chip,
                )
            )

            if field_name == "authors":
                search_terms = [term.strip() for term in search_term.split(',')]
                filtered_sources = [
                    s for s in filtered_sources if s.authors and 
                    any(any(st in author.lower() for st in search_terms) for author in s.authors)
                ]
            else:
                filtered_sources = [s for s in filtered_sources if search_term in str(getattr(s, field_name, '') or '').lower()]

        self.current_sources = filtered_sources
        self._update_results_list()
        self.update()
        
    def _remove_filter_chip(self, e):
        """Removes a filter when a chip's delete icon is clicked."""
        if e.control.data in self.filter_controls:
            self.filter_controls[e.control.data].value = ""
        self._apply_all_filters(e)
            
    def _clear_all_filters(self, e):
        """Resets all filter text fields and clears results."""
        for control in self.filter_controls.values():
            control.value = ""
        self.active_filter_chips.controls.clear()
        self.current_sources = self.all_sources
        self._update_results_list()
        self.update()

    def _update_results_list(self):
        """Clears and repopulates the results list with the current sources."""
        project = self.controller.project_controller.get_current_project()
        self.results_list.controls.clear()
        
        if self.current_sources:
            for source in sorted(self.current_sources, key=lambda s: s.title):
                self.results_list.controls.append(
                    OnDeckCard(
                        source=source,
                        controller=self.controller,
                        show_add_button=bool(project)
                    )
                )
        else:
            self.results_list.controls.append(ft.Text("No sources match your criteria.", italic=True, text_align=ft.TextAlign.CENTER))
