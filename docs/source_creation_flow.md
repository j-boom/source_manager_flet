# Source Management Flow Documentation

This document explains the complete flows for managing sources in the Source Manager application, including creation, editing, adding to projects, and removal. All class and method names are provided for clear traceability.

## Overview

The Source Manager supports several source-related operations:
1. **Creating new master sources** - Adding sources to regional master lists
2. **Editing existing sources** - Modifying master source details
3. **Adding sources to projects** - Linking master sources to specific projects
4. **Removing sources from projects** - Unlinking sources from projects
5. **Reordering project sources** - Changing the order of sources within projects

## Flow Diagrams

```
Source Creation: User Action → UI Component → Controller → Service → Data Model → File System
Source Editing:  Card Action → Controller → Dialog → Controller → Service → File System
Project Linking: Card Action → Controller → Service → Project Model → File System
Source Removal:  Card Action → Controller → Service → Project Model → File System
```

## Detailed Flows

## Flow 1: Creating New Master Sources

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

## Flow 2: Editing Existing Sources

### 1. User Initiates Source Editing

**Entry Points:**
- **Class:** `ProjectSourceCard`
- **Method:** `_handle_view_edit_source()`
- **Location:** `src/views/components/cards/project_source_card.py`
- **Trigger:** User clicks the edit/view button on a project source card

```python
def _handle_view_edit_source(self, e):
    """Handles the view/edit source action."""
    if hasattr(self.controller, "show_source_editor_dialog"):
        self.controller.show_source_editor_dialog(self.source.id)
```

### 2. Controller Shows Editor Dialog

**Class:** `AppController`
**Method:** `show_source_editor_dialog()`
**Location:** `src/controllers/app_controller.py`

**Process:**
1. Retrieves source by ID from data service
2. Creates and displays the source editor dialog
3. Sets up callback for dialog closure

```python
def show_source_editor_dialog(self, source_id: str):
    """Shows a dialog to view and edit a master source's details."""
    source = self.data_service.get_source_by_id(source_id)
    if not source:
        # Show error message
        return
    
    def on_dialog_close():
        # Refresh the sources tab
        current_view = self.views.get("project_dashboard")
        if current_view and hasattr(current_view, 'sources_tab'):
            current_view.sources_tab._update_view()
    
    dialog = SourceEditorDialog(self.page, self, source, on_close=on_dialog_close)
    dialog.show()
```

### 3. Editor Dialog Handles Updates

**Class:** `SourceEditorDialog`
**Location:** `src/views/components/dialogs/source_editor_dialog.py`
**Parent Class:** `BaseDialog`

**Process:**
1. Pre-populates form with existing source data
2. Allows user to modify fields
3. Submits changes back to controller

### 4. Controller Processes Updates

**Class:** `AppController`
**Method:** `submit_source_update()`
**Location:** `src/controllers/app_controller.py`

```python
def submit_source_update(self, source_id: str, form_data: Dict[str, Any]):
    """Receives updated data from the source editor and tells the DataService to save it."""
    success, message = self.data_service.update_master_source(source_id, form_data)
    
    # Show feedback to user
```

### 5. Data Service Updates Source

**Class:** `DataService`
**Method:** `update_master_source()`
**Location:** `src/services/data_service.py`

**Process:**
1. Finds the source in the appropriate regional file
2. Updates the source data
3. Saves the modified file
4. Clears relevant caches

## Flow 3: Adding Sources to Projects

### 1. User Adds Source

**Entry Points:**
- **Class:** `OnDeckCard`
- **Method:** `_on_add_clicked()`
- **Location:** `src/views/components/cards/on_deck_card.py`
- **Trigger:** User clicks "Add" button on an "On Deck" source

```python
def _on_add_clicked(self, e):
    """Handles adding the source to the project."""
    if hasattr(self.controller, "add_source_to_project"):
        self.controller.add_source_to_project(self.source.id)
```

### 2. Controller Processes Addition

**Class:** `AppController`
**Method:** `add_source_to_project()`
**Location:** `src/controllers/app_controller.py`

```python
def add_source_to_project(self, source_id: str):
    """Adds a source to the current project."""
    project = self.project_state_manager.current_project
    if not project:
        return
    
    self.data_service.add_source_to_project(project, source_id)
```

### 3. Data Service Links Source

**Class:** `DataService`
**Method:** `add_source_to_project()`
**Location:** `src/services/data_service.py`

**Process:**
1. Creates `ProjectSourceLink` object
2. Adds link to project's sources list
3. Saves project file

## Flow 4: Removing Sources from Projects

### 1. User Removes Source

