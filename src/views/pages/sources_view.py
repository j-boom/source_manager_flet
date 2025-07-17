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

    def __init__(self, page, controller):
        super().__init__(page=page, controller=controller)
        self.all_sources: List[SourceRecord] = []
        self.current_sources: List[SourceRecord] = []
        self.selected_country: str = "All"

        # UI Components
        self.project_title_header = ft.Text(
            visible=False, weight=ft.FontWeight.BOLD, color=ft.colors.PRIMARY
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
        self.results_list = ft.ListView(
            expand=True, spacing=10, padding=ft.padding.only(top=10)
        )

        self.directions_prompt = "Use the filters on the left to search the library." if self.controller.project_state_manager.current_project else "Select a project to add sources to your 'On Deck' list."

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
                                "Apply", on_click=self._apply_all_filters, expand=True
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
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
                    color=ft.colors.ON_SURFACE_VARIANT,
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
        project = self.controller.project_controller.get_current_project()
        if project:
            self.project_title_header.value = f"| Adding to: {project.project_title}"
            self.project_title_header.visible = True
        else:
            self.project_title_header.visible = False

        # Re-fetch the sources for the currently selected country to get the latest data.
        self._load_sources_for_country(self.selected_country)

        # Re-apply any active filters to the new data, which will also
        # call _update_results_list() to refresh the list view.
        self._apply_all_filters(None)

        # Update the page to show the changes.
        if self.page:
            self.page.update()

    def _populate_country_dropdown(self):
        """Populates the country dropdown using data from the SourceController."""
        available_countries = (
            self.controller.source_controller.get_available_countries()
        )
        self.country_dropdown.options = [ft.dropdown.Option("All", "All Countries")]
        for country in sorted(available_countries):
            self.country_dropdown.options.append(ft.dropdown.Option(country, country))
        self.country_dropdown.value = self.selected_country

    def _on_country_changed(self, e):
        """
        Handles country dropdown changes by reloading data and resetting the view.
        """
        self.selected_country = e.control.value

        # 1. Load the sources for the newly selected country.
        self._load_sources_for_country(self.selected_country)

        # 2. Reset the filter state completely.
        for control in self.filter_controls.values():
            control.value = ""
        self.active_filter_chips.controls.clear()

        # 3. Set the list to display to be the complete, unfiltered list for the new country.
        self.current_sources = self.all_sources

        # 4. Update the UI to reflect these changes.
        self._update_results_list()
        if self.page:
            self.page.update()

    def _load_sources_for_country(self, country: str):
        """Loads sources for the selected country via the SourceController."""
        if country == "All":
            self.all_sources = (
                self.controller.source_controller.get_all_source_records()
            )
        else:
            self.all_sources = self.controller.source_controller.get_sources_by_country(
                country
            )
        self.current_sources = self.all_sources

    def _on_add_source_clicked(self, e):
        """Handles the 'Add New Source' button click, delegating to the DialogController."""
        country_to_pass = (
            self.selected_country if self.selected_country != "All" else None
        )
        self.controller.dialog_controller.open_new_source_dialog(
            target_country_from_view=country_to_pass
        )

    def _build_filter_controls(self):
        """
        Dynamically creates filter TextFields based on the central config.
        """
        self.filter_controls_column.controls.clear()
        self.filter_controls = {}

        # Get all fields marked as 'is_filterable' from the config
        filterable_fields = get_filterable_fields()

        # Create a text field for each one
        for field_config in filterable_fields:
            field = ft.TextField(label=field_config.label, border_radius=8, dense=True)
            self.filter_controls[field_config.name] = field
            self.filter_controls_column.controls.append(field)

    def _apply_all_filters(self, e):
        """Applies all active filters from the text fields with improved logic."""
        filtered_sources = self.all_sources[
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

            # Split the search term into individual words
            search_words = search_term.split()

            # Filter the list, keeping only sources that match all search words
            if field_name == "authors":
                # Special handling for authors list
                filtered_sources = [
                    s
                    for s in filtered_sources
                    if s.authors
                    and all(
                        any(word in author.lower() for author in s.authors)
                        for word in search_words
                    )
                ]
            else:
                # General handling for other text fields
                filtered_sources = [
                    s
                    for s in filtered_sources
                    if all(
                        word in str(getattr(s, field_name, "") or "").lower()
                        for word in search_words
                    )
                ]

        self.current_sources = filtered_sources
        self._update_results_list()

        # This check prevents an error if called from update_view
        if e is not None and self.page:
            self.page.update()

    def _remove_filter_chip(self, e):
        """Removes a filter when a chip's delete icon is clicked."""
        if e.control.data in self.filter_controls:
            self.filter_controls[e.control.data].value = ""
        self._apply_all_filters(e)

    def _clear_all_filters(self, e):
        """
        Directly clears all filter controls and resets the view to show all sources.
        """
        # 1. Clear the input value of each filter text field.
        for control in self.filter_controls.values():
            control.value = ""

        # 2. Remove all the "active filter" chips from the UI.
        self.active_filter_chips.controls.clear()

        # 3. Reset the list of currently displayed sources to the full list.
        self.current_sources = self.all_sources

        # 4. Refresh the list view with the full, unfiltered list of sources.
        self._update_results_list()

        # 5. Update the page to make all changes visible.
        if self.page:
            self.page.update()

    def _update_results_list(self):
        """Clears and repopulates the results list with the current sources."""
        project = self.controller.project_controller.get_current_project()
        self.results_list.controls.clear()

        # Get a list of source IDs already associated with the project
        associated_source_ids = set()
        if project:
            on_deck_ids = set(project.metadata.get("on_deck_sources", []))
            project_source_ids = {link.source_id for link in project.sources}
            associated_source_ids = on_deck_ids.union(project_source_ids)

        # Filter out associated sources
        display_sources = [
            source for source in self.current_sources 
            if source.id not in associated_source_ids
        ]

        if display_sources:
            for source in sorted(display_sources, key=lambda s: s.title):
                self.results_list.controls.append(
                    OnDeckCard(
                        source=source,
                        controller=self.controller,
                        show_add_button=bool(project),
                    )
                )
        else:
            self.results_list.controls.append(
                ft.Text(
                    "No sources match your criteria.",
                    italic=True,
                    text_align=ft.TextAlign.CENTER,
                )
            )