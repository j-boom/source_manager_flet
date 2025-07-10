# Source Manager UI Testing Protocol

## Overview
This document provides a comprehensive testing protocol for the Source Manager Flet application to ensure all features work correctly before shipping.

## Pre-Testing Setup

### Environment Preparation
- [ ] Clean test environment with no existing projects
- [ ] Verify all required dependencies are installed
- [ ] Check that `data/` directory structure exists
- [ ] Backup any existing user data
- [ ] Test with both light and dark themes
- [ ] Test on target screen resolutions (minimum 800x600)

### Test Data Preparation
- [ ] Create test master sources in different regions
- [ ] Prepare sample project folders in different locations
- [ ] Have test project metadata ready

---

## 1. Application Startup & First Run

### Initial Launch
- [ ] Application starts without errors
- [ ] Window opens with correct dimensions (1200x800)
- [ ] First-time setup dialog appears (if new user)
- [ ] User can set display name successfully
- [ ] Theme selection works (light/dark)
- [ ] Application navigates to home page after setup

### Error Handling
- [ ] App handles missing data directories gracefully
- [ ] App handles corrupted config files
- [ ] App displays appropriate error messages

---

## 2. Navigation & Layout Testing

### Main Navigation (Sidebar)
- [ ] Home button navigates to home view
- [ ] Project button navigates to project browser
- [ ] Sources button navigates to sources view
- [ ] Reports button navigates to reports view
- [ ] Navigation rail highlights current page correctly
- [ ] Navigation works with keyboard (Tab, Enter)

### App Bar
- [ ] App title displays correctly
- [ ] Settings button opens settings dialog
- [ ] Help button opens help view
- [ ] User greeting displays correctly
- [ ] Theme toggle works (if available)

### Window Management
- [ ] Window resizes properly (minimum 800x600)
- [ ] Window maximizes/minimizes correctly
- [ ] Window position is remembered between sessions
- [ ] Application responds to window events

---

## 3. Home View Testing

### Home Page Elements
- [ ] Welcome message displays user's name
- [ ] Recent projects section shows correct projects
- [ ] Quick actions are available and functional
- [ ] Navigation buttons work correctly

### Recent Projects
- [ ] Recent projects list loads correctly
- [ ] Projects display with correct titles and paths
- [ ] Clicking a project opens it successfully
- [ ] Non-existent projects are removed from list
- [ ] Recent projects limit is respected

---

## 4. Project Browser (New Project View) Testing

### Folder Navigation
- [ ] Primary folder dropdown populates correctly
- [ ] Selecting primary folder shows 4-digit folders
- [ ] Clicking 4-digit folder shows 10-digit folders
- [ ] Breadcrumb navigation works correctly
- [ ] Search functionality works for folder names
- [ ] Search clears after submission

### Project Browser Actions
- [ ] "Add Project" button appears in correct contexts
- [ ] "Create New Folder" button appears when appropriate
- [ ] Folder creation dialog opens correctly
- [ ] Project creation dialog opens correctly
- [ ] Navigation back to home works

### Error Handling
- [ ] Handles missing directories gracefully
- [ ] Shows "No results found" when appropriate
- [ ] Handles search with no results
- [ ] Validates folder permissions

---

## 5. Project Creation Dialog Testing

### Dialog Behavior
- [ ] Dialog opens with correct dimensions
- [ ] Dialog is modal and blocks interaction with main window
- [ ] Dialog can be closed with Cancel button
- [ ] Dialog can be closed with X button
- [ ] Dialog validates required fields

### Form Fields
- [ ] Project type dropdown shows all available types
- [ ] Form fields update based on project type selection
- [ ] BE Number field accepts correct format
- [ ] Facility name field works correctly
- [ ] All required fields are marked appropriately
- [ ] Field validation provides clear error messages

### Project Creation
- [ ] Creates project file in correct location
- [ ] Generates correct filename format
- [ ] Saves all form data to project file
- [ ] Opens newly created project after creation
- [ ] Handles duplicate project names appropriately

---

## 6. Project View Testing

### Project Loading
- [ ] Project loads and displays correct title
- [ ] Project type displays correctly
- [ ] Navigation back to project browser works
- [ ] Project metadata loads correctly

### Project Metadata Tab
- [ ] Displays all project metadata fields
- [ ] Fields can be edited when in edit mode
- [ ] Changes can be saved successfully
- [ ] Changes can be cancelled
- [ ] Field validation works correctly
- [ ] Required fields are properly marked

### Project Sources Tab
- [ ] Displays list of project sources
- [ ] Sources display with correct titles and types
- [ ] "Add Source" button works correctly
- [ ] Source removal works correctly
- [ ] Source reordering works (if implemented)
- [ ] On-deck sources display correctly

### Cite Sources Tab (if implemented)
- [ ] Tab loads without errors
- [ ] Displays sources available for citation
- [ ] Source grouping functionality works
- [ ] Citation export works correctly

---

## 7. Source Management Testing

### Source Creation Dialog
- [ ] Dialog opens from project sources tab
- [ ] All source type options are available
- [ ] Form fields adapt to source type
- [ ] Required fields are validated
- [ ] Source creation saves to correct regional file
- [ ] Dialog closes after successful creation

