# Project Metadata Configuration Guide

This guide explains how to configure the project metadata forms for different project types in the Source Manager application.

## Overview

The Source Manager uses a simplified, JSON-based project system where:
- **Project creation dialog** collects essential project information
- **Metadata tab** displays and allows editing of comprehensive project data
- **Configuration-driven forms** define what fields are available for each project type
- **Column layout** organizes fields into logical groups

## System Architecture

### Data Flow
1. **Project Creation**: User fills out creation dialog with basic info
2. **JSON File Creation**: System creates a JSON file with project data
3. **Metadata Display**: Metadata tab shows all fields in organized columns
4. **Field Mapping**: Dialog data automatically populates corresponding metadata fields

### Key Components
- **Project Types Configuration**: `config/project_types_config.py` - Single source of truth
- **Project Creation Service**: Handles dialog data and file creation
- **Metadata Tab**: Displays configurable forms with column layout

## Project Types

The system supports 7 project types with unified configuration:

| Code | Display Name | Description |
|------|-------------|-------------|
| `CCR` | Component Characterization | Simple characterization projects |
| `GSC` | Geotechnical Site Characterization | Site investigation projects |
| `STD` | Standard Design | Standard design projects |
| `FCR` | Facility Change Request | Facility modification projects |
| `COM` | Commissioning | System commissioning projects |
| `CRS` | Corrective Action | Problem correction projects |
| `OTH` | Other | Custom/miscellaneous projects |

## Field Organization

Each project type has fields organized into logical sections:

### Project Information Section
**Purpose**: Contains data collected by the project creation dialog
**Fields**: All project types include these core fields:
- Project Type (dropdown selection from dialog)
- Facility Number (10-digit number from folder selection)
- Facility Name (user input, required)
- Building Number (user input with format validation: XX123)
- Project Title (user input, required)
- Created Date (automatically set)
- Document Title (for OTH projects only)

### Additional Sections
**Basic Information**: Additional project fields like request year
**Team Information**: Team member assignments (engineer, analyst, etc.)
**Type-Specific**: Fields unique to each project type (e.g., "GSC Specific", "STD Specific")

## Configuration File Structure

The main configuration is in `config/project_types_config.py`:

```python
# Field group definitions
PROJECT_INFO_FIELDS = [...]      # Dialog fields (core project data)
BASE_PROJECT_FIELDS = [...]      # Common additional fields  
TEAM_FIELDS = [...]              # Team assignment fields
FACILITY_FIELDS = [...]          # Additional facility fields

# Project type configurations
PROJECT_TYPES_CONFIG = {
    "CCR": ProjectTypeConfig(
        name="CCR",
        display_name="Component Characterization",
        description="Simple characterization projects",
        filename_pattern="{facility_number} - {building_number} - CCR - {request_year}.json",
        fields=PROJECT_INFO_FIELDS + BASE_PROJECT_FIELDS + TEAM_FIELDS
    ),
    # ... other project types
}
```

## Field Configuration

Each field is defined using `FieldConfig`:

```python
FieldConfig(
    name="field_name",                    # Internal name (JSON key)
    label="Display Label *",              # User-visible label (* = required)
    field_type=FieldType.TEXT,           # Input widget type
    required=True,                       # Mandatory field
    hint_text="Helper text",             # Placeholder/help text
    width=300,                           # Field width in pixels
    tab_order=1,                         # Keyboard navigation order
    column_group="Project Information"   # Column/section for layout
)
```

### Field Types

| Type | Description | Example Use |
|------|-------------|-------------|
| `TEXT` | Single-line text input | Names, titles, codes |
| `TEXTAREA` | Multi-line text input | Descriptions, justifications |
| `DROPDOWN` | Select from options | Status, categories, types |
| `NUMBER` | Numeric input only | Depths, quantities, costs |
| `DATE` | Date selection | Due dates, start dates |
| `BOOLEAN` | Checkbox (true/false) | Approval flags, toggles |

### Validation Rules

Add validation using the `validation_rules` parameter:

```python
FieldConfig(
    name="building_number",
    validation_rules={ValidationRule.PATTERN: r'^[A-Z]{2}\d{3}$'},
    hint_text="Format: Two letters + three digits (e.g., DC123)"
)
```

Available validation rules:
- `REQUIRED`: Field must have a value
- `PATTERN`: Regular expression validation
- `MIN_LENGTH`/`MAX_LENGTH`: Text length limits
- `MIN_VALUE`/`MAX_VALUE`: Numeric range limits

## Column Layout System

### How Columns Work

Fields are automatically organized into columns based on their `column_group` property:

1. **Same Group = Same Column**: Fields with identical `column_group` values appear together
2. **Different Groups = Different Columns**: Each unique `column_group` creates a separate column
3. **Order**: Fields within each column are sorted by `tab_order`

### Visual Example

With these field configurations:
```python
FieldConfig(name="project_type", column_group="Project Information", tab_order=1)
FieldConfig(name="facility_name", column_group="Project Information", tab_order=2)
FieldConfig(name="request_year", column_group="Basic Information", tab_order=1)
FieldConfig(name="engineer", column_group="Team Information", tab_order=1)
```

The metadata tab displays:

```
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│ Project Information │  │ Basic Information   │  │ Team Information    │
├─────────────────────┤  ├─────────────────────┤  ├─────────────────────┤
│ Project Type *      │  │ Request Year *      │  │ Engineer            │
│ [Component Char. ▼] │  │ [2025            ▼] │  │ [_______________]   │
│                     │  │                     │  │                     │
│ Facility Name *     │  │                     │  │                     │
│ [_______________]   │  │                     │  │                     │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
```

