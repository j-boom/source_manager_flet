#!/usr/bin/env python3
"""
Example queries and analytics using the SQLite database
Demonstrates the power of moving from JSON to relational data
"""

from database_manager import DatabaseManager, Customer, Project, Source
import uuid

def demonstrate_analytics():
    """Demonstrate analytics capabilities with the new database"""
    db = DatabaseManager("demo_analytics.db")
    
    print("Creating sample data for analytics demonstration...")
    
    # Create customers
    customers = [
        Customer("1001", "1001", None, "ACME Corporation"),
        Customer("1002", "1002", None, "TechCorp Inc"),
        Customer("2001", "2001", "A", "Global Manufacturing")
    ]
    
    customer_ids = {}
    for customer in customers:
        customer_ids[customer.key] = db.create_customer(customer)
    
    # Create projects
    projects_data = [
        ("1001", "DC123", "Project Alpha", "John Doe", "Jane Smith"),
        ("1001", "DC124", "Project Beta", "John Doe", "Bob Wilson"),
        ("1002", "DC125", "Tech Upgrade", "Alice Brown", "Carol Davis"),
        ("1002", "DC126", "System Migration", "Alice Brown", "Dave Miller"),
        ("2001", "DC127", "Factory Automation", "Eve Wilson", "Frank Taylor"),
    ]
    
    project_ids = {}
    for customer_key, code, title, engineer, drafter in projects_data:
        project = Project(
            uuid=str(uuid.uuid4()),
            customer_id=customer_ids[customer_key],
            engineer=engineer,
            drafter=drafter,
            project_code=code,
            title=title
        )
        project_id = db.create_project(project)
        project_ids[code] = project_id
    
    # Create sources (some will be reused across projects)
    sources_data = [
        ("Contract Template v1.0", "Legal Dept", "TMPL-001"),
        ("Safety Guidelines", "Safety Officer", "SAFE-002"),
        ("Technical Specifications", "Engineering", "TECH-003"),
        ("Project Charter", "PM Office", "CHAR-004"),
        ("Budget Template", "Finance", "BUDG-005"),
    ]
    
    source_ids = {}
    for title, originator, identifier in sources_data:
        source = Source(
            uuid=str(uuid.uuid4()),
            title=title,
            originator=originator,
            identifier=identifier
        )
        source_id = db.create_source(source)
        source_ids[identifier] = source_id
    
    # Associate sources with projects (demonstrating reuse)
    associations = [
        ("DC123", ["TMPL-001", "SAFE-002", "TECH-003"]),
        ("DC124", ["TMPL-001", "TECH-003", "BUDG-005"]),  # Reuses TMPL-001, TECH-003
        ("DC125", ["SAFE-002", "TECH-003", "CHAR-004"]),  # Reuses SAFE-002, TECH-003
        ("DC126", ["CHAR-004", "BUDG-005"]),              # Reuses CHAR-004, BUDG-005
        ("DC127", ["TMPL-001", "SAFE-002", "BUDG-005"]), # Reuses multiple
    ]
    
    for project_code, source_identifiers in associations:
        project_id = project_ids[project_code]
        for i, identifier in enumerate(source_identifiers):
            source_id = source_ids[identifier]
            db.associate_source_with_project(project_id, source_id, i + 1)
    
    # Add some slide assignments
    slide_data = [
        ("DC123", "TMPL-001", 1, "Project Overview"),
        ("DC123", "SAFE-002", 3, "Safety Requirements"),
        ("DC124", "TECH-003", 2, "Technical Details"),
        ("DC125", "CHAR-004", 1, "Project Charter"),
    ]
    
    for project_code, source_identifier, slide_num, slide_title in slide_data:
        project_id = project_ids[project_code]
        source_id = source_ids[source_identifier]
        db.assign_source_to_slide(project_id, source_id, slide_num, slide_title)
    
    print("Sample data created! Now demonstrating analytics queries...\n")
    
    # Analytics queries that were impossible with JSON files
    if not db.connection:
        raise RuntimeError("Database not connected")
    cursor = db.connection.cursor()
    
    print("=" * 60)
    print("ANALYTICS DEMONSTRATIONS")
    print("=" * 60)
    
    # 1. Customer project summary
    print("\n1. PROJECTS BY CUSTOMER:")
    print("-" * 30)
    cursor.execute("""
        SELECT 
            c.name as customer_name,
            COUNT(p.id) as project_count,
            GROUP_CONCAT(p.project_code) as project_codes
        FROM customers c
        LEFT JOIN projects p ON c.id = p.customer_id
        GROUP BY c.id
        ORDER BY project_count DESC
    """)
    
    for row in cursor.fetchall():
        print(f"Customer: {row[0]}")
        print(f"  Projects: {row[1]}")
        print(f"  Codes: {row[2]}")
        print()
    
    # 2. Source reuse analysis
    print("2. SOURCE REUSE ANALYSIS:")
    print("-" * 30)
    cursor.execute("""
        SELECT 
            s.title,
            s.identifier,
            COUNT(ps.project_id) as usage_count,
            GROUP_CONCAT(p.project_code) as used_in_projects
        FROM sources s
        LEFT JOIN project_sources ps ON s.id = ps.source_id
        LEFT JOIN projects p ON ps.project_id = p.id
        GROUP BY s.id
        ORDER BY usage_count DESC
    """)
    
    for row in cursor.fetchall():
        print(f"Source: {row[0]} ({row[1]})")
        print(f"  Used in {row[2]} projects: {row[3]}")
        print()
    
    # 3. Engineer workload
    print("3. ENGINEER WORKLOAD:")
    print("-" * 30)
    cursor.execute("""
        SELECT 
            engineer,
            COUNT(*) as project_count,
            GROUP_CONCAT(project_code) as projects
        FROM projects 
        WHERE engineer IS NOT NULL
        GROUP BY engineer
        ORDER BY project_count DESC
    """)
    
    for row in cursor.fetchall():
        print(f"Engineer: {row[0]}")
        print(f"  Projects: {row[1]} ({row[2]})")
        print()
    
    # 4. Slide assignment summary
    print("4. SLIDE ASSIGNMENTS:")
    print("-" * 30)
    cursor.execute("""
        SELECT 
            p.project_code,
            COUNT(sa.id) as slides_with_sources,
            GROUP_CONCAT(sa.slide_number || ': ' || s.title) as assignments
        FROM projects p
        LEFT JOIN slide_assignments sa ON p.id = sa.project_id
        LEFT JOIN sources s ON sa.source_id = s.id
        WHERE sa.id IS NOT NULL
        GROUP BY p.id
        ORDER BY slides_with_sources DESC
    """)
    
    for row in cursor.fetchall():
        print(f"Project: {row[0]}")
        print(f"  Slides with sources: {row[1]}")
        print(f"  Assignments: {row[2]}")
        print()
    
    # 5. Cross-customer source sharing (potential issue)
    print("5. SOURCES SHARED ACROSS CUSTOMERS:")
    print("-" * 30)
    cursor.execute("""
        SELECT 
            s.title,
            s.identifier,
            COUNT(DISTINCT c.id) as customer_count,
            GROUP_CONCAT(DISTINCT c.name) as customers
        FROM sources s
        JOIN project_sources ps ON s.id = ps.source_id
        JOIN projects p ON ps.project_id = p.id
        JOIN customers c ON p.customer_id = c.id
        GROUP BY s.id
        HAVING customer_count > 1
        ORDER BY customer_count DESC
    """)
    
    cross_customer_sources = cursor.fetchall()
    if cross_customer_sources:
        for row in cross_customer_sources:
            print(f"⚠️  Source: {row[0]} ({row[1]})")
            print(f"   Shared across {row[2]} customers: {row[3]}")
            print()
    else:
        print("✅ No sources are shared across customers (good security!)")
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print("\nThese analytics would be very difficult with JSON files!")
    print("The relational database makes complex queries simple and fast.")
    
    db.close()

if __name__ == "__main__":
    demonstrate_analytics()
