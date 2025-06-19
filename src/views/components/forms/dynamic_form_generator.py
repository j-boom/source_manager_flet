"""
Dynamic Form Generator
Creates form fields based on project type configuration
"""

import flet as ft
import re
from typing import Dict, List, Any, Optional, Callable
from config.project_types_config import (
    ProjectTypeConfig, FieldConfig, FieldType, ValidationRule,
    get_project_type_config, get_all_project_types, get_project_type_display_names
)


class DynamicFormField:
    """Wrapper for a dynamic form field with validation"""
    
    def __init__(self, config: FieldConfig, control: ft.Control):
        self.config = config
        self.control = control
        self._value = ""
    
    @property
    def value(self) -> str:
        """Get the field value"""
        if isinstance(self.control, (ft.TextField, ft.Dropdown)):
            return self.control.value or ""
        elif isinstance(self.control, ft.Checkbox):
            return str(self.control.value) if self.control.value else "false"
        return ""
    
    @value.setter
    def value(self, val: str):
        """Set the field value"""
        if isinstance(self.control, (ft.TextField, ft.Dropdown)):
            self.control.value = val
        elif isinstance(self.control, ft.Checkbox):
            self.control.value = val.lower() in ('true', '1', 'yes')
    
    @property
    def visible(self) -> bool:
        """Get field visibility"""
        return self.control.visible
    
    @visible.setter
    def visible(self, val: bool):
        """Set field visibility"""
        self.control.visible = val
    
    def validate(self) -> List[str]:
        """Validate the field and return errors"""
        errors = []
        value = self.value.strip()
        
        # Required field validation
        if self.config.required and not value:
            errors.append(f"{self.config.label.replace(' *', '')} is required")
            return errors
        
        # Skip other validations if field is empty and not required
        if not value:
            return errors
        
        # Apply validation rules
        if self.config.validation_rules:
            for rule, rule_value in self.config.validation_rules.items():
                if rule == ValidationRule.PATTERN:
                    if not re.match(rule_value, value):
                        errors.append(f"{self.config.label.replace(' *', '')} format is invalid")
                elif rule == ValidationRule.MIN_LENGTH:
                    if len(value) < rule_value:
                        errors.append(f"{self.config.label.replace(' *', '')} must be at least {rule_value} characters")
                elif rule == ValidationRule.MAX_LENGTH:
                    if len(value) > rule_value:
                        errors.append(f"{self.config.label.replace(' *', '')} must be no more than {rule_value} characters")
                elif rule == ValidationRule.MIN_VALUE:
                    try:
                        if float(value) < rule_value:
                            errors.append(f"{self.config.label.replace(' *', '')} must be at least {rule_value}")
                    except ValueError:
                        errors.append(f"{self.config.label.replace(' *', '')} must be a valid number")
                elif rule == ValidationRule.MAX_VALUE:
                    try:
                        if float(value) > rule_value:
                            errors.append(f"{self.config.label.replace(' *', '')} must be no more than {rule_value}")
                    except ValueError:
                        errors.append(f"{self.config.label.replace(' *', '')} must be a valid number")
        
        return errors


