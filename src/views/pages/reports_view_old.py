"""
Reports View - Generate bibliographies and export citations
"""

import flet as ft
import os
from typing import Optional, List, Dict, Any
from views.base_view import BaseView
from views.components.source_ui_factory import SourceUIFactory, SourceItem


class ReportsView(BaseView):
    """View for generating reports, bibliographies, and exporting citations"""
    
    def __init__(self, page: ft.Page, theme_manager=None, 
                 user_config=None, on_navigate=None):
        super().__init__(page)
        self.theme_manager = theme_manager
        self.user_config = user_config
        self.on_navigate = on_navigate
        
        # Current project data
        self.current_project = "Strategic Analysis 2025"
        self.slide_citations = self._create_dummy_slide_citations()
        self.project_sources = self._create_dummy_project_sources()
        
        # Export file paths
        self.word_export_path = ""
        self.pdf_export_path = ""
        self.powerpoint_export_path = ""
        
        # Initialize UI components
        self._init_components()
    
"""
Reports View - Generate bibliographies and export citations
"""

import flet as ft
import os
from typing import Optional, List, Dict, Any
from views.base_view import BaseView
from views.components.source_ui_factory import SourceUIFactory, SourceItem


class ReportsView(BaseView):
    """Modern export-focused view for generating reports and managing citations"""
    
    def __init__(self, page: ft.Page, theme_manager=None, 
                 user_config=None, on_navigate=None, controller=None):
        super().__init__(page, controller)
        self.theme_manager = theme_manager
        self.user_config = user_config
        self.on_navigate = on_navigate
        
        # Current project data
        self.current_project = "Strategic Analysis 2025"
        self.slide_citations = self._create_dummy_slide_citations()
        self.project_sources = self._create_dummy_project_sources()
        
        # Export settings
        self.export_paths = {
            'word': "",
            'pdf': "",
            'powerpoint': ""
        }
        
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
        """Initialize modern UI components"""
        # Project overview card
        self.project_overview = self._create_project_overview()
        
        # Export cards
        self.word_export_card = self._create_export_card(
            title="Word Document",
            subtitle="Professional bibliography for reports",
            icon=ft.icons.DESCRIPTION,
            color=ft.colors.BLUE_600,
            export_type="word"
        )
        
        self.pdf_export_card = self._create_export_card(
            title="PDF Export",
            subtitle="Portable document format",
            icon=ft.icons.PICTURE_AS_PDF,
            color=ft.colors.RED_600,
            export_type="pdf"
        )
        
        self.powerpoint_export_card = self._create_export_card(
            title="PowerPoint Citations",
            subtitle="Attach citations to slides",
            icon=ft.icons.SLIDESHOW,
            color=ft.colors.ORANGE_600,
            export_type="powerpoint"
        )
        
        # Bibliography preview
        self.bibliography_preview = self._create_bibliography_preview()
    
    def _create_project_overview(self) -> ft.Card:
        """Create project overview card"""
        total_slides = len(self.slide_citations)
        cited_slides = len([s for s in self.slide_citations.values() if s])
        completion_rate = cited_slides / total_slides if total_slides > 0 else 0
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.icons.ASSESSMENT, size=24, color=self._get_theme_color()),
                        ft.Text("Project Overview", size=18, weight=ft.FontWeight.BOLD)
                    ], spacing=10),
                    
                    ft.Divider(),
                    
                    ft.Row([
                        # Project name
                        ft.Column([
                            ft.Text("Current Project", size=12, color=ft.colors.GREY_600),
                            ft.Text(self.current_project, size=16, weight=ft.FontWeight.W_500)
                        ], spacing=4, expand=1),
                        
                        # Sources count
                        ft.Column([
                            ft.Text("Total Sources", size=12, color=ft.colors.GREY_600),
                            ft.Text(str(len(self.project_sources)), size=20, weight=ft.FontWeight.BOLD, color=self._get_theme_color())
                        ], spacing=4, expand=1),
                        
                        # Citation progress
                        ft.Column([
                            ft.Text("Citation Progress", size=12, color=ft.colors.GREY_600),
                            ft.Row([
                                ft.Text(f"{cited_slides}/{total_slides}", size=16, weight=ft.FontWeight.W_500),
                                ft.Container(
                                    content=ft.ProgressBar(value=completion_rate, color=self._get_theme_color(), height=8),
                                    width=80
                                )
                            ], spacing=8)
                        ], spacing=4, expand=1)
                    ], spacing=20)
                ], spacing=15),
                padding=ft.padding.all(20)
            ),
            elevation=2
        )
    
    def _create_export_card(self, title: str, subtitle: str, icon: str, color: str, export_type: str) -> ft.Card:
        """Create modern export option card"""
        
        # File path display
        path_display = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.FOLDER_OUTLINED, size=16, color=ft.colors.GREY_500),
                ft.Text(
                    self.export_paths.get(export_type, "No location selected"),
                    size=12,
                    color=ft.colors.GREY_600,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    expand=True
                )
            ], spacing=8),
            bgcolor=ft.colors.GREY_50,
            border_radius=6,
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            margin=ft.margin.only(bottom=15)
        )
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    # Header
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(icon, size=24, color=ft.colors.WHITE),
                            bgcolor=color,
                            border_radius=8,
                            padding=ft.padding.all(8)
                        ),
                        ft.Column([
                            ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(subtitle, size=12, color=ft.colors.GREY_600)
                        ], spacing=2, expand=True)
                    ], spacing=12),
                    
                    # File path
                    path_display,
                    
                    # Action buttons
                    ft.Row([
                        ft.ElevatedButton(
                            "Choose Location",
                            icon=ft.icons.FOLDER_OPEN,
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.GREY_100,
                                color=ft.colors.GREY_700
                            ),
                            on_click=lambda e, t=export_type: self._choose_export_location(t)
                        ),
                        ft.ElevatedButton(
                            "Export",
                            icon=ft.icons.DOWNLOAD,
                            style=ft.ButtonStyle(
                                bgcolor=color,
                                color=ft.colors.WHITE
                            ),
                            on_click=lambda e, t=export_type: self._perform_export(t)
                        )
                    ], spacing=10, alignment=ft.MainAxisAlignment.END)
                ], spacing=15),
                padding=ft.padding.all(20)
            ),
            elevation=2
        )
    
    def _create_bibliography_preview(self) -> ft.Card:
        """Create bibliography preview card"""
        bibliography_text = self._generate_bibliography_text()
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.icons.LIBRARY_BOOKS, size=24, color=self._get_theme_color()),
                        ft.Text("Bibliography Preview", size=18, weight=ft.FontWeight.BOLD),
                        ft.Spacer(),
                        ft.IconButton(
                            icon=ft.icons.COPY,
                            tooltip="Copy to clipboard",
                            on_click=self._copy_bibliography
                        )
                    ]),
                    
                    ft.Divider(),
                    
                    ft.Container(
                        content=ft.Column([
                            ft.Text(bibliography_text, size=12, selectable=True)
                        ], scroll=ft.ScrollMode.AUTO),
                        height=300,
                        bgcolor=ft.colors.GREY_50,
                        border_radius=8,
                        padding=ft.padding.all(15)
                    )
                ], spacing=15),
                padding=ft.padding.all(20)
            ),
            elevation=2
        )
    
    def _generate_bibliography_text(self) -> str:
        """Generate formatted bibliography text"""
        sources = [
            "Corporate Finance Department. (2024). Annual Financial Report 2024. Company Publications.",
            "Customer Experience Team. (2024). Customer Satisfaction Survey 2024. Internal Report.",
            "Executive Team. (2025). Strategic Plan 2025-2030. Internal Documentation.",
            "Finance Team. (2024). Budget Allocation Analysis 2024. Financial Reports.",
            "Market Research Inc. (2024). Consumer Trends Study Q4. Market Research Publications."
        ]
        return "\n\n".join(sources)
    
    def _choose_export_location(self, export_type: str):
        """Open file picker to choose export location"""
        def on_result(e: ft.FilePickerResultEvent):
            if e.path:
                self.export_paths[export_type] = e.path
                self._update_export_card(export_type)
        
        # File extensions based on export type
        extensions = {
            'word': ['docx'],
            'pdf': ['pdf'],
            'powerpoint': ['pptx']
        }
        
        file_picker = ft.FilePicker(on_result=on_result)
        self.page.overlay.append(file_picker)
        self.page.update()
        
        file_picker.save_file(
            dialog_title=f"Choose {export_type.title()} export location",
            file_name=f"bibliography.{extensions[export_type][0]}",
            allowed_extensions=extensions[export_type]
        )
    
    def _update_export_card(self, export_type: str):
        """Update export card with new path"""
        # This would update the UI - simplified for this implementation
        self.page.update()
    
    def _perform_export(self, export_type: str):
        """Perform the actual export"""
        if not self.export_paths.get(export_type):
            self._show_error(f"Please choose a location for {export_type} export first")
            return
        
        # Here you would integrate with your existing export logic
        if export_type == "word":
            self._export_word()
        elif export_type == "pdf":
            self._export_pdf()
        elif export_type == "powerpoint":
            self._attach_to_powerpoint()
    
    def _copy_bibliography(self, e):
        """Copy bibliography to clipboard"""
        bibliography_text = self._generate_bibliography_text()
        if hasattr(self.page, 'set_clipboard'):
            self.page.set_clipboard(bibliography_text)
        self._show_success("Bibliography copied to clipboard!")
    
    def _show_error(self, message: str):
        """Show error message"""
        snack = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.colors.RED_400
        )
        self.page.snack_bar = snack
        snack.open = True
        self.page.update()
    
    def _show_success(self, message: str):
        """Show success message"""
        snack = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.colors.GREEN_400
        )
        self.page.snack_bar = snack
        snack.open = True
        self.page.update()
    
    # Export methods (integrate with your existing production code)
    def _export_word(self):
        """Export bibliography as Word document"""
        # TODO: Integrate with your existing Word export logic
        self._show_success("Word document exported successfully!")
    
    def _export_pdf(self):
        """Export bibliography as PDF"""
        # TODO: Integrate with your existing PDF export logic
        self._show_success("PDF exported successfully!")
    
    def _attach_to_powerpoint(self):
        """Attach citations to PowerPoint slides"""
        # TODO: Integrate with your existing PowerPoint service
        self._show_success("Citations attached to PowerPoint successfully!")
    
    def build(self) -> ft.Control:
        """Build the modern reports view"""
        return ft.Column([
            # Header
            ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text("Reports & Export", size=28, weight=ft.FontWeight.BOLD),
                        ft.Text("Export your bibliography and citations in multiple formats", 
                               size=16, color=ft.colors.GREY_600)
                    ], spacing=8),
                ]),
                padding=ft.padding.all(30),
                bgcolor=ft.colors.with_opacity(0.02, self._get_theme_color())
            ),
            
            # Main content
            ft.Container(
                content=ft.Column([
                    # Project overview
                    self.project_overview,
                    
                    ft.Container(height=20),
                    
                    # Export options grid
                    ft.ResponsiveRow([
                        ft.Column([
                            self.word_export_card
                        ], col={"md": 4}),
                        ft.Column([
                            self.pdf_export_card
                        ], col={"md": 4}),
                        ft.Column([
                            self.powerpoint_export_card
                        ], col={"md": 4})
                    ]),
                    
                    ft.Container(height=20),
                    
                    # Bibliography preview
                    self.bibliography_preview
                ], spacing=20),
                padding=ft.padding.all(30),
                expand=True
            )
        ], expand=True, spacing=0)
