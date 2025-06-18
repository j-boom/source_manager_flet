-- Source Manager Database Schema

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    number INTEGER NOT NULL,
    suffix TEXT,
    name TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT UNIQUE NOT NULL,
    customer_id INTEGER NOT NULL,
    engineer TEXT,
    drafter TEXT,
    reviewer TEXT,
    architect TEXT,
    project_code TEXT,
    project_type TEXT,
    title TEXT,
    description TEXT,
    status TEXT DEFAULT 'active',
    requestor_name TEXT,
    request_date TEXT,
    relook BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Sources table
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    author TEXT,
    publication_date TEXT,
    source_type TEXT,
    identifier TEXT,
    url TEXT,
    date_created TEXT,
    content_type TEXT,
    file_path TEXT,
    file_size INTEGER,
    checksum TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Project sources junction table
CREATE TABLE IF NOT EXISTS project_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    assignment_order INTEGER,
    notes TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (source_id) REFERENCES sources(id),
    UNIQUE(project_id, source_id)
);

-- Slide assignments table
CREATE TABLE IF NOT EXISTS slide_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    slide_number INTEGER NOT NULL,
    slide_title TEXT,
    notes TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (source_id) REFERENCES sources(id),
    UNIQUE(project_id, source_id, slide_number)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_customers_key ON customers(key);
CREATE INDEX IF NOT EXISTS idx_projects_uuid ON projects(uuid);
CREATE INDEX IF NOT EXISTS idx_projects_customer_id ON projects(customer_id);
CREATE INDEX IF NOT EXISTS idx_project_sources_project_id ON project_sources(project_id);
CREATE INDEX IF NOT EXISTS idx_project_sources_source_id ON project_sources(source_id);
CREATE INDEX IF NOT EXISTS idx_slide_assignments_project_id ON slide_assignments(project_id);