class DynamicFormGenerator:
    """Generates dynamic forms based on project type configuration"""
    
    def __init__(self, theme_manager=None, on_field_change: Optional[Callable] = None):
        self.theme_manager = theme_manager
        self.on_field_change = on_field_change
        self.fields: Dict[str, DynamicFormField] = {}
        self.current_project_type = None
        self.sections: Dict[str, ft.Container] = {}
    
    def create_field(self, config: FieldConfig) -> DynamicFormField:
        """Create a form field based on configuration"""
        if config.field_type == FieldType.TEXT:
            control = ft.TextField(
                label=config.label,
                hint_text=config.hint_text,
                width=config.width,
                on_change=self._on_field_change if self.on_field_change else None
            )
        elif config.field_type == FieldType.TEXTAREA:
            control = ft.TextField(
                label=config.label,
                hint_text=config.hint_text,
                width=config.width,
                multiline=True,
                min_lines=3,
                max_lines=5,
                on_change=self._on_field_change if self.on_field_change else None
            )
        elif config.field_type == FieldType.DROPDOWN:
            options = config.options or []
            control = ft.Dropdown(
                label=config.label,
                hint_text=config.hint_text,
                width=config.width,
                options=[ft.dropdown.Option(opt) for opt in options],
                on_change=self._on_field_change if self.on_field_change else None
            )
        elif config.field_type == FieldType.NUMBER:
            control = ft.TextField(
                label=config.label,
                hint_text=config.hint_text,
                width=config.width,
                keyboard_type=ft.KeyboardType.NUMBER,
                on_change=self._on_field_change if self.on_field_change else None
            )
        elif config.field_type == FieldType.DATE:
            control = ft.TextField(
                label=config.label,
                hint_text=config.hint_text or "YYYY-MM-DD",
                width=config.width,
                on_change=self._on_field_change if self.on_field_change else None
            )
        elif config.field_type == FieldType.BOOLEAN:
            control = ft.Checkbox(
                label=config.label.replace(' *', ''),
                value=False,
                on_change=self._on_field_change if self.on_field_change else None
            )
        else:
            # Default to text field
            control = ft.TextField(
                label=config.label,
                hint_text=config.hint_text,
                width=config.width,
                on_change=self._on_field_change if self.on_field_change else None
            )
        
        control.visible = config.visible
        return DynamicFormField(config, control)
    
    def _on_field_change(self, e):
        """Handle field changes"""
        if self.on_field_change:
            self.on_field_change(e)
        self._update_field_visibility()
    
    def _update_field_visibility(self):
        """Update field visibility based on dependencies"""
        for field_name, field in self.fields.items():
            if field.config.depends_on and field.config.depends_value:
                dependent_field = self.fields.get(field.config.depends_on)
                if dependent_field:
                    field.visible = dependent_field.value == field.config.depends_value
    
    def generate_form(self, project_type: str) -> Dict[str, ft.Container]:
        """Generate form sections for a project type"""
        config = get_project_type_config(project_type)
        if not config:
            return {}
        
        self.current_project_type = project_type
        self.fields.clear()
        self.sections.clear()
        
        # Create fields
        for field_config in config.fields:
            field = self.create_field(field_config)
            self.fields[field_config.name] = field
        
        # Group fields into sections
        facility_fields = []
        project_fields = []
        team_fields = []
        custom_fields = []
        
        for field_name, field in self.fields.items():
            if field_name in ["facility_number", "facility_name", "building_number", "customer_suffix"]:
                facility_fields.append(field.control)
            elif field_name in ["project_title", "project_description", "request_year"]:
                project_fields.append(field.control)
            elif field_name in ["engineer", "drafter", "reviewer", "architect", "geologist"]:
                team_fields.append(field.control)
            else:
                custom_fields.append(field.control)
        
        # Create sections
        self.sections["facility"] = self._create_section(
            "Facility Information",
            facility_fields,
            ft.colors.BLUE_700
        )
        
        self.sections["project"] = self._create_section(
            "Project Information",
            project_fields + custom_fields,
            ft.colors.GREEN_700
        )
        
        self.sections["team"] = self._create_section(
            "Project Team",
            team_fields,
            ft.colors.PURPLE_700
        )
        
        return self.sections
    
    def _create_section(self, title: str, fields: List[ft.Control], color: str) -> ft.Container:
        """Create a form section with fields"""
        if not fields:
            return ft.Container()
        
        # Arrange fields in rows of 2
        rows = []
        for i in range(0, len(fields), 2):
            row_fields = fields[i:i+2]
            if len(row_fields) == 1:
                rows.append(ft.Row([row_fields[0]], spacing=10))
            else:
                rows.append(ft.Row(row_fields, spacing=10))
        
        return ft.Container(
            content=ft.Column([
                ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=color),
                *rows
            ], spacing=8),
            padding=ft.padding.all(10),
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=5
        )
    
    def get_field_values(self) -> Dict[str, Any]:
        """Get all field values as a dictionary"""
        values = {}
        for field_name, field in self.fields.items():
            values[field_name] = field.value
        return values
    
    def set_field_values(self, values: Dict[str, Any]):
        """Set field values from a dictionary"""
        for field_name, value in values.items():
            if field_name in self.fields:
                self.fields[field_name].value = str(value) if value is not None else ""
    
    def validate_form(self) -> List[str]:
        """Validate all fields and return errors"""
        errors = []
        for field_name, field in self.fields.items():
            if field.visible:  # Only validate visible fields
                field_errors = field.validate()
                errors.extend(field_errors)
        return errors
    
    def get_field(self, field_name: str) -> Optional[DynamicFormField]:
        """Get a specific field by name"""
        return self.fields.get(field_name)
    
    def clear_form(self):
        """Clear all field values"""
        for field in self.fields.values():
            field.value = ""
    
    def get_project_type_dropdown(self, on_change: Optional[Callable] = None) -> ft.Dropdown:
        """Create project type selection dropdown"""
        display_names = get_project_type_display_names()
        options = [
            ft.dropdown.Option(key=code, text=f"{code} - {name}")
            for code, name in display_names.items()
        ]
        
        return ft.Dropdown(
            label="Project Type *",
            hint_text="Select project type",
            width=300,
            options=options,
            on_change=on_change
        )
