# Configuration-Driven Project Form System

## Overview

This system provides a flexible, maintainable way to manage different project types in the Source Manager application. Instead of hardcoding form fields and validation rules, everything is driven by configuration files that can be easily modified without touching the core application code.

## Key Benefits

✅ **Single Source of Truth**: All project type definitions in one configuration file  
✅ **Easy to Extend**: Add new project types by just updating configuration  
✅ **Consistent UI**: All forms generated using the same components and styling  
✅ **Type-Safe Validation**: Validation rules defined alongside field definitions  
✅ **Database Schema Automation**: Database tables generated automatically from config  
✅ **Backward Compatible**: Works alongside existing JSON-based project files  

## Architecture

### Core Components

1. **`config/project_types_config.py`** - Master configuration file
2. **`src/views/components/forms/dynamic_form_generator.py`** - Form generation engine
3. **`src/models/database_schema_generator.py`** - Database schema generator
4. **`src/views/components/dialogs/dynamic_project_creation_dialog.py`** - Dynamic dialog implementation

## Configuration Structure

### Project Type Configuration

Each project type is defined with:

```python
ProjectTypeConfig(
    name="CCR",                           # Short code
    display_name="Construction Change Request",  # Human-readable name
    description="Construction Change Request projects",  # Description
    table_name="projects_ccr",           # Database table name
    filename_pattern="{facility_number} - {building_number} - CCR - {request_year}.json",
    fields=[...]                         # List of form fields
)
```

### Field Configuration

Each field is defined with:

```python
FieldConfig(
    name="building_number",              # Field identifier
    label="Building Number",             # UI label
    field_type=FieldType.TEXT,          # Field type (TEXT, DROPDOWN, etc.)
    required=False,                      # Whether field is required
    hint_text="Format: [A-Z]{2}\\d{3}",  # Helper text
    width=200,                           # Field width in pixels
    validation_rules={                   # Validation rules
        ValidationRule.PATTERN: r'^[A-Z]{2}\\d{3}$'
    }
)
```

### Field Types

- **TEXT** - Single-line text input
- **TEXTAREA** - Multi-line text input
- **DROPDOWN** - Selection from predefined options
- **NUMBER** - Numeric input with validation
- **DATE** - Date input field
- **BOOLEAN** - Checkbox input

### Validation Rules

- **REQUIRED** - Field must have a value
- **PATTERN** - Must match regex pattern
- **MIN_LENGTH** / **MAX_LENGTH** - String length constraints
- **MIN_VALUE** / **MAX_VALUE** - Numeric value constraints

## Current Project Types

### CCR - Construction Change Request
- **Special Fields**: `suffix`, `change_order_number`, `estimated_cost`
- **Filename**: `{facility_number} - {building_number} - CCR - {request_year}.json`
- **Requirements**: Suffix required, change order tracking

### GSC - Geotechnical Site Characterization  
- **Special Fields**: `site_location`, `investigation_type`, `depth_required`
- **Filename**: `{facility_number} - {building_number} - GSC - {request_year}.json`
- **Requirements**: No suffix required, site-specific data

### STD - Standard Design
- **Special Fields**: `suffix`, `design_category`, `applicable_codes`
- **Filename**: `{facility_number} - {building_number} - STD - {suffix} - {request_year}.json`
- **Requirements**: Design standards and codes tracking

### FCR - Facility Change Request
- **Special Fields**: `suffix`, `change_type`, `justification`
- **Filename**: `{facility_number} - {building_number} - FCR - {suffix} - {request_year}.json`
- **Requirements**: Change justification required

### COM - Commissioning
- **Special Fields**: `suffix`, `commissioning_phase`, `systems_involved`
- **Filename**: `{facility_number} - {building_number} - COM - {suffix} - {request_year}.json`
- **Requirements**: Commissioning phase tracking

### CRS - Corrective Action
- **Special Fields**: `suffix`, `deficiency_description`, `priority_level`
- **Filename**: `{facility_number} - {building_number} - CRS - {suffix} - {request_year}.json`
- **Requirements**: Deficiency description required

### OTH - Other
- **Special Fields**: `document_title`, `project_category`, `deliverables`
- **Filename**: `{facility_number} - {building_number} - OTH - {document_title} - {request_year}.json`
- **Requirements**: Custom document title required

## Database Schema

### Base Tables

