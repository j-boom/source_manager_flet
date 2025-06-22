# Service and Manager Methods Reference

This document provides a comprehensive reference of all available methods in the Source Manager application's service and manager layers.

## Architecture Overview

- **DatabaseManager**: Core data access layer - handles direct database operations
- **Services**: Business logic layer - handles validation, formatting, and orchestration
- **UI**: Presentation layer - should only call services, never DatabaseManager directly

---

## 1. DatabaseManager (src/models/database_manager.py)

**Core Database Operations Layer - Direct data access only**

### Connection Management
```python
def __init__(self, db_path: Optional[str] = None)
def connect(self) -> sqlite3.Connection
def close(self)
def __enter__(self)
def __exit__(self, exc_type, exc_val, exc_tb)
```

### Project Operations
```python
def create_project(self, project: Project) -> int
    """Create a new project"""

def get_project(self, project_uuid: str) -> Optional[Project]
    """Get project by UUID"""

def get_projects_by_facility_number(self, facility_number: str) -> List[Project]
    """Get all projects for a specific facility number"""

def update_project(self, project_uuid: str, project_data: Dict[str, Any]) -> bool
    """Update an existing project"""
```

### Source Operations
```python
def create_source(self, source: Source) -> int
    """Create a new source"""

def get_source(self, source_uuid: str) -> Optional[Source]
    """Get source by UUID"""

def get_source_by_uuid(self, source_uuid: str) -> Optional[Source]
    """Get source by UUID (duplicate method)"""

def get_or_create_source(self, source_data: Dict[str, Any]) -> int
    """Get existing source or create new one"""

def get_all_sources(self) -> List[Dict[str, Any]]
    """Get all sources from database"""

def get_sources_by_facility_number(self, facility_number: str) -> List[Dict[str, Any]]
    """Get all sources associated with projects for a specific facility number"""

def check_source_exists_by_metadata(self, source_type: str, metadata: Dict[str, Any]) -> Optional[str]
    """Check if a source exists based on key metadata fields and return UUID if found"""
```

### Project-Source Association Operations
```python
def associate_source_with_project(self, project_id: int, source_id: int, assignment_order: Optional[int] = None, usage_notes: Optional[str] = None)
    """Associate a source with a project"""

def get_project_sources(self, project_uuid: str) -> List[Dict[str, Any]]
    """Get all sources for a project"""

def get_project_sources_detailed(self, project_uuid: str) -> List[ProjectSourceDetails]
    """Get detailed information about sources associated with a project"""

def create_project_source_association(self, project_uuid: str, source_uuid: str, usage_notes: str, assignment_order: Optional[int] = None) -> bool
    """Create a project-source association with usage notes"""

def remove_source_from_project(self, project_uuid: str, source_uuid: str) -> bool
    """Remove a source from a project"""

def update_project_source_usage_notes(self, project_uuid: str, source_uuid: str, usage_notes: str) -> bool
    """Update usage notes for a source in a project"""
```

### Slide Assignment Operations
```python
def assign_source_to_slide(self, project_id: int, source_id: int, slide_number: int, slide_title: Optional[str] = None, notes: Optional[str] = None)
    """Assign a source to a PowerPoint slide"""

def get_slide_assignments(self, project_uuid: str) -> List[Dict[str, Any]]
    """Get all slide assignments for a project"""
```

---

## 2. Data Models (src/models/)

**Core data structures used throughout the application**

### Project Models (src/models/project_models.py)
```python
@dataclass
class Project:
    uuid: str
    facility_number: Optional[str] = None  # 10-digit facility number
    facility_suffix: Optional[str] = None  # facility suffix
    engineer: Optional[str] = None
    drafter: Optional[str] = None
    reviewer: Optional[str] = None
    architect: Optional[str] = None
    geologist: Optional[str] = None
    project_code: Optional[str] = None
    project_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: str = 'active'
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

@dataclass
class SlideAssignment:
    project_id: int
    source_id: int
    slide_number: int
    slide_title: Optional[str] = None
    notes: Optional[str] = None
    id: Optional[int] = None
```

### Source Models (src/models/source_models.py)
```python
@dataclass
class Source:
    uuid: str
    source_type: str
    title: str
    # ... other source fields

@dataclass
class ProjectSource:
    # Association between projects and sources
    # ... fields

@dataclass 
class ProjectSourceDetails:
    # Detailed view of project-source associations
    # ... fields
```

---

## 3. SourceManagementService (src/services/source_management_service.py)

**Business Logic Layer - Source operations with validation and formatting**

### Initialization
```python
def __init__(self, database_manager=None)
```

### Source Type & Form Management
```python
def get_available_source_types(self) -> List[Dict[str, str]]
    """Get available source types for dropdown"""

def get_form_fields_for_source_type(self, source_type: str) -> List[Dict[str, Any]]
    """Get form field definitions for a specific source type"""

def validate_source_data(self, source_type: str, form_data: Dict[str, Any]) -> List[str]
    """Validate source data and return list of errors"""
```

### Source Creation & Retrieval
```python
def check_source_exists(self, source_type: str, form_data: Dict[str, Any]) -> Optional[str]
    """Check if a source with similar data already exists, return UUID if found"""

def create_source(self, source_type: str, form_data: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]
    """Create a new source or return existing one
    Returns: (success, message, source_uuid)"""

def get_source_by_uuid(self, source_uuid: str) -> Optional[BaseSource]
    """Get source by UUID from database"""
```

