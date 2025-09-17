import flet as ft
from typing import Dict, Any
from .base_tab import BaseTab
from views.components import ProjectSourceCard, OnDeckCard
from views.components.dialogs import AddSourceToProjectDialog


class ProjectSourcesTab(BaseTab):
    """A tab for managing project sources with a user-curated 'On Deck' list."""

    def __init__(self, controller):
        super().__init__(controller)
        self.dragged_source_id: str | None = None
        # --- UI Components ---
        self.on_deck_list = ft.ListView(
            expand=True, spacing=5, padding=ft.padding.only(top=10)
        )
        self.project_sources_list = ft.Column(
            expand=True, spacing=5, scroll=ft.ScrollMode.ADAPTIVE
        )
        self.project_actions_menu = ft.PopupMenuButton(
            icon=ft.icons.MORE_VERT,
            tooltip="Project Actions",
            items=[
                ft.PopupMenuItem(
                    text="Import sources from another project",
                    icon=ft.icons.CONTENT_COPY,
                    # on_click will be implemented in a future step
                ),
            ],
        )
        # --- Boilerplate Components ---
        self.boilerplate_dropdown = ft.Dropdown(
            label="Add Boilerplate Source",
            hint_text="Select a source...",
            options=[],
            width=350,
            visible=False,
            on_change=self._on_boilerplate_selection_change
        )
        self.add_boilerplate_button = ft.ElevatedButton(
            "Add to Project",
            icon=ft.icons.ADD_CIRCLE_OUTLINE,
            on_click=self._on_add_boilerplate_clicked,
            disabled=True,
            visible=False
        )
        self._load_boilerplate_sources()

    def build(self) -> ft.Control:
        """Builds the UI for the project sources tab."""
        on_deck_column = ft.Column(
            [
                ft.Text("On Deck", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.Text(
                    "Sources selected for this project.",
                    italic=True,
                    size=12,
                    color=ft.colors.ON_SURFACE_VARIANT,
                ),
                ft.Divider(),
                ft.Container(
                    self.on_deck_list,
                    expand=True,
                    border_radius=ft.border_radius.all(8),
                ),
            ],
            width=350,
            spacing=5,
        )

        project_sources_header = ft.Row(
            controls=[
                ft.Text(
                    "Project Sources",
                    theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                    expand=True,
                ),
                ft.ElevatedButton(
                    text="Add Source",
                    icon=ft.icons.ADD_ROUNDED,
                    on_click=lambda _: self.controller.dialog_controller.open_new_source_dialog(
                        from_project_sources_tab=True
                    ),
                    tooltip="Add a new source to the master list",
                ),
                self.project_actions_menu,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        project_sources_column = ft.Column(
            [
                ft.Container(project_sources_header, padding=ft.padding.only(right=5)),
                ft.Text(
                    "Sources currently included in this project. (Drag to Reorder)",
                    italic=True,
                    size=12,
                    color=ft.colors.ON_SURFACE_VARIANT,
                ),
                ft.Divider(),
                ft.Container(self.project_sources_list, expand=True),
            ],
            expand=True,
            spacing=5,
        )

        main_content = ft.Row(
            [
                ft.Container(
                    on_deck_column,
                    padding=10,
                    bgcolor=ft.colors.SURFACE_VARIANT,
                    border_radius=8,
                ),
                project_sources_column,
            ],
            expand=True,
            spacing=20,
        )
        
        boilerplate_tool = ft.Row(
            [self.boilerplate_dropdown, self.add_boilerplate_button],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )

        return ft.Column(
            [boilerplate_tool, ft.Divider(height=15), main_content],
            expand=True,
            spacing=10,
        )

    def _update_view(self):
        """Refreshes both lists based on the current project's state."""
        project = self.controller.project_state_manager.current_project
        if not project:
            return

        self.on_deck_list.controls.clear()
        self.project_sources_list.controls.clear()

        # --- Data Fetching ---
        on_deck_ids = project.metadata.get("on_deck_sources", [])
        project_source_ids = {link.source_id for link in project.sources}
        source_usage_map = self.controller.powerpoint_controller.get_source_usage_map()

        # --- Populate "On Deck" List ---
        for source_id in on_deck_ids:
            if source_id not in project_source_ids:
                source = self.controller.source_service.get_source_by_id(source_id)
                if source:
                    card = OnDeckCard(
                        source=source,
                        controller=self.controller,
                        show_add_button=True,
                        show_remove_button=True,
                        context="project_tab", # This context adds the source to the project
                    )
                    self.on_deck_list.controls.append(card)

        # --- Populate "Project Sources" List ---
        for link in project.sources:
            source = self.controller.source_service.get_source_by_id(link.source_id)
            if source:
                used_on_slides = source_usage_map.get(link.source_id, [])
                card = ProjectSourceCard(
                    source=source, link=link, controller=self.controller, used_on_slides=used_on_slides
                )
                self.project_sources_list.controls.append(
                    ft.DragTarget(
                        group="project_sources",
                        content=ft.Draggable(
                            group="project_sources",
                            content=card,
                            data=link.source_id,
                            on_drag_start=self._on_drag_start,
                        ),
                        data=link.source_id,
                        on_will_accept=self._drag_will_accept,
                        on_accept=self._drag_accept,
                        on_leave=self._drag_leave,
                    )
                )

        # --- Handle Empty States ---
        if not self.project_sources_list.controls:
            self.project_sources_list.controls.append(
                ft.Text(
                    "No sources added yet.", italic=True, text_align=ft.TextAlign.CENTER
                )
            )
        if not self.on_deck_list.controls:
            self.on_deck_list.controls.append(
                ft.Text(
                    "Add sources from the main 'Sources' page or use boilerplate sources.",
                    text_align=ft.TextAlign.CENTER,
                )
            )

    # --- Boilerplate Source Methods ---

    def _load_boilerplate_sources(self):
        """Fetches boilerplate sources and populates the dropdown."""
        all_boilerplate_sources = self.controller.source_controller.get_boilerplate_sources()

        # --- Filter out sources that require project-specific link data ---
        # This prevents adding sources that need more info directly from this simple dropdown.
        filtered_sources = []
        for source in all_boilerplate_sources:
            # Get the configuration for the source's type
            source_type_config = self.controller.admin_controller.get_source_type_config(source.source_type)
            
            # Check if any field in the config has 'storage_scope' set to 'link'
            has_link_fields = any(
                field.get("storage_scope") == "link"
                for field in source_type_config.get("fields", [])
            )
            
            # Only include sources that do NOT have link-specific fields
            if not has_link_fields:
                filtered_sources.append(source)

        if filtered_sources:
            self.boilerplate_dropdown.options = [
                ft.dropdown.Option(key=source.id, text=source.display_name)
                for source in sorted(filtered_sources, key=lambda s: s.display_name)
            ]
            self.boilerplate_dropdown.visible = True
            self.add_boilerplate_button.visible = True
        else:
            self.boilerplate_dropdown.visible = False
            self.add_boilerplate_button.visible = False

        self.controller.update_view()

    def _on_boilerplate_selection_change(self, e: ft.ControlEvent):
        """Enables or disables the add button based on dropdown selection."""
        self.add_boilerplate_button.disabled = not e.control.value
        self.controller.update_view()

    def _on_add_boilerplate_clicked(self, e: ft.ControlEvent):
        """Handles the click event for adding a boilerplate source."""
        source_id = self.boilerplate_dropdown.value
        if source_id:
            # The controller method will trigger a view update, so no direct update is needed here.
            self.controller.source_controller.add_boilerplate_source_to_project(source_id)
            self.boilerplate_dropdown.value = None
            self.add_boilerplate_button.disabled = True

    def _on_drag_start(self, e: ft.DragStartEvent):
        """Stores the ID of the source being dragged."""
        self.dragged_source_id = e.control.data

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

        src_id_being_dragged = self.dragged_source_id
        target_id = e.control.data

        if src_id_being_dragged == target_id:
            e.control.update()
            return

        source_links = project.sources
        dragged_link = next(
            (link for link in source_links if link.source_id == src_id_being_dragged),
            None,
        )

        target_index = -1
        for i, link in enumerate(source_links):
            if link.source_id == target_id:
                target_index = i
                break

        if dragged_link and target_index != -1:
            source_links.remove(dragged_link)
            source_links.insert(target_index, dragged_link)
            self.controller.project_service.save_project(project)
            self.controller.update_view()
        else:
            e.control.update()

    def update_project_data(self, project_data: Dict[str, Any], project_path: str):
        """Called by the parent view to refresh the data."""
        self._update_view()

    def _show_add_to_project_dialog(self, source_id: str):
        source = self.controller.source_controller.get_source_record_by_id(source_id)
        if not source:
            self.controller.show_error_message("Could not find source to add.")
            return

        def on_save(link_data: Dict[str, Any]):
            self.controller.source_controller.add_source_to_project(source_id, link_data)
            self._update_view()

        dialog = AddSourceToProjectDialog(
            page=self.page, 
            source_type=source.source_type,
            dialog_controller=self.controller.dialog_controller,
            on_save=on_save
        )
        dialog.show()
