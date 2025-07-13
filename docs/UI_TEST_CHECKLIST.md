# Source Manager UI Test Checklist

## Overview
This comprehensive checklist ensures all features of the Source Manager application are functioning correctly after the recent refactoring and admin feature integration.

## Test Environment Setup
- [√] Application starts without errors
- [√] No critical errors in logs during startup
- [√] Window opens with correct size (1400x900)
- [√] Window minimum size constraints work (1000x700)
- [√] Theme and color scheme apply correctly

---

## 🏠 Home View Tests

### Navigation and Layout
- [√] Home view loads successfully
- [√] App bar displays correctly with title "Source Manager"
- [√] Navigation rail shows all expected options
- [√] Theme toggle works (light/dark mode)
- [√] Settings icon is accessible

### Recent Projects Section
- [√] Recent projects section displays
- [√] Shows "No recent projects" if none exist
- [√] Recent projects list populates if projects exist
- [√] Clicking recent project opens it correctly

### Quick Actions
- [√] "New Project" button works
- [√] "Recent Projects" button works
- [√] "Manage Sources" button works
- [√] All buttons navigate to correct views

---

## 📁 Project Management Tests

### New Project Creation
- [√] Navigate to "New Project" view
- [√] File browser displays correctly
- [√] Can navigate through directory structure
- [√] Can select different regions (AMERICAS, ROW, etc.)
- [√] Can drill down to specific project folders
- [√] Can select existing project files
- [√] Folder Search Functionality Works

### Project File Handling
- [ ] **New Format Projects**: Can open migrated project files
- [ ] **Legacy Format Projects**: Shows migration dialog for old format files
- [ ] **Migration Process**: Migration dialog works and converts files correctly
- [ ] **File Validation**: Handles corrupted files gracefully
- [ ] **Error Handling**: Shows appropriate error messages for invalid files

### Project Creation Dialog
- [ ] Project creation dialog opens
- [ ] All form fields are present and functional:
  - [ ] Project Type dropdown
  - [ ] Benjamin field (10-digit validation)
  - [ ] Oscar field
  - [ ] Year field
- [ ] Form validation works correctly
- [ ] Can cancel dialog
- [ ] Can create new project successfully

---

## 📋 Project View Tests

### Project Metadata Tab
- [ ] Project metadata tab loads
- [ ] Three-column layout displays correctly:
  - [ ] **Column 1: Facility Information**
    - [ ] Benjamin field (read-only, auto-filled)
    - [ ] Oscar field (read-only, auto-filled)
    - [ ] Facility Name field (editable)
    - [ ] Facility Surrogate Key field (editable)
  - [ ] **Column 2: Team**
    - [ ] All team member fields present
    - [ ] Fields are editable
    - [ ] Data saves correctly
  - [ ] **Column 3: Project Info**
    - [ ] Project title field (editable)
    - [ ] Project type field (editable)
    - [ ] Requestor field (editable)
    - [ ] Request year field (editable)
    - [ ] Relook checkbox (functional)

### Project Sources Tab
- [ ] Project sources tab loads
- [ ] Sources list displays correctly
- [ ] **Add Source Functionality**:
  - [ ] "Add Source" button works
  - [ ] Source selection dialog opens
  - [ ] Can search/filter sources
  - [ ] Can select source and add to project
  - [ ] Source appears in project sources list
- [ ] **Source Management**:
  - [ ] Sources display in correct order (list position)
  - [ ] Can edit source usage notes
  - [ ] Can remove sources from project
  - [ ] Can reorder sources (drag and drop or buttons)
- [ ] **Source Details**:
  - [ ] Source information displays correctly
  - [ ] Usage notes field works
  - [ ] Source UUID is preserved

### Data Persistence
- [ ] Changes save automatically or on save action
- [ ] Saved data persists after closing/reopening project
- [ ] File format matches expected new format structure

---

## 📚 Sources Management Tests

### Sources View
- [ ] Sources view loads correctly
- [ ] Country/region filter works
- [ ] Source type filter works
- [ ] Search functionality works
- [ ] Sources list displays properly

### Source Creation
- [ ] "Create New Source" button works
- [ ] Source creation dialog opens
- [ ] All source fields are present and functional
- [ ] Form validation works
- [ ] Can save new source successfully
- [ ] New source appears in sources list

### Source Editing
- [ ] Can select source to edit
- [ ] Source editor dialog opens with existing data
- [ ] Can modify source information
- [ ] Changes save correctly
- [ ] Updated source reflects changes in sources list

---

## 🔧 Admin Features Tests

### Admin Access
- [ ] Admin icon appears in app bar
- [ ] Admin login dialog opens when clicked
- [ ] **Authentication**:
  - [ ] Can enter master password (SM_1234_ADMIN17698$)
  - [ ] Correct password grants access
  - [ ] Incorrect password shows error
  - [ ] Can cancel login

### User Management (Admin Only)
- [ ] After admin login, user management panel appears
- [ ] **User List**:
  - [ ] Shows all users in the system
  - [ ] Displays user roles correctly
