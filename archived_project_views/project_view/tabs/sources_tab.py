"""
Sources Tab for Project View
Handles source document management
"""

import flet as ft
from .base_tab import BaseProjectTab


class SourcesTab(BaseProjectTab):
    """Source management tab"""
    
    def build(self) -> ft.Control:
        """Build sources management tab"""
        return ft.Column([
            ft.Text("Source Management", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            
            # Source management controls
            ft.Row([
                ft.ElevatedButton(
                    "Add Source Manually",
                    icon=ft.icons.ADD,
                    on_click=lambda e: self._add_source_manually(),
                    style=ft.ButtonStyle(
                        bgcolor=self._get_theme_color(),
                        color=ft.colors.WHITE
                    )
                ),
                ft.ElevatedButton(
                    "Import Sources",
                    icon=ft.icons.UPLOAD_FILE,
                    on_click=lambda e: self._import_sources()
                ),
                ft.ElevatedButton(
                    "Scan Directory",
                    icon=ft.icons.FOLDER_OPEN,
                    on_click=lambda e: self._scan_directory()
                )
            ], spacing=10),
            
            ft.Container(height=20),
            
            # Sources list (placeholder)
            ft.Container(
                content=ft.Column([
                    ft.Text("Sources will be listed here", size=14, color=ft.colors.GREY_600),
                    ft.Text("• Add sources manually", size=12, color=ft.colors.GREY_500),
                    ft.Text("• Import from other projects", size=12, color=ft.colors.GREY_500),
                    ft.Text("• Scan project directories", size=12, color=ft.colors.GREY_500),
                ], spacing=5),
                padding=ft.padding.all(20),
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=5,
                height=300
            )
            
        ], spacing=5, scroll=ft.ScrollMode.AUTO)
    
    def _add_source_manually(self):
        """Add a source manually"""
        print("Add source manually - to be implemented")
    
    def _import_sources(self):
        """Import sources from external systems"""
        print("Import sources - to be implemented")
    
    def _scan_directory(self):
        """Scan directory for sources"""
        print("Scan directory - to be implemented")
