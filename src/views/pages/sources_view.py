"""
Sources View - Manage and add sources to the on-deck circle
"""

import flet as ft
from typing import Optional, List, Dict, Any
from views.base_view import BaseView
from views.components.source_ui_factory import SourceUIFactory, SourceItem


class SourcesView(BaseView):
    """View for managing sources and adding them to the on-deck circle"""
    
    def __init__(self, page: ft.Page, theme_manager=None, 
                 user_config=None, on_navigate=None):
        super().__init__(page)
        self.theme_manager = theme_manager
        self.user_config = user_config
        self.on_navigate = on_navigate
        
        # UI Factory
        self.ui_factory = SourceUIFactory()
        
        # Dummy data for UI testing
        self.all_sources: List[SourceItem] = self._create_dummy_all_sources()
        self.on_deck_sources: List[SourceItem] = self._create_dummy_on_deck_sources()
        
        # Initialize UI components
        self._init_components()
    
    def _create_dummy_all_sources(self) -> List[SourceItem]:
        """Create dummy source library for UI testing"""
        return [
            SourceItem(
                uuid="lib-1",
                title="2024 Annual Report - Financial Performance",
                source_type="FCR",
                description="Comprehensive financial analysis and performance metrics",
                citation="Corporate Finance Department, Annual Report 2024"
            ),
            SourceItem(
                uuid="lib-2",
                title="Market Research Study - Consumer Trends",
                source_type="GSC",
                description="Quarterly consumer behavior and market trend analysis",
                citation="Market Research Inc., Q4 2024 Consumer Study"
            ),
            SourceItem(
                uuid="lib-3",
                title="Internal Operations Assessment",
                source_type="STD",
                description="Operational efficiency and process improvement analysis",
                citation="Operations Department, Internal Assessment 2024"
            ),
            SourceItem(
                uuid="lib-4",
                title="Compliance Audit Results",
                source_type="CRS",
                description="Annual regulatory compliance review and findings",
                citation="External Audit Firm, Compliance Report 2024"
            ),
            SourceItem(
                uuid="lib-5",
                title="Strategic Planning Document",
                source_type="STD",
                description="Five-year strategic plan with goals and initiatives",
                citation="Executive Team, Strategic Plan 2025-2030"
            ),
            SourceItem(
                uuid="lib-6",
                title="Customer Satisfaction Survey",
                source_type="GSC",
                description="Annual customer feedback and satisfaction metrics",
                citation="Customer Experience Team, Survey 2024"
            ),
            SourceItem(
                uuid="lib-7",
                title="Budget Allocation Analysis",
                source_type="FCR",
                description="Departmental budget breakdown and variance analysis",
                citation="Finance Team, Budget Analysis 2024"
            ),
            SourceItem(
                uuid="lib-8",
                title="Technology Infrastructure Report",
                source_type="STD",
                description="IT systems assessment and modernization recommendations",
                citation="IT Department, Infrastructure Report 2024"
            ),
            SourceItem(
                uuid="lib-9",
                title="Risk Management Assessment",
                source_type="CRS",
                description="Enterprise risk evaluation and mitigation strategies",
                citation="Risk Management Team, Assessment 2024"
            ),
            SourceItem(
                uuid="lib-10",
                title="Employee Engagement Study",
                source_type="GSC",
                description="Workforce satisfaction and engagement analysis",
                citation="HR Department, Engagement Study 2024"
            )
        ]
    
    def _create_dummy_on_deck_sources(self) -> List[SourceItem]:
        """Create dummy on-deck sources for UI testing"""
        return [
            SourceItem(
                uuid="lib-1",
                title="2024 Annual Report - Financial Performance",
                source_type="FCR",
                description="Comprehensive financial analysis and performance metrics",
                citation="Corporate Finance Department, Annual Report 2024"
            ),
            SourceItem(
                uuid="lib-3",
                title="Internal Operations Assessment",
                source_type="STD",
                description="Operational efficiency and process improvement analysis",
                citation="Operations Department, Internal Assessment 2024"
            )
        ]
    
    def _get_theme_color(self) -> str:
        """Get theme color for buttons and UI elements"""
        if self.theme_manager:
            return self.theme_manager.get_primary_color() if hasattr(self.theme_manager, 'get_primary_color') else ft.colors.BLUE_600
        return ft.colors.BLUE_600 if self.page.theme_mode != ft.ThemeMode.DARK else ft.colors.BLUE_400
    
    def _init_components(self):
        """Initialize UI components"""
        # Search/filter controls
        self.search_field = ft.TextField(
            hint_text="Search sources...",
            prefix_icon=ft.icons.SEARCH,
            border_radius=8,
            on_change=self._on_search_change
        )
        
        self.filter_dropdown = ft.Dropdown(
            label="Filter by type",
            options=[
                ft.dropdown.Option("ALL", "All Types"),
                ft.dropdown.Option("FCR", "Financial Reports"),
                ft.dropdown.Option("STD", "Standard Documents"),
                ft.dropdown.Option("GSC", "General Sources"),
                ft.dropdown.Option("CRS", "Compliance Reports")
            ],
            value="ALL",
            width=200,
            on_change=self._on_filter_change
        )
        
        # Source lists
        self.source_library_list = ft.ListView(
            controls=[],
            spacing=5,
            expand=True,
            padding=ft.padding.all(10)
        )
        
        self.on_deck_list = ft.ListView(
            controls=[],
            spacing=5,
            height=300,
            padding=ft.padding.all(10)
        )
        
        # Populate initial data
        self._refresh_source_library()
        self._refresh_on_deck()
    
    def _create_library_source_card(self, source: SourceItem) -> ft.Card:
        """Create a source card for the library"""
        is_in_on_deck = any(s.uuid == source.uuid for s in self.on_deck_sources)
        
        action_btn = ft.IconButton(
            icon=ft.icons.REMOVE_CIRCLE_OUTLINE if is_in_on_deck else ft.icons.ADD_CIRCLE_OUTLINE,
            icon_color=ft.colors.ORANGE_600 if is_in_on_deck else ft.colors.GREEN_600,
            tooltip="Remove from on-deck" if is_in_on_deck else "Add to on-deck circle",
            on_click=lambda _, src=source: self._remove_from_on_deck(src.uuid) if is_in_on_deck else self._add_to_on_deck(src.uuid)
        )
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Column([
                            ft.Text(
                                source.title,
                                weight=ft.FontWeight.BOLD,
                                size=14,
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS
                            ),
                            ft.Text(
                                source.source_type,
                                size=12,
                                color=self._get_theme_color(),
                                weight=ft.FontWeight.W_500
                            )
                        ], spacing=2, expand=True),
                        action_btn
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(
                        source.description,
                        size=12,
                        color=ft.colors.GREY_600,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS
                    )
                ], spacing=5),
                padding=ft.padding.all(12),
                bgcolor=ft.colors.GREEN_50 if is_in_on_deck else None
            ),
            elevation=1,
            margin=ft.margin.symmetric(vertical=2)
        )
    
    def _create_on_deck_source_card(self, source: SourceItem) -> ft.Card:
        """Create a compact card for on-deck sources"""
        return ft.Card(
            content=ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text(
                            source.title,
                            weight=ft.FontWeight.BOLD,
                            size=12,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS
                        ),
                        ft.Text(
                            source.source_type,
                            size=10,
                            color=self._get_theme_color(),
                            weight=ft.FontWeight.W_500
                        )
                    ], spacing=2, expand=True),
                    ft.IconButton(
                        icon=ft.icons.REMOVE_CIRCLE_OUTLINE,
                        icon_color=ft.colors.RED_600,
                        tooltip="Remove from on-deck",
                        icon_size=16,
                        on_click=lambda _, src=source: self._remove_from_on_deck(src.uuid)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.padding.all(8)
            ),
            elevation=1,
            margin=ft.margin.symmetric(vertical=1)
        )
    
    def _refresh_source_library(self):
        """Refresh the source library list"""
        self.source_library_list.controls.clear()
        
        # Filter sources based on search and filter criteria
        filtered_sources = self._get_filtered_sources()
        
        for source in filtered_sources:
            self.source_library_list.controls.append(
                self._create_library_source_card(source)
            )
        
        if hasattr(self, 'page') and self.page:
            self.page.update()
    
    def _refresh_on_deck(self):
        """Refresh the on-deck circle list"""
        self.on_deck_list.controls.clear()
        
        for source in self.on_deck_sources:
            self.on_deck_list.controls.append(
                self._create_on_deck_source_card(source)
            )
        
        if hasattr(self, 'page') and self.page:
            self.page.update()
    
    def _get_filtered_sources(self) -> List[SourceItem]:
        """Get sources filtered by search and type"""
        sources = self.all_sources.copy()
        
        # Apply search filter
        if hasattr(self.search_field, 'value') and self.search_field.value:
            search_term = self.search_field.value.lower()
            sources = [s for s in sources if search_term in s.title.lower() or search_term in s.description.lower()]
        
        # Apply type filter
        if hasattr(self.filter_dropdown, 'value') and self.filter_dropdown.value != "ALL":
            sources = [s for s in sources if s.source_type == self.filter_dropdown.value]
        
        return sources
    
    def _add_to_on_deck(self, source_uuid: str):
        """Add a source to the on-deck circle"""
        source = next((s for s in self.all_sources if s.uuid == source_uuid), None)
        if source and not any(s.uuid == source_uuid for s in self.on_deck_sources):
            self.on_deck_sources.append(source)
            self._refresh_source_library()  # Refresh to update button states
            self._refresh_on_deck()
    
    def _remove_from_on_deck(self, source_uuid: str):
        """Remove a source from the on-deck circle"""
        self.on_deck_sources = [s for s in self.on_deck_sources if s.uuid != source_uuid]
        self._refresh_source_library()  # Refresh to update button states
        self._refresh_on_deck()
    
    def _on_search_change(self, e):
        """Handle search field changes"""
        self._refresh_source_library()
    
    def _on_filter_change(self, e):
        """Handle filter dropdown changes"""
        self._refresh_source_library()
    
    def build(self) -> ft.Control:
        """Build the sources view"""
        return ft.Column([
            # Header
            ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text("Sources Library", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text("Manage your source collection and build your on-deck circle", size=14, color=ft.colors.GREY_600)
                    ], spacing=2),
                ], spacing=10),
                padding=ft.padding.all(20),
                bgcolor=ft.colors.GREY_100 if self.page.theme_mode != ft.ThemeMode.DARK else ft.colors.GREY_800,
                border=ft.border.only(bottom=ft.BorderSide(1, ft.colors.GREY_300))
            ),
            
            # Main content
            ft.Container(
                content=ft.Row([
                    # Left column - Source Library
                    ft.Container(
                        content=ft.Column([
                            # Search and filter controls
                            ft.Container(
                                content=ft.Row([
                                    ft.Container(content=self.search_field, expand=True),
                                    self.filter_dropdown
                                ], spacing=10),
                                padding=ft.padding.only(bottom=15)
                            ),
                            
                            # Source library header
                            ft.Text(
                                "Source Library",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=self._get_theme_color()
                            ),
                            
                            # Source library list
                            ft.Container(
                                content=self.source_library_list,
                                bgcolor=ft.colors.WHITE,
                                border_radius=8,
                                border=ft.border.all(1, ft.colors.GREY_300),
                                expand=True
                            )
                        ], expand=True),
                        expand=True,
                        padding=ft.padding.all(20)
                    ),
                    
                    # Divider
                    ft.VerticalDivider(width=1, color=ft.colors.GREY_300),
                    
                    # Right column - On Deck Circle
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                "On Deck Circle",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=self._get_theme_color()
                            ),
                            ft.Text(
                                "Sources ready for project assignment",
                                size=12,
                                color=ft.colors.GREY_600
                            ),
                            ft.Container(height=10),
                            ft.Container(
                                content=self.on_deck_list,
                                bgcolor=ft.colors.GREY_50,
                                border_radius=8,
                                border=ft.border.all(1, ft.colors.GREY_300),
                                expand=True
                            )
                        ], expand=True),
                        width=350,
                        padding=ft.padding.all(20)
                    )
                ], expand=True),
                expand=True
            )
        ], expand=True, spacing=0)
