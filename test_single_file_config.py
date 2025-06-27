#!/usr/bin/env python3
"""
Test the new single-file user config system
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.models.user_config import UserConfigManager

def test_single_file_config():
    """Test the new single-file user configuration"""
    
    print("🧪 Testing Single-File User Configuration")
    print("=" * 50)
    
    # Test 1: Create user config manager
    user_config = UserConfigManager()
    print(f"✅ UserConfigManager created for user: {user_config.get_username()}")
    
    # Test 2: Check initial display name
    initial_name = user_config.get_display_name()
    print(f"📋 Initial display name: {initial_name or 'None'}")
    
    # Test 3: Set a display name
    test_name = "Test User Single File"
    user_config.save_display_name(test_name)
    print(f"💾 Saved display name: {test_name}")
    
    # Test 4: Verify the name was saved
    saved_name = user_config.get_display_name()
    assert saved_name == test_name, f"Expected '{test_name}', got '{saved_name}'"
    print(f"✅ Display name correctly saved and retrieved: {saved_name}")
    
    # Test 5: Create another user config instance to test persistence
    user_config2 = UserConfigManager()
    saved_name2 = user_config2.get_display_name()
    assert saved_name2 == test_name, f"Expected '{test_name}', got '{saved_name2}'"
    print(f"✅ Display name persisted across instances: {saved_name2}")
    
    # Test 6: Check greeting generation
    greeting = user_config.get_greeting()
    expected_greeting = f"Hi, {test_name}!"
    assert greeting == expected_greeting, f"Expected '{expected_greeting}', got '{greeting}'"
    print(f"👋 Greeting generated correctly: {greeting}")
    
    # Test 7: Test setup completion
    user_config.mark_setup_completed()
    print(f"🔧 Setup marked as completed")
    
    # Test 8: Verify setup completion persists
    user_config3 = UserConfigManager()
    assert user_config3.is_setup_completed(), "Setup completion should persist"
    print(f"✅ Setup completion persisted: {user_config3.is_setup_completed()}")
    
    print("\n" + "=" * 50)
    print("✅ All single-file configuration tests passed!")
    print("=" * 50)

if __name__ == "__main__":
    test_single_file_config()