### Project-Source Management
```python
def add_source_to_project(self, source_uuid: str, project_uuid: str, usage_notes: str = "") -> bool
    """Add a source to a project with usage notes"""

def remove_source_from_project(self, source_uuid: str, project_uuid: str) -> bool
    """Remove a source from a project"""

def update_project_source_notes(self, source_uuid: str, project_uuid: str, usage_notes: str) -> bool
    """Update usage notes for a source in a project"""

def get_sources_for_project(self, project_uuid: str) -> List[Dict[str, Any]]
    """Get all sources assigned to a project with their usage notes"""

def get_all_available_sources(self, exclude_project_uuid: Optional[str] = None) -> List[Dict[str, Any]]
    """Get all sources not assigned to a specific project (on-deck sources)"""
```

### Private Methods
```python
def _save_source_to_database(self, source: BaseSource) -> bool
    """Save source to database"""
```

---

## 4. ProjectManagementService (src/services/project_management_service.py)

**Business Logic Layer - Project operations with file system integration**

### Initialization
```python
def __init__(self, database_manager: Optional['DatabaseManager'] = None)
```

### Project Creation & Management
```python
def create_project(self, project_data: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]
    """Create a new project in database and JSON file
    Returns: (success, message, project_uuid)"""

def get_project_by_uuid(self, project_uuid: str) -> Optional[Dict[str, Any]]
    """Get project by UUID from database"""
```

### Source Ordering (JSON-based)
```python
def update_project_source_order(self, project_uuid: str, source_uuids: List[str]) -> bool
    """Update the source order in project JSON file"""

def get_project_source_order(self, project_uuid: str) -> List[str]
    """Get source order from project JSON file"""
```

### Private Methods
```python
def _save_project_to_database(self, project_uuid: str, project_data: Dict[str, Any], created_at: str) -> bool
    """Save project to database"""

def _create_project_json(self, project_uuid: str, project_data: Dict[str, Any], created_at: str) -> bool
    """Create JSON file for project with source ordering"""

def _get_project_directory(self, project_uuid: str, project_data: Dict[str, Any]) -> str
    """Get the directory path for project files"""

def _remove_project_from_database(self, project_uuid: str) -> bool
    """Remove project from database (rollback)"""

def _find_project_json_path(self, project_uuid: str) -> Optional[str]
    """Find the JSON file path for a project"""
```

---

## 5. Other Services Referenced in Code

### DirectoryService
Based on the new_project_view.py file, this service appears to handle directory operations:

```python
# Properties
.directory_source_citations_path
.primary_folders

# Methods (inferred from usage)
def get_four_digit_folders(self, primary_folder: str)
def search_four_digit_folders(self, primary_folder: str, search_term: str)
def get_folder_contents(self, folder_path: str)
def get_folder_path_from_breadcrumb(self, breadcrumb: List[str])
def is_ten_digit_folder(self, breadcrumb: List[str]) -> bool
def is_four_digit_folder(self, breadcrumb: List[str]) -> bool
def extract_ten_digit_number(self, folder_name: str) -> Optional[str]
```

### ProjectCreationService
Referenced in new_project_view.py but appears to be legacy (should be replaced with ProjectManagementService):

```python
def __init__(self, user_config)
# Other methods not documented as this service should be deprecated
```

---

## Usage Guidelines

### For UI Components:
1. **Never import DatabaseManager directly** - always use services
2. **Use SourceManagementService** for all source-related operations
3. **Use ProjectManagementService** for all project-related operations
4. **Handle return values properly** - many service methods return tuples with success/failure status

### For Service Development:
1. **Services should validate inputs** before calling DatabaseManager
2. **Services should format outputs** for UI consumption
3. **Services should handle errors gracefully** and return meaningful messages
4. **Services should not expose database-specific details** to the UI

### Method Naming Conventions:
- **get_*** - Retrieve data
- **create_*** - Create new records
- **update_*** - Modify existing records
- **remove_*** - Delete records
- **check_*** - Validation methods
- **validate_*** - Data validation methods

### Return Value Patterns:
- **Simple operations**: `bool` (success/failure)
- **Complex operations**: `Tuple[bool, str, Optional[str]]` (success, message, optional_data)
- **Data retrieval**: `Optional[DataType]` or `List[DataType]`
- **Validation**: `List[str]` (list of error messages)

---

## Migration Notes

### Completed:
- ✅ Removed all customer operations from DatabaseManager
- ✅ Updated Project model to use facility_number and facility_suffix
- ✅ Clean separation between DatabaseManager (data access) and Services (business logic)
- ✅ Deleted redundant/legacy services
- ✅ **Refactored data models into separate files**:
  - `src/models/project_models.py` - Project and SlideAssignment models
  - `src/models/source_models.py` - Source-related models
  - `src/models/database_manager.py` - Database operations only (no model definitions)

### Architecture Benefits:
- **Single Responsibility**: Each file has one clear purpose
- **Better Imports**: Clean import paths for models (`from models.project_models import Project`)
- **Easier Testing**: Models can be tested independently of database code
- **Reduced Coupling**: DatabaseManager doesn't define data structures
- **Reusability**: Models can be imported by services without pulling in database operations

### Recommendations:
- Consider consolidating duplicate methods (e.g., `get_source` vs `get_source_by_uuid`)
- Replace legacy ProjectCreationService with ProjectManagementService
- Add comprehensive error handling and logging
- Consider adding transaction support for complex operations
