import flet as ft
from typing import List, Tuple, Callable

class SlideCarousel:
    """
    A self-contained, horizontally-scrolling carousel component with arrow buttons
    to display and select presentation slides.
    """
    def __init__(self, on_slide_selected: Callable[[str], None]):
        """
        Initializes the carousel.

        Args:
            on_slide_selected: A callback function to execute when a slide is clicked.
                               It receives the selected slide's ID as an argument.
        """
        self.on_slide_selected = on_slide_selected
        
        self.list_view = ft.ListView(
            horizontal=True,
            spacing=15,
            padding=ft.padding.symmetric(vertical=5, horizontal=10),
            height=65,
            expand=True,
        )

        self.view = ft.Row(
            [
                ft.IconButton(
                    icon=ft.icons.ARROW_BACK_IOS_NEW_ROUNDED,
                    on_click=self._scroll_left,
                    tooltip="Scroll Left"
                ),
                self.list_view,
                ft.IconButton(
                    icon=ft.icons.ARROW_FORWARD_IOS_ROUNDED,
                    on_click=self._scroll_right,
                    tooltip="Scroll Right"
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

    def update(self, slide_data: List[Tuple[str, str]], current_slide_id: str):
        """
        Rebuilds the carousel with new slide data and highlights the selected slide.

        Args:
            slide_data: A list of tuples, where each is (slide_id, slide_title).
            current_slide_id: The ID of the slide to mark as currently selected.
        """
        self.list_view.controls.clear()

        if not slide_data:
            if self.list_view.page:
                self.list_view.update()
            return

        for i, (slide_id, title) in enumerate(slide_data):
            is_selected = (slide_id == current_slide_id)

            slide_icon = ft.Container(
                key=slide_id,
                content=ft.Text(str(i + 1), weight=ft.FontWeight.BOLD, size=16),
                width=52,
                height=52,
                alignment=ft.alignment.center,
                bgcolor=ft.colors.PRIMARY_CONTAINER if is_selected else ft.colors.SURFACE_VARIANT,
                border=ft.border.all(2, ft.colors.PRIMARY if is_selected else ft.colors.TRANSPARENT),
                border_radius=26,
                tooltip=title,
                on_click=self._handle_click,
                data=slide_id,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=4,
                    color=ft.colors.with_opacity(0.2, ft.colors.BLACK),
                    offset=ft.Offset(1, 2),
                )
            )
            self.list_view.controls.append(slide_icon)
        
        if self.list_view.page:
            self.list_view.update()

    def scroll_to_key(self, key: str):
        """Public method to scroll the list to a specific key."""
        # This check ensures the control has been added to the page before scrolling.
        if self.list_view and self.list_view.page:
            self.list_view.scroll_to(key=key, duration=300, curve=ft.AnimationCurve.EASE_OUT)

    def _scroll_left(self, e):
        """Scrolls the list to the left."""
        if self.list_view and self.list_view.page:
            self.list_view.scroll_to(delta=-200, duration=300)

    def _scroll_right(self, e):
        """Scrolls the list to the right."""
        if self.list_view and self.list_view.page:
            self.list_view.scroll_to(delta=200, duration=300)

    def _handle_click(self, e):
        """Internal click handler that calls the provided callback."""
        self.on_slide_selected(e.control.data)