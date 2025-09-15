import flet as ft
from ..base_view import BaseView
from typing import Dict, Any, List

# --- Refactor: Import tab components from the new 'admin' sub-package ---
from .admin.source_type_editor import SourceTypeEditor
from .admin.project_type_editor import ProjectTypeEditor
from .admin.user_management_tab import UserManagementTab
from .admin.legacy_migration_tab import LegacyMigrationTab


class BoilerplateSourcesTab(ft.Column):
    """A UI component for managing boilerplate sources in the admin panel."""

    def __init__(self, controller):
        super().__init__(expand=True, scroll=ft.ScrollMode.ADAPTIVE, spacing=10)
        self.controller = controller
        self.sources_list = ft.ListView(expand=True, spacing=10)
        self._build_ui()
        self.update_sources_list()

    def _build_ui(self):
        """Constructs the static parts of the UI."""
        self.controls.extend([
            ft.Text("Manage Boilerplate Sources", theme_style=ft.TextThemeStyle.TITLE_LARGE),
            ft.Text("These sources are available to all projects and are not tied to a specific country.", color=self.controller.page.theme.color_scheme.on_surface_variant),
            ft.Divider(),
            self.sources_list
        ])

    def update_sources_list(self):
        """Fetches the latest boilerplate source list and rebuilds the list view."""
        self.sources_list.controls.clear()
        sources = self.controller.admin_controller.get_boilerplate_sources()
        for source in sorted(sources, key=lambda s: s.get_title()):
            self.sources_list.controls.append(ft.Card(content=ft.ListTile(leading=ft.Icon(ft.icons.DESCRIPTION_OUTLINED),title=ft.Text(source.get_title(), weight=ft.FontWeight.BOLD),subtitle=ft.Text(f"Type: {source.source_type.replace('_', ' ').title()}"))))
        if self.page:
            self.page.update()

class AdminView(BaseView):
    """The UI for the Admin page, focused on configuration management."""

    def __init__(self, page: ft.Page, controller):
        super().__init__(page, controller)
        self.controller = controller

        # --- UI State ---
        self.selected_config_type: str | None = None # e.g., 'source' or 'project'
        self.selected_item_name: str | None = None   # e.g., 'book' or 'STD'

        # --- UI Components ---
        self.source_types_list = ft.ListView(expand=True, spacing=5)
        self.project_types_list = ft.ListView(expand=True, spacing=5)
        
        # Each tab needs its own editor column, as a control can only have one parent.
        self.source_editor_column = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.ADAPTIVE,
            spacing=15,
        )
        self.project_editor_column = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.ADAPTIVE,
            spacing=15,
        )
        
        self.tabs_control: ft.Tabs | None = None

    def build(self) -> ft.Control:
        """Builds the UI for the admin page content with a tabbed interface."""
        # Populate the lists for both tabs initially
        self._populate_source_types()
        self._populate_project_types()

        # Create the content for each tab using the helper layout
        source_types_tab_content = self._build_config_editor_layout(
            "Source Types", 
            self.source_types_list,
            self._on_add_source_type_clicked,
            self.source_editor_column
        )
        project_types_tab_content = self._build_config_editor_layout(
            "Project Types", 
            self.project_types_list,
            self._on_add_project_type_clicked,
            self.project_editor_column
        )

        # --- NEW: Placeholder content for new tabs ---
        users_tab_content = UserManagementTab(controller=self.controller)
        boilerplate_tab_content = BoilerplateSourcesTab(controller=self.controller)
        migration_tab_content = LegacyMigrationTab(controller=self.controller)

        self.tabs_control = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="Source Types", content=source_types_tab_content),
                ft.Tab(text="Project Types", content=project_types_tab_content),
                ft.Tab(text="Boilerplate Sources", content=boilerplate_tab_content),
                ft.Tab(text="Users", content=users_tab_content),
                ft.Tab(text="Legacy Migration", content=migration_tab_content),
            ],
            on_change=self._on_tab_change,
            expand=True,
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Configuration Management", theme_style=ft.TextThemeStyle.HEADLINE_LARGE),
                    ft.Text("Define the data structure for source and project types across the application."),
                    self.tabs_control,
                ],
                expand=True,
                spacing=10,
            ),
            padding=20,
            expand=True,
        )

    def _build_config_editor_layout(self, title: str, list_view: ft.ListView, on_add_callback, editor_column: ft.Column) -> ft.Row:
        """Helper to create the consistent two-column layout for a config type."""
        types_column = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(title, theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                    ft.IconButton(icon=ft.icons.ADD, on_click=on_add_callback, tooltip=f"Add New {title.replace('s', '')}")
                ]),
                ft.Divider(),
                list_view, # This is the ft.ListView
            ]),
            padding=15,
            border_radius=8,
            bgcolor=self.colors.surface_variant,
            expand=1, # Use a ratio for the flex layout
        )

        editor_container = ft.Container(
            content=editor_column, # Use the passed-in editor_column
            padding=20,
            expand=3, # Give the editor more space
            border_radius=8,
            alignment=ft.alignment.top_left, # Justify content to the top
        )

        return ft.Row(
            [
                types_column,
                ft.VerticalDivider(),
                editor_container,
            ],
            expand=True, # Ensure expand is set here
            spacing=10,
        )

    def _populate_source_types(self):
        """Fetches source types and populates the source types list."""
        self.source_types_list.controls.clear()
        source_types_items = self.controller.admin_controller.get_all_source_types()
        # Sort by display_order, then by name as a fallback
        sorted_source_types = sorted(source_types_items, key=lambda item: (item[1].get('display_order', 0), item[0]))
        
        for type_name, type_config in sorted_source_types:
            self.source_types_list.controls.append(
                ft.ListTile(
                    title=ft.Text(type_name.replace("_", " ").title()),
                    on_click=lambda e, t='source': self._on_item_selected(e, t),
                    data=type_name,
                )
            )
        if self.page.window:  # Avoid error on first build
            self.page.update()
    
    def _populate_project_types(self):
        """Fetches project types and populates the project types list."""
        self.project_types_list.controls.clear()
        project_types_items = self.controller.admin_controller.get_all_project_types()
        # Sort by display_order, then by name as a fallback
        sorted_project_types = sorted(project_types_items, key=lambda item: (item[1].get('display_order', 0), item[0]))

        for type_name, type_config in sorted_project_types:
            # Use display_name for the title if available, otherwise use the type_name
            display_name = type_config.get('display_name', type_name)
            self.project_types_list.controls.append(
                ft.ListTile(
                    title=ft.Text(display_name),
                    on_click=lambda e, t='project': self._on_item_selected(e, t),
                    data=type_name,
                )
            )
        if self.page.window:  # Avoid error on first build
            self.page.update()

    def _on_tab_change(self, e):
        self.selected_config_type = None # Clear selection on tab change
        self.selected_item_name = None
        self._build_editor_for_selection() # Rebuild editor for empty selection
        self._update_selection_visuals() # Clear selection visuals

    def _on_item_selected(self, e, config_type: str):
        """Handles the selection of any item from either list."""
        self.selected_config_type = config_type
        self.selected_item_name = e.control.data
        self._update_selection_visuals()
        self._build_editor_for_selection()
        self.page.update()

    def _update_selection_visuals(self):
        """Updates the background color of the selected item in the correct list."""
        # Update source list visuals
        for control in self.source_types_list.controls:
            if isinstance(control, ft.ListTile):
                is_selected = self.selected_config_type == 'source' and control.data == self.selected_item_name
                control.bgcolor = self.colors.primary_container if is_selected else None
        
        # Update project list visuals
        for control in self.project_types_list.controls:
            if isinstance(control, ft.ListTile):
                is_selected = self.selected_config_type == 'project' and control.data == self.selected_item_name
                control.bgcolor = self.colors.primary_container if is_selected else None

