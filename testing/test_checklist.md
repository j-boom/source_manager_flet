
# Source Manager - In-Depth Test Checklist

This checklist provides a detailed set of test cases to rigorously validate the functionality, usability, and robustness of the Source Manager application.

## I. UI/UX Tests (User Interaction & Experience)

This section focuses on ensuring all visual components behave as expected and the user flow is intuitive and error-free.

### 1. General Application & Windowing

- [ ] **Application Startup**
  - [ ] Does the application launch without any console errors or visible exceptions?
  - [ ] Is the initial view (Home) loaded correctly and promptly?

- [ ] **First-Time Setup**
  - [ ] After deleting user_config.json, does the "First Time Setup" dialog appear automatically on launch?
  - [ ] Does the dialog prevent continuation until a valid data path is selected?
  - [ ] Does clicking "Begin" successfully create the necessary config files and close the dialog?

- [ ] **Window State Persistence**
  - [ ] Resize the window, close the app, and relaunch. Does it open with the previous dimensions?
  - [ ] Move the window, close, and relaunch. Does it open at the last position?

- [ ] **Theme Switching**
  - [ ] Does the theme toggle button in the app bar have a clear icon change (e.g., sun to moon)?
  - [ ] Is the theme change applied instantly to all elements, including text, backgrounds, and controls?
  - [ ] Is the selected theme correctly loaded when the app restarts?

- [ ] **Responsiveness & Layout**
  - [ ] Shrink the window to its minimum possible size. Do all elements remain visible and usable (e.g., via scrolling)?
  - [ ] Expand the window to full screen. Does the layout expand gracefully without excessive whitespace or stretched elements?
  - [ ] Are there any components that overlap or become misaligned during resizing?


### 2. Navigation

- [ ] **Sidebar Navigation**
  - [ ] Does clicking each icon reliably navigate to the correct view?
  - [ ] Is the selected_index visually distinct (highlighted) for the active view?
  - [ ] Is there a tooltip on hover for each navigation icon?

- [ ] **Breadcrumb Navigation**
  - [ ] Is the breadcrumb hidden on top-level views (Home, Settings, etc.)?
  - [ ] When navigating to a project, does it show Home > [Project Name]?
  - [ ] Does clicking "Home" in the breadcrumb navigate back to the home screen?
  - [ ] If navigating deeper (e.g., to a source within a project), does the breadcrumb update accordingly?


### 3. Home View (/)

- [ ] **Recent Projects Section**
  - [ ] Empty State: If no projects have been opened, is a helpful message displayed (e.g., "No recent projects. Create one to get started!")?
  - [ ] Does it correctly display the most recently opened projects, with the latest one first?
  - [ ] Does clicking a "Recent Project" card navigate to the correct project's view?

- [ ] **On Deck Sources Section**
  - [ ] Empty State: If all sources are assigned to projects, is a message like "All sources are organized!" displayed?
  - [ ] Does it correctly show only sources that are not currently part of any project?
  - [ ] Does clicking an "On Deck" card open the Source Editor dialog pre-filled with that source's data?

### 4. Project Creation & Management

- [ ] **Create New Project Dialog**
  - [ ] Can the dialog be opened from both the sidebar and the Floating Action Button (FAB)?
  - [ ] Validation: Is the "Create" button disabled if the project name is empty or just whitespace?
  - [ ] Does it prevent the creation of projects with duplicate names?
  - [ ] Does pressing Enter in the text field trigger the creation?
  - [ ] Does clicking "Cancel" or the background overlay close the dialog without creating a project?

- [ ] **Project View (/project/{project_id})**
  - [ ] **Metadata Tab**
    - [ ] Are all project details (name, type, creation date) displayed accurately?
    - [ ] Does the "Edit Display Name" dialog work, and does the name update on the view immediately?
  - [ ] **Project Sources Tab**
    - [ ] Are source cards displayed correctly, showing key information?
    - [ ] Add Source Dialog: Does the list show all available sources not already in the project?
    - [ ] Remove Source: Does the confirmation dialog appear before removing a source? Does the UI update instantly upon removal?
    - [ ] Drag and Drop: Is the drag-and-drop functionality smooth? Is the new order reflected immediately and persisted?
  - [ ] **Cite Sources Tab**
    - [ ] Are all sources listed with their details?
    - [ ] Does the "Generate Citations" button produce correctly formatted citations for all selected styles?
    - [ ] Does the "Copy to Clipboard" button provide feedback (e.g., a snackbar message) on success?
    - [ ] PowerPoint Export: Does the feature generate a .pptx file? Does the file contain the citations as expected?


### 5. Source Library (/sources)

- [ ] **View All Sources**
  - [ ] Is a list of all sources displayed, regardless of project assignment?
  - [ ] Is there a search or filter functionality? Does it work correctly?

- [ ] **Create/Edit Source Dialog**
  - [ ] Does the form dynamically update to show the correct fields when the "Source Type" dropdown is changed?
  - [ ] Validation: Are required fields for each source type marked and validated?
  - [ ] When editing, are all fields pre-populated with the correct existing data?

- [ ] **Delete Source**
  - [ ] Does a confirmation dialog appear before permanent deletion?
  - [ ] Upon deletion, is the source removed from this view and any projects it was part of?

### 6. Settings View (/settings)

- [ ] **Data Path Selection**
  - [ ] Is the current data path displayed correctly?
  - [ ] Does clicking "Change" open the system's file/directory picker?
  - [ ] Does the app handle the case where a user cancels the directory selection?
  - [ ] Does the app correctly prompt for a restart after a successful path change?

## II. Data & Persistence Tests

This section focuses on verifying that data is correctly created, read, updated, and deleted in the underlying JSON files.

### 1. user_config.json

- [ ] Initial Creation: Is the file created with all default keys (data_path, theme_mode, window_size, recent_projects) on first run?
- [ ] Theme Persistence: Is the theme_mode value correctly written as "light" or "dark"?
- [ ] **Recent Projects**
  - [ ] Is the recent_projects list updated with the correct project ID at the beginning of the list when a project is opened?
  - [ ] Does the list correctly handle duplicates by moving the existing ID to the front?
- [ ] **File Corruption**
  - [ ] Delete a key from the JSON. Does the app recreate it with a default value on next launch?
  - [ ] Enter invalid JSON. Does the app handle the parsing error gracefully and reset the file?

### 2. projects.json

- [ ] Project Creation: Is a new entry with a valid uuid, name, type, and empty sources array added?
- [ ] Project Update: When a project's name is edited, is only the name field for that project's entry updated?
- [ ] **Source Association**
  - [ ] When sources are added/removed/reordered, is the sources array of IDs updated correctly and in the right order?
- [ ] **Data Integrity**
  - [ ] Manually add a non-existent source ID to a project's sources array. Does the app handle this gracefully without crashing?

### 3. sources.json

- [ ] Source Creation: Is a new entry with a unique uuid and all the correct fields for its source_type added?
- [ ] Source Update: Are edits to a source reflected correctly in its corresponding JSON object?
- [ ] Source Deletion: Is the entire object for the deleted source removed from the JSON array?
- [ ] **Data Integrity**
  - [ ] If a source is deleted, is it also removed from the sources array of any project in projects.json?