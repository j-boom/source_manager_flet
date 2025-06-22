"""
Cite Sources Tab - Dual select interface for managing slide citations
"""

import flet as ft
from typing import Optional, List, Dict, Any


class CiteSourcesTab:
    """Tab for managing source citations with dual select interface"""
    
    def __init__(self, page: ft.Page, database_manager=None, project_data=None, project_path=None, theme_manager=None):
        self.page = page
        self.database_manager = database_manager
        self.project_data = project_data or {}
        self.project_path = project_path
        self.theme_manager = theme_manager
        
        # Dummy data for UI testing
        self.available_sources = self._create_dummy_available_sources()
        self.cited_sources = self._create_dummy_cited_sources()
        self.current_slide = 1
        self.total_slides = 5
        self.slide_titles = self._create_dummy_slide_titles()  # Add slide titles
        
        # Track selected items for multi-select
        self.selected_available = set()  # IDs of selected available sources
        self.selected_cited = set()     # IDs of selected cited sources
        
        # Create UI components
        self._init_components()
    
    def _create_dummy_available_sources(self) -> List[Dict[str, Any]]:
        """Create dummy available sources for UI testing"""
        return [
            {"id": "src-1", "title": "Annual Financial Report 2024", "type": "FCR"},
            {"id": "src-2", "title": "Quarterly Marketing Analysis", "type": "STD"},
            {"id": "src-3", "title": "Customer Survey Results", "type": "GSC"},
            {"id": "src-4", "title": "Compliance Audit Report", "type": "CRS"},
            {"id": "src-5", "title": "Strategic Plan 2025", "type": "STD"},
            {"id": "src-6", "title": "Budget Allocation Report", "type": "FCR"},
            {"id": "src-7", "title": "Market Research Data", "type": "GSC"},
            {"id": "src-8", "title": "Operations Manual", "type": "STD"}
        ]
    
    def _create_dummy_cited_sources(self) -> List[Dict[str, Any]]:
        """Create dummy cited sources for UI testing"""
        return [
            {"id": "src-1", "title": "Annual Financial Report 2024", "type": "FCR"},
            {"id": "src-5", "title": "Strategic Plan 2025", "type": "STD"}
        ]
    
    def _create_dummy_slide_titles(self) -> List[str]:
        """Create dummy slide titles for UI testing"""
        return [
            "Executive Summary",
            "Market Analysis & Trends",
            "Financial Performance Review",
            "Strategic Recommendations",
            "Implementation Timeline"
        ]
    
    def _get_theme_color(self) -> str:
        """Get theme color for buttons and UI elements"""
        if self.theme_manager:
            return self.theme_manager.get_primary_color() if hasattr(self.theme_manager, 'get_primary_color') else ft.colors.BLUE_600
        return ft.colors.BLUE_600 if self.page.theme_mode != ft.ThemeMode.DARK else ft.colors.BLUE_400
    
    def _init_components(self):
        """Initialize UI components"""
        # Create the dual select lists
        self.available_list = ft.ListView(
            controls=[],
            spacing=5,
            height=400,
            padding=ft.padding.all(10)
        )
        
        self.cited_list = ft.ListView(
            controls=[],
            spacing=5,
            height=400,
            padding=ft.padding.all(10)
        )
        
        # Create slide navigation as compact scrollable container
        self.slide_row = ft.Row(
            controls=[],
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            tight=True
        )
        self.slide_container = ft.Container(
            content=self.slide_row,
            height=50,  # Much more compact
            padding=ft.padding.symmetric(horizontal=15)
        )
        
        # Create arrow buttons that will be updated
        self.move_to_cited_btn = ft.IconButton(
            icon=ft.icons.ARROW_FORWARD,
            icon_size=24,
            icon_color=self._get_theme_color(),
            tooltip="Move selected sources to cited",
            on_click=lambda _: self._move_selected_to_cited(),
            disabled=True
        )
        
        self.move_to_available_btn = ft.IconButton(
            icon=ft.icons.ARROW_BACK,
            icon_size=24,
            icon_color=self._get_theme_color(),
            tooltip="Remove selected sources from cited",
            on_click=lambda _: self._move_selected_to_available(),
            disabled=True
        )
        
        # Create title control that can be updated
        self.title_text = ft.Text(
            f"Slide {self.current_slide}: {self.slide_titles[self.current_slide - 1]}",
            size=20,
            weight=ft.FontWeight.BOLD,
            color=self._get_theme_color(),
            text_align=ft.TextAlign.CENTER
        )
        
        # Populate initial data
        self._refresh_lists()
        self._refresh_slide_container()
    
    def _create_source_item(self, source: Dict[str, Any], is_available: bool = True) -> ft.Card:
        """Create a compact, selectable source item"""
        # Determine if this source is selected
        selected_set = self.selected_available if is_available else self.selected_cited
        is_selected = source["id"] in selected_set
        
        # Colors based on selection state
        if is_selected:
            bg_color = self._get_theme_color()
            text_color = ft.colors.WHITE
            border_color = self._get_theme_color()
        else:
            bg_color = ft.colors.WHITE
            text_color = ft.colors.BLACK87
            border_color = ft.colors.GREY_300
        
        return ft.Card(
            content=ft.Container(
                content=ft.Text(
                    source["title"],
                    weight=ft.FontWeight.W_500,
                    size=12,  # Compact text
                    max_lines=1,  # Single line for compactness
                    overflow=ft.TextOverflow.ELLIPSIS,
                    color=text_color
                ),
                padding=ft.padding.all(8),  # Very compact padding
                bgcolor=bg_color,
                border_radius=6,
                border=ft.border.all(1, border_color),
                on_click=lambda e, src_id=source["id"], available=is_available: self._toggle_selection(src_id, available)
            ),
            elevation=1 if not is_selected else 2,
            margin=ft.margin.symmetric(vertical=1)
        )
    
    def _refresh_lists(self):
        """Refresh both source lists"""
        # Clear existing controls
        self.available_list.controls.clear()
        self.cited_list.controls.clear()
        
        # Get available sources (excluding already cited ones)
        cited_ids = {src["id"] for src in self.cited_sources}
        available_sources = [src for src in self.available_sources if src["id"] not in cited_ids]
        
        # Populate available sources list
        for source in available_sources:
            self.available_list.controls.append(
                self._create_source_item(source, is_available=True)
            )
        
        # Populate cited sources list
        for source in self.cited_sources:
            self.cited_list.controls.append(
                self._create_source_item(source, is_available=False)
            )
        
        # Update UI
        self._update_arrow_buttons()
        if hasattr(self, 'page') and self.page:
            self.page.update()
    
    def _refresh_slide_container(self):
        """Refresh the slide container with compact slide number buttons"""
        self.slide_row.controls.clear()
        
        for i in range(1, self.total_slides + 1):
            # Create compact slide number button
            slide_btn = ft.Container(
                content=ft.Text(
                    str(i),
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE if i == self.current_slide else self._get_theme_color(),
                    text_align=ft.TextAlign.CENTER
                ),
                width=40,
                height=40,
                bgcolor=self._get_theme_color() if i == self.current_slide else ft.colors.GREY_100,
                border_radius=20,  # Circular buttons
                border=ft.border.all(
                    2, 
                    self._get_theme_color() if i == self.current_slide else ft.colors.GREY_300
                ),
                alignment=ft.alignment.center,
                on_click=lambda e, slide_num=i: self._on_slide_click(slide_num),
            )
            
            self.slide_row.controls.append(slide_btn)
    
    def _add_source(self, source_id: str):
        """Add a source to cited sources"""
        # Find the source in available sources
        source = next((src for src in self.available_sources if src["id"] == source_id), None)
        if source and source not in self.cited_sources:
            self.cited_sources.append(source)
            self._refresh_lists()
    
    def _remove_source(self, source_id: str):
        """Remove a source from cited sources"""
        source = next((src for src in self.cited_sources if src["id"] == source_id), None)
        if source:
            self.cited_sources.remove(source)
            self._refresh_lists()
    
    def _on_slide_click(self, slide_num: int):
        """Handle slide card click"""
        if slide_num != self.current_slide:
            self.current_slide = slide_num
            # Update the title text
            self.title_text.value = f"Slide {self.current_slide}: {self.slide_titles[self.current_slide - 1]}"
            self._refresh_slide_container()  # Refresh to update the active slide styling
            # In real implementation, this would load the citations for the selected slide
            if hasattr(self, 'page') and self.page:
                # Update the title display
                self.page.update()

    def _on_slide_change(self, e):
        """Handle slide selector change - deprecated but kept for compatibility"""
        if e.control.value:
            self.current_slide = int(e.control.value)
            self._show_message(f"Switched to Slide {self.current_slide}", self._get_theme_color())
            # In real implementation, this would load the citations for the selected slide
    
    def _show_message(self, message: str, color: str):
        """Show a temporary message to the user"""
        if hasattr(self.page, 'show_snack_bar'):
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(message, color=ft.colors.WHITE),
                    bgcolor=color
                )
            )
    
    def _toggle_selection(self, source_id: str, is_available: bool):
        """Toggle selection state of a source item"""
        selected_set = self.selected_available if is_available else self.selected_cited
        
        if source_id in selected_set:
            selected_set.discard(source_id)
        else:
            selected_set.add(source_id)
        
        # Refresh the lists to update visual state
        self._refresh_lists()
        
        # Update arrow button states
        self._update_arrow_buttons()

    def _on_item_select(self, source_id: str, is_available: bool, selected: bool):
        """Handle item selection/deselection"""
        selected_set = self.selected_available if is_available else self.selected_cited
        
        if selected:
            selected_set.add(source_id)
        else:
            selected_set.discard(source_id)
        
        # Update arrow button states
        self._update_arrow_buttons()
        
        # Update UI to reflect selection changes
        if hasattr(self, 'page') and self.page:
            self.page.update()
    
    def _update_arrow_buttons(self):
        """Update the state of arrow buttons based on selections"""
        self.move_to_cited_btn.disabled = len(self.selected_available) == 0
        self.move_to_available_btn.disabled = len(self.selected_cited) == 0
    
    def _move_selected_to_cited(self):
        """Move all selected available sources to cited sources"""
        if not self.selected_available:
            return
            
        # Find selected sources and move them
        sources_to_move = [src for src in self.available_sources if src["id"] in self.selected_available]
        for source in sources_to_move:
            if source not in self.cited_sources:
                self.cited_sources.append(source)
        
        # Clear selections and refresh
        self.selected_available.clear()
        self._refresh_lists()
    
    def _move_selected_to_available(self):
        """Move all selected cited sources back to available sources"""
        if not self.selected_cited:
            return
            
        # Find selected sources and remove them from cited
        sources_to_remove = [src for src in self.cited_sources if src["id"] in self.selected_cited]
        for source in sources_to_remove:
            self.cited_sources.remove(source)
        
        # Clear selections and refresh
        self.selected_cited.clear()
        self._refresh_lists()
    
    def build(self) -> ft.Control:
        """Build the cite sources tab content"""
        return ft.Column([
            # Current slide title display at the top
            ft.Container(
                content=self.title_text,
                alignment=ft.alignment.center,
                padding=ft.padding.only(top=20, bottom=15)
            ),
            
            # Dual select interface
            ft.Container(
                content=ft.Row([
                    # Available Sources (Left)
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                "Available Sources",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=self._get_theme_color()
                            ),
                            ft.Container(
                                content=self.available_list,
                                bgcolor=ft.colors.GREY_50,
                                border_radius=8,
                                border=ft.border.all(1, ft.colors.GREY_300),
                                expand=True
                            )
                        ], spacing=10),
                        expand=True,
                        padding=ft.padding.all(15)
                    ),
                    
                    # Divider with clickable arrows
                    ft.Container(
                        content=ft.Column([
                            self.move_to_cited_btn,
                            self.move_to_available_btn
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
                        width=60,
                        alignment=ft.alignment.center
                    ),
                    
                    # Cited Sources (Right)
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                "Cited Sources",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=self._get_theme_color()
                            ),
                            ft.Container(
                                content=self.cited_list,
                                bgcolor=ft.colors.GREY_50,
                                border_radius=8,
                                border=ft.border.all(1, ft.colors.GREY_300),
                                expand=True
                            )
                        ], spacing=10),
                        expand=True,
                        padding=ft.padding.all(15)
                    )
                ], expand=True),
                expand=True
            ),
            
            # Compact slide navigation at the bottom
            ft.Container(
                content=ft.Row([
                    ft.Text(
                        "Slide:",
                        size=14,
                        weight=ft.FontWeight.W_500
                    ),
                    ft.Container(
                        content=self.slide_row,
                        expand=True
                    )
                ], spacing=10, alignment=ft.MainAxisAlignment.START),
                padding=ft.padding.all(12),
                bgcolor=ft.colors.GREY_100 if self.page.theme_mode != ft.ThemeMode.DARK else ft.colors.GREY_800,
                border=ft.border.only(top=ft.BorderSide(1, ft.colors.GREY_300))
            )
        ], expand=True, spacing=0)
