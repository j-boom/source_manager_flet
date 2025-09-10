import flet as ft
from src.views.base_view import BaseView
from typing import Dict, Any, List

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
        # --- Component References for Robustness ---
        self.fields_list_column: ft.Column | None = None
        self.project_form_fields: Dict[str, ft.Control] = {}
        self.project_field_selector_checks: Dict[str, ft.Checkbox] = {}

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

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Configuration Management", theme_style=ft.TextThemeStyle.HEADLINE_LARGE),
                    ft.Text("Define the data structure for source and project types across the application."),
                    tabs_control,
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
        source_types = self.controller.admin_controller.get_all_source_types()
        for type_name in source_types:
            self.source_types_list.controls.append(
                ft.ListTile(
                    title=ft.Text(type_name.replace("_", " ").title()),
                    on_click=lambda e, t='source': self._on_item_selected(e, t),
                    data=type_name,
                )
            )
        if self.page.window.width:  # Avoid error on first build
            self.page.update()
    
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
        if self.page.window.width:  # Avoid error on first build
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

    def _build_editor_for_selection(self):
        """Routes to the correct editor builder based on the selected type."""
        # Clear both editor columns before building
        self.source_editor_column.controls.clear()
        self.project_editor_column.controls.clear()

        if self.selected_config_type == 'source':
            self._build_source_editor(self.selected_item_name)
        elif self.selected_config_type == 'project':
            self._build_project_editor(self.selected_item_name)
        else:
            # Add placeholder text to both columns for the initial state
            placeholder_text = "Select an item from a list to begin."
            self.source_editor_column.controls.append(ft.Text(placeholder_text, italic=True))
            self.project_editor_column.controls.append(ft.Text(placeholder_text, italic=True))

    def _build_source_editor(self, type_name: str):
        """Dynamically builds the editor UI for the selected source type."""
        if not type_name: return
        type_config = self.controller.admin_controller.get_source_type_config(type_name)
        if not type_config:
            self.source_editor_column.controls.append(ft.Text(f"Could not load config for {type_name}.", color=self.colors.error))
            return

        self.fields_list_column = ft.Column(spacing=10)
        for field in type_config.get('fields', []):
            # Pass autofocus=True only for the first field card
            is_first = not self.fields_list_column.controls
            self.fields_list_column.controls.append(self._create_field_editor_card(field, autofocus=is_first))

        self.source_editor_column.controls.extend([
            ft.Text(f"Editing Source Type: {type_name.replace('_', ' ').title()}", theme_style=ft.TextThemeStyle.HEADLINE_SMALL),
            ft.Divider(),
            ft.Text("Source Fields", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            ft.Text("Define the fields that make up this source type.", size=12, color=self.colors.on_surface_variant),
            self.fields_list_column, # The column of field editor cards
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
            self.project_editor_column.controls.append(ft.Text(f"Could not load config for {type_name}.", color=self.colors.error))
            return

        # Clear and rebuild form fields dictionary
        self.project_form_fields.clear()

        # UI elements for project type properties
        self.project_form_fields["display_name"] = ft.TextField(
            label="Display Name",
            value=project_config.get("display_name", ""),
            expand=True,
            autofocus=True
        )
        self.project_form_fields["description"] = ft.TextField(
            label="Description",
            value=project_config.get("description", ""),
            multiline=True,
            min_lines=3,
            max_lines=5,
            expand=True
        )
        self.project_form_fields["filename_pattern"] = ft.TextField(
            label="Filename Pattern",
            value=project_config.get("filename_pattern", ""),
            expand=True
        )

        # --- Metadata Field Editor ---
        self.fields_list_column = ft.Column(spacing=10)
        for field in project_config.get('fields', []):
            is_first = not self.fields_list_column.controls
            self.fields_list_column.controls.append(self._create_project_field_editor_card(field, autofocus=is_first))

        field_editor_section = ft.Column([
            ft.Text("Metadata Fields", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            ft.Text("Define the fields to be collected for this project type.", size=12, color=self.colors.on_surface_variant),
            self.fields_list_column,
            ft.Row([
                ft.ElevatedButton("Add Field", icon=ft.icons.ADD, on_click=lambda e: self._on_add_field_clicked()),
            ])
        ])

        self.project_editor_column.controls.extend([
            ft.Text(f"Editing Project Type: {type_name}", theme_style=ft.TextThemeStyle.HEADLINE_SMALL),
            ft.Divider(),
            ft.Text("Project Type Properties", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            self.project_form_fields.get("display_name"),
            self.project_form_fields.get("description"),
            self.project_form_fields.get("filename_pattern"),
            ft.Divider(height=20),
            field_editor_section,
            ft.Row([
                ft.Container(expand=True), # Pushes button to the right
                ft.FilledButton(
                    "Save Changes",
                    icon=ft.icons.SAVE,
                    on_click=lambda e: self._on_save_project_changes_clicked(type_name)
                ),
            ])
        ])

    def _on_save_project_changes_clicked(self, type_name: str):
        """Saves the complete configuration for a project type, including its defined fields."""
        new_config = {
            "display_name": self.project_form_fields.get("display_name").value,
            "description": self.project_form_fields.get("description").value,
            "filename_pattern": self.project_form_fields.get("filename_pattern").value,
        }

        # Collect the defined metadata fields
        defined_fields = []
        if self.fields_list_column:
            for card in self.fields_list_column.controls:
                field_data = {}
                # card.content.content is the Column containing the two Rows of controls
                rows_container = card.content.content
                all_controls = rows_container.controls[0].controls + rows_container.controls[1].controls
                validation_rules = {}
                for control in all_controls:
                    if hasattr(control, 'data') and control.data:
                        if control.data == 'pattern':
                            if control.value: # Only add pattern if it's not empty
                                validation_rules['pattern'] = control.value
                        elif control.data == 'tab_order':
                            try:
                                field_data[control.data] = int(control.value)
                            except (ValueError, TypeError):
                                field_data[control.data] = 0  # Default to 0 if invalid
                        else:
                            field_data[control.data] = control.value
                
                if validation_rules:
                    field_data['validation_rules'] = validation_rules

                if field_data.get("name"):  # Only add fields that have a name
                    defined_fields.append(field_data)
        
        new_config["fields"] = defined_fields

        self.controller.admin_controller.save_project_type_config(type_name, new_config)
        self.page.overlay.append(ft.SnackBar(ft.Text(f"Successfully saved configuration for {type_name}."), open=True))
        self.page.update()

    def _create_field_editor_card(self, field_data: Dict[str, Any], autofocus: bool = False) -> ft.Card:
        """Creates a card with controls to edit a single source or project field."""
        name_field = ft.TextField(label="Field Name", value=field_data.get("name", ""), expand=2, autofocus=autofocus)
        name_field.data = "name" # Use data attribute for robust access

        label_field = ft.TextField(label="Display Label", value=field_data.get("label", ""), expand=2)
        label_field.data = "label"

        type_dropdown = ft.Dropdown(
            label="Field Type",
            options=[ft.dropdown.Option(key=t, text=t) for t in self.controller.admin_controller.get_field_types()],
            value=field_data.get("field_type", "text"),
            expand=1
        )
        type_dropdown.data = "field_type"

        required_check = ft.Checkbox(label="Required", value=field_data.get("required", False))
        required_check.data = "required"

        # --- Create the card and button separately to link them ---
        delete_button = ft.IconButton(icon=ft.icons.DELETE_OUTLINE, icon_color=self.colors.error)
        
        # Determine which type of card to create
        if self.selected_config_type == 'source':
            title_part_check = ft.Checkbox(label="Title Part", value=field_data.get("is_title_part", False), data="is_title_part")
            pattern_field = ft.TextField(
                label="Validation Pattern (Regex)",
                value=field_data.get("validation_rules", {}).get("pattern", ""),
                expand=2,
                data="pattern"
            )
            row1 = ft.Row([name_field, label_field, type_dropdown], spacing=10)
            row2 = ft.Row([required_check, title_part_check, pattern_field, ft.Container(expand=True), delete_button], spacing=10)
            card_content = ft.Column([row1, row2], spacing=10)
        else: # 'project'
            column_group_dd = ft.Dropdown(label="Column Group", options=[ft.dropdown.Option("Facility Information"), ft.dropdown.Option("Team"), ft.dropdown.Option("Project Info")], value=field_data.get("column_group", "Project Info"), expand=1, data="column_group")
            collection_stage_dd = ft.Dropdown(label="Collect In", options=[ft.dropdown.Option("dialog", "Creation Dialog"), ft.dropdown.Option("metadata_tab", "Metadata Tab")], value=field_data.get("collection_stage", "metadata_tab"), expand=1, data="collection_stage")
            tab_order_tf = ft.TextField(label="Order", value=str(field_data.get("tab_order", 0)), width=70, data="tab_order")
            
            row1 = ft.Row([name_field, label_field, type_dropdown, required_check], spacing=10)
            row2 = ft.Row([column_group_dd, collection_stage_dd, tab_order_tf, ft.Container(expand=True), delete_button], spacing=10)
            card_content = ft.Column([row1, row2], spacing=10)

        card = ft.Card(
            content=ft.Container(
                content=card_content,
                padding=15
            )
        )
        # Now that the card exists, set the button's on_click to reference it
        delete_button.on_click = lambda e: self._on_delete_field_clicked(card)
        return card

    def _create_project_field_editor_card(self, field_data: Dict[str, Any], autofocus: bool = False) -> ft.Card:
        """Creates a card with controls to edit a single project metadata field."""
        name_field = ft.TextField(label="Field Name", value=field_data.get("name", ""), expand=2, autofocus=autofocus, data="name")
        label_field = ft.TextField(label="Display Label", value=field_data.get("label", ""), expand=2, data="label")
        type_dropdown = ft.Dropdown(label="Field Type", options=[ft.dropdown.Option(key=t, text=t) for t in self.controller.admin_controller.get_field_types()], value=field_data.get("field_type"), expand=1, data="field_type")
        required_check = ft.Checkbox(label="Required", value=field_data.get("required", False), data="required")
        column_group_dd = ft.Dropdown(label="Column Group", options=[ft.dropdown.Option("Facility Information"), ft.dropdown.Option("Team"), ft.dropdown.Option("Project Info")], value=field_data.get("column_group", "Project Info"), expand=1, data="column_group")
        collection_stage_dd = ft.Dropdown(label="Collect In", options=[ft.dropdown.Option("dialog", "Creation Dialog"), ft.dropdown.Option("metadata_tab", "Metadata Tab")], value=field_data.get("collection_stage", "metadata_tab"), expand=1, data="collection_stage")
        pattern_field = ft.TextField(
            label="Validation Pattern (Regex)",
            value=field_data.get("validation_rules", {}).get("pattern", ""),
            expand=2,
            data="pattern"
        )
        calculation_dd = ft.Dropdown(
            label="Calculation",
            options=[
                ft.dropdown.Option(key=None, text="None"),
                ft.dropdown.Option(key="current_year", text="Current Year"),
                ft.dropdown.Option(key="be_number_from_path", text="BE Number (from path)"),
            ],
            value=field_data.get("calculation"),
            expand=1,
            data="calculation",
            hint_text="Auto-calculates value"
        )
        tab_order_tf = ft.TextField(label="Order", value=str(field_data.get("tab_order", 0)), width=70, data="tab_order")

        delete_button = ft.IconButton(icon=ft.icons.DELETE_OUTLINE, icon_color=self.colors.error)

        row1 = ft.Row([name_field, label_field, type_dropdown, pattern_field], spacing=10)
        row2 = ft.Row([required_check, column_group_dd, collection_stage_dd, calculation_dd, tab_order_tf, ft.Container(expand=True), delete_button], spacing=10)

        card = ft.Card(
            content=ft.Container(
                content=ft.Column([row1, row2], spacing=10),
                padding=15
            )
        )
        delete_button.on_click = lambda e: self._on_delete_field_clicked(card)
        return card

    def _on_add_source_type_clicked(self, e):
        self.page.snack_bar = ft.SnackBar(ft.Text("Add Source Type functionality not yet implemented."), open=True)
        self.page.update()

    def _on_add_project_type_clicked(self, e):
        self.page.snack_bar = ft.SnackBar(ft.Text("Add Project Type functionality not yet implemented."), open=True)
        self.page.update()
        
    def _on_add_field_clicked(self):
        if self.selected_item_name and self.fields_list_column:
            if self.selected_config_type == 'source':
                new_field_card = self._create_field_editor_card({}, autofocus=True)
            elif self.selected_config_type == 'project':
                new_field_card = self._create_project_field_editor_card({}, autofocus=True)
            else:
                return # Should not happen

            self.fields_list_column.controls.append(new_field_card)
            self.page.update()

    def _on_delete_field_clicked(self, card_to_delete: ft.Card):
        if self.fields_list_column and card_to_delete in self.fields_list_column.controls:
            self.fields_list_column.controls.remove(card_to_delete)
            self.page.update()

    def _on_save_changes_clicked(self):
        if self.selected_config_type == 'source' and self.selected_item_name and self.fields_list_column:
            new_config = {"fields": []}
            for card in self.fields_list_column.controls:
                field_data = {}
                rows_container = card.content.content
                all_controls = rows_container.controls[0].controls + rows_container.controls[1].controls
                validation_rules = {}
                for control in all_controls:
                    if hasattr(control, 'data') and control.data:
                        if control.data == 'pattern':
                            if control.value:
                                validation_rules['pattern'] = control.value
                        else:
                            field_data[control.data] = control.value
                if validation_rules:
                    field_data['validation_rules'] = validation_rules
                new_config["fields"].append(field_data)
            
            self.controller.admin_controller.save_source_type_config(self.selected_item_name, new_config)
            self.page.overlay.append(ft.SnackBar(ft.Text(f"Successfully saved configuration for {self.selected_item_name}."), open=True))
            self.page.update()
        else:
            self.page.overlay.append(ft.SnackBar(ft.Text("No configuration to save."), open=True))
            self.page.update()