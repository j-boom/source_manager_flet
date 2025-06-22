#!/usr/bin/env python3

# Test the updated filename generation
import sys
from pathlib import Path

# Add the src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from services.project_creation_service import ProjectCreationService

def test_filename_generation():
    """Test the new filename generation with suffix support"""
    service = ProjectCreationService()
    
    # Test cases: (ten_digit, type, year, doc_title, suffix, expected)
    test_cases = [
        ("1234567890", "STD", "2025", "", "ABC123", "1234567890 - ABC123 - STD - 2025.json"),
        ("1234567890", "COM", "2025", "", "DEF456", "1234567890 - DEF456 - COM - 2025.json"),
        ("1234567890", "FCR", "2025", "", "GHI789", "1234567890 - GHI789 - FCR - 2025.json"),
        ("1234567890", "CRS", "2025", "", "JKL012", "1234567890 - JKL012 - CRS - 2025.json"),
        ("1234567890", "CCR", "2025", "", "MNO345", "1234567890 - MNO345 - CCR - 2025.json"),
        ("1234567890", "GSC", "2025", "", "PQR678", "1234567890 - PQR678 - GSC - 2025.json"),
        ("1234567890", "OTH", "2025", "Special Study", "", "1234567890 - OTH - Special Study - 2025.json"),
        # Test without suffix for types that don't require it
        ("1234567890", "STD", "2025", "", "", "1234567890 - STD - 2025.json"),
    ]
    
    print("Testing filename generation:")
    print("=" * 60)
    
    for ten_digit, ptype, year, doc_title, suffix, expected in test_cases:
        result = service.generate_filename(ten_digit, ptype, year, doc_title, suffix)
        status = "✓" if result == expected else "✗"
        print(f"{status} {ptype} with suffix '{suffix}': {result}")
        if result != expected:
            print(f"  Expected: {expected}")
            print(f"  Got:      {result}")
        print()

if __name__ == "__main__":
    test_filename_generation()
