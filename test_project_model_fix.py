#!/usr/bin/env python3
"""
Test the Project model fix for old format files
"""
import json
import sys
from pathlib import Path

# Add the project root to path
sys.path.insert(0, '/Users/jim/Documents/Development/source_manager_flet')

from src.models.project_models import Project

def test_old_format_handling():
    """Test that old format files give clear error messages."""
    
    # Test with old format file
    old_file = Path('/Users/jim/Documents/Source Manager/Directory Source Citations/EUROPE/France/be_2024333333 - CA003 - STD - 2024.json')
    
    if not old_file.exists():
        print(f"❌ Test file not found: {old_file}")
        return False
    
    try:
        with open(old_file, 'r') as f:
            data = json.load(f)
        
        print(f"📄 Testing old format file: {old_file.name}")
        print(f"📋 File contains keys: {list(data.keys())}")
        
        # This should fail with a clear message
        project = Project.from_dict(data)
        print('❌ ERROR: Should have failed but did not')
        return False
        
    except ValueError as e:
        if "old format" in str(e):
            print(f'✅ SUCCESS: Got expected error: {e}')
            return True
        else:
            print(f'⚠️  Got ValueError but wrong message: {e}')
            return False
            
    except Exception as e:
        print(f'❌ UNEXPECTED ERROR: {e}')
        return False

if __name__ == "__main__":
    success = test_old_format_handling()
    if success:
        print("\n🎉 Project model now handles old format files correctly!")
    else:
        print("\n💥 Test failed - need to investigate further")
