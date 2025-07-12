# Source Manager Controller Refactoring - Testing Checklist

## Pre-Commit Testing Checklist

This checklist ensures that the controller refactoring maintains all existing functionality before merging back to main.

### 🚀 **Application Startup**
- [√] App starts without errors
- [√] No critical errors in terminal output during startup
- [√] Main window appears with correct layout
- [√] Theme loads correctly (check both light/dark if applicable)
- [√] User greeting displays correctly in header
- [√] Sidebar navigation is visible and functional

### 🧭 **Navigation Testing**
- [√] **Home View**: Navigate to Home from sidebar
- [√] **New Project View**: Navigate to New Project from sidebar
- [√] **Recent Projects View**: Navigate to Recent Projects from sidebar
- [√] **Project View**: Navigate to Project View from sidebar (should redirect appropriately)
- [√] **Sources View**: Navigate to Sources from sidebar
- [√] **Reports View**: Navigate to Reports from sidebar
- [√] **Settings View**: Navigate to Settings from sidebar
- [√] **Help View**: Navigate to Help from sidebar
- [√] Navigation highlighting updates correctly when switching views
- [√] No JavaScript/Python errors during navigation

### 📁 **Project Management (ProjectController)**
- [√] **Browse Directories**: Can navigate through project directory structure
- [√] **Create Project Dialog**: 
  - [√] Click "Add Project" button opens dialog
  - [√] Dialog displays without errors
  - [√] Form fields are populated correctly
  - [√] BE number derivation works (or shows appropriate warning)
  - [√] Can select project type from dropdown
  - [√] Required fields are validated (uses config validation rules)
  - [√] Form fields have proper outlines/borders
  - [√] Real-time validation with visual feedback as user types
  - [√] Invalid fields show red border and error message
  - [√] Dialog can be closed/cancelled
- [√] **Submit New Project**:
  - [√] Form submission works without errors
  - [√] Project file is created in correct location
  - [√] Project opens automatically after creation
  - [√] Navigation switches to project view
- [] **Open Existing Project**:
  - [ ] Can click on existing .json project files
  - [ ] Valid projects open correctly
  - [ ] Empty/corrupt project files show appropriate error messages
  - [ ] Old format projects trigger migration dialog (if applicable)
- [ ] **Project Migration** (if old format files exist):
  - [√] Migration service correctly transforms old format to new format
  - [√] Migration tested on all sample project types (STD, FCR, COM, CRS, GSC, RFS, MIL)
  - [√] All 10 test files migrate successfully (100% success rate)
  - [√] Project metadata generation works with UUIDs and proper structure
  - [√] Facility information correctly derived from filename and site properties
  - [√] Sources transformed from full objects to simplified format
  - [√] Deprecated fields properly removed (initialized, data_path, etc.)
  - [ ] Migration dialog appears for old format files
  - [ ] Can accept or cancel migration
  - [ ] Migration progress dialog shows during process
  - [ ] Success message appears after migration
  - [ ] Migrated project opens correctly

### 📋 **Source Management (SourceController)**
- [ ] **Add Source to On Deck**:
  - [ ] Can add sources to on-deck list
  - [ ] On-deck sources appear in project view
  - [ ] Duplicate additions are handled gracefully
- [ ] **Add Source to Project**:
  - [ ] Can promote sources from on-deck to main project
  - [ ] Sources appear in project sources list
  - [ ] Source is removed from on-deck when promoted
  - [ ] Source ordering is maintained
  - [ ] Proper user notification - toast - that source was added
  - [ ] Drag & Drop functioning as expected.
  - [ ] Can remove forms back to the On Deck list
  - [ ] Can edit source.
  - [ ] A button properly allows previewing the source
  - [ ] Clicking the FAB brings up the add source dialog
- [ ] **Source Dialog Operations**:
  - [ ] Source creation dialog opens
  - [ ] Source editing dialog opens
  - [ ] Form validation works
  - [ ] Source updates save correctly
  - [ ] Dialog close callbacks refresh views appropriately

### 📊 **PowerPoint Integration (PowerPointController)**
- [ ] **File Selection**:
  - [ ] PowerPoint file picker opens
  - [ ] Properly formatted toast for error message
  - [ ] Can select .pptx/.ppt files
  - [ ] File path is stored in project metadata
- [ ] **Slide Processing**:
  - [ ] Slides are extracted from PowerPoint file
  - [ ] Slide data is stored in project metadata
  - [ ] Success message displays with slide count
  - [ ] Error handling for invalid PowerPoint files
- [ ] **Force Reselect**:
  - [ ] Can force reselection of existing PowerPoint file
  - [ ] Existing file is reprocessed correctly

