import flet as ft
from typing import Dict, Any, Callable, List

class FieldEditorCard(ft.Card):
    """A self-contained card for editing the properties of a single configuration field."""

    def __init__(
        self,
        field_data: Dict[str, Any],
        config_type: str,
        colors: ft.colors,
        on_delete: Callable[['FieldEditorCard'], None],
        field_types: List[str],
        autofocus: bool = False,
    ):
        super().__init__()
        self.field_data = field_data
        self.config_type = config_type
        self.colors = colors
        self.on_delete_callback = on_delete
        self.field_types = field_types
        self.autofocus = autofocus

        # The delete button is part of the content, but its action needs to reference this card.
        self.delete_button = ft.IconButton(icon=ft.icons.DELETE_OUTLINE, icon_color=self.colors.error, on_click=lambda e: self.on_delete_callback(self))

        self.content = ft.Container(
            content=self._build_content(),
            padding=15
        )

    def _build_content(self) -> ft.Column:
        """Builds the card's content based on the config_type."""
        name_field = ft.TextField(label="Field Name", value=self.field_data.get("name", ""), expand=2, autofocus=self.autofocus, data="name")
        label_field = ft.TextField(label="Display Label", value=self.field_data.get("label", ""), expand=2, data="label")
        type_dropdown = ft.Dropdown(
            label="Field Type",
            options=[ft.dropdown.Option(key=t, text=t) for t in self.field_types],
            value=self.field_data.get("field_type", "text"),
            expand=1,
            data="field_type"
        )
        required_check = ft.Checkbox(label="Required", value=self.field_data.get("required", False), data="required")
        pattern_field = ft.TextField(
            label="Validation Pattern (Regex)",
            value=self.field_data.get("validation_rules", {}).get("pattern", ""),
            expand=2,
            data="pattern"
        )

        if self.config_type == 'source':
            return self._build_source_field_layout(name_field, label_field, type_dropdown, required_check, pattern_field)
        else: # 'project'
            return self._build_project_field_layout(name_field, label_field, type_dropdown, required_check, pattern_field)

    def _build_source_field_layout(self, name_field, label_field, type_dropdown, required_check, pattern_field):
        """Builds the specific layout for a source field."""
        title_part_check = ft.Checkbox(label="Title Part", value=self.field_data.get("is_title_part", False), data="is_title_part")
        show_in_editor_check = ft.Checkbox(label="Show in Editor", value=self.field_data.get("show_in_editor", True), data="show_in_editor")
        display_order_tf = ft.TextField(label="Order", value=str(self.field_data.get("display_order", 0)), width=70, data="display_order")
        storage_scope_dd = ft.Dropdown(
            label="Storage Scope",
            options=[ft.dropdown.Option(key="core", text="Master Record"), ft.dropdown.Option(key="link", text="Project Link")],
            value=self.field_data.get("storage_scope", "core"),
            data="storage_scope",
            expand=True
        )
        row1 = ft.Row([name_field, label_field, type_dropdown], spacing=10)
        row2 = ft.Row([storage_scope_dd, pattern_field], spacing=10)
        row3 = ft.Row([required_check, title_part_check, show_in_editor_check, display_order_tf, ft.Container(expand=True), self.delete_button], spacing=10)
        return ft.Column([row1, row2, row3], spacing=10)

    def _build_project_field_layout(self, name_field, label_field, type_dropdown, required_check, pattern_field):
        """Builds the specific layout for a project field."""
        column_group_dd = ft.Dropdown(label="Column Group", options=[ft.dropdown.Option("Facility Information"), ft.dropdown.Option("Team"), ft.dropdown.Option("Project Info")], value=self.field_data.get("column_group", "Project Info"), expand=1, data="column_group")
        collection_stage_dd = ft.Dropdown(label="Collect In", options=[ft.dropdown.Option("dialog", "Creation Dialog"), ft.dropdown.Option("metadata_tab", "Metadata Tab")], value=self.field_data.get("collection_stage", "metadata_tab"), expand=1, data="collection_stage")
        calculation_dd = ft.Dropdown(
            label="Calculation",
            options=[ft.dropdown.Option(key=None, text="None"), ft.dropdown.Option(key="current_year", text="Current Year"), ft.dropdown.Option(key="be_number_from_path", text="BE Number (from path)")],
            value=self.field_data.get("calculation"),
            expand=1,
            data="calculation",
            hint_text="Auto-calculates value"
        )
        tab_order_tf = ft.TextField(label="Order", value=str(self.field_data.get("tab_order", 0)), width=70, data="tab_order")
        row1 = ft.Row([name_field, label_field, type_dropdown, pattern_field], spacing=10)
        row2 = ft.Row([required_check, column_group_dd, collection_stage_dd, calculation_dd, tab_order_tf, ft.Container(expand=True), self.delete_button], spacing=10)
        return ft.Column([row1, row2], spacing=10)

    def get_field_data(self) -> Dict[str, Any]:
        """Extracts the data from the controls in the card."""
        field_data = {}
        validation_rules = {}
        
        all_controls = []
        for row in self.content.content.controls:
            all_controls.extend(row.controls)
            
        for control in all_controls:
            if hasattr(control, 'data') and control.data:
                if control.data == 'pattern':
                    if control.value:
                        validation_rules['pattern'] = control.value
                elif control.data in ['tab_order', 'display_order']:
                    try:
                        field_data[control.data] = int(control.value)
                    except (ValueError, TypeError):
                        field_data[control.data] = 0
                else:
                    field_data[control.data] = control.value
        
        if validation_rules:
            field_data['validation_rules'] = validation_rules
            
        return field_data