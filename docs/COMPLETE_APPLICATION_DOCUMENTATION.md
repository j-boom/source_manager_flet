# Source Manager - Complete Application Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Data Models](#data-models)
5. [Configuration System](#configuration-system)
6. [User Interface](#user-interface)
7. [Services](#services)
8. [Project Structure](#project-structure)
9. [Running the Application](#running-the-application)
10. [Development Guide](#development-guide)

## Overview

Source Manager is a comprehensive desktop application built with Python and Flet for managing project sources, citations, and generating reports. The application provides a modern, intuitive interface for organizing research materials, tracking citations, and creating bibliographies.

### Key Features
- **Project Management**: Create and manage multiple projects with metadata
- **Source Organization**: Import, categorize, and manage source materials
- **Citation Tracking**: Link sources to specific slides/sections
- **Report Generation**: Generate bibliographies and export citations
- **User Personalization**: Customizable themes and user preferences
- **Multi-format Support**: Handle various source types (FCR, STD, GSC, CRS)

### Technology Stack
- **Frontend**: Flet (Python-based UI framework)
- **Backend**: Python 3.12+
- **Data Storage**: JSON files with dataclass serialization
- **Configuration**: YAML-like Python configuration files
- **Logging**: Structured logging with configurable levels

## Architecture

### Application Architecture Pattern
The application follows a **Model-View-Controller (MVC)** pattern with additional service layers:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Views       │    │   Controllers   │    │     Models      │
│  (UI Components)│◄──►│ (App Controller)│◄──►│ (Data Managers) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         │              │    Services     │              │
         └─────────────►│(Business Logic) │◄─────────────┘
                        └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │ Configuration   │
                        │  & Data Models  │
                        └─────────────────┘
```

### Key Architectural Principles
1. **Separation of Concerns**: Clear boundaries between UI, business logic, and data
2. **Dependency Injection**: Managers and services are injected into views
3. **Event-Driven**: Navigation and state changes through callbacks
4. **Modular Design**: Components can be developed and tested independently
5. **Configuration-Driven**: Behavior controlled through configuration files

## Core Components

### 1. Application Controller (`src/controllers/app_controller.py`)
The central orchestrator that manages all application components.

**Responsibilities:**
- Initialize all managers (User, Theme, Window, Navigation, Settings)
- Handle navigation between views
- Manage view lifecycle and state
- Coordinate callbacks between components
- Handle project loading and state management

**Key Methods:**
```python
def __init__(self, page: ft.Page)          # Initialize application
def _handle_navigation(self, page_name)    # Route navigation requests
def _handle_project_selected(self, path)   # Load selected projects
def run(self)                              # Start the application
def cleanup(self)                          # Clean up before exit
```

### 2. Main View (`src/views/main_view.py`)
The primary UI container that houses the application shell.

**Components:**
- **App Bar**: Title, user greeting, settings/help buttons
- **Navigation Rail**: Sidebar with Home, Projects, Sources, Reports
- **Content Area**: Dynamic container for current view
- **Theme Integration**: Applies current color scheme

### 3. Manager Classes (`src/models/`)
Specialized managers handle different aspects of application state:

#### User Config Manager
- Manages user preferences and settings
- Handles display name, recent projects, window state
- Provides personalized greetings
- Persists configuration to JSON

#### Theme Manager  
- Manages light/dark mode and color schemes
- Provides color data for UI components
- Supports 7 color themes (blue, red, orange, green, yellow, purple, indigo)

#### Window Manager
- Handles window positioning, sizing, and state
- Restores previous window configuration
- Manages min/max window constraints

#### Navigation Manager
- Tracks current page and navigation history
- Provides page-to-index mapping
- Manages navigation callbacks

#### Settings Manager
- Coordinates all settings-related functionality
- Provides settings UI dialogs
- Handles theme and display name changes

## Data Models

### Core Data Structures
All data models are implemented as dataclasses with JSON serialization support:

#### ProjectData
```python
@dataclass
class ProjectData:
    uuid: str
    project_type: ProjectType
    created_date: str
    metadata: ProjectMetadata
    title: str
    document_title: Optional[str]
    description: Optional[str]
    sources: List[ProjectSource]
    citations: Optional[List[SlideCitations]]
```

#### UserConfig
```python
@dataclass
class UserConfig:
    window: WindowConfig
    theme: ThemeConfig
    last_page: str
    recent_sites: List[RecentSite]
    display_name: Optional[str]
    setup_completed: bool
```

#### ProjectSource
```python
@dataclass
class ProjectSource:
    source_id: str
    usage_notes: str
    user_description: str
    date_of_information: str
```

### Data Persistence
- **Format**: JSON with UTF-8 encoding
- **Serialization**: Automatic via dataclass `asdict()` and `from_dict()` methods
- **Location**: `data/user_data/users/{username}.json`
- **Backup**: Previous versions maintained for recovery

## Configuration System

### Configuration Files (`config/`)

#### App Config (`app_config.py`)
- Application constants and paths
- Default window dimensions and constraints
- File system paths and directories
- Version information

#### Project Types Config (`project_types_config.py`)
Defines available project types and their metadata:
```python
PROJECT_TYPES = {
    ProjectType.FCR: "Financial/Compliance Report",
    ProjectType.STD: "Standard Document", 
    ProjectType.GSC: "General Source Collection",
    ProjectType.CRS: "Compliance/Regulatory Study",
    ProjectType.OTH: "Other Project Type"
}
```

#### Source Types Config (`source_types_config.py`)
- Source categorization and validation
- Regional source mappings
- Source file management utilities

#### Logging Config (`logging_config.py`)
- Structured logging configuration
- File and console output
- Log level management
- Rotation and archival

## User Interface

### View Hierarchy
```
MainView (Application Shell)
├── HomeView (Landing page with quick actions)
├── NewProjectView (Project creation and browsing)
├── ProjectView (Tabbed project interface)
│   ├── ProjectMetadataTab (Project details and editing)
│   ├── ProjectSourcesTab (Source management)
│   └── CiteSourcesTab (Citation management)
├── SourcesView (Source library and on-deck management)
├── ReportsView (Bibliography and export tools)
└── RecentProjectsView (Recently accessed projects)
```

### Base View Pattern
All views inherit from `BaseView` which provides:
- Consistent initialization pattern
- Loading states and error handling
- Empty state displays
- Theme-aware styling
- Content refresh capabilities

### Dialog System
Specialized dialogs for common operations:
- **FirstTimeSetupDialog**: Initial user onboarding
- **ProjectCreationDialog**: New project creation wizard
- **FolderCreationDialog**: Directory structure creation
- **EditDisplayNameDialog**: User personalization

### Component Factory Pattern
The `SourceUIFactory` creates standardized UI components:
- Source item cards with consistent styling
- Action buttons with theme integration
- Status indicators and badges
- Responsive layout components

## Services

### Directory Service (`src/services/directory_service.py`)
Handles file system operations and project discovery:
- Scans for existing projects
- Manages directory structures
- Validates project folder patterns
- Provides file system utilities

**Key Features:**
- Pattern matching for 4-digit and 10-digit folders
- Recursive project discovery
- Path validation and sanitization
- Directory creation with proper permissions

### Project Creation Service (`src/services/project_creation_service.py`)
Manages the creation of new projects:
- Generates unique project UUIDs
- Creates project JSON files with proper structure
- Sets up directory hierarchies
- Validates project metadata

**Project Creation Flow:**
1. Validate project parameters
2. Generate unique identifier
3. Create directory structure
4. Initialize project JSON file
5. Update recent projects list

## Project Structure

### Root Directory
```
source_manager_flet/
├── requirements.txt           # Python dependencies
├── .gitignore                # Git ignore patterns
├── config/                   # Configuration modules
├── src/                      # Application source code
├── data/                     # Application data storage
└── docs/                     # Documentation
```

### Source Code Structure (`src/`)
```
src/
├── __init__.py              # Package initialization
├── main.py                  # Application entry point
├── controllers/             # Application controllers
│   ├── __init__.py
│   └── app_controller.py    # Main application controller
├── models/                  # Data managers
│   ├── __init__.py
│   ├── user_config.py       # User configuration management
│   ├── theme_manager.py     # Theme and styling
│   ├── window_manager.py    # Window state management
│   ├── navigation_manager.py # Navigation handling
│   └── settings_manager.py  # Settings coordination
├── services/                # Business logic services
│   ├── __init__.py
│   ├── directory_service.py # File system operations
│   └── project_creation_service.py # Project creation
└── views/                   # User interface components
    ├── __init__.py
    ├── main_view.py         # Application shell
    ├── base_view.py         # Base view class
    ├── components/          # Reusable UI components
    │   ├── source_ui_factory.py # Component factory
    │   ├── dialogs/         # Modal dialogs
    │   └── forms/           # Form components
    └── pages/               # Main application views
        ├── home_view.py
        ├── sources_view.py
        ├── reports_view.py
        ├── recent_projects_view.py
        ├── new_project_view/
        │   ├── __init__.py
        │   └── new_project_view.py
        └── project_view/
            ├── __init__.py
            ├── project_view.py
            └── tabs/
                ├── __init__.py
                ├── project_metadata.py
                ├── project_sources.py
                └── cite_sources.py
```

### Configuration Structure (`config/`)
```
config/
├── __init__.py              # Configuration package exports
├── app_config.py            # Application constants
├── data_models.py           # Data structure definitions
├── enums.py                 # Enumeration types
├── logging_config.py        # Logging configuration
├── project_types_config.py  # Project type definitions
├── regional_sources_config.py # Regional source mapping
└── source_types_config.py   # Source type definitions
```

### Data Structure (`data/`)
```
data/
├── __init__.py
├── user_data/
│   └── users/
│       └── {username}.json  # User configuration files
└── Directory_Source_Citations/
    └── {region}/
        └── {customer_id}/
            └── {project_folder}/
                └── {project_file}.json
```

## Running the Application

### Prerequisites
- Python 3.12 or higher
- Flet 0.21.0 or higher
- Operating System: macOS, Windows, or Linux

### Installation
```bash
# Clone the repository
git clone <repository_url>
cd source_manager_flet

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Standard method (from project root)
flet run

# Alternative method
cd src
python main.py
```

### First-Time Setup
On first launch, the application will:
1. Display a welcome dialog for user personalization
2. Create necessary data directories
3. Initialize user configuration
4. Set default theme and window preferences

## Development Guide

### Adding New Views
1. Create view class inheriting from `BaseView`
2. Implement required `build()` method
3. Add to `app_controller.py` views dictionary
4. Update navigation mapping in `navigation_manager.py`

### Adding New Data Models
1. Define dataclass in `config/data_models.py`
2. Include `to_dict()` and `from_dict()` methods
3. Add to configuration exports in `config/__init__.py`
4. Update serialization tests

### Extending Configuration
1. Add new configuration values to appropriate config file
2. Update `__all__` exports in `config/__init__.py`
3. Document configuration options
4. Provide sensible defaults

### Theme Development
1. Define color scheme in `theme_manager.py`
2. Add to available colors list
3. Test with both light and dark modes
4. Ensure accessibility compliance

### Service Development
1. Create service class in `src/services/`
2. Follow dependency injection pattern
3. Add to services `__init__.py` exports
4. Write comprehensive tests

### Best Practices
- **Type Hints**: Use typing annotations throughout
- **Documentation**: Add docstrings to all public methods
- **Error Handling**: Implement graceful error recovery
- **Logging**: Use structured logging for debugging
- **Testing**: Write unit tests for business logic
- **Performance**: Profile and optimize data operations

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Keep functions focused and concise
- Group related functionality in classes
- Use dataclasses for data structures

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all `__init__.py` files are present
2. **Path Issues**: Check that project root is in Python path
3. **Config Errors**: Verify configuration file syntax
4. **Data Corruption**: Check JSON file validity
5. **Theme Issues**: Ensure color values are valid

### Debugging
- Enable debug logging in `logging_config.py`
- Use print statements for immediate debugging
- Check data directory permissions
- Validate JSON file structure

### Performance Optimization
- Profile view rendering times
- Optimize large data set handling
- Implement lazy loading for complex views
- Cache frequently accessed data

---

*This documentation was generated on July 1, 2025. For the most current information, please refer to the source code and inline documentation.*
