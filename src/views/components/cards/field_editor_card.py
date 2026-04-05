import flet as ft
from typing import Dict, Any, Callable, List


class FieldEditorCard(ft.Card):
    """A card for editing the properties of a single field within a type configuration."""

    def __init__(
        self,
        field_data: Dict[str, Any],
        config_type: str,
        on_delete: Callable,
        field_types: List[str],
        autofocus: bool = False,
    ):
        super().__init__(elevation=1, margin=ft.margin.only(bottom=10))
        self.field_data = field_data
        self.config_type = config_type
        self.on_delete = on_delete
        self.field_types = field_types
        self.autofocus = autofocus
        self.form_controls: Dict[str, ft.Control] = {}
        self.content = self._build_card_content()

    def _build_card_content(self) -> ft.Container:
        """Builds the UI controls for editing a field's properties."""
        # --- Define Controls ---
        self.form_controls["name"] = ft.TextField(
            label="Field Name (key)",
            value=self.field_data.get("name", ""),
            dense=True,
            autofocus=self.autofocus,
            tooltip="The internal key for this field (e.g., 'publication_year'). Cannot be changed after creation if data exists.",
            read_only=bool(
                self.field_data.get("name")
            ),  # Make name read-only if it already exists
            expand=2,
        )
        self.form_controls["label"] = ft.TextField(
            label="Display Label",
            value=self.field_data.get("label", ""),
            dense=True,
            tooltip="The user-friendly label shown in forms.",
            expand=2,
        )
        # --- NEW FIELD ---
        self.form_controls["hint_text"] = ft.TextField(
            label="Hint Text (Optional)",
            value=self.field_data.get("hint_text", ""),
            dense=True,
            tooltip="Placeholder text shown inside the input field.",
        )
        self.form_controls["field_type"] = ft.Dropdown(
            label="Field Type",
            options=[ft.dropdown.Option(t) for t in self.field_types],
            value=self.field_data.get("field_type", "text"),
            dense=True,
            expand=1,
        )
        self.form_controls["display_order"] = ft.TextField(
            label="Order",
            value=str(self.field_data.get("display_order", 0)),
            dense=True,
            width=80,
            tooltip="Sort order in forms (lower numbers appear first).",
        )
        self.form_controls["required"] = ft.Switch(
            label="Required", value=self.field_data.get("required", False)
        )
        self.form_controls["is_filterable"] = ft.Switch(
            label="Filterable",
            value=self.field_data.get("is_filterable", False),
            visible=(self.config_type == "source"),
        )
        self.form_controls["is_title_part"] = ft.Switch(
            label="Part of Title",
            value=self.field_data.get("is_title_part", False),
            visible=(self.config_type == "source"),
        )
        self.form_controls["show_in_editor"] = ft.Switch(
            label="Show in Editor", value=self.field_data.get("show_in_editor", True)
        )
        self.form_controls["collection_stage"] = ft.Dropdown(
            label="Collection Stage",
            options=[
                ft.dropdown.Option("dialog", "Creation Dialog"),
                ft.dropdown.Option("metadata_editor", "Metadata Editor"),
            ],
            value=self.field_data.get("collection_stage", "metadata_editor"),
            dense=True,
            expand=1,
            visible=(self.config_type == "project"),
            tooltip="Where should this field be collected from the user?",
        )
        self.form_controls["calculation"] = ft.Dropdown(
            label="Calculation Rule",
            options=[
                ft.dropdown.Option("", "None"),
                ft.dropdown.Option("current_year", "Current Year"),
                ft.dropdown.Option("be_number_from_path", "BE Number from Path"),
            ],
            value=self.field_data.get("calculation", ""),
            dense=True,
            visible=(self.config_type == "project"),
            tooltip="Set a rule to auto-calculate this field's value during project creation.",
        )

        storage_scope_control = None
        if self.config_type == "source":
            self.form_controls["storage_scope"] = ft.Dropdown(
                label="Storage Scope",
                options=[
                    ft.dropdown.Option("core", "Master Record"),
                    ft.dropdown.Option("link", "Project Link"),
                ],
                value=self.field_data.get("storage_scope", "core"),
                dense=True,
                expand=1,
            )
            storage_scope_control = self.form_controls["storage_scope"]

        # --- Layout ---
        content = ft.Column(
            controls=[
                ft.Row(
                    [
                        self.form_controls["name"],
                        self.form_controls["label"],
                        self.form_controls["display_order"],
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            on_click=lambda e: self.on_delete(self),
                            tooltip="Delete Field",
                            icon_color=ft.Colors.ERROR,
                        ),
                    ],
                    spacing=10,
                ),
                # --- ADDED HINT TEXT FIELD TO LAYOUT ---
                self.form_controls["hint_text"],
                ft.Row(
                    [
                        self.form_controls["field_type"],
                        *([storage_scope_control] if storage_scope_control else []),
                        self.form_controls["calculation"],
                    ],
                    spacing=10,
                ),
                ft.Row(
                    [
                        self.form_controls["required"],
                        self.form_controls["is_filterable"],
                        self.form_controls["is_title_part"],
                        self.form_controls["show_in_editor"],
                        self.form_controls["collection_stage"],
                    ],
                    spacing=10,
                ),
            ],
            spacing=10,
        )

        return ft.Container(
            content,
            padding=15,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=8,
        )

    def get_field_data(self) -> Dict[str, Any]:
        """Collects and returns the current data from the form controls."""
        data = {}
        for name, control in self.form_controls.items():
            if isinstance(control, (ft.TextField, ft.Dropdown)):
                data[name] = control.value
            elif isinstance(control, ft.Switch):
                data[name] = control.value

        # --- Type Conversions ---
        try:
            data["display_order"] = int(data.get("display_order", 0))
        except (ValueError, TypeError):
            data["display_order"] = 0

        return data