### Standard Column Groups

Use these consistent group names across project types:

- **`"Project Information"`**: Core dialog data (always first column)
- **`"Basic Information"`**: Additional project details
- **`"Team Information"`**: Staff assignments
- **`"[Type] Specific"`**: Type-specific fields (e.g., "GSC Specific")
- **`"Technical Information"`**: Technical specifications
- **`"Documentation"`**: Notes, justifications, deliverables
- **`"Administrative"`**: Dates, status, workflow

## Data Mapping

### Dialog to Metadata Mapping

The system automatically maps project creation dialog data to metadata fields:

| Dialog Field | Maps To | Description |
|--------------|---------|-------------|
| `customer_name` | `facility_name` | Facility name from dialog |
| `customer_number` | `building_number` | Building number from dialog |
| `customer_key` | `facility_number` | 10-digit facility number |
| `title` | `project_title` | Project title from dialog |
| `project_suffix` | `request_year` | Year for the project |
| Team fields | Team fields | Direct mapping (engineer, etc.) |

### JSON Structure

Created projects have this JSON structure:
```json
{
  "project_id": "1234567890",
  "project_type": "CCR", 
  "project_title": "Sample Project",
  "facility_number": "1234567890",
  "facility_name": "Test Facility",
  "building_number": "DC123",
  "request_year": "2025",
  "created_date": "2025-06-23T...",
  "metadata": {
    "folder_path": "/path/to/project",
    "filename": "1234567890 - DC123 - CCR - 2025.json"
  }
}
```

## Adding a New Project Type

### Step 1: Define the Project Type

Add your new type to `PROJECT_TYPES_CONFIG`:

```python
"NEW": ProjectTypeConfig(
    name="NEW",
    display_name="New Project Type",
    description="Description of new project type",
    filename_pattern="{facility_number} - {building_number} - NEW - {request_year}.json",
    fields=PROJECT_INFO_FIELDS + BASE_PROJECT_FIELDS + [
        # Add type-specific fields here
    ]
)
```

### Step 2: Add Type-Specific Fields

Define fields unique to your project type:

```python
FieldConfig(
    name="special_requirement",
    label="Special Requirement *",
    field_type=FieldType.DROPDOWN,
    required=True,
    options=["Option A", "Option B", "Option C"],
    tab_order=20,
    column_group="NEW Specific"
),
```

### Step 3: Test the Configuration

The new project type will automatically appear in:
- Project creation dialog dropdown
- Metadata tab forms with proper column layout
- File naming patterns

## Customizing Existing Project Types

### Adding Fields to CCR

To add a new field to CCR projects:

```python
# Find the CCR configuration and add to its fields list:
"CCR": ProjectTypeConfig(
    # ... existing config ...
    fields=PROJECT_INFO_FIELDS + BASE_PROJECT_FIELDS + TEAM_FIELDS + [
        FieldConfig(
            name="new_ccr_field",
            label="New CCR Field",
            field_type=FieldType.TEXT,
            tab_order=25,
            column_group="CCR Specific"  # Creates a new column
        )
    ]
),
```

### Modifying Column Layout

To reorganize fields into different columns, change their `column_group`:

```python
# Move engineer from "Team Information" to "Project Information"
FieldConfig(
    name="engineer",
    # ... other properties ...
    column_group="Project Information"  # Changed from "Team Information"
)
```

## Best Practices

### Field Design
- **Use descriptive labels**: Make it clear what users should enter
- **Add hint text**: Provide examples or format requirements
- **Mark required fields**: Add asterisk (*) to required field labels
- **Logical tab order**: Number fields in the order users should complete them

### Column Organization
- **Keep related fields together**: Group logically related fields in the same column
- **Limit columns**: 3-4 columns maximum for good usability
- **Consistent naming**: Use standard column group names across project types
- **Balance columns**: Try to distribute fields evenly across columns

### Validation
- **Validate critical fields**: Use patterns for codes, formats, etc.
- **Provide clear error messages**: Make validation failures easy to understand
- **Don't over-validate**: Only add validation where truly necessary

### Data Structure
- **Consistent field names**: Use similar naming across project types where possible
- **Meaningful field names**: Choose names that clearly indicate the field's purpose
- **Consider reporting**: Think about how data will be used in reports or analysis

## Troubleshooting

### Common Issues

**Fields not appearing**: Check that field is included in project type's `fields` list

**Wrong column layout**: Verify `column_group` values are correct and consistent

**Validation errors**: Check `validation_rules` syntax and regular expressions

**Dialog data not populating**: Ensure field names match the mapping in `_map_dialog_data_to_form_fields`

### Testing Changes

After making configuration changes:

1. **Restart the application** to load new configuration
2. **Create a test project** to verify dialog works
3. **Check metadata tab** to confirm layout and data mapping
4. **Test validation** by entering invalid data
5. **Verify JSON output** by checking created project files

## Technical Reference

### File Locations
- **Main config**: `config/project_types_config.py`
- **Project creation**: `src/services/project_creation_service.py`
- **Metadata tab**: `src/views/pages/project_view/tabs/project_metadata.py`
- **Dialog**: `src/views/components/dialogs/project_creation_dialog.py`

### Key Functions
- `get_project_type_config(type)`: Get configuration for a project type
- `get_fields_by_column_group(fields)`: Group fields by column for layout
- `create_field_widget(config, value)`: Create UI widget from field config
- `validate_field_value(config, value)`: Validate field input

The system is designed to be easily configurable while maintaining consistency and good user experience across all project types.