**Entry Points:**
- **Class:** `ProjectSourceCard`
- **Method:** `_handle_remove_from_project()`
- **Location:** `src/views/components/cards/project_source_card.py`
- **Trigger:** User clicks delete button on a project source card

```python
def _handle_remove_from_project(self, e):
    """Handles removing the source from the project via the controller."""
    if hasattr(self.controller, "remove_source_from_project"):
        self.controller.remove_source_from_project(self.source.id)
```

### 2. Controller Processes Removal

**Class:** `AppController`
**Method:** `remove_source_from_project()`
**Location:** `src/controllers/app_controller.py`

```python
def remove_source_from_project(self, source_id: str):
    """Removes a source link from the currently loaded project."""
    project = self.project_state_manager.current_project
    if not project:
        return
    
    self.data_service.remove_source_from_project(project, source_id)
    
    # Refresh the sources tab
    current_view = self.views.get("project_dashboard")
    if current_view and hasattr(current_view, 'sources_tab'):
        current_view.sources_tab._update_view()
```

### 3. Data Service Removes Link

**Class:** `DataService`
**Method:** `remove_source_from_project()`
**Location:** `src/services/data_service.py`

**Process:**
1. Finds and removes the source link from project
2. Saves updated project file

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

**Class:** `ProjectSourceLink`
**Location:** `src/models/project_models.py`

**Key Methods:**
- Links sources to projects with additional metadata
- Tracks order, notes, and other project-specific information

### 7. File System Storage

**Master Sources Location:** `data/master_sources/{region}_sources.json`

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

**Project Files Location:** `data/projects/{project_name}.json`

**Structure:**
```json
{
    "title": "Project Name",
    "file_path": "/path/to/project",
    "sources": [
        {
            "source_id": "src_xxxxxxxx",
            "notes": "Project-specific notes",
            "order": 1,
            "date_added": "2025-07-07T20:32:15.331779"
        }
    ]
}
```

### 8. UI Refresh

After successful operations:

**Class:** `ProjectSourcesTab`
**Method:** `_update_view()`
**Location:** `src/views/pages/project_view/tabs/project_sources.py`

**Process:**
1. Clears existing UI controls
2. Reloads master sources for the region
3. Rebuilds "On Deck" list (sources not in project)
4. Rebuilds "Project Sources" list with drag-and-drop capability
5. Refreshes the page

```python
def _update_view(self):
    """
    Refreshes both the "On Deck" and "Project Sources" lists.
    
    Rebuilds the UI by:
    1. Clearing existing controls from both lists
    2. Fetching master sources for the project's region
    3. Populating "On Deck" with available sources not yet in the project
    4. Populating "Project Sources" with draggable/droppable cards in order
    5. Adding placeholder text when lists are empty
    """
```

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

### Dialog Components

**Source Creation:**
- **Class:** `SourceCreationDialog`
- **Location:** `src/views/components/dialogs/source_creation_dialog.py`
- **Purpose:** Handles new source creation forms

**Source Editing:**
- **Class:** `SourceEditorDialog`
- **Location:** `src/views/components/dialogs/source_editor_dialog.py`
- **Purpose:** Handles existing source modification forms

### Card Components

**Project Source Cards:**
- **Class:** `ProjectSourceCard`
- **Location:** `src/views/components/cards/project_source_card.py`
- **Actions:** Edit source, remove from project, drag-and-drop reordering

**On Deck Cards:**
- **Class:** `OnDeckCard`
- **Location:** `src/views/components/cards/on_deck_card.py`
- **Actions:** Add source to project, view source details

### Drag and Drop Functionality

**Class:** `ProjectSourcesTab`
**Methods:**
- `on_drag_accept()` - Handles drop actions for reordering
- `on_drag_will_accept()` - Visual feedback during drag
- `on_drag_leave()` - Removes visual feedback

**Process:**
1. Sources wrapped in `Draggable` and `DragTarget` controls
2. User drags source to new position
3. Controller method `reorder_project_sources()` called
4. Data service updates project file
5. UI refreshes to show new order

### File Locations and Regional Mapping

**Master Sources:**
- `data/master_sources/General_sources.json` - Default region
- `data/master_sources/Europe_sources.json` - European projects
- `data/master_sources/ROW_sources.json` - Rest of World projects

**Project Files:**
- `data/projects/{project_name}.json` - Individual project data

**Regional Determination:**
- **Method:** `DataService.get_region_for_project()`
- **Logic:** Uses `REGIONAL_MAPPINGS` configuration
- **Priority:** Configurable priority-based matching

This comprehensive flow documentation ensures data integrity, proper validation, and consistent user experience throughout all source management processes. Each operation maintains clear separation of concerns between UI components, controllers, services, and data models.
