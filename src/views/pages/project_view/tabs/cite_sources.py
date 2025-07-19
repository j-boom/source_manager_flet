import flet as ft
from .base_tab import BaseTab
from typing import List
from views.components import SlideCarousel
import logging


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
        self.current_slide_id: Optional[str] = None

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
        self.logger = logging.getLogger(self.__class__.__name__)

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
                    on_click=self._request_pptx_association,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            expand=True,
            visible=False, # Initially hidden
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
                self.slide_carousel,
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
        Updates the current slide index and refreshes the view.
        """
        self.current_slide_id = slide_id
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
            cb.data
            for cb in source_list.controls
            if isinstance(cb, ft.Checkbox) and cb.value
        ]

    def _move_to_cited(self, e):
        """
        Moves selected sources from the available list to the cited list
        and updates the project data model.
        """
        selected_ids = self._get_selected_ids(self.available_list)
        if selected_ids:
            self.controller.powerpoint_controller.add_citations_to_slide(
                self.current_slide_id, selected_ids
            )
            self.update_view() # Refresh UI after data change

    def _move_to_available(self, e):
        """
        Moves selected sources from the cited list to the available list
        and updates the project data model.
        """
        selected_ids = self._get_selected_ids(self.cited_list)
        if selected_ids:
            self.controller.powerpoint_controller.remove_citations_from_slide(
                self.current_slide_id, selected_ids
            )
            self.update_view() # Refresh UI after data change

    def _show_create_group_dialog(self, e):
        """Placeholder for showing a dialog to group sources."""
        # Future implementation: show a dialog to create a source group.
        if self.page:
            self.page.show_snack_bar(ft.SnackBar(ft.Text("Grouping not yet implemented."), open=True))


    def update_view(self):
        """
        Refreshes the entire view based on the current project state.
        This is the main method for synchronizing the UI with the data model.
        """
        project = self.controller.project_controller.get_current_project()
        if not project: return

        self.controller.powerpoint_controller.get_synced_slide_data()
        slides = project.metadata.get("slide_data", [])
        has_slides = bool(slides)

        self.prompt_view.visible = not has_slides
        self.main_view.visible = has_slides

        if not has_slides:
            if self.page: self.page.update()
            return
        
        if not self.current_slide_id and slides:
            self.current_slide_id = slides[0].get("slide_id", "")

        self.slide_carousel.update(slides, self.current_slide_id)
        self.slide_carousel.scroll_to_key(self.current_slide_id)

        current_slide_title_text = "Select a Slide"
        for slide in slides:
            if str(slide.get("slide_id")) == str(self.current_slide_id):
                current_slide_title_text = slide.get("title", "Untitled Slide")
                break
        self.current_slide_title.value = f"Slide: {current_slide_title_text}"

        # Get all sources for the project and the sources cited on the current slide.
        all_project_source_ids = {link.source_id for link in project.sources}
   
        cited_on_this_slide_ids = set()
        slide_data = getattr(project, "slide_data", [])
        for slide in slide_data:
            if str(slide.get("slide_id")) == str(self.current_slide_id):
                cited_on_this_slide_ids = set(slide.get("sources", []))
                break
        # Clear and repopulate the available and cited lists.
        self.available_list.controls.clear()
        self.cited_list.controls.clear()

        for source_link in project.sources:
            source_id = source_link.source_id
            source_record = self.controller.source_service.get_source_by_id(source_id)
            if source_record:
                checkbox = ft.Checkbox(label=f"{source_record.title} ({source_record.source_id})", data=source_id)
                if source_id in cited_on_this_slide_ids:
                    self.cited_list.controls.append(checkbox)
                else:
                    self.available_list.controls.append(checkbox)

        if self.page: self.page.update()

    def _request_pptx_association(self, e):
        """
        Handles the button click to start the file selection process.
        """
        self.logger.info("Requesting PowerPoint file association")
        self.controller.powerpoint_controller.pick_powerpoint_file()