- **`customers`** - Facility information (unchanged)
- **`projects_base`** - Common project data
- **`sources`** - Source documents (unchanged)
- **`project_sources`** - Project-source relationships

### Project Type Tables

Each project type gets its own table:
- `projects_ccr`
- `projects_gsc` 
- `projects_std`
- `projects_fcr`
- `projects_com`
- `projects_crs`
- `projects_oth`

Each type table includes:
- Reference to `projects_base`
- All configured fields for that project type
- Proper SQL types based on field configuration
- Indexes for performance

## Usage Examples

### Adding a New Project Type

1. **Define the configuration** in `config/project_types_config.py`:

```python
"NEW": ProjectTypeConfig(
    name="NEW",
    display_name="New Project Type",
    description="Description of new project type",
    table_name="projects_new",
    filename_pattern="{facility_number} - {building_number} - NEW - {request_year}.json",
    fields=FACILITY_FIELDS + BASE_PROJECT_FIELDS + [
        FieldConfig(
            name="special_field",
            label="Special Field *",
            field_type=FieldType.TEXT,
            required=True,
            hint_text="Enter special data",
            width=300
        ),
    ] + TEAM_FIELDS
)
```

2. **Regenerate database schema** (automatic on next run)

3. **Test the new project type** - it will automatically appear in the UI

### Customizing Field Behavior

```python
FieldConfig(
    name="priority",
    label="Priority Level",
    field_type=FieldType.DROPDOWN,
    options=["Critical", "High", "Medium", "Low"],
    required=True,
    depends_on="change_type",        # Only show if change_type has value
    depends_value="Emergency"        # Only show for Emergency changes
)
```

### Adding Validation Rules

```python
FieldConfig(
    name="budget",
    label="Project Budget",
    field_type=FieldType.NUMBER,
    validation_rules={
        ValidationRule.MIN_VALUE: 0,
        ValidationRule.MAX_VALUE: 1000000
    }
)
```

## Integration with Existing Code

### Form Generation

```python
from src.views.components.forms.dynamic_form_generator import DynamicFormGenerator

# Create form generator
form_gen = DynamicFormGenerator(theme_manager=theme_manager)

# Generate form for project type
sections = form_gen.generate_form("CCR")

# Get form values
values = form_gen.get_field_values()

# Validate form
errors = form_gen.validate_form()
```

### Database Schema Management

```python
from src.models.database_schema_generator import DatabaseSchemaGenerator

# Create schema generator
schema_gen = DatabaseSchemaGenerator("path/to/database.db")

# Create all tables
schema_gen.create_database()

# Add new project type table
schema_gen.add_project_type_table("NEW")
```

## Migration Strategy

### Phase 1: Configuration System (Current)
- ✅ Project type configuration defined
- ✅ Dynamic form generator implemented  
- ✅ Database schema generator created
- ✅ Basic dynamic dialog structure

### Phase 2: Integration (Next Steps)
- 🔄 Update existing ProjectCreationDialog to use dynamic system
- 🔄 Extend DatabaseManager with project type table support
- 🔄 Add data migration utilities
- 🔄 Update existing projects to new schema

### Phase 3: Enhancement (Future)
- 📋 Conditional field visibility
- 📋 Field validation dependencies
- 📋 Custom field types (file upload, date picker, etc.)
- 📋 Form sections and grouping
- 📋 Export/import of project type configurations

## Best Practices

### Configuration
1. **Keep field names descriptive** and consistent
2. **Use validation rules** for data quality
3. **Group related fields** logically
4. **Provide helpful hint text** for complex fields

### Database
1. **Use consistent naming** for tables and columns
2. **Add indexes** for frequently queried fields
3. **Maintain referential integrity** with foreign keys
4. **Plan for data migration** when updating schemas

### UI/UX
1. **Keep forms organized** in logical sections
2. **Use appropriate field types** for data
3. **Provide clear error messages** for validation
4. **Test with real data** before deployment

## Troubleshooting

### Common Issues

**Forms not updating after config changes**
- Restart the application to reload configuration
- Check for syntax errors in config file

**Database errors when adding new project types**
- Ensure table names are unique
- Check field types are supported
- Verify foreign key relationships

**Validation not working**
- Check regex patterns for proper escaping
- Ensure validation rules are properly defined
- Test patterns independently

### Debug Mode

Enable debug logging to see form generation details:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This comprehensive system provides a solid foundation for managing project types while maintaining flexibility for future enhancements!