### Source Editor Dialog
- [ ] Opens when editing existing source
- [ ] Pre-populates with existing source data
- [ ] Allows editing of all fields
- [ ] Saves changes to master source file
- [ ] Updates all projects using the source

### Source Operations
- [ ] Adding source to project works correctly
- [ ] Removing source from project works correctly
- [ ] Source search/filter works correctly
- [ ] Regional source files are maintained correctly

---

## 8. Settings & Configuration Testing

### Settings Dialog
- [ ] Opens from app bar settings button
- [ ] Display name can be changed
- [ ] Theme selection works
- [ ] Window settings are saved
- [ ] Settings persist between sessions

### User Configuration
- [ ] User config file is created correctly
- [ ] Recent projects are tracked properly
- [ ] Settings changes are saved immediately
- [ ] Invalid settings are handled gracefully

---

## 9. Reports & Export Testing

### Reports View
- [ ] Displays available reports
- [ ] Bibliography generation works
- [ ] Export options are functional
- [ ] Report previews work correctly

### Export Functions
- [ ] PDF export works (if implemented)
- [ ] Word export works (if implemented)
- [ ] Text export works (if implemented)
- [ ] Citations format correctly

---

## 10. Data Integrity Testing

### File Operations
- [ ] Project files are saved correctly
- [ ] Source files are updated properly
- [ ] Backup files are created when appropriate
- [ ] File corruption is handled gracefully

### Data Validation
- [ ] Invalid JSON files are handled properly
- [ ] Missing source references are handled
- [ ] Circular references are prevented
- [ ] Data migrations work correctly

---

## 11. Error Handling & Edge Cases

### File System Errors
- [ ] Handles read-only directories
- [ ] Handles file permission errors
- [ ] Handles disk space issues
- [ ] Handles network drive disconnections

### User Input Validation
- [ ] Handles empty required fields
- [ ] Handles invalid characters in filenames
- [ ] Handles extremely long input values
- [ ] Handles special characters appropriately

### Application State
- [ ] Handles missing project files gracefully
- [ ] Recovers from corrupted user config
- [ ] Handles concurrent access issues
- [ ] Maintains state during navigation

---

## 12. Performance Testing

### Load Testing
- [ ] Application starts quickly (< 5 seconds)
- [ ] Large project lists load efficiently
- [ ] Many sources load without lag
- [ ] File operations complete reasonably quickly

### Memory Usage
- [ ] Application memory usage is reasonable
- [ ] No memory leaks during extended use
- [ ] Large datasets don't cause crashes
- [ ] File handles are properly closed

---

## 13. Accessibility Testing

### Keyboard Navigation
- [ ] All functions accessible via keyboard
- [ ] Tab order is logical
- [ ] Keyboard shortcuts work correctly
- [ ] Focus indicators are visible

### Screen Reader Support
- [ ] UI elements have appropriate labels
- [ ] Error messages are announced
- [ ] Dynamic content updates are announced
- [ ] Form field labels are properly associated

---

## 14. Platform-Specific Testing

### macOS Testing
- [ ] Application follows macOS design guidelines
- [ ] Menu bar integration works correctly
- [ ] Window controls work properly
- [ ] File system integration works

### Cross-Platform Considerations
- [ ] File paths work correctly across platforms
- [ ] Unicode handling is consistent
- [ ] Line endings are handled properly
- [ ] Font rendering is consistent

---

## Debugging Checklist

### When Things Go Wrong
1. **Check the logs** - Look in `logs/` directory for error messages
2. **Verify file permissions** - Ensure app can read/write to data directories
3. **Check user config** - Verify `data/user_data/users/[username].json` is valid
4. **Test with clean data** - Try with empty data directories
5. **Verify dependencies** - Ensure all required packages are installed
6. **Check project files** - Verify JSON files are valid
7. **Test in isolation** - Try reproducing issue with minimal data
8. **Check network connectivity** - If using remote resources
9. **Verify theme files** - Ensure theme resources are available
10. **Test with different users** - Check if issue is user-specific

### Common Issues & Solutions
- **App won't start**: Check Python version, dependencies, file permissions
- **Navigation doesn't work**: Check controller routing, view registration
- **Projects won't load**: Verify JSON format, file paths, permissions
- **Sources don't display**: Check regional source files, data service
- **UI elements missing**: Check theme files, CSS resources
- **Performance issues**: Check data size, file operations, memory usage

---

## Testing Sign-Off

### Pre-Release Checklist
- [ ] All critical features tested and working
- [ ] No high-severity bugs remain
- [ ] Performance meets requirements
- [ ] User experience is smooth and intuitive
- [ ] Documentation is complete and accurate
- [ ] Error handling is comprehensive
- [ ] Data integrity is maintained
- [ ] Security considerations addressed

### Final Verification
- [ ] Test with fresh installation
- [ ] Test with sample data
- [ ] Test with production-like data
- [ ] Test with multiple users
- [ ] Test with concurrent usage
- [ ] Test with edge cases
- [ ] Test with malformed data
- [ ] Test with system stress

**Tested By:** _________________  
**Date:** _________________  
**Version:** _________________  
**Environment:** _________________  
**Notes:** _________________

---

## Automated Testing Notes

Consider implementing automated tests for:
- Unit tests for data models
- Integration tests for service layers
- UI automation tests for critical workflows
- Performance regression tests
- Data integrity tests

This protocol should be executed before each release to ensure quality and reliability.