- [ ] **User Role Management**:
  - [ ] Can toggle admin role for users
  - [ ] Can toggle local saver role for users
  - [ ] Role changes persist
- [ ] **User Deletion**:
  - [ ] Can delete users (with confirmation)
  - [ ] Deleted users removed from system
- [ ] **Admin Config Persistence**:
  - [ ] Admin settings save to admin_config.json
  - [ ] Settings persist between app restarts

---

## 🎨 UI/UX Tests

### Theme and Styling
- [ ] Light theme displays correctly
- [ ] Dark theme displays correctly
- [ ] Theme toggle works smoothly
- [ ] Color scheme is consistent across all views
- [ ] Text is readable in both themes

### Responsive Design
- [ ] App works at minimum window size
- [ ] App works at larger window sizes
- [ ] Controls scale appropriately
- [ ] Text remains readable at different sizes

### Navigation
- [ ] Navigation rail works correctly
- [ ] Active page is highlighted
- [ ] Can navigate between all main views
- [ ] Back navigation works where applicable

### Dialogs and Modals
- [ ] All dialogs open correctly
- [ ] Dialogs are properly centered
- [ ] Can close dialogs with X button
- [ ] Can close dialogs with cancel button
- [ ] Dialog content is properly formatted

---

## 💾 Data Management Tests

### File Operations
- [ ] **Project Files**:
  - [ ] Can save project files
  - [ ] Can load project files
  - [ ] File paths are correct
  - [ ] File format is valid JSON
- [ ] **Source Files**:
  - [ ] Sources save to correct location
  - [ ] Source data format is correct
  - [ ] Can load existing sources

### Migration System
- [ ] **Legacy File Detection**:
  - [ ] App detects old format files
  - [ ] Offers migration when opening old files
- [ ] **Migration Process**:
  - [ ] Migration service converts files correctly
  - [ ] All data is preserved during migration
  - [ ] New format files work with current app
- [ ] **Batch Migration** (if applicable):
  - [ ] Can migrate multiple files at once
  - [ ] Progress is shown during batch migration
  - [ ] All files migrate successfully

### User Configuration
- [ ] User preferences save correctly
- [ ] Theme preference persists
- [ ] Window size/position preferences work
- [ ] Recent projects list updates correctly

---

## 🚨 Error Handling Tests

### Graceful Failures
- [ ] **File Errors**:
  - [ ] Handles missing files gracefully
  - [ ] Shows appropriate error for corrupted files
  - [ ] Recovers from file read/write errors
- [ ] **Network/Permission Errors**:
  - [ ] Handles permission denied errors
  - [ ] Shows helpful error messages
  - [ ] Doesn't crash on file system errors
- [ ] **Data Validation**:
  - [ ] Validates form input correctly
  - [ ] Shows validation errors clearly
  - [ ] Prevents invalid data submission

### Logging
- [ ] Application logs are generated
- [ ] Log files are in correct location
- [ ] Log level is appropriate
- [ ] Error details are captured in logs

---

## 🔄 Integration Tests

### Workflow Tests
- [ ] **Complete Project Workflow**:
  1. [ ] Create new project
  2. [ ] Add project metadata
  3. [ ] Add sources to project
  4. [ ] Edit source usage notes
  5. [ ] Save project
  6. [ ] Close and reopen project
  7. [ ] Verify all data is preserved

- [ ] **Migration Workflow**:
  1. [ ] Open old format project file
  2. [ ] Accept migration prompt
  3. [ ] Verify migration completes successfully
  4. [ ] Verify all data transferred correctly
  5. [ ] Save migrated project
  6. [ ] Reopen to confirm persistence

- [ ] **Admin Workflow**:
  1. [ ] Login as admin
  2. [ ] Create/modify user
  3. [ ] Change user roles
  4. [ ] Logout and login as different user
  5. [ ] Verify role changes took effect

---

## 📊 Performance Tests

### Startup Performance
- [ ] App starts in reasonable time (< 5 seconds)
- [ ] No significant delays in UI rendering
- [ ] Memory usage is reasonable

### Runtime Performance
- [ ] Navigation between views is smooth
- [ ] Large project files load in reasonable time
- [ ] Source filtering/searching is responsive
- [ ] File save operations complete quickly

---

## ✅ Final Verification

### Critical Path Test
- [ ] Can complete entire project creation and management workflow
- [ ] All core features work without errors
- [ ] Data integrity is maintained throughout
- [ ] No critical errors in logs

### Regression Test
- [ ] All previously working features still work
- [ ] New features don't break existing functionality
- [ ] Migration doesn't corrupt existing projects

---

## 📝 Test Results Summary

**Date Tested**: ___________  
**Tester**: ___________  
**App Version**: 2.0.0  
**Branch**: feature/admin (rebased with main)

### Issues Found
- [ ] No issues found ✅
- [ ] Minor issues found (list below)
- [ ] Major issues found (list below)

**Issue Details**:
```
[Record any issues found during testing]
```

### Overall Assessment
- [ ] App is ready for production ✅
- [ ] App needs minor fixes before release
- [ ] App needs major fixes before release

**Additional Notes**:
```
[Any additional observations or recommendations]
```
