# Database Migration Strategy: JSON to SQLite3

## Recommendation: Hybrid Approach with SQLite3 Primary

After analyzing your requirements, I recommend **transitioning to SQLite3 as the primary data store** while maintaining selective JSON usage for specific scenarios.

## Why SQLite3 + Selective JSON?

### ✅ **Move to SQLite3:**
- **Relational data** (Customer, Project, Source relationships)
- **Slide assignments** (source-to-slide mappings)
- **Data analysis capabilities** (queries, reporting, aggregations)
- **Data integrity** (foreign keys, constraints)
- **Performance** (indexed queries, efficient joins)
- **Concurrent access** (multiple users/processes)

### ✅ **Keep JSON for:**
- **Project export/import** (portable format)
- **UI state/preferences** (per-project settings)
- **Temporary working data** (draft states)
- **Backup/archival** (human-readable format)

## Migration Benefits

### 🎯 **Immediate Gains:**
1. **Data Deduplication** - Sources shared across projects
2. **Referential Integrity** - Consistent customer/project relationships
3. **Query Capabilities** - Find all projects by customer, source usage analysis
4. **Scalability** - Handle thousands of projects efficiently
5. **Data Analysis** - Reports on source usage, project metrics

### 📊 **Analytics You Can Now Do:**
- Which sources are used most frequently?
- How many projects does each customer have?
- Which engineers work on which types of projects?
- Source reuse patterns across customers
- Project timeline analysis

## Implementation Plan

### Phase 1: Database Setup
```bash
# 1. Create database with schema
python database_manager.py

# 2. Test with sample data
# (Run the example at the bottom of database_manager.py)
```

### Phase 2: Migration Script
```python
from database_manager import DatabaseManager, JSONMigrator
from pathlib import Path

# Initialize database
db = DatabaseManager("source_manager.db")

# Create migrator
migrator = JSONMigrator(db)

# Migrate existing JSON files
json_directory = Path("your_existing_json_projects")
migrator.migrate_directory(json_directory)
```

### Phase 3: Integration
1. **Update project creation** to use database
2. **Modify source management** to check for existing sources
3. **Update slide assignment** functionality
4. **Keep JSON export** for portability

## File Structure After Migration

```
source_manager_flet/
├── source_manager.db          # Main SQLite database
├── database_manager.py        # Database operations
├── database_schema.sql        # Schema definition
├── exports/                   # JSON exports for sharing
│   ├── project_123.json
│   └── project_456.json
├── attachments/              # Source file storage
│   ├── documents/
│   ├── images/
│   └── pdfs/
└── backups/                  # Database backups
    └── source_manager_backup_2025-06-17.db
```

## Updated Workflow

### Creating a New Project:
1. **Check if customer exists** in database (create if new)
2. **Create project record** with proper customer relationship
3. **Sources can be:**
   - New (add to database)
   - Existing (link to project)
   - Imported (from another project)

### Adding Sources:
1. **Check if source already exists** (by identifier/checksum)
2. **If exists:** Link to current project
3. **If new:** Add to database and link to project
4. **Slide assignments:** Stored in database with source references

### Benefits for PowerPoint/Word Integration:
- **Consistent source data** across all projects
- **Slide assignment tracking** in database
- **Source notes/metadata** easily accessible
- **Bulk operations** (assign multiple sources to slides)

## Data Migration Example

### Before (JSON):
```json
{
  "project_uuid": "abc-123",
  "customer": {"key": "1001", "name": "ACME Corp"},
  "sources": [
    {"uuid": "src-1", "title": "Contract.pdf"},
    {"uuid": "src-2", "title": "Specs.docx"}
  ],
  "slide_assignments": [
    {"source_uuid": "src-1", "slide_number": 5}
  ]
}
```

### After (SQLite + JSON export):
**Database:** Normalized relational data
**JSON Export:** Same format for sharing/backup

## Recommended Next Steps

1. **✅ Review the database schema** (database_schema.sql)
2. **✅ Test the DatabaseManager** with sample data
3. **✅ Run migration on a copy** of your existing JSON files
4. **✅ Update your UI** to use database operations
5. **✅ Keep JSON export** functionality for project sharing

## Code Integration Points

### In your existing services:
```python
# Replace direct JSON operations with database calls
from database_manager import DatabaseManager

db = DatabaseManager()

# Instead of loading project JSON:
project = db.get_project(project_uuid)
sources = db.get_project_sources(project_uuid)
slides = db.get_slide_assignments(project_uuid)

# For slide assignments:
db.assign_source_to_slide(project_id, source_id, slide_number, notes)
```

This hybrid approach gives you the best of both worlds: **powerful relational queries** for analysis and **JSON flexibility** for exports and sharing.
