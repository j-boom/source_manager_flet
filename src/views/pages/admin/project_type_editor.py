import flet as ft
from typing import Dict, Any
from ...components.cards.field_editor_card import FieldEditorCard

class ProjectTypeEditor(ft.Column):
    """A self-contained component for editing a single project type's configuration."""

    def __init__(self, type_name: str, controller, colors: ft.ColorScheme):
        super().__init__(expand=True, scroll=ft.ScrollMode.ADAPTIVE, spacing=15)
        self.type_name = type_name
        self.controller = controller
        self.colors = colors
        self.project_config: Dict[str, Any] = self.controller.admin_controller.get_project_type_config(type_name)
        self.form_fields: Dict[str, ft.Control] = {}
        
        if not self.project_config:
            self.controls.append(ft.Text(f"Could not load config for {type_name}.", color=ft.colors.ERROR))
            return
            
        self._build_ui()

    def _build_ui(self):
        """Constructs the editor interface."""
        self.form_fields["display_name"] = ft.TextField(label="Display Name", value=self.project_config.get("display_name", ""), expand=True, autofocus=True)
        self.form_fields["description"] = ft.TextField(label="Description", value=self.project_config.get("description", ""), multiline=True, min_lines=3, max_lines=5, expand=True)
        self.form_fields["filename_pattern"] = ft.TextField(label="Filename Pattern", value=self.project_config.get("filename_pattern", ""), expand=True)

        self.fields_list_column = ft.Column(spacing=10)
        # Sort fields by their 'tab_order' before displaying them
        sorted_fields = sorted(self.project_config.get('fields', []), key=lambda f: f.get('tab_order', 0))
        for field in sorted_fields:
            is_first = not self.fields_list_column.controls
            self.fields_list_column.controls.append(
                FieldEditorCard(
                    field_data=field,
                    config_type='project',
                    colors=self.colors,
                    on_delete=self._on_delete_field_clicked,
                    field_types=self.controller.admin_controller.get_field_types(),
                    autofocus=is_first
                )
            )

        field_editor_section = ft.Column([
            ft.Text("Metadata Fields", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            ft.Text("Define the fields to be collected for this project type.", size=12, color=self.colors.on_surface_variant),
            self.fields_list_column,
            ft.Row([ft.ElevatedButton("Add Field", icon=ft.icons.ADD, on_click=self._on_add_field_clicked)])
        ])

        self.controls.extend([
            ft.Text(f"Editing Project Type: {self.type_name}", theme_style=ft.TextThemeStyle.HEADLINE_SMALL),
            ft.Divider(),
            ft.Text("Project Type Properties", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            self.form_fields["display_name"],
            self.form_fields["description"],
            self.form_fields["filename_pattern"],
            ft.Divider(height=20),
            field_editor_section,
            ft.Row([
                ft.Container(expand=True),
                ft.FilledButton("Save Changes", icon=ft.icons.SAVE, on_click=self._on_save_clicked)
            ])
        ])

    def _on_add_field_clicked(self, e):
        new_card = FieldEditorCard(
            field_data={}, config_type='project',
            colors=self.colors,
            on_delete=self._on_delete_field_clicked,
            field_types=self.controller.admin_controller.get_field_types(),
            autofocus=True
        )
        self.fields_list_column.controls.append(new_card)
        self.controller.update_view()

    def _on_delete_field_clicked(self, card_to_delete: FieldEditorCard):
        self.fields_list_column.controls.remove(card_to_delete)
        self.controller.update_view()

    def _on_save_clicked(self, e):
        # The current state is the "old" config for migration purposes

        new_config = self.project_config.copy()
        new_config["display_name"] = self.form_fields["display_name"].value
        new_config["description"] = self.form_fields["description"].value
        new_config["filename_pattern"] = self.form_fields["filename_pattern"].value

        # Extract field data from each card, filtering out any empty/invalid cards
        all_field_data = [card.get_field_data() for card in self.fields_list_column.controls if card.get_field_data().get("name")]
        # Sort the fields based on their 'tab_order' before saving
        sorted_fields = sorted(all_field_data, key=lambda f: f.get('tab_order', 0))
        new_config["fields"] = sorted_fields

        self.controller.admin_controller.save_project_type_config(self.type_name, new_config)
        self.page.overlay.append(ft.SnackBar(ft.Text(f"Successfully saved configuration for {self.type_name}."), open=True))
        self.controller.update_view()