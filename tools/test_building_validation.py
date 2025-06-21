import re

def test_building_number_validation():
    """Test the building number validation pattern"""
    pattern = r'^[A-Z]{2}\d{3}$'
    
    test_cases = [
        ('DC123', True),   # Valid
        ('AB456', True),   # Valid
        ('XY789', True),   # Valid
        ('dc123', False),  # Lower case
        ('D123', False),   # Too short
        ('ABC123', False), # Too long
        ('12345', False),  # No letters
        ('ABCDE', False),  # No numbers
        ('A1234', False),  # Wrong format
        ('', False),       # Empty
    ]
    
    print("Building Number Validation Test:")
    print("Pattern: r'^[A-Z]{2}\\d{3}$' (Two uppercase letters + three digits)")
    print()
    
    all_passed = True
    for test_input, expected in test_cases:
        result = bool(re.match(pattern, test_input))
        status = "✅" if result == expected else "❌"
        print(f"{status} '{test_input}' -> {result} (expected: {expected})")
        if result != expected:
            all_passed = False
    
    print()
    print(f"All tests passed: {'✅' if all_passed else '❌'}")
    return all_passed

if __name__ == "__main__":
    test_building_number_validation()
