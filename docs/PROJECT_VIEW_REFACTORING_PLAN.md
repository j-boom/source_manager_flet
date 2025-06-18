# Project View Refactoring Plan

## Current Issue
The `project_view.py` file is 699 lines and contains three distinct tabs:
1. Metadata Tab - Project information editing
2. Sources Tab - Source document management 
3. Slide Assignments Tab - Slide generation and assignments

## Refactoring Strategy

### New File Structure
```
src/views/pages/project_view/
├── __init__.py                 # Main ProjectView class
├── base_project_tab.py         # Base class for all tabs
├── metadata_tab.py            # Metadata editing tab
├── sources_tab.py             # Sources management tab
└── slide_assignments_tab.py   # Slide assignments tab
```

### Implementation Steps

1. **Create base tab class** (`base_project_tab.py`)
   - Abstract base class with common functionality
   - Theme management, database access, project state access
   - Common UI utilities

2. **Extract Metadata Tab** (`metadata_tab.py`)
   - Move all metadata-related methods
   - Form creation, validation, saving
   - Edit mode management

3. **Extract Sources Tab** (`sources_tab.py`) 
   - Source management functionality
   - File scanning, import/export
   - Source assignment to projects

4. **Extract Slide Assignments Tab** (`slide_assignments_tab.py`)
   - Slide creation and management
   - Source-to-slide assignments
   - Report generation

5. **Refactor Main ProjectView** (`__init__.py`)
   - Orchestrate the three tabs
   - Handle tab switching
   - Manage shared state

### Benefits
- **Separation of Concerns**: Each tab handles its own functionality
- **Maintainability**: Smaller, focused files are easier to maintain
- **Testability**: Each tab can be tested independently
- **Team Development**: Multiple developers can work on different tabs

### Estimated Impact
- Main file: 699 lines → ~150 lines
- Each tab: ~150-200 lines
- Base class: ~100 lines