def _update_selection_visuals(self):
        """Updates the background color of the selected item in the correct list."""
        # Update source list visuals
        for control in self.source_types_list.controls:
            if isinstance(control, ft.ListTile):
                is_selected = self.selected_config_type == 'source' and control.data == self.selected_item_name
                control.bgcolor = self.colors.primary_container if is_selected else None
        
        # Update project list visuals
        for control in self.project_types_list.controls:
            if isinstance(control, ft.ListTile):
                is_selected = self.selected_config_type == 'project' and control.data == self.selected_item_name
                control.bgcolor = self.colors.primary_container if is_selected else None


    def _build_editor_for_selection(self):
        """Routes to the correct editor builder based on the selected type."""
        # Clear both editor columns before building
        self.source_editor_column.controls.clear()
        self.project_editor_column.controls.clear()

        if self.selected_config_type and self.selected_item_name:
            if self.selected_config_type == 'source':
                editor = SourceTypeEditor(self.selected_item_name, self.controller, self.colors)
                self.source_editor_column.controls.append(editor)
            elif self.selected_config_type == 'project':
                editor = ProjectTypeEditor(self.selected_item_name, self.controller, self.colors)
                self.project_editor_column.controls.append(editor)
        else: # No item selected
            # Add placeholder text to both columns for the initial state
            placeholder_text = "Select an item from a list to begin."
            self.source_editor_column.controls.append(ft.Text(placeholder_text, italic=True))
            self.project_editor_column.controls.append(ft.Text(placeholder_text, italic=True))

    def update_view(self):
        """Refreshes the lists of types when a new one is added."""
        self._populate_source_types()
        self._populate_project_types()
        self._update_selection_visuals()
        # Also update the user management tab if it exists
        if self.tabs_control:
            for tab in self.tabs_control.tabs:
                if isinstance(tab.content, UserManagementTab):
                    tab.content.update_users_list()
                if isinstance(tab.content, BoilerplateSourcesTab):
                    tab.content.update_sources_list()
        self.page.update()

    def _on_add_source_type_clicked(self, e):
        """Opens the dialog to add a new source type."""
        self.controller.dialog_controller.open_add_source_type_dialog()

    def _on_add_project_type_clicked(self, e):
        """Opens the dialog to add a new project type."""
        self.controller.dialog_controller.open_add_project_type_dialog()