### 🎨 **Theme and UI**
- [ ] **Theme Switching** (in Settings):
  - [ ] Can switch between light/dark themes
  - [ ] Theme changes apply immediately
  - [ ] All views refresh with new theme
  - [ ] Theme preference is saved
- [ ] **Display Name**:
  - [ ] Can change display name in settings
  - [ ] Display name updates in header immediately
  - [ ] Settings view refreshes after name change

### 💾 **Data Persistence**
- [ ] **Project State**:
  - [ ] Project metadata saves correctly
  - [ ] Recent projects list updates when opening projects
  - [ ] Window size/position is remembered (if implemented)
- [ ] **Configuration**:
  - [ ] User settings persist between app restarts
  - [ ] Theme preferences are maintained
  - [ ] Recent projects list is maintained

### 🔍 **Error Handling**
- [ ] **File System Errors**:
  - [ ] Missing files show appropriate error messages
  - [ ] Permission errors are handled gracefully
  - [ ] Invalid project files show helpful error dialogs
- [ ] **Dialog Errors**:
  - [ ] Form validation errors are displayed clearly
  - [ ] Dialog cancellation works without errors
  - [ ] Overlapping dialogs are prevented
- [ ] **Navigation Errors**:
  - [ ] Invalid navigation requests are handled
  - [ ] Missing views show error messages instead of crashing

### 📱 **Responsive Behavior**
- [ ] **Window Resizing**:
  - [ ] App layout adjusts to different window sizes
  - [ ] Sidebar remains functional at smaller sizes
  - [ ] Content areas scroll appropriately
- [ ] **View Refreshing**:
  - [ ] Views refresh correctly when data changes
  - [ ] Cache invalidation works for project-dependent views
  - [ ] No stale data is displayed

### 🧪 **Controller Architecture Verification**
- [ ] **Delegation Working**:
  - [ ] AppController properly delegates to subcontrollers
  - [ ] ProjectController handles project operations
  - [ ] SourceController handles source operations
  - [ ] PowerPointController handles PowerPoint operations
- [ ] **Error Propagation**:
  - [ ] Errors from subcontrollers are handled in main app
  - [ ] Logging works correctly in all controllers
  - [ ] No missing method calls or broken delegation

### 🏗️ **Development Environment**
- [ ] **Clean Startup**:
  - [ ] No import errors in terminal
  - [ ] All required dependencies are available
  - [ ] Python environment is configured correctly
- [ ] **Code Quality**:
  - [ ] No obvious syntax errors in logs
  - [ ] Type hints are working (if using a type checker)
  - [ ] Linting passes (if configured)

---

## 🚨 **Critical Issues to Watch For**

### High Priority Issues:
1. **App won't start** - Check import errors, missing dependencies
2. **Navigation broken** - Core app functionality compromised
3. **Project creation fails** - Primary workflow blocked
4. **Data corruption** - Projects or sources not saving correctly

### Medium Priority Issues:
1. **Dialog parameter errors** - Forms may not work correctly
2. **Missing error handling** - App may crash on edge cases
3. **Theme issues** - UI may be unusable in certain modes
4. **Memory leaks** - Views not properly cached/cleared

### Low Priority Issues:
1. **Minor UI glitches** - Cosmetic issues that don't affect functionality
2. **Logging verbosity** - Too much or too little log output
3. **Performance** - Slight delays that don't break functionality

---

## 📋 **Testing Notes Template**

Use this template to document your testing session:

```
Date: [DATE]
Tester: [NAME]
App Version: Controller Refactoring Branch
Environment: [macOS/Windows/Linux + Python Version]

## Startup Test:
- App started: [✅/❌]
- Errors observed: [NONE/LIST ERRORS]

## Navigation Test:
- All views accessible: [✅/❌]
- Issues found: [DESCRIBE]

## Project Management Test:
- Project creation: [✅/❌]
- Project opening: [✅/❌]
- Issues found: [DESCRIBE]

## Source Management Test:
- Source operations: [✅/❌]
- Issues found: [DESCRIBE]

## PowerPoint Integration Test:
- File picker works: [✅/❌]
- Slide processing: [✅/❌]
- Issues found: [DESCRIBE]

## Overall Assessment:
- Ready for commit: [✅/❌]
- Critical issues found: [LIST]
- Recommended actions: [LIST]
```

---

## 🏁 **Sign-off Criteria**

The refactoring is ready for commit when:

✅ **All High Priority tests pass**  
✅ **No critical functionality is broken**  
✅ **App starts and runs without errors**  
✅ **Core workflows (navigation, project creation, source management) work**  
✅ **Controller delegation is functioning correctly**  

---

*Last Updated: July 11, 2025*  
*Controller Refactoring Phase 2 - Complete*
