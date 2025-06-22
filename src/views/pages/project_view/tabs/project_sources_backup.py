"""
Project Sources Tab - Manage sources for the current project (UI Only Version)
"""

import flet as ft
from typing import Optional, Dict, Any, List
from views.components.source_ui_factory import SourceUIFactory, SourceItem


class ProjectSourcesTab:
    """Tab for managing project sources with drag-and-drop functionality (UI Only)"""
    
    def __init__(self, page: ft.Page, database_manager=None, project_data=None, project_path=None, theme_manager=None):
        self.page = page
        self.database_manager = database_manager
        self.project_data = project_data or {}
        self.project_path = project_path
        self.theme_manager = theme_manager
        
        # UI Factory
        self.ui_factory = SourceUIFactory()
        
        # Dummy data for UI testing
        self.on_deck_sources: List[SourceItem] = self._create_dummy_on_deck_sources()
        self.project_sources: List[SourceItem] = self._create_dummy_project_sources()
        
        # Create the main containers
        self._init_containers()
        
        # Load initial UI
        self._refresh_ui()
    
    def _create_dummy_on_deck_sources(self) -> List[SourceItem]:
        """Create dummy on-deck sources for UI testing"""
        return [
            SourceItem(
                uuid="on-deck-1",
                title="Annual Financial Report 2024",
                source_type="FCR",
                description="Complete financial statements and analysis",
                citation="Company Annual Report 2024"
            ),
            SourceItem(
                uuid="on-deck-2", 
                title="Quarterly Marketing Analysis",
                source_type="STD",
                description="Q3 marketing performance metrics",
                citation="Internal Marketing Report Q3-2024"
            ),
            SourceItem(
                uuid="on-deck-3",
                title="Customer Survey Results",
                source_type="GSC", 
                description="Customer satisfaction survey data",
                citation="Customer Survey 2024-Q4"
            ),
            SourceItem(
                uuid="on-deck-4",
                title="Compliance Audit Report",
                source_type="CRS",
                description="Annual compliance review findings",
                citation="Internal Audit Report 2024"
            )
        ]
    
    def _create_dummy_project_sources(self) -> List[SourceItem]:
        """Create dummy project sources for UI testing"""
        return [
            SourceItem(
                uuid="project-1",
                title="Strategic Plan 2025",
                source_type="STD",
                description="Five-year strategic planning document",
                citation="Strategic Planning Committee 2025",
                usage_notes="Used for long-term goal analysis in Section 3"
            ),
            SourceItem(
                uuid="project-2",
                title="Budget Allocation Report",
                source_type="FCR", 
                description="Departmental budget breakdown",
                citation="Finance Department 2024",
                usage_notes="Referenced in financial projections table"
            )
        ]
    
    def _get_theme_color(self) -> str:
        """Get theme color for buttons and UI elements"""
        if self.theme_manager:
            return self.theme_manager.get_primary_color() if hasattr(self.theme_manager, 'get_primary_color') else ft.colors.BLUE_600
        return ft.colors.BLUE_600 if self.page.theme_mode != ft.ThemeMode.DARK else ft.colors.BLUE_400
    
    def _init_containers(self):
        """Initialize the main containers for the tab"""
        # On Deck Circle - smaller left column
        self.on_deck_list = ft.Column(
            controls=[],  # Will be populated with sources
            spacing=10,
            scroll=ft.ScrollMode.AUTO
        )
        
        self.on_deck_container = ft.Container(
            content=ft.Column([
                self.ui_factory.create_section_header("On Deck Circle"),
                ft.Container(height=10),
                ft.Container(
                    content=self.on_deck_list,
                    expand=True,
                    bgcolor=ft.colors.GREY_50,
                    border_radius=8,
                    border=ft.border.all(1, ft.colors.GREY_300),
                    padding=ft.padding.all(15)
                )
            ], spacing=0),
            width=300,
            expand=False,
            padding=ft.padding.only(right=15)
        )
        
        # Main Sources - larger right column with drag/drop
        self.sources_list = ft.Column(
            controls=[],  # Will be populated with sources
            spacing=10
        )
        
        self.sources_container = ft.Container(
            content=ft.Column([
                # Header with Add Source button
                ft.Row([
                    self.ui_factory.create_section_header("Project Sources"),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "Add Source",
                        icon=ft.icons.ADD,
                        on_click=self._on_add_source_clicked,
                        style=ft.ButtonStyle(
                            color=ft.colors.WHITE,
                            bgcolor=self._get_theme_color()
                        )
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                ft.Container(
                    content=self.sources_list,
                    expand=True,
                    bgcolor=ft.colors.WHITE,
                    border_radius=8,
                    border=ft.border.all(1, ft.colors.BLUE_200),
                    padding=ft.padding.all(20)
                )
            ], spacing=0),
            expand=True
        )
    
    def _load_data(self):
        """Load data from service"""
        project_id = self.project_data.get('project_id', '')
        
        # Load sources from service
        self.on_deck_sources = self.sources_service.get_on_deck_sources(project_id)
        self.project_sources = self.sources_service.get_project_sources(project_id)
        
        # Update UI
        self._refresh_ui()
    
    def _refresh_ui(self):
        """Refresh the UI with current data"""
        # Clear existing controls
        self.on_deck_list.controls.clear()
        self.sources_list.controls.clear()
        
        # Update section headers with counts
        on_deck_header = self.ui_factory.create_section_header("On Deck Circle", len(self.on_deck_sources))
        project_header = self.ui_factory.create_section_header("Project Sources", len(self.project_sources))
        
        # Update headers in containers (access the Column content and update first control)
        if isinstance(self.on_deck_container.content, ft.Column):
            self.on_deck_container.content.controls[0] = on_deck_header
        if isinstance(self.sources_container.content, ft.Column):
            # Update the header part of the Row (first element of the Row)
            header_row = self.sources_container.content.controls[0]
            if isinstance(header_row, ft.Row):
                header_row.controls[0] = project_header
        
        # Populate On Deck Circle
        if self.on_deck_sources:
            for source in self.on_deck_sources:
                card = self.ui_factory.create_on_deck_source_card(
                    source,
                    on_add_to_project=self._handle_add_to_project
                )
                self.on_deck_list.controls.append(card)
        else:
            empty_message = self.ui_factory.create_empty_state_message(
                "No sources available",
                ft.icons.INBOX
            )
            self.on_deck_list.controls.append(empty_message)
        
        # Populate Project Sources
        if self.project_sources:
            for source in self.project_sources:
                card = self.ui_factory.create_project_source_card(
                    source,
                    on_remove_from_project=self._handle_remove_from_project,
                    on_edit_usage=self._handle_edit_usage
                )
                self.sources_list.controls.append(card)
        else:
            empty_message = self.ui_factory.create_empty_state_message(
                "No sources assigned to this project",
                ft.icons.SOURCE
            )
            self.sources_list.controls.append(empty_message)
        
        # Update the page
        if hasattr(self, 'page'):
            self.page.update()
    
    def _handle_add_to_project(self, source_id: str):
        """Handle adding a source to the project"""
        project_id = self.project_data.get('project_id', '')
        success = self.sources_service.add_source_to_project(source_id, project_id)
        
        if success:
            # Reload data and refresh UI
            self._load_data()
        else:
            # Show error message (could use a snackbar or dialog)
            print(f"Failed to add source {source_id} to project")
    
    def _handle_remove_from_project(self, source_id: str):
        """Handle removing a source from the project"""
        project_id = self.project_data.get('project_id', '')
        success = self.sources_service.remove_source_from_project(source_id, project_id)
        
        if success:
            # Reload data and refresh UI
            self._load_data()
        else:
            # Show error message
            print(f"Failed to remove source {source_id} from project")
    
    def _handle_edit_usage(self, source_id: str):
        """Handle editing usage notes for a source"""
        # TODO: Show dialog for editing usage notes
        # For now, just print the action
        print(f"Edit usage notes for source: {source_id}")
    
    def _on_add_source_clicked(self, e):
        """Handle add source button click - show dialog"""
        # Create the dynamic source entry form
        source_form = DynamicSourceEntryForm(
            page=self.page,
            database_manager=self.database_manager,
            on_source_created=self._on_source_created_from_dialog
        )
        
        # Create dialog
        dialog = ft.AlertDialog(
            title=ft.Text("Add New Source"),
            content=ft.Container(
                content=ft.Column(
                    controls=[source_form.build()],
                    scroll=ft.ScrollMode.AUTO
                ),
                width=500,
                height=600
            ),
            actions=[
                ft.TextButton(
                    text="Close",
                    on_click=lambda _: self._close_add_source_dialog()
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        # Store dialog reference and show it
        self.add_source_dialog = dialog
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _close_add_source_dialog(self):
        """Close the add source dialog"""
        if hasattr(self, 'add_source_dialog'):
            self.add_source_dialog.open = False
            self.page.update()
    
    def _on_source_created_from_dialog(self, source_uuid: str, source_type: str, form_data: Dict[str, Any]):
        """Handle when a source is created from the dialog"""
        print(f"Source created: {source_uuid} of type {source_type}")
        
        # Add the source to this project
        project_id = self.project_data.get('project_id', '')
        if project_id:
            # You could add usage notes here or prompt for them
            success = self.sources_service.add_source_to_project(source_uuid, project_id, "")
            if success:
                # Refresh the sources display
                self._load_data()
                print(f"Source {source_uuid} added to project {project_id}")
        
        # Close the dialog after a short delay
        self.page.run_task(self._close_dialog_after_delay)
    
    async def _close_dialog_after_delay(self):
        """Close dialog after a short delay"""
        import asyncio
        await asyncio.sleep(1.5)  # Wait 1.5 seconds
        self._close_add_source_dialog()
    
    def update_project_data(self, project_data: Dict[str, Any], project_path: str):
        """Update the tab with new project data"""
        self.project_data = project_data or {}
        self.project_path = project_path
        # Reload data for the new project
        self._load_data()
    
    def refresh_data(self):
        """Refresh the tab data"""
        self._load_data()
    
    def build(self) -> ft.Control:
        """Build the sources tab content with two-column layout"""
        return ft.Container(
            content=ft.Row([
                self.on_deck_container,
                self.sources_container
            ], 
            spacing=0,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START
            ),
            padding=ft.padding.all(20),
            expand=True
        )
    
    def can_navigate_away(self) -> bool:
        """Check if user can navigate away from this tab"""
        # For now, always allow navigation
        return True
