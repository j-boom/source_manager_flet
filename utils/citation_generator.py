import re
from typing import TYPE_CHECKING
from src.models import SourceRecord

if TYPE_CHECKING:
    from src.controllers.app_controller import AppController

def generate_citation(source: SourceRecord, controller: "AppController") -> str:
    """
    Generates a citation string for a source based on its type.

    Args:
        source: The SourceRecord object.
        controller: The main AppController to access services.

    Returns:
        A formatted citation string.
    """
    source_type = source.source_type.value if hasattr(source.source_type, 'value') else source.source_type

    try:
        config = controller.admin_controller.get_source_type_config(source_type)
        format_string = config.get("citation_format")
    except Exception:
        format_string = None

    if not format_string:
        # Fallback to a default format if none is defined
        return f"{source.get_field_value('authors', 'N/A')} - {source.get_title()} ({source.get_field_value('publication_year', 'n.d.')})"

    # Find all placeholders like {field_name} in the string
    placeholders = re.findall(r"\{(.+?)\}", format_string)
    
    # Create a dictionary of values from the source record
    values = {}
    for placeholder in placeholders:
        value = source.get_field_value(placeholder.strip())
        
        if value is None:
            values[placeholder] = ""
        elif isinstance(value, list):
            values[placeholder] = ", ".join(map(str, value))
        else:
            values[placeholder] = str(value)
            
    try:
        return format_string.format(**values)
    except KeyError as e:
        return f"[Citation format error: Missing field {e}]"