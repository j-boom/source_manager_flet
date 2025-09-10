import flet as ft
from src.views.base_view import BaseView
from typing import Dict, Any

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
        self.editor_column = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.ADAPTIVE,
            spacing=15,
        )

    def build(self) -> ft.Control:
        """Builds the UI for the admin page content with a tabbed interface."""
        
        # Populate the lists for both tabs initially
        self._populate_source_types()
        self._populate_project_types()

        # Create the content for each tab
        source_types_tab_content = self._build_config_editor_layout(
            "Source Types", 
            self.source_types_list,
            self._on_add_source_type_clicked
        )
        project_types_tab_content = self._build_config_editor_layout(
            "Project Types", 
            self.project_types_list,
            self._on_add_project_type_clicked
        )

        tabs_control = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="Source Types", content=source_types_tab_content),
                ft.Tab(text="Project Types", content=project_types_tab_content),
            ],
            on_change=self._on_tab_change,
            expand=True,
        )

        return ft.Column(
            [
                ft.Text("Configuration Management", theme_style=ft.TextThemeStyle.HEADLINE_LARGE),
                ft.Text("Define the data structure for source and project types across the application."),
                tabs_control,
            ],
            expand=True,
            spacing=10,
        )

    def _build_config_editor_layout(self, title: str, list_view: ft.ListView, on_add_callback) -> ft.Row:
        """Helper to create the consistent two-column layout for a config type."""
        types_column = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(title, theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                    ft.IconButton(icon=ft.icons.ADD, on_click=on_add_callback, tooltip=f"Add New {title.replace('s', '')}")
                ]),
                ft.Divider(),
                list_view,
            ]),
            padding=15,
            border_radius=8,
            bgcolor=self.colors.surface_variant,
        )

        editor_container = ft.Container(
            content=self.editor_column,
            padding=20,
            expand=True,
        )

        return ft.Row(
            [
                types_column,
                ft.VerticalDivider(),
                editor_container,
            ],
            expand=True,
            spacing=10
        )

    def _populate_source_types(self):
        """Fetches source types and populates the source types list."""
        self.source_types_list.controls.clear()
        source_types = self.controller.admin_controller.get_all_source_types()
        for type_name in source_types:
            self.source_types_list.controls.append(
                ft.ListTile(
                    title=ft.Text(type_name.replace("_", " ").title()),
                    on_click=lambda e, t='source': self._on_item_selected(e, t),
                    data=type_name,
                )
            )
    
    def _populate_project_types(self):
        """Fetches project types and populates the project types list."""
        self.project_types_list.controls.clear()
        project_types = self.controller.admin_controller.get_all_project_types()
        for type_name in project_types:
            self.project_types_list.controls.append(
                ft.ListTile(
                    title=ft.Text(type_name),
                    on_click=lambda e, t='project': self._on_item_selected(e, t),
                    data=type_name,
                )
            )

    def _on_tab_change(self, e):
        """Resets the view when the user switches tabs."""
        self.selected_config_type = None
        self.selected_item_name = None
        self._build_editor_for_selection()
        self._update_selection_visuals()
        self.page.update()

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

    def _build_editor_for_selection(self):
        """Routes to the correct editor builder based on the selected type."""
        self.editor_column.controls.clear()
        if self.selected_config_type == 'source':
            self._build_source_editor(self.selected_item_name)
        elif self.selected_config_type == 'project':
            self._build_project_editor(self.selected_item_name)
        else:
            self.editor_column.controls.append(ft.Text("Select an item from a list to begin.", italic=True))

    def _build_source_editor(self, type_name: str):
        """Dynamically builds the editor UI for the selected source type."""
        if not type_name: return
        type_config = self.controller.admin_controller.get_source_type_config(type_name)
        if not type_config:
            self.editor_column.controls.append(ft.Text(f"Could not load config for {type_name}.", color=self.colors.error))
            return

        fields_list = ft.Column(spacing=10)
        for field in type_config.get('fields', []):
            fields_list.controls.append(self._create_field_editor_card(field))

        self.editor_column.controls.extend([
            ft.Text(f"Editing Source Type: {type_name.replace('_', ' ').title()}", theme_style=ft.TextThemeStyle.HEADLINE_SMALL),
            ft.Divider(),
            fields_list,
            ft.Row([
                ft.ElevatedButton("Add Field", icon=ft.icons.ADD, on_click=lambda e: self._on_add_field_clicked()),
                ft.Container(expand=True),
                ft.FilledButton("Save Changes", icon=ft.icons.SAVE, on_click=lambda e: self._on_save_changes_clicked()),
            ])
        ])

    def _build_project_editor(self, type_name: str):
        """Dynamically builds the editor UI for the selected project type."""
        if not type_name: return
        project_config = self.controller.admin_controller.get_project_type_config(type_name)
        if not project_config:
            self.editor_column.controls.append(ft.Text(f"Could not load config for {type_name}.", color=self.colors.error))
            return

        # UI elements for project type properties
        display_name_field = ft.TextField(
            label="Display Name",
            value=project_config.get("display_name", ""),
            expand=True
        )
        description_field = ft.TextField(
            label="Description",
            value=project_config.get("description", ""),
            multiline=True,
            min_lines=3,
            max_lines=5,
            expand=True
        )
        filename_pattern_field = ft.TextField(
            label="Filename Pattern",
            value=project_config.get("filename_pattern", ""),
            expand=True
        )

        # For field_names, we'll display them as a comma-separated string for now
        # A more advanced editor would allow adding/removing/reordering fields
        field_names_str = ", ".join(project_config.get("field_names", []))
        field_names_field = ft.TextField(
            label="Field Names (comma-separated)",
            value=field_names_str,
            multiline=True,
            min_lines=3,
            max_lines=5,
            expand=True
        )

        self.editor_column.controls.extend([
            ft.Text(f"Editing Project Type: {type_name}", theme_style=ft.TextThemeStyle.HEADLINE_SMALL),
            ft.Divider(),
            display_name_field,
            description_field,
            filename_pattern_field,
            field_names_field,
            ft.Row([
                ft.Container(expand=True), # Pushes button to the right
                ft.FilledButton(
                    "Save Changes",
                    icon=ft.icons.SAVE,
                    on_click=lambda e: self._on_save_project_changes_clicked(
                        type_name,
                        display_name_field.value,
                        description_field.value,
                        filename_pattern_field.value,
                        field_names_field.value
                    )
                ),
            ])
        ])

    def _on_save_project_changes_clicked(self, type_name: str, display_name: str, description: str, filename_pattern: str, field_names_str: str):
        new_config = {
            "display_name": display_name,
            "description": description,
            "filename_pattern": filename_pattern,
            "field_names": [name.strip() for name in field_names_str.split(',') if name.strip()]
        }
        self.controller.admin_controller.save_project_type_config(type_name, new_config)
        self.page.snack_bar = ft.SnackBar(ft.Text(f"Successfully saved configuration for {type_name}."), open=True)
        self.page.update()

    def _create_field_editor_card(self, field_data: Dict[str, Any]) -> ft.Card:
        """Creates a card with controls to edit a single source or project field."""
        return ft.Card(
            content=ft.Container(
                content=ft.Row([
                    ft.TextField(label="Field Name", value=field_data.get("name"), expand=2),
                    ft.TextField(label="Display Label", value=field_data.get("label"), expand=2),
                    ft.Dropdown(
                        label="Field Type",
                        options=[ft.dropdown.Option(t.value) for t in self.controller.admin_controller.get_field_types()],
                        value=field_data.get("field_type"),
                        expand=1
                    ),
                    ft.Checkbox(label="Required", value=field_data.get("required", False)),
                    ft.Checkbox(label="Title Part", value=field_data.get("is_title_part", False)),
                    ft.IconButton(icon=ft.icons.DELETE_OUTLINE, icon_color=self.colors.error, on_click=lambda e: self._on_delete_field_clicked(e.control.parent))
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=10),
                padding=15
            )
        )

    def _on_add_source_type_clicked(self, e):
        self.page.snack_bar = ft.SnackBar(ft.Text("Functionality to add a new source type will be implemented here."), open=True)
        self.page.update()

    def _on_add_project_type_clicked(self, e):
        self.page.snack_bar = ft.SnackBar(ft.Text("Functionality to add a new project type will be implemented here."), open=True)
        self.page.update()
        
    def _on_add_field_clicked(self):
        if self.selected_item_name:
            new_field_card = self._create_field_editor_card({})
            fields_list_control = self.editor_column.controls[2]
            if isinstance(fields_list_control, ft.Column):
                fields_list_control.controls.append(new_field_card)
                self.page.update()

    def _on_delete_field_clicked(self, card_row_to_delete: ft.Row):
        fields_list_control = self.editor_column.controls[2]
        if isinstance(fields_list_control, ft.Column):
            card_to_remove = next((card for card in fields_list_control.controls if card.content.content == card_row_to_delete), None)
            if card_to_remove:
                fields_list_control.controls.remove(card_to_remove)
                self.page.update()

    def _on_save_changes_clicked(self):
        if self.selected_config_type == 'source' and self.selected_item_name:
            fields_list_control = self.editor_column.controls[2]
            if isinstance(fields_list_control, ft.Column):
                new_config = {"fields": []}
                for card in fields_list_control.controls:
                    field_data = {}
                    row = card.content.content
                    field_data["name"] = row.controls[0].value
                    field_data["label"] = row.controls[1].value
                    field_data["field_type"] = row.controls[2].value
                    field_data["required"] = row.controls[3].value
                    field_data["is_title_part"] = row.controls[4].value
                    new_config["fields"].append(field_data)
                
                self.controller.admin_controller.save_source_type_config(self.selected_item_name, new_config)
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Successfully saved configuration for {self.selected_item_name}."), open=True)
                self.page.update()
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text("No configuration to save."), open=True)
            self.page.update()