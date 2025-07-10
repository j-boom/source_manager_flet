import flet as ft
from .base_tab import BaseTab
from typing import List
from pathlib import Path
from views.components import SlideCarousel

class CiteSourcesTab(BaseTab):
    """
    A tab dedicated to managing source citations for a presentation.

    This class provides a user interface for associating sources with specific
    slides in a PowerPoint presentation. It features a dual-list system
    where users can move sources from a project-wide "available" list to a
    slide-specific "cited" list.
    """

    def __init__(self, controller):
        """
        Initializes the CiteSourcesTab.

        Args:
            controller: The main application controller.
        """
        super().__init__(controller)
        self.current_slide_index = 0

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
            on_click=self._on_sync_clicked,
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
        
        # Initialize the view state based on current project
        self.update_view()

    def build(self) -> ft.Control:
        """
        Builds the tab content, which is a Stack of the main view and prompt.
        This allows toggling between the two states.
        """
        return ft.Stack(controls=[self.prompt_view, self.main_view])

    def _build_associate_file_prompt(self) -> ft.Column:
        """
        Returns the UI for prompting the user to select a .pptx file.
        This view is shown when no presentation is associated with the project.
        """
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
                    on_click=lambda e: self.controller.get_slides_for_current_project(),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            expand=True,
            visible=True, # Show by default
        )

    def _build_main_view(self) -> ft.Column:
        """
        Returns the main dual-list interface for citing sources.
        This is the primary view when a presentation is available.
        """
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
            visible=False, # Initially hidden
        )

    def _build_source_column(self, title: str, list_view: ft.ListView) -> ft.Column:
        """
        Helper to build a column for the source lists (Available and Cited).
        
        Args:
            title: The title to display above the list.
            list_view: The ft.ListView control to embed in the column.
            
        Returns:
            A ft.Column control containing the title and list view.
        """
        return ft.Column(
            [
                ft.Row(
                    [ft.Text(title, weight=ft.FontWeight.BOLD)],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(
                    list_view,
                    border=ft.border.all(1, ft.colors.OUTLINE),
                    border_radius=8,
                    padding=10,
                    expand=True,
                ),
            ],
            expand=True,
        )

    def _on_slide_selected(self, slide_id: str):
        """
        Callback for when a new slide is selected from the carousel.
        Updates the current slide and refreshes the view.
        """
        # Find the slide index from the slide_id
        project = self.controller.project_state_manager.current_project
        if project:
            slides = project.metadata.get("slides", [])
            for i, (sid, title) in enumerate(slides):
                if sid == slide_id:
                    self.current_slide_index = i
                    self.current_slide_title.value = title
                    break
        self.update_view()

    def _get_selected_ids(self, source_list: ft.ListView) -> List[str]:
        """
        Gets the IDs of the checked items in a given ListView.

        Args:
            source_list: The ListView to inspect (either available_list or cited_list).

        Returns:
            A list of source IDs for the selected items.
        """
        return [
            str(cb.data)
            for cb in source_list.controls
            if isinstance(cb, ft.Checkbox) and cb.value and cb.data is not None
        ]

    def _move_to_cited(self, e):
        """
        Moves selected sources from the available list to the cited list
        and updates the project data model.
        """
        selected_ids = self._get_selected_ids(self.available_list)
        if selected_ids:
            # Get the current slide ID (not index)
            project = self.controller.project_state_manager.current_project
            slides = project.metadata.get("slides", [])
            if 0 <= self.current_slide_index < len(slides):
                current_slide_id = slides[self.current_slide_index][0]
                self.controller.add_citations_to_slide(current_slide_id, selected_ids)
                self.update_view() # Refresh UI after data change

    def _move_to_available(self, e):
        """
        Moves selected sources from the cited list to the available list
        and updates the project data model.
        """
        selected_ids = self._get_selected_ids(self.cited_list)
        if selected_ids:
            # Get the current slide ID (not index)
            project = self.controller.project_state_manager.current_project
            slides = project.metadata.get("slides", [])
            if 0 <= self.current_slide_index < len(slides):
                current_slide_id = slides[self.current_slide_index][0]
                self.controller.remove_citations_from_slide(current_slide_id, selected_ids)
                self.update_view() # Refresh UI after data change

    def _on_sync_clicked(self, e):
        """
        Handle sync button click with visual feedback.
        """
        project = self.controller.project_state_manager.current_project
        if not project:
            return
        
        ppt_path = project.metadata.get("powerpoint_path")
        if not ppt_path:
            if self.page:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        ft.Text("No PowerPoint file associated with this project"),
                        bgcolor=ft.colors.ORANGE
                    )
                )
                self.page.snack_bar.open = True
                self.page.update()
            return
        
        # Show loading state
        original_text = self.change_ppt_btn.text
        original_icon = self.change_ppt_btn.icon
        self.change_ppt_btn.text = "Syncing..."
        self.change_ppt_btn.icon = ft.icons.HOURGLASS_EMPTY
        self.change_ppt_btn.disabled = True
        if self.page:
            self.page.update()
        
        # Perform the sync
        try:
            self.controller.get_slides_for_current_project(force_reselect=True)
        finally:
            # Restore button state
            self.change_ppt_btn.text = original_text
            self.change_ppt_btn.icon = original_icon
            self.change_ppt_btn.disabled = False
            if self.page:
                self.page.update()

    def _show_create_group_dialog(self, e):
        """Placeholder for showing a dialog to group sources."""
        # Future implementation: show a dialog to create a source group.
        if self.page:
            self.page.show_snack_bar(ft.SnackBar(ft.Text("Grouping not yet implemented."), open=True))


    def update_view(self):
        """
        Refreshes the entire view based on the current project state.
        Automatically checks for existing PowerPoint files and loads slide data if available.
        """
        project = self.controller.project_state_manager.current_project
        if not project:
            return

        # Check if there's an existing PowerPoint file path in metadata
        ppt_path = project.metadata.get("powerpoint_path")
        has_slides = project.metadata.get("slides")
        
        # If we have a PowerPoint path but no slides, try to reload the slides
        if ppt_path and not has_slides:
            if Path(ppt_path).exists():
                # File exists but we don't have slide data - reload it
                self.controller._process_powerpoint_file(ppt_path)
                # Force a refresh after processing
                project = self.controller.project_state_manager.current_project
                has_slides = project.metadata.get("slides") if project else None
            else:
                # File doesn't exist anymore - clear the path and show prompt
                project.metadata.pop("powerpoint_path", None)
                project.metadata.pop("slides", None)
                self.controller.data_service.save_project(project)
                has_slides = False
        
        # If we have a PowerPoint path and the file exists, but slides are empty, reload
        if ppt_path and has_slides and Path(ppt_path).exists():
            if not has_slides or len(has_slides) == 0:
                self.controller._process_powerpoint_file(ppt_path)
                project = self.controller.project_state_manager.current_project
                has_slides = project.metadata.get("slides") if project else None
        
        # Determine which view to show: the prompt or the main interface
        has_slides = project.metadata.get("slides")
        self.prompt_view.visible = not has_slides
        self.main_view.visible = bool(has_slides)

        if not has_slides:
            if self.page:
                self.page.update()
            return

        # --- Populate Main View ---
        slides = project.metadata.get("slides", [])
        current_slide_id = slides[self.current_slide_index][0] if 0 <= self.current_slide_index < len(slides) else ""
        self.slide_carousel.update(slides, current_slide_id)

        # Update slide title if it's out of sync
        if 0 <= self.current_slide_index < len(slides):
            self.current_slide_title.value = slides[self.current_slide_index][1]

        # Get all sources for the project and the sources cited on the current slide.
        all_project_source_ids = {link.source_id for link in project.sources}
        citations = project.metadata.get("citations", {})
        
        # Get the current slide ID to look up citations
        current_slide_id = ""
        if 0 <= self.current_slide_index < len(slides):
            current_slide_id = slides[self.current_slide_index][0]
            
        cited_on_this_slide_ids = set(citations.get(current_slide_id, []))

        # Clear and repopulate the available and cited lists.
        self.available_list.controls.clear()
        self.cited_list.controls.clear()

        # Sort sources for consistent ordering.
        for source_id in sorted(list(all_project_source_ids)):
            source_record = self.controller.data_service.get_source_by_id(source_id)
            if source_record:
                # Create a checkbox for each source.
                checkbox = ft.Checkbox(
                    label=f"{source_record.title} ({source_record.id})",
                    data=source_id
                )
                if source_id in cited_on_this_slide_ids:
                    self.cited_list.controls.append(checkbox)
                else:
                    self.available_list.controls.append(checkbox)

        if self.page:
            self.page.update()

