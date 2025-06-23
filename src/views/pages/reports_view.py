"""
Reports View - Generate bibliographies and manage citations
"""

import flet as ft
from typing import Optional, List, Dict, Any
from views.base_view import BaseView
from views.components.source_ui_factory import SourceUIFactory, SourceItem


class ReportsView(BaseView):
    """View for generating reports, bibliographies, and managing citations"""
    
    def __init__(self, page: ft.Page, theme_manager=None, database_manager=None, 
                 user_config=None, on_navigate=None):
        super().__init__(page)
        self.theme_manager = theme_manager
        self.database_manager = database_manager
        self.user_config = user_config
        self.on_navigate = on_navigate
        
        # Dummy data for UI testing
        self.current_project = "Strategic Analysis 2025"
        self.citation_style = "APA"
        self.slide_citations = self._create_dummy_slide_citations()
        self.project_sources = self._create_dummy_project_sources()
        
        # Initialize UI components
        self._init_components()
    
    def _create_dummy_slide_citations(self) -> Dict[int, List[str]]:
        """Create dummy slide citation assignments"""
        return {
            1: ["Annual Financial Report 2024", "Strategic Plan 2025"],
            2: ["Market Research Study - Consumer Trends", "Customer Satisfaction Survey"],
            3: ["Budget Allocation Analysis", "Annual Financial Report 2024"],
            4: ["Strategic Plan 2025", "Risk Management Assessment"],
            5: ["Employee Engagement Study"]
        }
    
    def _create_dummy_project_sources(self) -> List[SourceItem]:
        """Create dummy project sources for bibliography"""
        return [
            SourceItem(
                uuid="src-1",
                title="Annual Financial Report 2024",
                source_type="FCR",
                description="Comprehensive financial analysis and performance metrics",
                citation="Corporate Finance Department. (2024). Annual Financial Report 2024. Company Publications."
            ),
            SourceItem(
                uuid="src-2",
                title="Market Research Study - Consumer Trends",
                source_type="GSC",
                description="Quarterly consumer behavior analysis",
                citation="Market Research Inc. (2024). Consumer Trends Study Q4. Market Research Publications."
            ),
            SourceItem(
                uuid="src-3",
                title="Strategic Plan 2025",
                source_type="STD",
                description="Five-year strategic planning document",
                citation="Executive Team. (2025). Strategic Plan 2025-2030. Internal Documentation."
            ),
            SourceItem(
                uuid="src-4",
                title="Customer Satisfaction Survey",
                source_type="GSC",
                description="Annual customer feedback metrics",
                citation="Customer Experience Team. (2024). Customer Satisfaction Survey 2024. Internal Report."
            ),
            SourceItem(
                uuid="src-5",
                title="Budget Allocation Analysis",
                source_type="FCR",
                description="Departmental budget breakdown",
                citation="Finance Team. (2024). Budget Allocation Analysis 2024. Financial Reports."
            )
        ]
    
    def _get_theme_color(self) -> str:
        """Get theme color for buttons and UI elements"""
        if self.theme_manager:
            return self.theme_manager.get_primary_color() if hasattr(self.theme_manager, 'get_primary_color') else ft.colors.BLUE_600
        return ft.colors.BLUE_600 if self.page.theme_mode != ft.ThemeMode.DARK else ft.colors.BLUE_400
    
    def _init_components(self):
        """Initialize UI components"""
        # Citation style dropdown
        self.style_dropdown = ft.Dropdown(
            label="Citation Style",
            options=[
                ft.dropdown.Option("APA", "APA Style"),
                ft.dropdown.Option("MLA", "MLA Style"),
                ft.dropdown.Option("Chicago", "Chicago Style"),
                ft.dropdown.Option("Harvard", "Harvard Style")
            ],
            value=self.citation_style,
            width=200,
            on_change=self._on_style_change
        )
        
        # Bibliography preview text
        self.bibliography_preview = ft.Container(
            content=ft.Column([
                ft.Text("Bibliography", size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text(self._generate_bibliography_preview(), size=12, selectable=True)
            ], spacing=10, scroll=ft.ScrollMode.AUTO),
            bgcolor=ft.colors.WHITE,
            border_radius=8,
            border=ft.border.all(1, ft.colors.GREY_300),
            padding=ft.padding.all(15),
            height=300
        )
        
        # Citation summary table
        self.citation_table = self._create_citation_table()
        
        # Progress indicators
        self.progress_stats = self._create_progress_stats()
        
        # Main tabs
        self.main_tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Bibliography Preview",
                    icon=ft.icons.LIBRARY_BOOKS,
                    content=self._build_bibliography_tab()
                ),
                ft.Tab(
                    text="Citation Summary",
                    icon=ft.icons.ASSIGNMENT,
                    content=self._build_citation_summary_tab()
                ),
                ft.Tab(
                    text="Export Options",
                    icon=ft.icons.DOWNLOAD,
                    content=self._build_export_tab()
                )
            ]
        )
    
    def _generate_bibliography_preview(self) -> str:
        """Generate a formatted bibliography preview"""
        if self.citation_style == "APA":
            return "\n\n".join([
                "Corporate Finance Department. (2024). Annual Financial Report 2024. Company Publications.",
                "Customer Experience Team. (2024). Customer Satisfaction Survey 2024. Internal Report.",
                "Executive Team. (2025). Strategic Plan 2025-2030. Internal Documentation.",
                "Finance Team. (2024). Budget Allocation Analysis 2024. Financial Reports.",
                "Market Research Inc. (2024). Consumer Trends Study Q4. Market Research Publications."
            ])
        return "Bibliography will be formatted according to selected style..."
    
    def _create_progress_stats(self) -> ft.Container:
        """Create progress statistics display"""
        total_slides = 5
        cited_slides = len([s for s in self.slide_citations.values() if s])
        completion_rate = cited_slides / total_slides if total_slides > 0 else 0
        
        return ft.Container(
            content=ft.Row([
                # Project info
                ft.Column([
                    ft.Text("Current Project", size=12, color=ft.colors.GREY_600),
                    ft.Text(self.current_project, size=16, weight=ft.FontWeight.BOLD)
                ], spacing=2),
                
                # Source count
                ft.Column([
                    ft.Text("Total Sources", size=12, color=ft.colors.GREY_600),
                    ft.Text(str(len(self.project_sources)), size=16, weight=ft.FontWeight.BOLD, color=self._get_theme_color())
                ], spacing=2),
                
                # Citation progress
                ft.Column([
                    ft.Text("Citation Progress", size=12, color=ft.colors.GREY_600),
                    ft.Row([
                        ft.Text(f"{cited_slides}/{total_slides}", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.ProgressBar(value=completion_rate, color=self._get_theme_color()),
                            width=100
                        )
                    ], spacing=10)
                ], spacing=2)
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            bgcolor=ft.colors.GREY_50,
            border_radius=8,
            border=ft.border.all(1, ft.colors.GREY_300),
            padding=ft.padding.all(15)
        )
    
    def _create_citation_table(self) -> ft.DataTable:
        """Create citation summary table"""
        rows = []
        for slide_num in range(1, 6):  # 5 slides
            citations = self.slide_citations.get(slide_num, [])
            status_color = ft.colors.GREEN if citations else ft.colors.RED
            status_text = f"{len(citations)} sources" if citations else "No citations"
            
            rows.append(
                ft.DataRow([
                    ft.DataCell(ft.Text(f"Slide {slide_num}")),
                    ft.DataCell(ft.Text(f"Slide Title {slide_num}")),  # Placeholder
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(status_text, color=status_color, size=12),
                            bgcolor=ft.colors.with_opacity(0.1, status_color),
                            border_radius=4,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4)
                        )
                    ),
                    ft.DataCell(
                        ft.IconButton(
                            icon=ft.icons.EDIT,
                            tooltip="Edit citations",
                            on_click=lambda _, slide=slide_num: self._edit_slide_citations(slide)
                        )
                    )
                ])
            )
        
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Slide")),
                ft.DataColumn(ft.Text("Title")),
                ft.DataColumn(ft.Text("Citations")),
                ft.DataColumn(ft.Text("Actions"))
            ],
            rows=rows,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=8
        )
    
    def _build_bibliography_tab(self) -> ft.Container:
        """Build the bibliography preview tab"""
        return ft.Container(
            content=ft.Column([
                # Controls
                ft.Row([
                    self.style_dropdown,
                    ft.ElevatedButton(
                        "Copy Bibliography",
                        icon=ft.icons.COPY,
                        on_click=self._copy_bibliography
                    ),
                    ft.ElevatedButton(
                        "Refresh Preview",
                        icon=ft.icons.REFRESH,
                        on_click=self._refresh_bibliography
                    )
                ], spacing=10),
                
                ft.Container(height=20),
                
                # Bibliography preview
                self.bibliography_preview
            ], expand=True),
            padding=ft.padding.all(20)
        )
    
    def _build_citation_summary_tab(self) -> ft.Container:
        """Build the citation summary tab"""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Slide Citation Summary",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=self._get_theme_color()
                ),
                ft.Text(
                    "Review and manage citations for each slide",
                    size=14,
                    color=ft.colors.GREY_600
                ),
                
                ft.Container(height=20),
                
                # Citation table
                ft.Container(
                    content=self.citation_table,
                    expand=True
                )
            ], expand=True),
            padding=ft.padding.all(20)
        )
    
    def _build_export_tab(self) -> ft.Container:
        """Build the export options tab"""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Export Options",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=self._get_theme_color()
                ),
                
                ft.Container(height=20),
                
                # Export options
                ft.Row([
                    # Bibliography exports
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Bibliography Export", size=16, weight=ft.FontWeight.BOLD),
                            ft.Container(height=10),
                            ft.ElevatedButton(
                                "Export as Word Document",
                                icon=ft.icons.DESCRIPTION,
                                style=ft.ButtonStyle(
                                    bgcolor=self._get_theme_color(),
                                    color=ft.colors.WHITE
                                ),
                                on_click=self._export_word
                            ),
                            ft.ElevatedButton(
                                "Export as PDF",
                                icon=ft.icons.PICTURE_AS_PDF,
                                on_click=self._export_pdf
                            ),
                            ft.ElevatedButton(
                                "Export as Text File",
                                icon=ft.icons.TEXT_SNIPPET,
                                on_click=self._export_text
                            )
                        ], spacing=10),
                        expand=True
                    ),
                    
                    # PowerPoint integration
                    ft.Container(
                        content=ft.Column([
                            ft.Text("PowerPoint Integration", size=16, weight=ft.FontWeight.BOLD),
                            ft.Container(height=10),
                            ft.ElevatedButton(
                                "Attach Citations to Slides",
                                icon=ft.icons.SLIDESHOW,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.colors.ORANGE_600,
                                    color=ft.colors.WHITE
                                ),
                                on_click=self._attach_to_powerpoint
                            ),
                            ft.ElevatedButton(
                                "Export Slide Notes",
                                icon=ft.icons.NOTES,
                                on_click=self._export_slide_notes
                            ),
                            ft.Text(
                                "PowerPoint Status: Ready",
                                size=12,
                                color=ft.colors.GREEN_600
                            )
                        ], spacing=10),
                        expand=True
                    )
                ], spacing=30)
            ], expand=True),
            padding=ft.padding.all(20)
        )
    
    # Event handlers (placeholder implementations)
    def _on_style_change(self, e):
        """Handle citation style change"""
        self.citation_style = e.control.value
        self._refresh_bibliography()
    
    def _copy_bibliography(self, e):
        """Copy bibliography to clipboard"""
        # Placeholder implementation
        if hasattr(self.page, 'set_clipboard'):
            self.page.set_clipboard(self._generate_bibliography_preview())
    
    def _refresh_bibliography(self, e=None):
        """Refresh bibliography preview"""
        new_preview = self._generate_bibliography_preview()
        self.bibliography_preview.content.controls[2].value = new_preview
        if hasattr(self, 'page') and self.page:
            self.page.update()
    
    def _edit_slide_citations(self, slide_num: int):
        """Navigate to cite sources tab for specific slide"""
        # Placeholder - would navigate to cite sources tab
        pass
    
    def _export_word(self, e):
        """Export bibliography as Word document"""
        # Placeholder for Word export functionality
        pass
    
    def _export_pdf(self, e):
        """Export bibliography as PDF"""
        # Placeholder for PDF export functionality
        pass
    
    def _export_text(self, e):
        """Export bibliography as text file"""
        # Placeholder for text export functionality
        pass
    
    def _attach_to_powerpoint(self, e):
        """Attach citations to PowerPoint slides"""
        # Placeholder for PowerPoint integration
        pass
    
    def _export_slide_notes(self, e):
        """Export slide notes with citations"""
        # Placeholder for slide notes export
        pass
    
    def build(self) -> ft.Control:
        """Build the reports view"""
        return ft.Column([
            # Header
            ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text("Reports & Citations", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text("Generate bibliographies and manage PowerPoint citations", size=14, color=ft.colors.GREY_600)
                    ], spacing=2),
                ], spacing=10),
                padding=ft.padding.all(20),
                bgcolor=ft.colors.GREY_100 if self.page.theme_mode != ft.ThemeMode.DARK else ft.colors.GREY_800,
                border=ft.border.only(bottom=ft.BorderSide(1, ft.colors.GREY_300))
            ),
            
            # Progress stats
            ft.Container(
                content=self.progress_stats,
                padding=ft.padding.symmetric(horizontal=20, vertical=15)
            ),
            
            # Main tabbed content
            ft.Container(
                content=self.main_tabs,
                expand=True,
                padding=ft.padding.symmetric(horizontal=20)
            )
        ], expand=True, spacing=0)
