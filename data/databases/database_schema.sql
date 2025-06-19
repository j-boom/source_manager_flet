-- SQLite3 Database Schema for Source Manager
-- Migration from JSON to relational structure

-- Customers table
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,           -- Facility Number (10-digit folder number, e.g., "1001678921")
    number TEXT NOT NULL,               -- Building Number (pattern: [A-Z]{2}\d{3}, e.g., "DC123")
    suffix TEXT,                        -- Customer suffix
    name TEXT NOT NULL,                 -- Facility Name
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Projects table
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT UNIQUE NOT NULL,          -- Project UUID
    customer_id INTEGER NOT NULL,       -- Foreign key to customers
    engineer TEXT,                      -- Engineer name
    drafter TEXT,                       -- Drafter name
    reviewer TEXT,                      -- Reviewer name
    architect TEXT,                     -- Architect name
    geologist TEXT,                     -- Geologist name
    project_code TEXT,                  -- Project code (e.g., "DC123")
    project_type TEXT,                  -- Project type (e.g., "Design", "Construction", "Analysis")
    title TEXT,                         -- Project title
    description TEXT,                   -- Project description
    status TEXT DEFAULT 'active',      -- Project status
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- Sources table
CREATE TABLE sources (
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

-- Project-Source associations (many-to-many)
CREATE TABLE project_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    assignment_order INTEGER,           -- Order of sources in project
    notes TEXT,                         -- Project-specific notes about this source
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE CASCADE,
    UNIQUE(project_id, source_id)       -- Prevent duplicate associations
);

-- Slide assignments table
CREATE TABLE slide_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    slide_number INTEGER NOT NULL,
    slide_title TEXT,
    notes TEXT,                         -- Notes to add to the slide
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE CASCADE
);

-- Indexes for better performance
CREATE INDEX idx_customers_key ON customers(key);
CREATE INDEX idx_projects_uuid ON projects(uuid);
CREATE INDEX idx_projects_customer ON projects(customer_id);
CREATE INDEX idx_sources_uuid ON sources(uuid);
CREATE INDEX idx_project_sources_project ON project_sources(project_id);
CREATE INDEX idx_project_sources_source ON project_sources(source_id);
CREATE INDEX idx_slide_assignments_project ON slide_assignments(project_id);
CREATE INDEX idx_slide_assignments_source ON slide_assignments(source_id);

-- Views for common queries
CREATE VIEW project_summary AS
SELECT 
    p.uuid as project_uuid,
    p.project_code,
    p.project_type,
    p.title as project_title,
    c.key as customer_key,
    c.name as customer_name,
    p.engineer,
    p.drafter,
    p.reviewer,
    p.architect,
    COUNT(ps.source_id) as source_count,
    p.status,
    p.created_at,
    p.updated_at
FROM projects p
JOIN customers c ON p.customer_id = c.id
LEFT JOIN project_sources ps ON p.id = ps.project_id
GROUP BY p.id;

CREATE VIEW source_usage AS
SELECT 
    s.uuid as source_uuid,
    s.title,
    s.originator,
    s.identifier,
    COUNT(ps.project_id) as project_count,
    GROUP_CONCAT(p.project_code) as used_in_projects
FROM sources s
LEFT JOIN project_sources ps ON s.id = ps.source_id
LEFT JOIN projects p ON ps.project_id = p.id
GROUP BY s.id;
