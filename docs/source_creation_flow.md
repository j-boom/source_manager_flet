# Source Creation Flow Documentation

This document explains the complete flow for creating a new source in the Source Manager application, including all classes and methods involved in the process.

## Overview

The source creation process allows users to create new master sources that are saved regionally and can be added to projects. The flow involves UI components, controllers, services, and data models working together.

## Flow Diagram

```
User Action → UI Component → Controller → Service → Data Model → File System
```

## Detailed Flow

### 1. User Initiates Source Creation

**Entry Points:**
- **Class:** `ProjectSourcesTab`
- **Method:** `_on_create_source_clicked()`
- **Location:** `src/views/pages/project_view/tabs/project_sources.py`
- **Trigger:** User clicks the floating action button (FAB) with "+" icon

```python
def _on_create_source_clicked(self, e):
    """Handles the floating action button click to create a new master source."""
    if hasattr(self.controller, "show_create_source_dialog"):
        self.controller.show_create_source_dialog()
```

### 2. Controller Shows Creation Dialog

**Class:** `AppController`
**Method:** `show_create_source_dialog()`
**Location:** `src/controllers/app_controller.py`

**Process:**
1. Validates that a project is currently loaded
2. Creates and displays the source creation dialog
3. Sets up callback for dialog closure

```python
def show_create_source_dialog(self):
    """Shows the dialog to create a new master source."""
    project = self.project_state_manager.current_project
    if not project:
        # Show error message and return
        return
    
    def on_dialog_close():
        # Refresh the sources tab
        current_view = self.views.get("project_dashboard")
        if current_view and hasattr(current_view, "sources_tab"):
            current_view.sources_tab._update_view()
    
    dialog = SourceCreationDialog(self.page, self, on_close=on_dialog_close)
    dialog.show()
```

### 3. Dialog Handles User Input

**Class:** `SourceCreationDialog`
**Location:** `src/views/components/dialogs/source_creation_dialog.py`
**Parent Class:** `BaseDialog`

**Key Methods:**
- `__init__()` - Initializes the dialog with form fields
- `show()` - Displays the dialog to the user
- `_on_submit()` - Processes form submission
- `_close()` - Handles dialog closure

**Form Fields:**
- Source Type (dropdown)
- Title (text input)
- Authors (text input, comma-separated)
- Publication Year (optional)
- Publisher (optional)
- URL (optional)

### 4. Controller Processes Form Data

**Class:** `AppController`
**Method:** `submit_new_source()`
**Location:** `src/controllers/app_controller.py`

**Process:**
1. Receives form data from dialog
2. Determines the region for the current project
3. Calls the data service to create the source
4. Shows success/error feedback to user

```python
def submit_new_source(self, form_data: Dict[str, Any]):
    """Receives data from the source dialog and tells the DataService to create it."""
    project = self.project_state_manager.current_project
    if not project:
        return
    
    region = self.data_service.get_region_for_project(project.file_path)
    success, message, _ = self.data_service.create_new_source(region, form_data)
    
    # Show feedback to user
```

### 5. Data Service Creates Source

**Class:** `DataService`
**Method:** `create_new_source()`
**Location:** `src/services/data_service.py`

**Process:**
1. Validates form data
2. Generates unique source ID
3. Processes authors (converts string to list)
4. Creates `SourceRecord` model
5. Loads existing regional source file
6. Appends new source to the list
7. Saves updated file
8. Clears cache for the region

```python
def create_new_source(self, region: str, form_data: Dict[str, Any]) -> Tuple[bool, str, Optional[SourceRecord]]:
    """Creates a new master source record and saves it to the regional file."""
    # Generate unique ID
    source_data['id'] = f"src_{uuid.uuid4().hex[:8]}"
    source_data['region'] = region
    
    # Process authors
    if 'authors' in source_data and isinstance(source_data['authors'], str):
        source_data['authors'] = [author.strip() for author in source_data['authors'].split(',')]
    
    # Create model
    new_source = SourceRecord.from_dict(source_data)
    
    # Save to file
    source_file_path = self.master_sources_dir / f"{region}_sources.json"
    # ... file operations
```

### 6. Data Model Validation

**Class:** `SourceRecord`
**Location:** `src/models/source_models.py`

**Key Methods:**
- `from_dict()` - Creates instance from dictionary data
- `to_dict()` - Converts instance to dictionary for JSON serialization
- Field validation through dataclass

### 7. File System Storage

**File Location:** `data/master_sources/{region}_sources.json`

**Structure:**
```json
{
    "sources": [
        {
            "id": "src_xxxxxxxx",
            "source_type": "book|website|report|article|other",
            "title": "Source Title",
            "region": "General|Europe|ROW",
            "authors": ["Author1", "Author2"],
            "publication_year": "2023",
            "publisher": "Publisher Name",
            "url": "https://example.com",
            "date_created": "2025-07-07T20:32:15.331779",
            "last_modified": "2025-07-07T20:32:15.332210"
        }
    ]
}
```

### 8. UI Refresh

After successful creation:

**Class:** `ProjectSourcesTab`
**Method:** `_update_view()`
**Location:** `src/views/pages/project_view/tabs/project_sources.py`

**Process:**
1. Clears existing UI controls
2. Reloads master sources for the region
3. Rebuilds "On Deck" list with new source included
4. Updates project sources list
5. Refreshes the page

## Regional Mapping

**Class:** `DataService`
**Method:** `get_region_for_project()`

**Logic:**
- Determines region based on project file path
- Uses `REGIONAL_MAPPINGS` configuration
- Priority-based matching system
- Defaults to "General" region

**Supported Regions:**
- `General` - Default region
- `Europe` - European projects
- `ROW` - Rest of World projects

## Error Handling

**Common Error Scenarios:**
1. **No Project Loaded:** User tries to create source without opening a project
2. **Invalid Form Data:** Missing required fields or invalid data types
3. **File System Errors:** Permissions, disk space, file corruption
4. **Model Validation Errors:** Data doesn't conform to SourceRecord schema

**Error Display:**
- `ft.SnackBar` for user feedback
- Console logging for debugging
- Boolean return values with error messages

## Cache Management

**Class:** `DataService`
**Attribute:** `_master_source_cache`

**Process:**
- Cache is invalidated when new sources are created
- Ensures fresh data is loaded on next access
- Improves performance for repeated access

## Integration Points

**Adding Sources to Projects:**
- **Method:** `add_source_to_project()` in `AppController`
- **Trigger:** User clicks "Add" button on `OnDeckCard`
- **Result:** Source is added to current project's source list

**File Locations:**
- **Master Sources:** `data/master_sources/{region}_sources.json`
- **Project Files:** `data/projects/{project_name}.json`
- **Configuration:** `config/` directory for regional mappings

This flow ensures data integrity, proper validation, and consistent user experience throughout the source creation process.
