"""
Source Title Generator Utility

Provides a function to programmatically generate standardized titles for source records.
"""

from src.services.config_service import ConfigService

config_service = ConfigService()


def generate_source_title(source_type: str, form_data: dict) -> str:
    """
    Generates a standardized title for a source based on its type and data.

    It reads the configuration for the given source type, identifies which
    fields are marked as 'is_title_part', and joins their values together.
    """
    title_parts = []
    # Get the configuration for all fields related to this source type
    all_source_types = config_service.get_source_types()
    source_type_config = all_source_types.get(source_type, {})
    field_configs = source_type_config.get("fields", [])

    # Filter for fields that are marked as part of the title
    title_field_configs = [f for f in field_configs if f.get("is_title_part")]

    for config in title_field_configs:
        # Get the value from the form data, if it exists and is not empty
        value = form_data.get(config.get("name"))
        if value:
            title_parts.append(str(value).strip())

    # Join the parts with a consistent separator
    return " - ".join(title_parts)
