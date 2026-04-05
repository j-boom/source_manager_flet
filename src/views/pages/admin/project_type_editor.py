import flet as ft
from typing import Dict, Any
from ...components.cards.field_editor_card import FieldEditorCard


class ProjectTypeEditor(ft.Column):
    """A self-contained component for editing a single project type's configuration."""

    def __init__(self, type_name: str, controller):
        super().__init__(expand=True, scroll=ft.ScrollMode.ADAPTIVE, spacing=15)
        self.type_name = type_name
        self.controller = controller
        self.project_config: Dict[str, Any] = (
            self.controller.admin_controller.get_project_type_config(type_name)
        )
        self.form_fields: Dict[str, ft.Control] = {}
        self.placeholder_chips_row = ft.Row(wrap=True, spacing=5)

        # Add a file picker for the word template path
        self.word_template_path_picker = ft.FilePicker(on_result=self._on_word_template_picked)
        self.controller.page.overlay.append(self.word_template_path_picker)

        # Add a file picker for the powerpoint template path
        self.ppt_template_path_picker = ft.FilePicker(on_result=self._on_ppt_template_picked)
        self.controller.page.overlay.append(self.ppt_template_path_picker)

        if not self.project_config:
            self.controls.append(
                ft.Text(
                    f"Could not load config for {type_name}.", color=ft.Colors.ERROR
                )
            )
            return

        self._build_ui()

    def _build_ui(self):
        """Constructs the editor interface."""
        self.form_fields["display_name"] = ft.TextField(
            label="Display Name",
            value=self.project_config.get("display_name", ""),
            expand=True,
            autofocus=True,
        )
        self.form_fields["description"] = ft.TextField(
            label="Description",
            value=self.project_config.get("description", ""),
            multiline=True,
            min_lines=3,
            max_lines=5,
            expand=True,
        )
        self.form_fields["filename_pattern"] = ft.TextField(
            label="Filename Pattern",
            value=self.project_config.get("filename_pattern", ""),
            expand=True,
        )
        self.form_fields["word_template_path"] = ft.TextField(
            label="Word Report Template Path (.docx)",
            value=self.project_config.get("word_template_path", ""),
            expand=True,
            read_only=True,
        )
        browse_word_template_button = ft.IconButton(
            icon=ft.Icons.FOLDER_OPEN,
            tooltip="Browse for Word template file",
            on_click=lambda _: self.word_template_path_picker.pick_files(
                dialog_title="Select Word Template",
                allowed_extensions=["docx"],
            ),
        )
        self.form_fields["powerpoint_template_path"] = ft.TextField(
            label="PowerPoint Report Template Path (.pptx)",
            value=self.project_config.get("powerpoint_template_path", ""),
            expand=True,
            read_only=True,
        )
        browse_ppt_template_button = ft.IconButton(
            icon=ft.Icons.FOLDER_OPEN,
            tooltip="Browse for PowerPoint template file",
            on_click=lambda _: self.ppt_template_path_picker.pick_files(
                dialog_title="Select PowerPoint Template",
                allowed_extensions=["pptx"],
            ),
        )

        self.fields_list_column = ft.Column(spacing=10)
        # Sort fields by their 'display_order' before displaying them
        sorted_fields = sorted(
            self.project_config.get("fields", []), key=lambda f: f.get("display_order", 0)
        )
        for field in sorted_fields:
            is_first = not self.fields_list_column.controls
            self.fields_list_column.controls.append(
                FieldEditorCard(
                    field_data=field,
                    config_type="project",
                    on_delete=self._on_delete_field_clicked,
                    field_types=self.controller.admin_controller.get_field_types(),
                    autofocus=is_first,
                )
            )

        self._update_placeholder_display()

        field_editor_section = ft.Column(
            [
                ft.Text("Metadata Fields", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.Text(
                    "Define the fields to be collected for this project type.",
                    size=12,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                self.fields_list_column,
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Add Field",
                            icon=ft.Icons.ADD,
                            on_click=self._on_add_field_clicked,
                        )
                    ]
                ),
            ]
        )

        self.controls.extend(
            [
                ft.Text(
                    f"Editing Project Type: {self.type_name}",
                    theme_style=ft.TextThemeStyle.HEADLINE_SMALL,
                ),
                ft.Divider(),
                ft.Text(
                    "Project Type Properties",
                    theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                ),
                self.form_fields["display_name"],
                self.form_fields["description"],
                self.form_fields["filename_pattern"],
                ft.Row([self.form_fields["word_template_path"], browse_word_template_button]),
                ft.Row([self.form_fields["powerpoint_template_path"], browse_ppt_template_button]),
                ft.Divider(height=10),
                ft.Row([
                    ft.Text("Available Template Placeholders", theme_style=ft.TextThemeStyle.TITLE_SMALL),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        on_click=self._update_placeholder_display,
                        tooltip="Refresh list from fields below"
                    )
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(
                    content=self.placeholder_chips_row,
                    padding=ft.padding.all(8),
                    border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                    border_radius=8,
                ),
                ft.Divider(height=20),
                field_editor_section,
                ft.Row(
                    [
                        ft.Container(expand=True),
                        ft.FilledButton(
                            "Save Changes",
                            icon=ft.Icons.SAVE,
                            on_click=self._on_save_clicked,
                        ),
                    ]
                ),
            ]
        )

    def _on_word_template_picked(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.form_fields["word_template_path"].value = e.files[0].path
            self.form_fields["word_template_path"].update()

    def _on_ppt_template_picked(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.form_fields["powerpoint_template_path"].value = e.files[0].path
            self.form_fields["powerpoint_template_path"].update()

    def _update_placeholder_display(self, e=None):
        """Updates the list of placeholder chips based on the current field editor cards."""
        self.placeholder_chips_row.controls.clear()
        
        field_names = [
            card.get_field_data().get("name")
            for card in self.fields_list_column.controls
            if isinstance(card, FieldEditorCard) and card.get_field_data().get("name")
        ]
        
        if not field_names:
            self.placeholder_chips_row.controls.append(
                ft.Text("Add fields below and click Refresh to see available placeholders.", italic=True, size=12, color=ft.Colors.ON_SURFACE_VARIANT)
            )
        else:
            for name in sorted(field_names):
                self.placeholder_chips_row.controls.append(
                    ft.Chip(
                        label=ft.Text(f"{{{name}}}"),
                        tooltip=f"Click to copy '{{{name}}}'",
                        on_click=self._on_placeholder_chip_clicked,
                        data=f"{{{name}}}",
                    )
                )
        if self.page:
            self.update()

    def _on_placeholder_chip_clicked(self, e: ft.ControlEvent):
        """Copies the placeholder text to the clipboard."""
        placeholder = e.control.data
        self.page.set_clipboard(placeholder)
        self.controller.show_success_message(f"Copied '{placeholder}' to clipboard.")

    def _on_add_field_clicked(self, e):
        new_card = FieldEditorCard(
            field_data={},
            config_type="project",
            on_delete=self._on_delete_field_clicked,
            field_types=self.controller.admin_controller.get_field_types(),
            autofocus=True,
        )
        self.fields_list_column.controls.append(new_card)
        self.update()

    def _on_delete_field_clicked(self, card_to_delete: FieldEditorCard):
        self.fields_list_column.controls.remove(card_to_delete)
        self.update()
        self._update_placeholder_display()

    def _on_save_clicked(self, e):
        # The current state is the "old" config for migration purposes

        new_config = self.project_config.copy()
        new_config["display_name"] = self.form_fields["display_name"].value
        new_config["description"] = self.form_fields["description"].value
        new_config["filename_pattern"] = self.form_fields["filename_pattern"].value
        new_config["word_template_path"] = self.form_fields["word_template_path"].value
        new_config["powerpoint_template_path"] = self.form_fields["powerpoint_template_path"].value

        # Extract field data from each card, filtering out any empty/invalid cards
        all_field_data = [
            card.get_field_data()
            for card in self.fields_list_column.controls
            if card.get_field_data().get("name")
        ]
        # Sort the fields based on their 'display_order' before saving
        sorted_fields = sorted(all_field_data, key=lambda f: f.get("display_order", 0))
        new_config["fields"] = sorted_fields

        self.controller.admin_controller.save_project_type_config(
            self.type_name, new_config
        )
        self.controller.show_success_message(
            f"Successfully saved configuration for {self.type_name}."
        )
        self.controller.update_view()
