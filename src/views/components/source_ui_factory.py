"""
Source UI Component Factory - Creates UI components for source items
"""

import flet as ft
from typing import Callable, Optional, List
from dataclasses import dataclass


@dataclass
class SourceItem:
    """Simple dataclass for source items - UI only version"""
    uuid: str
    title: str
    source_type: str
    citation: str = ""
    usage_notes: Optional[str] = None
    description: str = ""
    id: str = ""
    
    def __post_init__(self):
        if not self.id:
            self.id = self.uuid


class SourceUIFactory:
    """Factory for creating source UI components"""
    
    @staticmethod
    def create_on_deck_source_card(
        source: SourceItem,
        on_add_to_project: Optional[Callable[[str], None]] = None
    ) -> ft.Card:
        """Create a compact card for an on-deck source"""
        # Create main content with title and type
        main_content = ft.Column([
            ft.Text(
                source.title, 
                weight=ft.FontWeight.BOLD, 
                size=12,
                max_lines=2,
                overflow=ft.TextOverflow.ELLIPSIS
            ),
            ft.Text(
                source.source_type, 
                size=10, 
                color=ft.colors.BLUE_600,
                weight=ft.FontWeight.W_500
            )
        ], spacing=2, tight=True)
        
        # Add button if callback provided
        if on_add_to_project:
            content_row = ft.Row([
                main_content,
                ft.IconButton(
                    icon=ft.icons.ADD_CIRCLE_OUTLINE,
                    icon_size=16,
                    tooltip="Add to project",
                    on_click=lambda _: on_add_to_project(source.id)
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, expand=True)
        else:
            content_row = main_content
        
        return ft.Card(
            content=ft.Container(
                content=content_row,
                padding=ft.padding.all(8)  # Reduced padding for compactness
            ),
            elevation=1,
            margin=ft.margin.symmetric(vertical=2)  # Reduced margin
        )
    
    @staticmethod
    def create_project_source_card(
        source: SourceItem,
        on_remove_from_project: Optional[Callable[[str], None]] = None,
        on_edit_usage: Optional[Callable[[str], None]] = None
    ) -> ft.Card:
        """Create a card for a project source"""
        content_rows = [
            ft.Text(
                source.title, 
                weight=ft.FontWeight.BOLD, 
                size=13  # Slightly smaller title
            ),
            ft.Text(
                f"{source.source_type} - {source.description}", 
                size=11,  # Smaller description text
                color=ft.colors.GREY_600
            )
        ]
        
        # Add usage notes if available
        if source.usage_notes:
            content_rows.append(
                ft.Text(
                    f"Usage: {source.usage_notes}",
                    size=10,  # Smaller usage notes
                    color=ft.colors.BLUE_600,
                    italic=True
                )
            )
        
        # Create the main content column
        content_column = ft.Column(
            content_rows,
            spacing=2,  # Reduced spacing for compactness
            expand=True
        )
        
        # Create action buttons if callbacks provided
        action_buttons = []
        
        if on_edit_usage:
            action_buttons.append(
                ft.IconButton(
                    icon=ft.icons.EDIT_NOTE,
                    icon_size=16,
                    tooltip="Edit usage notes",
                    on_click=lambda _: on_edit_usage(source.id)
                )
            )
        
        if on_remove_from_project:
            action_buttons.append(
                ft.IconButton(
                    icon=ft.icons.REMOVE_CIRCLE_OUTLINE,
                    icon_size=16,
                    tooltip="Remove from project",
                    on_click=lambda _: on_remove_from_project(source.id)
                )
            )
        
        # Create the main row with content and actions
        main_row = ft.Row([content_column], expand=True)
        
        if action_buttons:
            main_row.controls.append(
                ft.Row(
                    action_buttons,
                    spacing=5,
                    tight=True
                )
            )
        
        return ft.Card(
            content=ft.Container(
                content=main_row,
                padding=ft.padding.all(8)  # Reduced padding for compactness
            ),
            elevation=1,  # Slightly reduced elevation
            margin=ft.margin.only(bottom=6)  # Reduced margin between cards
        )
    
    @staticmethod
    def create_draggable_source_card(
        source: SourceItem,
        on_remove_from_project: Optional[Callable[[str], None]] = None,
        on_edit_usage: Optional[Callable[[str], None]] = None
    ) -> ft.Draggable:
        """Create a draggable source card for reordering"""
        card = SourceUIFactory.create_project_source_card(
            source, on_remove_from_project, on_edit_usage
        )
        
        return ft.Draggable(
            content=card,
            data=source.id
        )
    
    @staticmethod
    def create_add_source_button(
        on_add_source: Callable[[], None],
        theme_color: str = ft.colors.BLUE_600
    ) -> ft.ElevatedButton:
        """Create a compact add source button for inline placement"""
        return ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.icons.ADD, size=14),
                ft.Text("Add New Source", size=12)
            ], spacing=4, tight=True),
            style=ft.ButtonStyle(
                bgcolor=theme_color,
                color=ft.colors.WHITE,
                padding=ft.padding.symmetric(horizontal=12, vertical=6),  # More compact for inline
                shape=ft.RoundedRectangleBorder(radius=6)
            ),
            height=32,  # Fixed compact height
            on_click=lambda _: on_add_source()
        )
    
    @staticmethod
    def create_empty_state_message(message: str, icon: str = ft.icons.INBOX) -> ft.Container:
        """Create an empty state message"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(
                    icon,
                    size=48,
                    color=ft.colors.GREY_400
                ),
                ft.Text(
                    message,
                    size=14,
                    color=ft.colors.GREY_500,
                    text_align=ft.TextAlign.CENTER
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
            ),
            padding=ft.padding.all(20),
            alignment=ft.alignment.center
        )
    
    @staticmethod
    def create_section_header(title: str, count: int = 0) -> ft.Text:
        """Create a section header with optional count"""
        display_title = f"{title} ({count})" if count > 0 else title
        return ft.Text(
            display_title,
            size=18,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.BLUE_700
        )
