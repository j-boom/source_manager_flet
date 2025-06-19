"""
Dynamic Database Schema Generator
Creates database tables based on project type configurations
"""

import sqlite3
from typing import Dict, List, Optional, Any
from config.project_types_config import (
    ProjectTypeConfig, FieldConfig, FieldType,
    PROJECT_TYPES_CONFIG, get_project_type_config
)


class DatabaseSchemaGenerator:
    """Generates database schemas dynamically based on project type configurations"""
    
    # Map field types to SQL types
    SQL_TYPE_MAPPING = {
        FieldType.TEXT: "TEXT",
        FieldType.TEXTAREA: "TEXT",
        FieldType.DROPDOWN: "TEXT",
        FieldType.NUMBER: "REAL",
        FieldType.DATE: "DATE",
        FieldType.BOOLEAN: "BOOLEAN"
    }
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def generate_base_schema(self) -> str:
        """Generate the base schema with common tables"""
        schema = """
-- SQLite3 Database Schema for Source Manager
-- Migration from JSON to relational structure with dynamic project type tables

-- Customers table (unchanged)
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,           -- Facility Number (10-digit folder number)
    number TEXT NOT NULL,               -- Building Number (pattern: [A-Z]{2}\\d{3})
    suffix TEXT,                        -- Customer suffix
    name TEXT NOT NULL,                 -- Facility Name
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Base projects table (for common project data)
CREATE TABLE IF NOT EXISTS projects_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT UNIQUE NOT NULL,          -- Project UUID
    customer_id INTEGER NOT NULL,       -- Foreign key to customers
    project_type TEXT NOT NULL,         -- Project type (CCR, GSC, etc.)
    status TEXT DEFAULT 'active',      -- Project status
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- Sources table (unchanged)
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT UNIQUE NOT NULL,          -- Source UUID
    title TEXT NOT NULL,                -- Source title
    originator TEXT,                    -- Source originator
    identifier TEXT,                    -- Source identifier
    url TEXT,                           -- Source URL
    date_created DATE,                  -- Source date
    content_type TEXT,                  -- Type: pdf, image, document, etc.
    file_path TEXT,                     -- Path to actual file
    file_size INTEGER,                  -- File size in bytes
    checksum TEXT,                      -- File checksum for integrity
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Project sources relationship table (unchanged)
CREATE TABLE IF NOT EXISTS project_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_uuid TEXT NOT NULL,
    source_uuid TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_uuid) REFERENCES projects_base(uuid) ON DELETE CASCADE,
    FOREIGN KEY (source_uuid) REFERENCES sources(uuid) ON DELETE CASCADE,
    UNIQUE(project_uuid, source_uuid)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_customers_key ON customers(key);
CREATE INDEX IF NOT EXISTS idx_projects_base_uuid ON projects_base(uuid);
CREATE INDEX IF NOT EXISTS idx_projects_base_customer_id ON projects_base(customer_id);
CREATE INDEX IF NOT EXISTS idx_projects_base_type ON projects_base(project_type);
CREATE INDEX IF NOT EXISTS idx_sources_uuid ON sources(uuid);
CREATE INDEX IF NOT EXISTS idx_project_sources_project ON project_sources(project_uuid);
CREATE INDEX IF NOT EXISTS idx_project_sources_source ON project_sources(source_uuid);

"""
        return schema
    
    def generate_project_type_table_sql(self, project_type: str) -> str:
        """Generate SQL for a specific project type table"""
        config = get_project_type_config(project_type)
        if not config:
            return ""
        
        table_name = config.table_name
        
        # Start with base columns
        columns = [
            "id INTEGER PRIMARY KEY AUTOINCREMENT",
            "project_base_id INTEGER NOT NULL",
            "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ]
        
        # Add columns for each field in the configuration
        for field_config in config.fields:
            sql_type = self.SQL_TYPE_MAPPING.get(field_config.field_type, "TEXT")
            
            # Determine if field should be NOT NULL
            not_null = "NOT NULL" if field_config.required else ""
            
            column_def = f"{field_config.name} {sql_type} {not_null}".strip()
            columns.append(column_def)
        
        # Add foreign key constraint
        columns.append("FOREIGN KEY (project_base_id) REFERENCES projects_base(id) ON DELETE CASCADE")
        
        # Create the table SQL
        sql = f"""
-- {config.display_name} projects table
CREATE TABLE IF NOT EXISTS {table_name} (
    {',\\n    '.join(columns)}
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_{table_name}_project_base_id ON {table_name}(project_base_id);
"""
        
        return sql
    
    def generate_full_schema(self) -> str:
        """Generate the complete schema with all project type tables"""
        schema_parts = [self.generate_base_schema()]
        
        # Add table for each project type
        for project_type in PROJECT_TYPES_CONFIG.keys():
            table_sql = self.generate_project_type_table_sql(project_type)
            if table_sql:
                schema_parts.append(table_sql)
        
        return "\\n".join(schema_parts)
    
    def create_database(self) -> bool:
        """Create the database with all tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                schema = self.generate_full_schema()
                conn.executescript(schema)
                conn.commit()
                return True
        except Exception as e:
            print(f"Error creating database: {e}")
            return False
    
    def add_project_type_table(self, project_type: str) -> bool:
        """Add a table for a new project type"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                table_sql = self.generate_project_type_table_sql(project_type)
                if table_sql:
                    conn.executescript(table_sql)
                    conn.commit()
                    return True
                return False
        except Exception as e:
            print(f"Error adding project type table: {e}")
            return False
    
    def get_table_columns(self, table_name: str) -> List[str]:
        """Get column names for a table"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [row[1] for row in cursor.fetchall()]
                return columns
        except Exception as e:
            print(f"Error getting table columns: {e}")
            return []
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name=?
                """, (table_name,))
                return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error checking table existence: {e}")
            return False
    
    def migrate_existing_data(self) -> bool:
        """Migrate data from old schema to new schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if old projects table exists
                if not self.table_exists("projects"):
                    return True  # No migration needed
                
                # Migrate projects data to projects_base and project type tables
                cursor.execute("""
                    SELECT id, uuid, customer_id, project_type, engineer, drafter, 
                           reviewer, architect, geologist, project_code, title, 
                           description, status, created_at, updated_at
                    FROM projects
                """)
                
                projects = cursor.fetchall()
                
                for project in projects:
                    (old_id, uuid, customer_id, project_type, engineer, drafter,
                     reviewer, architect, geologist, project_code, title,
                     description, status, created_at, updated_at) = project
                    
                    # Insert into projects_base
                    cursor.execute("""
                        INSERT OR REPLACE INTO projects_base 
                        (uuid, customer_id, project_type, status, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (uuid, customer_id, project_type, status, created_at, updated_at))
                    
                    base_id = cursor.lastrowid
                    
                    # Insert into appropriate project type table
                    config = get_project_type_config(project_type)
                    if config:
                        # Prepare data for project type table
                        type_data = {
                            'project_base_id': base_id,
                            'facility_number': '',  # Would need to derive from customer
                            'facility_name': '',    # Would need to derive from customer
                            'building_number': '',  # Would need to derive from customer
                            'project_title': title or '',
                            'project_description': description or '',
                            'engineer': engineer or '',
                            'drafter': drafter or '',
                            'reviewer': reviewer or '',
                            'architect': architect or '',
                            'geologist': geologist or '',
                        }
                        
                        # Insert into project type table
                        self._insert_project_type_data(cursor, config.table_name, type_data)
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error migrating data: {e}")
            return False
    
    def _insert_project_type_data(self, cursor: sqlite3.Cursor, table_name: str, data: Dict[str, Any]):
        """Insert data into a project type table"""
        # Get existing columns for the table
        columns = self.get_table_columns(table_name)
        
        # Filter data to only include existing columns
        filtered_data = {k: v for k, v in data.items() if k in columns}
        
        if filtered_data:
            column_names = list(filtered_data.keys())
            placeholders = ', '.join(['?' for _ in column_names])
            column_list = ', '.join(column_names)
            
            sql = f"INSERT INTO {table_name} ({column_list}) VALUES ({placeholders})"
            cursor.execute(sql, list(filtered_data.values()))
