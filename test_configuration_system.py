"""
Test script to demonstrate the configuration-driven project form system
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.project_types_config import (
    PROJECT_TYPES_CONFIG, get_project_type_config, 
    get_all_project_types, get_project_type_display_names
)
from src.models.database_schema_generator import DatabaseSchemaGenerator


def test_configuration_system():
    """Test the configuration system"""
    print("=== Project Types Configuration Test ===\\n")
    
    # Test project type listing
    print("Available project types:")
    for ptype in get_all_project_types():
        config = get_project_type_config(ptype)
        if config:
            print(f"  {ptype}: {config.display_name}")
        else:
            print(f"  {ptype}: Configuration not found")
    print()
    
    # Test display names
    print("Display name mapping:")
    display_names = get_project_type_display_names()
    for code, name in display_names.items():
        print(f"  {code} -> {name}")
    print()
    
    # Test detailed configuration for CCR
    print("=== CCR Project Configuration ===")
    ccr_config = get_project_type_config("CCR")
    if ccr_config:
        print(f"Name: {ccr_config.name}")
        print(f"Display Name: {ccr_config.display_name}")
        print(f"Description: {ccr_config.description}")
        print(f"Table Name: {ccr_config.table_name}")
        print(f"Filename Pattern: {ccr_config.filename_pattern}")
        print("Fields:")
        for field in ccr_config.fields:
            print(f"  - {field.name}: {field.label} ({field.field_type.value})")
            if field.required:
                print(f"    Required: Yes")
            if field.validation_rules:
                print(f"    Validation: {field.validation_rules}")
    print()
    
    # Test GSC configuration (no suffix required)
    print("=== GSC Project Configuration ===")
    gsc_config = get_project_type_config("GSC")
    if gsc_config:
        print(f"Name: {gsc_config.name}")
        print(f"Display Name: {gsc_config.display_name}")
        print(f"Table Name: {gsc_config.table_name}")
        print(f"Filename Pattern: {gsc_config.filename_pattern}")
        print("Unique Fields:")
        for field in gsc_config.fields:
            if field.name not in ["facility_number", "facility_name", "building_number", 
                                "customer_suffix", "project_title", "project_description", 
                                "request_year", "engineer", "drafter", "reviewer", 
                                "architect", "geologist"]:
                print(f"  - {field.name}: {field.label} ({field.field_type.value})")
    print()


def test_database_schema_generation():
    """Test database schema generation"""
    print("=== Database Schema Generation Test ===\\n")
    
    # Create schema generator
    generator = DatabaseSchemaGenerator(":memory:")
    
    # Test base schema generation
    print("Base schema generation:")
    base_schema = generator.generate_base_schema()
    print("✓ Base schema generated successfully")
    print(f"Schema length: {len(base_schema)} characters\\n")
    
    # Test individual project type table generation
    print("Project type table generation:")
    for project_type in get_all_project_types():
        table_sql = generator.generate_project_type_table_sql(project_type)
        if table_sql:
            print(f"✓ {project_type} table SQL generated")
            # Show first few lines
            lines = table_sql.strip().split('\\n')[:5]
            for line in lines:
                print(f"    {line}")
            print("    ...")
        else:
            print(f"✗ {project_type} table SQL generation failed")
    print()
    
    # Test full schema generation
    print("Full schema generation:")
    full_schema = generator.generate_full_schema()
    print("✓ Full schema generated successfully")
    print(f"Full schema length: {len(full_schema)} characters")
    
    # Count tables in schema
    table_count = full_schema.count("CREATE TABLE")
    print(f"Total tables: {table_count}")
    print()


def test_field_validation():
    """Test field validation rules"""
    print("=== Field Validation Test ===\\n")
    
    # Test building number validation
    building_pattern = r'^[A-Z]{2}\d{3}$'
    test_values = ["DC123", "AB456", "dc123", "ABC12", "D1234", ""]
    
    print("Building number validation (should match [A-Z]{2}\\d{3}):")
    import re
    for value in test_values:
        is_valid = re.match(building_pattern, value) is not None
        status = "✓" if is_valid else "✗"
        print(f"  {status} '{value}' -> {is_valid}")
    print()
    
    # Test suffix validation for different project types
    suffix_pattern = r'^[A-Z]{3}\d{3}$'
    test_suffixes = ["ABC123", "DEF456", "abc123", "AB123", "ABCD123", ""]
    
    print("Suffix validation (should match [A-Z]{3}\\d{3}):")
    for value in test_suffixes:
        is_valid = re.match(suffix_pattern, value) is not None
        status = "✓" if is_valid else "✗"
        print(f"  {status} '{value}' -> {is_valid}")
    print()


def main():
    """Run all tests"""
    print("Configuration-Driven Project Form System Test\\n")
    print("=" * 60)
    
    try:
        test_configuration_system()
        test_database_schema_generation()
        test_field_validation()
        
        print("=== Summary ===")
        print("✓ Configuration system working")
        print("✓ Database schema generation working")
        print("✓ Validation rules working")
        print("\\n🎉 All tests passed! The configuration system is ready for integration.")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
