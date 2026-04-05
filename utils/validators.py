"""
Validation Utilities

This module provides centralized, reusable validation functions for form data
based on rules defined in the application's configuration.
"""
import re
from typing import Any, List, Optional, Dict, TYPE_CHECKING
from src.models.project_models import FieldConfig, ValidationRule, FieldType
import flet as ft

if TYPE_CHECKING:
    from src.services.admin_service import AdminService

def _get_project_type_fields(project_type_code: str, admin_service: "AdminService") -> List[FieldConfig]:
    """
    Retrieves the field configurations for a given project type.
    """
    project_types_config = admin_service.get_project_types()
    project_type_data = project_types_config.get(project_type_code, {})
    fields_data = project_type_data.get("fields", [])
    
    # The FieldConfig model does not accept layout-specific keys.
    # We must filter the dictionaries to only include keys that FieldConfig expects.
    expected_keys = ['name', 'label', 'field_type', 'required', 'hint_text', 'validation_rules', 'width', 'options']
    
    clean_field_data = []
    for field_data in fields_data:
        clean_dict = {key: value for key, value in field_data.items() if key in expected_keys}
        clean_field_data.append(clean_dict)
        
    return [FieldConfig(**f) for f in clean_field_data]


def validate_field_value(field_config: FieldConfig, value: Any) -> tuple[bool, str]:
    """
    Validates a single field's value against its configuration rules.

    Args:
        field_config: The configuration for the field to validate.
        value: The value to be validated.

    Returns:
        A tuple containing a boolean (is_valid) and an error message string.
    """
    val_str = str(value or "").strip()

    if field_config.required and not val_str:
        return False, f"{field_config.label} is required."

    rules = field_config.validation_rules
    if not rules or not val_str:
        return True, ""

    if ValidationRule.PATTERN in rules:
        pattern = rules[ValidationRule.PATTERN]
        if not re.match(pattern, val_str):
            return False, f"Invalid format for {field_config.label}."

    if ValidationRule.MIN_LENGTH in rules:
        min_len = rules[ValidationRule.MIN_LENGTH]
        if len(val_str) < min_len:
            return False, f"{field_config.label} must be at least {min_len} characters."

    if ValidationRule.MAX_LENGTH in rules:
        max_len = rules[ValidationRule.MAX_LENGTH]
        if len(val_str) > max_len:
            return False, f"{field_config.label} must not exceed {max_len} characters."

    return True, ""

def validate_form_data(project_type_code: str, form_data: dict, admin_service: "AdminService") -> tuple[bool, list[str]]:
    """
    Validates an entire dictionary of form data for a given project type.

    Args:
        project_type_code: The code for the project type (e.g., "STD").
        form_data: A dictionary of the submitted form data.

    Returns:
        A tuple containing a boolean (is_valid) and a list of error messages.
    """
    fields_to_validate = _get_project_type_fields(project_type_code, admin_service)
    errors = []

    for field in fields_to_validate:
        value = form_data.get(field.name, "")
        is_valid, error_msg = validate_field_value(field, value)
        if not is_valid:
            errors.append(error_msg)

    return not errors, errors

def create_validated_field(field_config: [FieldConfig, Dict], initial_value: str = "") -> ft.Control:
    """
    Creates a Flet widget with built-in real-time validation.

    Args:
        field_config: The configuration for the field (can be a FieldConfig object or a dict).
        initial_value: The starting value for the field.

    Returns:
        A Flet control with validation attached to its on_change event.
    """
    # Defensively convert dict to FieldConfig if needed. This makes the function
    # more robust if it's called from parts of the UI that handle raw config dicts.
    if isinstance(field_config, dict):
        expected_keys = ['name', 'label', 'field_type', 'required', 'hint_text', 'validation_rules', 'width', 'options']
        clean_dict = {key: value for key, value in field_config.items() if key in expected_keys}
        field_config = FieldConfig(**clean_dict)

    label = f"{field_config.label} *" if field_config.required else field_config.label

    def handle_validation(e: ft.ControlEvent):
        """Callback to validate the field and update its UI on change."""
        widget = e.control
        is_valid, error_message = validate_field_value(field_config, widget.value)
        if not is_valid and widget.value: # Show error only if there's content
            widget.error_text = error_message
            widget.border_color = ft.Colors.ERROR
        else:
            widget.error_text = None
            widget.border_color = None # Reset to default
        widget.update()

    # Default to TextField and override for other types
    if field_config.field_type == FieldType.CHECKBOX:
        return ft.Checkbox(label=label, value=(str(initial_value).lower() == 'true'))

    # Common properties for text-based fields
    widget_params = {
        "label": label,
        "value": initial_value,
        "hint_text": field_config.hint_text,
        "on_change": handle_validation,
        "width": field_config.width,
        "border_radius": 8,
    }

    if field_config.field_type == FieldType.DROPDOWN:
        return ft.Dropdown(
            options=[ft.dropdown.Option(o) for o in field_config.options or []],
            **widget_params
        )
    else: # TEXT, TEXTAREA, etc.
        if field_config.field_type == FieldType.TEXTAREA:
            widget_params.update({"multiline": True, "min_lines": 3})
        return ft.TextField(**widget_params)