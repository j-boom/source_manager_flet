"""
Database Manager for Source Manager Application
Handles SQLite3 database operations and migration from JSON
"""

import sqlite3
import json
import uuid
import sys
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime
import hashlib

# Add project root to path for config imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config import DEFAULT_DATABASE, DATABASE_SCHEMA, USER_DATA_DIR


@dataclass
class Customer:
    key: str
    number: str
    suffix: Optional[str]
    name: str
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class Project:
    uuid: str
    customer_id: int
    engineer: Optional[str] = None
    drafter: Optional[str] = None
    reviewer: Optional[str] = None
    architect: Optional[str] = None
    project_code: Optional[str] = None
    project_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: str = 'active'
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class Source:
    uuid: str
    title: str
    originator: Optional[str] = None
    identifier: Optional[str] = None
    url: Optional[str] = None
    date_created: Optional[str] = None
    content_type: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    checksum: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class ProjectSource:
    project_id: int
    source_id: int
    assignment_order: Optional[int] = None
    notes: Optional[str] = None
    id: Optional[int] = None


@dataclass
class SlideAssignment:
    project_id: int
    source_id: int
    slide_number: int
    slide_title: Optional[str] = None
    notes: Optional[str] = None
    id: Optional[int] = None


class DatabaseManager:
    """Manages SQLite database operations for the source manager"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(DEFAULT_DATABASE)
        self.connection: Optional[sqlite3.Connection] = None
        self._init_database()
    
    def _init_database(self):
        """Initialize database with schema"""
        self.connect()
        
        # Read and execute schema
        schema_path = DATABASE_SCHEMA
        if schema_path.exists():
            with open(schema_path, 'r') as f:
                schema = f.read()
            if self.connection:
                self.connection.executescript(schema)
                self.connection.commit()
    
    def connect(self) -> sqlite3.Connection:
        """Connect to the database"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Enable dict-like access
        return self.connection
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # Customer operations
    def create_customer(self, customer: Customer) -> int:
        """Create a new customer"""
        if not self.connection:
            raise RuntimeError("Database not connected")
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO customers (key, number, suffix, name)
            VALUES (?, ?, ?, ?)
        """, (customer.key, customer.number, customer.suffix, customer.name))
        self.connection.commit()
        return cursor.lastrowid or 0
    
    def get_customer(self, customer_key: str) -> Optional[Customer]:
        """Get customer by key"""
        if not self.connection:
            raise RuntimeError("Database not connected")
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM customers WHERE key = ?", (customer_key,))
        row = cursor.fetchone()
        if row:
            return Customer(**dict(row))
        return None
    
    def get_or_create_customer(self, customer_data: Dict[str, Any]) -> int:
        """Get existing customer or create new one"""
        customer = self.get_customer(customer_data['key'])
        if customer and customer.id:
            return customer.id
        
        new_customer = Customer(
            key=customer_data['key'],
            number=customer_data.get('number', ''),
            suffix=customer_data.get('suffix'),
            name=customer_data.get('name', '')
        )
        return self.create_customer(new_customer)
    
    # Project operations
    def create_project(self, project: Project) -> int:
        """Create a new project"""
        if not self.connection:
            raise RuntimeError("Database not connected")
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO projects (uuid, customer_id, engineer, drafter, reviewer, 
                                architect, project_code, project_type, title, description, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (project.uuid, project.customer_id, project.engineer, project.drafter,
              project.reviewer, project.architect, project.project_code, project.project_type,
              project.title, project.description, project.status))
        self.connection.commit()
        return cursor.lastrowid or 0
    
    def get_project(self, project_uuid: str) -> Optional[Project]:
        """Get project by UUID"""
        if not self.connection:
            raise RuntimeError("Database not connected")
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM projects WHERE uuid = ?", (project_uuid,))
        row = cursor.fetchone()
        if row:
            return Project(**dict(row))
        return None
    
    def get_projects_by_customer(self, customer_key: str) -> List[Project]:
        """Get all projects for a customer"""
        if not self.connection:
            raise RuntimeError("Database not connected")
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT p.* FROM projects p
            JOIN customers c ON p.customer_id = c.id
            WHERE c.key = ?
            ORDER BY p.created_at DESC
        """, (customer_key,))
        return [Project(**dict(row)) for row in cursor.fetchall()]
    
    # Source operations
    def create_source(self, source: Source) -> int:
        """Create a new source"""
        if not self.connection:
            raise RuntimeError("Database not connected")
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO sources (uuid, title, originator, identifier, url, 
                               date_created, content_type, file_path, file_size, checksum)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (source.uuid, source.title, source.originator, source.identifier,
              source.url, source.date_created, source.content_type, 
              source.file_path, source.file_size, source.checksum))
        self.connection.commit()
        return cursor.lastrowid or 0
    
    def get_source(self, source_uuid: str) -> Optional[Source]:
        """Get source by UUID"""
        if not self.connection:
            raise RuntimeError("Database not connected")
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM sources WHERE uuid = ?", (source_uuid,))
        row = cursor.fetchone()
        if row:
            return Source(**dict(row))
        return None
    
    def get_or_create_source(self, source_data: Dict[str, Any]) -> int:
        """Get existing source or create new one"""
        source_uuid = source_data.get('uuid')
        if not source_uuid:
            source_uuid = str(uuid.uuid4())
            source_data['uuid'] = source_uuid
        
        source = self.get_source(source_uuid)
        if source and source.id:
            return source.id
        
        new_source = Source(
            uuid=source_uuid,
            title=source_data.get('title', ''),
            originator=source_data.get('originator'),
            identifier=source_data.get('identifier'),
            url=source_data.get('url'),
            date_created=source_data.get('date'),
            content_type=source_data.get('content_type'),
            file_path=source_data.get('file_path'),
            file_size=source_data.get('file_size'),
            checksum=source_data.get('checksum')
        )
        return self.create_source(new_source)
    
    # Project-Source association operations
    def associate_source_with_project(self, project_id: int, source_id: int, 
                                     assignment_order: Optional[int] = None, notes: Optional[str] = None):
        """Associate a source with a project"""
        if not self.connection:
            raise RuntimeError("Database not connected")
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO project_sources (project_id, source_id, assignment_order, notes)
            VALUES (?, ?, ?, ?)
        """, (project_id, source_id, assignment_order, notes))
        self.connection.commit()
    
    def get_project_sources(self, project_uuid: str) -> List[Dict[str, Any]]:
        """Get all sources for a project"""
        if not self.connection:
            raise RuntimeError("Database not connected")
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT s.*, ps.assignment_order, ps.notes as project_notes
            FROM sources s
            JOIN project_sources ps ON s.id = ps.source_id
            JOIN projects p ON ps.project_id = p.id
            WHERE p.uuid = ?
            ORDER BY ps.assignment_order, ps.created_at
        """, (project_uuid,))
        return [dict(row) for row in cursor.fetchall()]
    
    # Slide assignment operations
    def assign_source_to_slide(self, project_id: int, source_id: int, 
                              slide_number: int, slide_title: Optional[str] = None, notes: Optional[str] = None):
        """Assign a source to a PowerPoint slide"""
        if not self.connection:
            raise RuntimeError("Database not connected")
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO slide_assignments 
            (project_id, source_id, slide_number, slide_title, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (project_id, source_id, slide_number, slide_title, notes))
        self.connection.commit()
    
    def get_slide_assignments(self, project_uuid: str) -> List[Dict[str, Any]]:
        """Get all slide assignments for a project"""
        if not self.connection:
            raise RuntimeError("Database not connected")
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT sa.*, s.title as source_title, s.identifier
            FROM slide_assignments sa
            JOIN sources s ON sa.source_id = s.id
            JOIN projects p ON sa.project_id = p.id
            WHERE p.uuid = ?
            ORDER BY sa.slide_number
        """, (project_uuid,))
        return [dict(row) for row in cursor.fetchall()]


class JSONMigrator:
    """Handles migration from JSON files to SQLite database"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def migrate_project_json(self, json_path: Path) -> Optional[str]:
        """Migrate a single project JSON file to database"""
        try:
            with open(json_path, 'r') as f:
                project_data = json.load(f)
            
            # Extract customer data
            customer_data = project_data.get('customer', {})
            customer_id = self.db.get_or_create_customer(customer_data)
            
            # Create project
            project_uuid = project_data.get('uuid', str(uuid.uuid4()))
            project = Project(
                uuid=project_uuid,
                customer_id=customer_id,
                engineer=project_data.get('engineer'),
                drafter=project_data.get('drafter'),
                reviewer=project_data.get('reviewer'),
                architect=project_data.get('architect'),
                project_code=project_data.get('project_code'),
                title=project_data.get('title'),
                description=project_data.get('description')
            )
            
            project_id = self.db.create_project(project)
            
            # Migrate sources
            sources = project_data.get('sources', [])
            for i, source_data in enumerate(sources):
                source_id = self.db.get_or_create_source(source_data)
                self.db.associate_source_with_project(project_id, source_id, i + 1)
            
            # Migrate slide assignments if they exist
            slide_assignments = project_data.get('slide_assignments', [])
            for assignment in slide_assignments:
                source_uuid = assignment.get('source_uuid')
                if source_uuid:
                    source = self.db.get_source(source_uuid)
                    if source and source.id:
                        self.db.assign_source_to_slide(
                            project_id, source.id,
                            assignment.get('slide_number'),
                            assignment.get('slide_title'),
                            assignment.get('notes')
                        )
            
            print(f"Successfully migrated project: {project_uuid}")
            return project_uuid
            
        except Exception as e:
            print(f"Error migrating {json_path}: {e}")
            return None
    
    def migrate_directory(self, json_directory: Path):
        """Migrate all JSON files in a directory"""
        migrated_count = 0
        
        for json_file in json_directory.glob("**/*.json"):
            if json_file.name.startswith("project"):  # Assuming project files start with "project"
                result = self.migrate_project_json(json_file)
                if result:
                    migrated_count += 1
        
        print(f"Migration complete. Migrated {migrated_count} projects.")


# Example usage and testing
if __name__ == "__main__":
    # Initialize database
    db = DatabaseManager("test_source_manager.db")
    
    # Example: Create test data
    customer_id = db.create_customer(Customer(
        key="1001", 
        number="1001", 
        suffix=None, 
        name="Test Customer"
    ))
    
    project_id = db.create_project(Project(
        uuid=str(uuid.uuid4()),
        customer_id=customer_id,
        engineer="John Doe",
        project_code="DC123"
    ))
    
    source_id = db.create_source(Source(
        uuid=str(uuid.uuid4()),
        title="Test Document",
        originator="Test Originator"
    ))
    
    db.associate_source_with_project(project_id, source_id)
    
    print("Test data created successfully!")
    db.close()
