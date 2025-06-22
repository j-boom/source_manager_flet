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
        # On Deck Circle - smaller left column with enhanced scrolling
        self.on_deck_list = ft.Column(
            controls=[],  # Will be populated with sources
            spacing=5,  # Reduced spacing for compactness
            scroll=ft.ScrollMode.AUTO,
            height=400  # Fixed height to ensure scrolling works
        )
        
        # Project Sources - main right column with reorderable list
        self.project_sources_list = ft.Column(
            controls=[],  # Will be populated with sources
            spacing=10,
            scroll=ft.ScrollMode.AUTO
        )
        
        # Main container with two-column layout
        self.main_container = ft.Row([
            # Left column - On Deck Circle (30% width)
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Text(
                            "On Deck Circle",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=self._get_theme_color()
                        ),
                        padding=ft.padding.only(bottom=10)
                    ),
                    # Scrollable container for on-deck sources
                    ft.Container(
                        content=self.on_deck_list,
                        bgcolor=ft.colors.GREY_50,
                        border_radius=8,
                        border=ft.border.all(1, ft.colors.GREY_300),
                        padding=ft.padding.all(10),
                        height=400,  # Fixed height for scrolling
                        expand=False
                    ),
                    ft.Container(height=10),  # Spacer
                    # Add source button
                    self.ui_factory.create_add_source_button(
                        on_add_source=self._on_add_source_clicked,
                        theme_color=self._get_theme_color()
                    )
                ], expand=True),
                width=280,  # Slightly reduced width for compactness
                padding=ft.padding.all(15)
            ),
            
            # Divider
            ft.VerticalDivider(width=1, color=ft.colors.GREY_300),
            
            # Right column - Project Sources (70% width)
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Text(
                            "Project Sources",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=self._get_theme_color()
                        ),
                        padding=ft.padding.only(bottom=10)
                    ),
                    ft.Text(
                        "Drag sources to reorder them",
                        size=12,
                        color=ft.colors.GREY_600,
                        italic=True
                    ),
                    ft.Container(height=5),  # Small spacer
                    self.project_sources_list
                ], expand=True),
                expand=True,
                padding=ft.padding.all(15)
            )
        ], expand=True)
    
    def _refresh_ui(self):
        """Refresh the UI with current data"""
        # Clear existing controls
        self.on_deck_list.controls.clear()
        self.project_sources_list.controls.clear()
        
        # Populate on-deck sources with compact cards
        for source in self.on_deck_sources:
            card = self.ui_factory.create_on_deck_source_card(
                source,
                on_add_to_project=self._on_add_to_project
            )
            self.on_deck_list.controls.append(card)
        
        # Add drag target for on-deck circle if there are sources
        if self.on_deck_list.controls:
            self.on_deck_list.controls.append(
                ft.Container(
                    content=ft.Text(
                        "Drop here to remove from project",
                        text_align=ft.TextAlign.CENTER,
                        color=ft.colors.GREY_500,
                        size=10
                    ),
                    height=30,  # Reduced height for compactness
                    bgcolor=ft.colors.GREY_100,
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=5,
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(top=5)
                )
            )
        
        # Populate project sources with draggable cards and drag targets
        for i, source in enumerate(self.project_sources):
            # Add drag target before each source (for reordering)
            self.project_sources_list.controls.append(
                ft.DragTarget(
                    content=ft.Container(
                        content=ft.Text(
                            "Drop here to reorder",
                            text_align=ft.TextAlign.CENTER,
                            color=ft.colors.TRANSPARENT
                        ),
                        height=5,
                        bgcolor=ft.colors.TRANSPARENT,
                        border=ft.border.all(1, ft.colors.TRANSPARENT),
                        border_radius=3
                    ),
                    on_accept=lambda e, index=i: self._on_reorder_source(e, index)
                )
            )
            
            # Add the draggable source card
            draggable_card = self.ui_factory.create_draggable_source_card(
                source,
                on_remove_from_project=self._on_remove_from_project,
                on_edit_usage=self._on_edit_usage_notes
            )
            self.project_sources_list.controls.append(draggable_card)
        
        # Add final drag target at the end for adding sources
        self.project_sources_list.controls.append(
            ft.DragTarget(
                content=ft.Container(
                    content=ft.Text(
                        "Drop here to add to project or reorder",
                        text_align=ft.TextAlign.CENTER,
                        color=ft.colors.GREY_500
                    ),
                    height=50,
                    bgcolor=ft.colors.GREY_100,
                    border=ft.border.all(2, ft.colors.GREY_300),
                    border_radius=5,
                    alignment=ft.alignment.center
                ),
                on_accept=self._on_drag_to_project
            )
        )
        
        if self.page:
            self.page.update()
    
    def _on_add_to_project(self, source_id: str):
        """Handle adding a source to the project"""
        # Find the source in on-deck
        source_to_move = None
        for source in self.on_deck_sources:
            if source.id == source_id:
                source_to_move = source
                break
        
        if source_to_move:
            # Move from on-deck to project
            self.on_deck_sources.remove(source_to_move)
            self.project_sources.append(source_to_move)
            self._refresh_ui()
            self._show_success_message(f"Added '{source_to_move.title}' to project")
    
    def _on_remove_from_project(self, source_id: str):
        """Handle removing a source from the project"""
        # Find the source in project
        source_to_move = None
        for source in self.project_sources:
            if source.id == source_id:
                source_to_move = source
                break
        
        if source_to_move:
            # Move from project to on-deck
            self.project_sources.remove(source_to_move)
            self.on_deck_sources.append(source_to_move)
            self._refresh_ui()
            self._show_success_message(f"Removed '{source_to_move.title}' from project")
    
    def _on_edit_usage_notes(self, source_id: str):
        """Handle editing usage notes for a source"""
        # Find the source
        source = None
        for s in self.project_sources:
            if s.id == source_id:
                source = s
                break
        
        if source:
            self._show_usage_notes_dialog(source)
    
    def _on_drag_to_project(self, e):
        """Handle dragging a source to the project area"""
        source_id = e.data
        self._on_add_to_project(source_id)
    
    def _on_drag_to_on_deck(self, e):
        """Handle dragging a source back to on-deck"""
        source_id = e.data
        self._on_remove_from_project(source_id)
    
    def _on_add_source_clicked(self):
        """Handle add new source button click"""
        self._show_add_source_dialog()
    
    def _on_reorder_source(self, e, drop_index: int):
        """Handle reordering sources within the project sources list"""
        source_id = e.data
        
        # Find the source being dragged
        source_to_move = None
        current_index = -1
        for i, source in enumerate(self.project_sources):
            if source.id == source_id:
                source_to_move = source
                current_index = i
                break
        
        if source_to_move and current_index != -1 and current_index != drop_index:
            # Remove from current position
            self.project_sources.pop(current_index)
            
            # Adjust drop index if necessary
            if current_index < drop_index:
                drop_index -= 1
            
            # Insert at new position
            self.project_sources.insert(drop_index, source_to_move)
            
            # Refresh UI to show new order
            self._refresh_ui()
            self._show_success_message(f"Moved '{source_to_move.title}' to position {drop_index + 1}")
    
    def _show_add_source_dialog(self):
        """Show dialog for adding a new source (dummy implementation)"""
        def on_create_source(e):
            # Create a dummy new source
            new_source = SourceItem(
                uuid=f"new-{len(self.on_deck_sources) + 1}",
                title=title_field.value or "New Source",
                source_type=type_field.value or "STD",
                description=desc_field.value or "New source description",
                citation=citation_field.value or "Citation needed"
            )
            self.on_deck_sources.append(new_source)
            self._refresh_ui()
            dialog.open = False
            self.page.update()
            self._show_success_message(f"Created new source: {new_source.title}")
        
        title_field = ft.TextField(label="Source Title", width=300)
        type_field = ft.Dropdown(
            label="Source Type",
            width=300,
            options=[
                ft.dropdown.Option("STD", "Standard"),
                ft.dropdown.Option("FCR", "Financial Report"),
                ft.dropdown.Option("GSC", "Government Source"),
                ft.dropdown.Option("CRS", "Compliance Report")
            ]
        )
        desc_field = ft.TextField(label="Description", width=300)
        citation_field = ft.TextField(label="Citation", width=300)
        
        dialog = ft.AlertDialog(
            title=ft.Text("Add New Source"),
            content=ft.Column([
                title_field,
                type_field,
                desc_field,
                citation_field
            ], tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
                ft.ElevatedButton("Create", on_click=on_create_source)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _show_usage_notes_dialog(self, source: SourceItem):
        """Show dialog for editing usage notes"""
        def on_save_notes(e):
            source.usage_notes = notes_field.value
            self._refresh_ui()
            dialog.open = False
            self.page.update()
            self._show_success_message(f"Updated usage notes for '{source.title}'")
        
        notes_field = ft.TextField(
            label="Usage Notes",
            value=source.usage_notes or "",
            multiline=True,
            max_lines=4,
            width=400
        )
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"Edit Usage Notes - {source.title}"),
            content=notes_field,
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
                ft.ElevatedButton("Save", on_click=on_save_notes)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _show_success_message(self, message: str):
        """Show a success message to the user"""
        snack = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.colors.GREEN_400
        )
        self.page.snack_bar = snack
        snack.open = True
        self.page.update()
    
    def update_project_data(self, project_data: Dict[str, Any], project_path: str):
        """Update the tab with new project data"""
        self.project_data = project_data or {}
        self.project_path = project_path
        # In a real implementation, this would reload data
        # For UI-only, we just keep the dummy data
    
    def refresh_data(self):
        """Refresh the tab data"""
        # In UI-only mode, just refresh the display
        self._refresh_ui()
    
    def can_navigate_away(self) -> bool:
        """Check if user can navigate away from this tab"""
        return True
    
    def build(self) -> ft.Container:
        """Build and return the main tab content"""
        return ft.Container(
            content=self.main_container,
            expand=True,
            padding=ft.padding.all(10)
        )
