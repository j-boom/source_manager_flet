"""
Source Title Generator Utility

Provides a function to programmatically generate standardized titles for source records.
"""
from typing import List, TYPE_CHECKING
from src.models.source_models import SourceFieldConfig

if TYPE_CHECKING:
    from src.services.admin_service import AdminService

def get_filterable_fields(admin_service: "AdminService") -> List[SourceFieldConfig]:
    """
    Gathers all unique fields marked as 'is_filterable' from all source types.
    """
    all_source_types = admin_service.get_source_types()
    filterable_fields = {}  # Use dict to avoid duplicates by name
    for type_config in all_source_types.values():
        for field_data in type_config.get("fields", []):
            if field_data.get("is_filterable"):
                # Use .get for name to avoid KeyError if name is missing
                field_name = field_data.get("name")
                if field_name and field_name not in filterable_fields:
                    filterable_fields[field_name] = SourceFieldConfig(**field_data)
    # Sort by label for consistent display order
    return sorted(list(filterable_fields.values()), key=lambda f: f.label)


def generate_source_title(source_type: str, form_data: dict, admin_service: "AdminService") -> str:
    """
    Generates a standardized title for a source based on its type and data.

    It reads the configuration for the given source type, identifies which
    fields are marked as 'is_title_part', and joins their values together.
    """
    title_parts = []
    all_source_types = admin_service.get_source_types()
    source_type_config = all_source_types.get(source_type, {})
    field_configs = source_type_config.get("fields", [])

    # Filter for fields that are marked as part of the title
    title_field_configs = [f for f in field_configs if f.get("is_title_part")]

    # Sort the title fields by their display_order to ensure a consistent title
    sorted_title_fields = sorted(title_field_configs, key=lambda f: f.get('display_order', 0))

    for config in sorted_title_fields:
        # Get the value from the form data, if it exists and is not empty
        value = form_data.get(config.get("name"))
        if value:
            title_parts.append(str(value).strip())

    # Join the parts with a consistent separator
    return " - ".join(title_parts)
