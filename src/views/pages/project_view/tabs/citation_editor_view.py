import flet as ft
import logging

class CitationEditorView(ft.Row):
    """
    The main UI for editing citations. It includes the slide list and the
    dual-selector for linking available sources to a selected slide.
    """
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # --- State Tracking ---
        self.selected_slide_id = None
        self.selected_available_source_id = None
        self.selected_linked_source_id = None
        self.all_project_sources = []

        # --- UI Controls ---
        

    def _on_slide_selected(self, e):
        """Handles user clicking on a slide."""
        selected_slide = e.control.data
        self.selected_slide_id = selected_slide['slide_id']
        self.logger.info(f"Slide selected: ID {self.selected_slide_id}")

        self.selected_slide_title.value = f"Managing: {selected_slide['title']}"
        self._update_source_selectors(selected_slide.get('sources', []))
        self.update()

    def _update_source_selectors(self, linked_source_ids):
        """Populates the available and linked source lists."""
        self.available_sources_list.controls.clear()
        self.linked_sources_list.controls.clear()
        self.selected_available_source_id = None
        self.selected_linked_source_id = None
        self.link_button.disabled = True
        self.unlink_button.disabled = True

        linked_ids_set = set(linked_source_ids)
        for source in self.all_project_sources:
            if source['id'] in linked_ids_set:
                self.linked_sources_list.controls.append(
                    ft.ElevatedButton(text=source.get('display_name'), data=source['id'], on_click=self._on_linked_source_click)
                )
            else:
                self.available_sources_list.controls.append(
                    ft.ElevatedButton(text=source.get('display_name'), data=source['id'], on_click=self._on_available_source_click)
                )
        self.update()

    def _on_available_source_click(self, e):
        self.selected_available_source_id = e.control.data
        self.selected_linked_source_id = None
        self.link_button.disabled = False
        self.unlink_button.disabled = True
        self.update()

    def _on_linked_source_click(self, e):
        self.selected_linked_source_id = e.control.data
        self.selected_available_source_id = None
        self.unlink_button.disabled = False
        self.link_button.disabled = True
        self.update()

    def _link_source(self, e):
        if self.selected_slide_id and self.selected_available_source_id:
            self.controller.add_source_to_slide(self.selected_slide_id, self.selected_available_source_id)

    def _unlink_source(self, e):
        if self.selected_slide_id and self.selected_linked_source_id:
            self.controller.remove_source_from_slide(self.selected_slide_id, self.selected_linked_source_id)

