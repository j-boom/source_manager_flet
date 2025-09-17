import flet as ft
from typing import Dict, Any
from ...components.cards.field_editor_card import FieldEditorCard


class SourceTypeEditor(ft.Column):
    """A self-contained component for editing a single source type's configuration."""

    def __init__(self, type_name: str, controller):
        super().__init__(expand=True, scroll=ft.ScrollMode.ADAPTIVE, spacing=15)
        self.type_name = type_name
        self.controller = controller
        self.type_config: Dict[str, Any] = (
            self.controller.admin_controller.get_source_type_config(type_name)
        )
        self.form_fields: Dict[str, ft.Control] = {}

        if not self.type_config:
            self.controls.append(
                ft.Text(
                    f"Could not load config for {type_name}.", color=ft.colors.ERROR
                )
            )
            return

        self._build_ui()

    def _build_ui(self):
        """Constructs the editor interface."""
        self.form_fields["citation_format"] = ft.TextField(
            label="Citation Format String",
            value=self.type_config.get("citation_format", ""),
            multiline=True,
            min_lines=2,
            max_lines=4,
            tooltip="Use {field_name} for placeholders, e.g., {authors} ({publication_year}).",
        )

        self.fields_list_column = ft.Column(spacing=10)
        # Sort fields by their 'display_order' before displaying them
        sorted_fields = sorted(
            self.type_config.get("fields", []), key=lambda f: f.get("display_order", 0)
        )
        for field in sorted_fields:
            is_first = not self.fields_list_column.controls
            self.fields_list_column.controls.append(
                FieldEditorCard(
                    field_data=field,
                    config_type="source",
                    on_delete=self._on_delete_field_clicked,
                    field_types=self.controller.admin_controller.get_field_types(),
                    autofocus=is_first,
                )
            )

        self.controls.extend(
            [
                ft.Text(
                    f"Editing Source Type: {self.type_name.replace('_', ' ').title()}",
                    theme_style=ft.TextThemeStyle.HEADLINE_SMALL,
                ),
                self.form_fields["citation_format"],
                ft.Divider(),
                ft.Text("Source Fields", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.Text(
                    "Define the fields that make up this source type.",
                    size=12,
                    color=ft.colors.ON_SURFACE_VARIANT,
                ),
                self.fields_list_column,
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Add Field",
                            icon=ft.icons.ADD,
                            on_click=self._on_add_field_clicked,
                        ),
                        ft.Container(expand=True),
                        ft.FilledButton(
                            "Save Changes",
                            icon=ft.icons.SAVE,
                            on_click=self._on_save_clicked,
                        ),
                    ]
                ),
            ]
        )

    def _on_add_field_clicked(self, e):
        new_card = FieldEditorCard(
            field_data={},
            config_type="source",
            on_delete=self._on_delete_field_clicked,
            field_types=self.controller.admin_controller.get_field_types(),
            autofocus=True,
        )
        self.fields_list_column.controls.append(new_card)
        self.update()

    def _on_delete_field_clicked(self, card_to_delete: FieldEditorCard):
        self.fields_list_column.controls.remove(card_to_delete)
        self.update()

    def _on_save_clicked(self, e):
        # The current state is the "old" config for migration purposes

        new_config = self.type_config.copy()
        new_config["citation_format"] = self.form_fields["citation_format"].value

        # Extract field data from each card, filtering out any empty/invalid cards
        all_field_data = [
            card.get_field_data()
            for card in self.fields_list_column.controls
            if card.get_field_data().get("name")
        ]
        # Sort the fields based on their 'display_order' before saving
        sorted_fields = sorted(all_field_data, key=lambda f: f.get("display_order", 0))
        new_config["fields"] = sorted_fields

        self.controller.admin_controller.save_source_type_config(
            self.type_name, new_config
        )
        self.controller.show_success_message(
            f"Successfully saved configuration for {self.type_name}."
        )
        self.controller.update_view()
