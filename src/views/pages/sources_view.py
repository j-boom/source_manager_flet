import flet as ft
from typing import Dict, List, Optional, Any
from ..base_view import BaseView
from ..components import OnDeckCard
from src.models.source_models import SourceRecord


class SourcesView(BaseView):
    """
    A view for browsing, searching, and filtering the entire master source library.
    """
    def __init__(self, page: ft.Page, controller):
        super().__init__(page, controller)
        self.country_sources: List[SourceRecord] = []
        self.current_sources: List[SourceRecord] = []
        self.selected_country: Optional[str] = None

        # --- UI Components ---
        self.project_title_header = ft.Text(
            visible=False, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY
        )
        self.country_dropdown = ft.Dropdown(
            label="Country",
            width=200,
            on_change=self._on_country_changed,
            border_radius=8,
        )
        self.filter_controls: Dict[str, ft.TextField] = {}
        self.active_filter_chips = ft.Row(wrap=True)
        self.filter_controls_column = ft.Column(
            spacing=10, scroll=ft.ScrollMode.ADAPTIVE
        )
        self.results_list = ft.ListView(expand=True, spacing=10)
        self.directions_prompt = "Use the filters on the left to search the library."

    def build(self) -> ft.Control:
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
                    ft.Text("Filters", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                    ft.Divider(),
                    ft.Container(self.filter_controls_column, expand=True),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "Clear", on_click=self._clear_all_filters, expand=True
                            ),
                            ft.FilledButton(
                                "Apply",
                                on_click=self._apply_all_filters,
                                expand=True,
                                icon=ft.Icons.SEARCH,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
            ),
            width=280,
            padding=15,
            bgcolor=ft.Colors.ON_SURFACE_VARIANT,
            border_radius=8,
        )

    def _build_results_panel(self) -> ft.Column:
        """Builds the main content panel for displaying source results."""
        add_source_button = ft.ElevatedButton(
            text="Add New Source",
            icon=ft.Icons.ADD,
            on_click=self._on_add_source_clicked,
        )

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            "Master Source Library",
                            theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                        ),
                        self.project_title_header,
                        ft.Container(expand=True),
                        self.country_dropdown,
                        add_source_button,
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Text(
                    self.directions_prompt,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
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
        """
        Updates the view by re-fetching source data and refreshing the UI.
        """
        project = self.controller.project_state_manager.current_project
        if project:
            self.project_title_header.value = f"| Adding to: {project.project_title}"
            self.project_title_header.visible = True
            self.directions_prompt = "Use the filters on the left to search the library."
        else:
            self.project_title_header.visible = False
            self.directions_prompt = "Select a project to add sources to your 'On Deck' list."

        # Re-fetch the sources for the currently selected country to get the latest data.
        self._load_sources_for_country(self.selected_country)

        # Re-apply any active filters to the new data, which will also
        # call _update_results_list() to refresh the list view.
        self._apply_all_filters()

    def _populate_country_dropdown(self):
        """Populates the country dropdown using data from the SourceController."""
        available_countries = (
            self.controller.source_controller.get_available_countries()
        )
        self.country_dropdown.options.clear()
        for country in sorted(available_countries):
            self.country_dropdown.options.append(ft.dropdown.Option(country, country))

        # If no country is selected yet, or the selected one is no longer valid,
        # default to the first available country.
        if available_countries and (
            self.selected_country is None
            or self.selected_country not in available_countries
        ):
            self.selected_country = sorted(available_countries)[0]

        self.country_dropdown.value = self.selected_country

    def _on_country_changed(self, e: ft.ControlEvent):
        """
        Handles country dropdown changes by reloading data and resetting the view.
        """
        self.selected_country = e.control.value

        # 1. Load the sources for the newly selected country.
        self._load_sources_for_country(self.selected_country)

        # 2. Reset the filter state completely.
        self._clear_all_filters()

        # 3. Set the list to display to be the complete, unfiltered list for the new country.
        self.current_sources = self.country_sources

        # 4. Update the UI to reflect these changes.
        self._clear_all_filters(e=None) # This will clear fields and trigger a page update

    def _load_sources_for_country(self, country: Optional[str]):
        """Loads sources for the selected country via the SourceController."""
        if country:
            self.country_sources = self.controller.source_controller.get_sources_by_country(
                country
            )
        else:
            # If no country is selected (e.g., no countries exist), the list is empty.
            self.country_sources = []
        self.current_sources = self.country_sources

    def _on_add_source_clicked(self, e):
        """Handles the 'Add New Source' button click, delegating to the DialogController."""
        country_to_pass = self.selected_country
        self.controller.dialog_controller.open_new_source_dialog(
            target_country_from_view=country_to_pass
        )

    def _get_all_filterable_fields(self) -> List[Dict[str, Any]]:
        """Scans all source types and aggregates all unique, core fields."""
        all_fields = {}
        source_types = self.controller.admin_controller.get_all_source_types()
        for _, type_config in source_types:
            for field_data in type_config.get("fields", []):
                # Only include fields that are part of the master record
                if field_data.get("storage_scope", "core") == "core":
                    if field_data["name"] not in all_fields:
                        all_fields[field_data["name"]] = {
                            "name": field_data["name"],
                            "label": field_data["label"],
                        }
        # Sort fields alphabetically by their user-facing label
        return sorted(all_fields.values(), key=lambda f: f["label"])

    def _build_filter_controls(self):
        """
        Dynamically creates filter TextFields based on the central config.
        """
        self.filter_controls_column.controls.clear()
        self.filter_controls = {}

        filterable_fields = self._get_all_filterable_fields()

        # Create a text field for each one
        for field_config in filterable_fields:
            field = ft.TextField(
                label=field_config["label"], border_radius=8, dense=True
            )
            self.filter_controls[field_config["name"]] = field
            self.filter_controls_column.controls.append(field)

    def _apply_all_filters(self, e=None):
        """Applies all active filters from the text fields. Does NOT update the page."""
        filtered_sources = self.country_sources[
            :
        ]  # Start with a copy of all sources for the country
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

            # Split the search term into individual words to allow for more flexible matching.
            search_words = search_term.split()
            if not search_words:
                continue

            # Filter the list, keeping only sources where all search words are present in the field.
            temp_results = []
            for source in filtered_sources:
                field_value_str = str(source.get_field_value(field_name, "")).lower()
                if all(word in field_value_str for word in search_words):
                    temp_results.append(source)
            filtered_sources = temp_results

        self.current_sources = filtered_sources
        self._update_results_list()
        # The event handler that calls this method is responsible for updating the page.

    def _remove_filter_chip(self, e):
        """Removes a filter when a chip's delete icon is clicked."""
        if e.control.data in self.filter_controls:
            self.filter_controls[e.control.data].value = ""
        # Re-apply all filters to update the view
        self._apply_all_filters()
        self.page.update()

    def _clear_all_filters(self, e=None):
        """
        Clears all filter controls and re-applies filters to reset the view.
        """
        # 1. Clear the input value of each filter text field.
        for control in self.filter_controls.values():
            control.value = ""

        # 2. Re-apply the (now empty) filters to reset the view.
        self._apply_all_filters()
        self.page.update()

    def _update_results_list(self):
        """Clears and repopulates the results list with the current sources."""
        project = self.controller.project_state_manager.current_project
        self.results_list.controls.clear()

        # Get a list of source IDs already associated with the project
        associated_source_ids = set()
        if project:
            on_deck_ids = set(project.metadata.get("on_deck_sources", []))
            project_source_ids = {link.source_id for link in project.sources}
            associated_source_ids = on_deck_ids.union(project_source_ids)

        # Filter out associated sources
        display_sources = [
            source
            for source in self.current_sources
            if source.id not in associated_source_ids
        ]

        if display_sources:
            for source in sorted(display_sources, key=lambda s: s.display_name):
                self.results_list.controls.append(
                    OnDeckCard(
                        source=source,
                        controller=self.controller,
                        show_add_button=bool(project),
                        context="library",
                    )
                )
        else:
            self.results_list.controls.append(
                ft.Text(
                    "No sources match your criteria, or all matching sources are already in the project.",
                    italic=True,
                    text_align=ft.TextAlign.CENTER,
                )
            )