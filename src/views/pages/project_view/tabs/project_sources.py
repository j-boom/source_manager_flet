import flet as ft
from typing import Dict, Any
from .base_tab import BaseTab
from models.project_models import ProjectSourceLink
from models.source_models import SourceRecord
from views.components import ProjectSourceCard
from views.components import OnDeckCard

class ProjectSourcesTab(BaseTab):
    """A tab for managing project sources with a two-column layout and drag-and-drop."""

    def __init__(self, controller):
        super().__init__(controller)
        self.on_deck_list = ft.ListView(expand=True, spacing=5, padding=ft.padding.only(top=10))
        self.project_sources_list = ft.ListView(expand=True, spacing=10, padding=ft.padding.only(top=10))

    def build(self) -> ft.Control:
        """Builds the UI for the project sources tab."""
        
        on_deck_column = ft.Column(
            [
                ft.Text("On Deck", style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.Text("Master sources available for this project's region.", italic=True, size=12, color=ft.colors.ON_SURFACE_VARIANT),
                ft.Divider(),
                ft.Container(self.on_deck_list, expand=True, border_radius=ft.border_radius.all(8)),
            ],
            width=350,
            spacing=5,
        )

        project_sources_column = ft.Column(
            [
                ft.Text("Project Sources", style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.Text("Sources currently included in this project. Drag and drop to reorder.", italic=True, size=12, color=ft.colors.ON_SURFACE_VARIANT),
                ft.Divider(),
                ft.Container(self.project_sources_list, expand=True),
            ],
            expand=True,
            spacing=5,
        )

        main_layout = ft.Row(
            [
                ft.Container(on_deck_column, padding=10, bgcolor=ft.colors.SURFACE_VARIANT, border_radius=8),
                project_sources_column,
            ],
            expand=True,
            spacing=20,
        )

        fab = ft.FloatingActionButton(icon=ft.icons.ADD, tooltip="Create New Master Source", on_click=self._on_create_source_clicked, right=20, bottom=20)
        return ft.Stack([main_layout, fab])

    def _update_view(self):
        """
        Refreshes both the "On Deck" and "Project Sources" lists.
        
        Rebuilds the UI by:
        1. Clearing existing controls from both lists
        2. Fetching master sources for the project's region
        3. Populating "On Deck" with available sources not yet in the project
        4. Populating "Project Sources" with draggable/droppable cards in order
        5. Adding placeholder text when lists are empty
        
        Project sources are wrapped in Draggable and DragTarget controls to
        enable drag-and-drop reordering functionality.
        """
        project = self.project_state_manager.current_project
        if not project: return

        self.on_deck_list.controls.clear()
        self.project_sources_list.controls.clear()

        region = self.controller.data_service.get_region_for_project(project.file_path)
        master_sources = self.controller.data_service.get_master_sources_for_region(region)
        
        project_sources_sorted = sorted(project.sources, key=lambda link: link.order)
        project_source_ids = {link.source_id for link in project_sources_sorted}

        for source in sorted(master_sources, key=lambda s: s.title):
            if source.id not in project_source_ids:
                self.on_deck_list.controls.append(OnDeckCard(source=source, controller=self.controller))

        for link in project_sources_sorted:
            source = self.controller.data_service.get_source_by_id(link.source_id)
            if source:
                card = ProjectSourceCard(source=source, link=link, controller=self.controller)
                
                # --- FIX: Each item is now a DragTarget containing a Draggable ---
                draggable_item = ft.Draggable(
                    group="project_source",
                    content=card,
                    data=source.id  # The data of the draggable is its own ID
                )
                target_item = ft.DragTarget(
                    group="project_source",
                    content=draggable_item,
                    on_accept=self.on_drag_accept,
                    on_will_accept=self.on_drag_will_accept,
                    on_leave=self.on_drag_leave,
                    data=source.id  # The data of the target is also the source ID
                )
                self.project_sources_list.controls.append(target_item)
                # --- END FIX ---

        if not self.project_sources_list.controls: self.project_sources_list.controls.append(ft.Text("No sources added yet.", text_align=ft.TextAlign.CENTER, italic=True))
        if not self.on_deck_list.controls: self.on_deck_list.controls.append(ft.Text("All regional sources have been added.", text_align=ft.TextAlign.CENTER, italic=True))
        if self.page: self.page.update()

    # --- Drag and Drop Handlers ---
    def on_drag_accept(self, e):
        """
        Handles the drop action to reorder project sources.
        
        Retrieves the source and destination IDs from the drag event,
        validates the reorder operation, and updates the project sources
        order both in memory and persistent storage.
        
        Args:
            e: The drag target accept event containing source control ID and destination data.
        """
        # Get the Draggable control that was dropped using its control ID
        src_control = self.page.get_control(e.src_id)
        if not src_control: return

        # The 'data' of the Draggable is the source ID of the item being dragged
        src_id = src_control.data
        # The 'data' of the DragTarget is the source ID of the item being dropped on
        dest_id = e.control.data

        # Remove visual highlight from the target card
        e.control.content.content.elevation = None
        e.control.update()

        if src_id == dest_id:
            # Dropped on itself, do nothing
            return

        current_ids = [c.data for c in self.project_sources_list.controls]
        
        try:
            src_index = current_ids.index(src_id)
            dest_index = current_ids.index(dest_id)
        except ValueError:
            # Should not happen if everything is correct, but good to be safe
            return

        # Reorder the list of IDs in memory
        current_ids.pop(src_index)
        current_ids.insert(dest_index, src_id)
        
        # Tell the controller to save the new order
        self.controller.reorder_project_sources(current_ids)
        
        # The view will be refreshed by the controller after a successful save
        # which will re-render the list in the correct order.
        self._update_view()

    def on_drag_will_accept(self, e: ft.DragTargetAcceptEvent):
        """
        Provides visual feedback when a draggable item hovers over a valid drop target.
        
        Highlights the target card by increasing its elevation to indicate
        it's a valid drop location.
        
        Args:
            e (ft.DragTargetAcceptEvent): The drag event for the potential drop target.
        """
        # Highlight the target card by changing its elevation
        e.control.content.content.elevation = 20 # Target -> Draggable -> Card
        e.control.update()

    def on_drag_leave(self, e: ft.DragTargetAcceptEvent):
        """
        Removes visual feedback when a draggable item leaves a drop target.
        
        Removes the highlight from the target card by resetting its elevation
        to the default state.
        
        Args:
            e (ft.DragTargetAcceptEvent): The drag event for the target being left.
        """
        # Remove highlight
        e.control.content.content.elevation = None # Target -> Draggable -> Card
        e.control.update()

    def _on_create_source_clicked(self, e):
        """
        Handles the floating action button click to create a new master source.
        
        Delegates to the controller to show the create source dialog if the
        controller supports this functionality.
        
        Args:
            e: The click event from the floating action button.
        """
        if hasattr(self.controller, "show_create_source_dialog"):
            self.controller.show_create_source_dialog()

    def update_project_data(self, project_data: Dict[str, Any], project_path: str):
        """
        Updates the tab's view when project data changes.
        
        This method is called by the parent controller when the project
        data is modified, ensuring the UI reflects the current state.
        
        Args:
            project_data (Dict[str, Any]): The updated project data.
            project_path (str): The file path to the project.
        """
        self._update_view()
