"""
Slide Assignments Tab for Project View
Handles slide creation and source assignments
"""

import flet as ft
from .base_tab import BaseProjectTab


class SlideAssignmentsTab(BaseProjectTab):
    """Slide assignments management tab"""
    
    def build(self) -> ft.Control:
        """Build slide assignments tab"""
        return ft.Column([
            ft.Text("Slide Assignments", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            
            # Slide management controls
            ft.Row([
                ft.ElevatedButton(
                    "Add Slide",
                    icon=ft.icons.ADD,
                    on_click=lambda e: self._add_slide(),
                    style=ft.ButtonStyle(
                        bgcolor=self._get_theme_color(),
                        color=ft.colors.WHITE
                    )
                ),
                ft.ElevatedButton(
                    "Assign Sources",
                    icon=ft.icons.LINK,
                    on_click=lambda e: self._assign_sources()
                ),
                ft.ElevatedButton(
                    "Generate Report",
                    icon=ft.icons.DESCRIPTION,
                    on_click=lambda e: self._generate_report()
                )
            ], spacing=10),
            
            ft.Container(height=20),
            
            # Slide assignments list (placeholder)
            ft.Container(
                content=ft.Column([
                    ft.Text("Slide assignments will be listed here", size=14, color=ft.colors.GREY_600),
                    ft.Text("• Create presentation slides", size=12, color=ft.colors.GREY_500),
                    ft.Text("• Assign sources to specific slides", size=12, color=ft.colors.GREY_500),
                    ft.Text("• Generate assignment reports", size=12, color=ft.colors.GREY_500),
                ], spacing=5),
                padding=ft.padding.all(20),
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=5,
                height=300
            )
            
        ], spacing=5, scroll=ft.ScrollMode.AUTO)
    
    def _add_slide(self):
        """Add a new slide"""
        print("Add slide - to be implemented")
    
    def _assign_sources(self):
        """Assign sources to slides"""
        print("Assign sources - to be implemented")
    
    def _generate_report(self):
        """Generate assignment report"""
        print("Generate report - to be implemented")
