# Configurable Project Metadata System

## Overview
The project metadata tab has been completely redesigned to use a configurable three-column layout that adapts based on project type. This system allows for customizable field layouts, proper tab ordering, and project-type-specific field configurations.

## Key Features

### 1. Three-Column Layout
- **Side-by-Side Columns**: Up to 3 columns displayed horizontally
- **Responsive Design**: If more than 3 columns are defined, they wrap to new rows
- **Full Width Fields**: All fields expand to use the full width of their column
- **Proper Spacing**: Each field is contained in its own padded container

### 2. Project Type Configurations
The system supports different field layouts based on project type:

#### Default Configuration
- **Basic Information**: Title, Project Type, Status, Created Date
- **Team Members**: Engineer, Drafter, Reviewer, Architect, Geologist
- **Project Details**: Description, Location, Client

#### Commercial Configuration
- **Basic Information**: Title, Project Type, Status, Building Code, Created Date
- **Team & Compliance**: Lead Engineer*, Architect*, Code Reviewer, CAD Drafter, Permit Status
- **Project Details**: Client/Owner*, Project Address*, Square Footage, Project Scope

#### Residential Configuration
- **Basic Information**: Title, Project Type, Status, Home Type, Created Date
- **Team Members**: Structural Engineer, Architect, Drafter, Geotechnical Engineer, Plan Reviewer
- **Property Details**: Homeowner, Property Address, Lot Size, Bedrooms, Bathrooms, Description

### 3. Field Types Supported
- **Text**: Standard text input fields
- **Multiline**: Multi-line text areas with configurable line limits
- **Dropdown**: Selection dropdowns with predefined options
- **Number**: Numeric input fields with number keyboard
- **Readonly**: Read-only fields (e.g., created date)

### 4. Tab Order System
- Each field has a configurable `tab_order` property
- Tab navigation flows top-to-bottom within each column, then left-to-right across columns
- Proper keyboard navigation support

### 5. Required Field Indicators
- Required fields are marked with an asterisk (*) in their labels
- Configurable per field via the `required` property

## Configuration Structure

### Field Configuration
Each field is defined with the following properties:
```python
{
    'key': 'field_name',           # Database/JSON key
    'label': 'Display Label',      # UI label
    'type': 'text',               # Field type (text, multiline, dropdown, number, readonly)
    'required': True,             # Whether field is required (adds *)
    'tab_order': 1,               # Tab navigation order
    'options': [...],             # For dropdown fields
    'min_lines': 3,               # For multiline fields
    'max_lines': 6                # For multiline fields
}
```

### Column Configuration
Columns are defined with:
```python
{
    'name': 'Column Title',       # Column header
    'fields': [...]               # List of field configurations
}
```

### Project Type Configuration
Each project type has:
```python
{
    'columns': [...]              # List of column configurations
}
```

## File Structure

### Main Files
- `src/views/pages/project_view/tabs/project_metadata.py` - Main tab implementation
- `config/metadata_config.py` - Full configuration definitions (external)

### Inline Configuration
The tab file contains inline configuration to avoid import issues, with support for:
- Default project type
- Commercial project type
- Residential project type

## Usage

### Creating a New Project Type Configuration
1. Add a new entry to `DEFAULT_METADATA_CONFIG`
2. Define columns with appropriate fields
3. Set proper tab order values
4. Test with sample data

### Adding New Field Types
1. Extend the `create_field_widget()` function
2. Add field type to the switch statement
3. Handle special properties (options, lines, etc.)

### Customizing Existing Configurations
1. Modify the appropriate project type configuration
2. Add/remove fields as needed
3. Adjust tab order values
4. Update field labels and types

## Benefits

### For Users
- **Consistent Layout**: Clean three-column design
- **Type-Specific Fields**: Relevant fields for each project type
- **Efficient Navigation**: Proper tab order and keyboard navigation
- **Clear Requirements**: Visual indicators for required fields

### For Developers
- **Easy Configuration**: Simple Python dictionaries
- **Extensible**: Easy to add new project types and field types
- **Maintainable**: Clear separation of configuration and UI logic
- **Fallback Support**: Graceful degradation if configuration fails

## Implementation Details

### Dynamic Field Creation
The system dynamically creates Flet widgets based on configuration:
- Field widgets are stored in `self.field_widgets` dictionary
- Field configurations are stored in `self.field_configs` dictionary
- Values are automatically populated from project data

### Save Functionality
The save process:
1. Collects values from all dynamic field widgets
2. Updates the project data dictionary
3. Saves to database (if available)
4. Saves to JSON file (if available)
5. Shows success/error messages

### Data Binding
- Project data is automatically bound to field widgets on initialization
- Values are updated when project data changes
- Dropdown fields handle validation of selected values

## Testing

The system has been tested with:
- ✅ Commercial project configuration
- ✅ Residential project configuration
- ✅ Default project configuration
- ✅ Integration with main application
- ✅ Save functionality
- ✅ Field validation
- ✅ Tab navigation

## Future Enhancements

Potential improvements:
- **Field Validation**: Custom validation rules per field
- **Conditional Fields**: Show/hide fields based on other field values
- **Field Groups**: Collapsible sections within columns
- **Custom Field Types**: Date pickers, file uploads, etc.
- **Configuration UI**: Admin interface for managing configurations
- **Import/Export**: Configuration backup and sharing

## Migration Notes

### From Previous Version
- Old hardcoded fields are replaced with configurable fields
- Same field keys are maintained for data compatibility
- Layout changed from vertical single-column to horizontal three-column
- Save functionality remains the same

### Data Compatibility
- All existing project data continues to work
- New fields will be empty for existing projects
- No data migration required
