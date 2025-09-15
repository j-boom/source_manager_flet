import flet as ft
import logging
from typing import Dict, Any, List

from src.views.components.dialogs.source_creation_dialog import SourceCreationDialog


class LegacyMigrationTab(ft.Column):
    """
    A UI tab for migrating legacy source data within project files.
    """

    def __init__(self, controller):
        super().__init__(expand=True, spacing=10)
        self.controller = controller
        self.migration_controller = self.controller.migration_controller
        self.logger = logging.getLogger(__name__)

        # --- UI Components ---
        self.file_picker = ft.FilePicker(on_result=self._on_file_picked)
        self.controller.page.overlay.append(self.file_picker)

        self.pick_file_button = ft.ElevatedButton(
            "Select Project File", icon=ft.icons.FOLDER_OPEN, on_click=lambda _: self.file_picker.pick_files(
                dialog_title="Select Project JSON to Migrate",
                allowed_extensions=["json"],
                allow_multiple=False
            )
        )
        self.status_text = ft.Text("Select a project file to begin migration.", italic=True)
        self.prev_button = ft.IconButton(icon=ft.icons.NAVIGATE_BEFORE, on_click=self._on_prev, disabled=True)
        self.next_button = ft.IconButton(icon=ft.icons.NAVIGATE_NEXT, on_click=self._on_next, disabled=True)
        self.save_button = ft.FilledButton("Save & Next", icon=ft.icons.SAVE, on_click=self._on_save, disabled=True)

        # Left side: Raw data display
        self.citation_text = ft.Text(selectable=True)
        self.comment_text = ft.Text(selectable=True)
        self.raw_data_container = ft.Container(
            content=ft.Column([
                ft.Text("Legacy Citation String", weight=ft.FontWeight.BOLD),
                ft.Container(self.citation_text, padding=10, border=ft.border.all(1, ft.colors.OUTLINE), border_radius=4),
                ft.Text("Legacy Comment", weight=ft.FontWeight.BOLD),
                ft.Container(self.comment_text, padding=10, border=ft.border.all(1, ft.colors.OUTLINE), border_radius=4),
            ]),
            padding=10,
        )

        # Right side: Dynamic form (reusing SourceCreationDialog's components)
        self.source_type_dropdown = self._build_source_type_dropdown()
        self.country_dropdown = self._build_country_dropdown()
        self.dynamic_fields_container = ft.Column(spacing=15, scroll=ft.ScrollMode.ADAPTIVE)
        self.form_fields: Dict[str, ft.Control] = {}
        self.field_configs: Dict[str, Any] = {}

        self.form_container = ft.Container(
            content=ft.Column([
                ft.Row([self.source_type_dropdown, self.country_dropdown], spacing=10),
                ft.Divider(),
                self.dynamic_fields_container
            ]),
            padding=10,
        )

        self._build_ui()

    def _build_ui(self):
        """Constructs the static layout of the tab."""
        header = ft.Row([
            self.pick_file_button,
            ft.VerticalDivider(),
            self.status_text,
            ft.Container(expand=True),
            self.prev_button,
            self.next_button,
            self.save_button
        ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER)

        main_content = ft.Row([
            ft.Container(self.raw_data_container, expand=2, border_radius=8, bgcolor=ft.colors.SURFACE_VARIANT, padding=15),
            ft.VerticalDivider(),
            ft.Container(self.form_container, expand=3, border_radius=8, padding=15),
        ], expand=True, spacing=10)

        self.controls.extend([
            ft.Text("Legacy Source Migration Tool", theme_style=ft.TextThemeStyle.TITLE_LARGE),
            ft.Text("Load a project JSON file, review the parsed source data, and save it to the new format.", color=self.controller.page.theme.color_scheme.on_surface_variant),
            ft.Divider(),
            header,
            main_content
        ])

    def _on_file_picked(self, e: ft.FilePickerResultEvent):
        if not e.files:
            return
        
        file_path = e.files[0].path
        self.logger.info(f"File picked for migration: {file_path}")
        if self.migration_controller.load_legacy_project(file_path):
            self.update_view()

    def update_view(self):
        """Refreshes the entire view based on the MigrationController's state."""
        state = self.migration_controller.state
        legacy_source = self.migration_controller.get_current_legacy_source()

        # Update status and button states
        self.status_text.value = self.migration_controller.get_migration_status()
        self.save_button.disabled = not state["is_loaded"]
        self.prev_button.disabled = not state["is_loaded"] or state["current_index"] == 0
        self.next_button.disabled = not state["is_loaded"] or state["current_index"] >= len(state["legacy_source_indices"]) - 1

        if legacy_source:
            # Populate left side (raw data)
            self.citation_text.value = legacy_source.get("citation", "N/A")
            self.comment_text.value = legacy_source.get("comment", "N/A")

            # Populate right side (form)
            pre_filled_data = self.migration_controller.parse_legacy_source(legacy_source)
            
            # Pre-select source type if parser provides it
            parsed_source_type = pre_filled_data.get("source_type")
            if parsed_source_type and parsed_source_type in self.source_type_dropdown.options:
                self.source_type_dropdown.value = parsed_source_type
            
            self._populate_dynamic_fields(self.source_type_dropdown.value, pre_filled_data)

        else:
            # Clear everything if no source is loaded
            self.citation_text.value = ""
            self.comment_text.value = ""
            self.dynamic_fields_container.controls.clear()

        if self.page:
            self.page.update()

    def _on_prev(self, e):
        self.migration_controller.go_to_previous_source()
        self.update_view()

    def _on_next(self, e):
        self.migration_controller.go_to_next_source()
        self.update_view()

    def _on_save(self, e):
        # --- Data Collection from form ---
        form_data = {
            "source_type": self.source_type_dropdown.value,
            "country": self.country_dropdown.value
        }
        for name, control in self.form_fields.items():
            if hasattr(control, "value"):
                form_data[name] = control.value
        
        # Generate title (reusing logic from SourceCreationDialog)
        generated_title = ft.generate_source_title(
            form_data["source_type"], form_data, self.controller.admin_service
        )
        form_data["display_name"] = generated_title

        # --- Validation (simplified for this tool) ---
        if not form_data["country"] or not form_data["source_type"]:
            self.controller.show_error_message("Country and Source Type are required.")
            return

        if self.migration_controller.save_migrated_source(form_data):
            self.controller.show_success_message("Source migrated successfully!")
            self.update_view() # Refresh to show next source or completion message

    # --- Form Building Logic (adapted from SourceCreationDialog) ---

    def _build_source_type_dropdown(self) -> ft.Dropdown:
        source_types = self.controller.admin_service.get_source_types()
        return ft.Dropdown(
            label="Source Type *",
            options=[
                ft.dropdown.Option(key=code, text=config.get("display_name", code.title()))
                for code, config in source_types.items()
            ],
            on_change=self._on_source_type_change,
            expand=True,
            value=list(source_types.keys())[0] if source_types else None
        )

    def _build_country_dropdown(self) -> ft.Dropdown:
        countries = self.controller.source_controller.get_available_countries()
        return ft.Dropdown(
            label="Country *",
            options=[ft.dropdown.Option(c, c) for c in sorted(countries or [])],
            expand=True
        )

    def _on_source_type_change(self, e: ft.ControlEvent):
        if e.control.value:
            self._populate_dynamic_fields(e.control.value, {}) # No pre-filled data on manual change

    def _populate_dynamic_fields(self, source_type_value: str, pre_filled_data: Dict[str, Any]):
        """Clears and rebuilds the form fields based on the selected source type."""
        self.form_fields.clear()
        self.field_configs.clear()
        self.dynamic_fields_container.controls.clear()

        if not source_type_value:
            if self.page: self.page.update()
            return

        fields_to_create = self.controller.dialog_controller.get_source_type_fields(source_type_value)
        fields_to_create.sort(key=lambda f: f.get("display_order", 0))

        for s_config_dict in fields_to_create:
            if s_config_dict.get("show_in_editor", True):
                # This re-uses the same validation and field creation logic
                compatible_config = SourceCreationDialog._CompatibleFieldConfig.from_source_field_config(
                    ft.SourceFieldConfig(**s_config_dict)
                )
                
                initial_value = pre_filled_data.get(compatible_config.name, "")
                widget = ft.create_validated_field(compatible_config, initial_value=str(initial_value))

                self.form_fields[compatible_config.name] = widget
                self.field_configs[compatible_config.name] = compatible_config
                self.dynamic_fields_container.controls.append(widget)

        if self.page:
            self.page.update()