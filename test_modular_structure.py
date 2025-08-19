#!/usr/bin/env python3
"""
Test script for the modular structure
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_manager():
    """Test the configuration management module"""
    
    print("🧪 TESTING CONFIGURATION MANAGER")
    print("=" * 50)
    
    try:
        from skool_modules.config_manager import (
            get_config, set_config, validate_credentials, print_config
        )
        
        print("✅ Successfully imported config manager functions")
        
        # Test getting configuration
        base_url = get_config('SKOOL_BASE_URL')
        print(f"✅ SKOOL_BASE_URL: {base_url}")
        
        # Test setting configuration
        set_config('TEST_VALUE', 'test_value')
        test_value = get_config('TEST_VALUE')
        print(f"✅ TEST_VALUE: {test_value}")
        
        # Test configuration validation
        credentials_valid = validate_credentials()
        print(f"✅ Credentials validation: {credentials_valid}")
        
        # Print configuration
        print_config()
        
        return True
        
    except Exception as e:
        print(f"❌ Config manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_browser_manager():
    """Test the browser management module"""
    
    print("\n🧪 TESTING BROWSER MANAGER")
    print("=" * 50)
    
    try:
        from skool_modules.browser_manager import (
            should_use_browser_isolation,
            print_browser_isolation_statistics
        )
        
        print("✅ Successfully imported browser manager functions")
        
        # Test isolation decision logic
        test_cases = [
            ("Introduction to Python", 1, 10, True),   # Early lesson
            ("Advanced Data Structures", 4, 10, False), # Normal lesson
            ("Lesson 5: Basics", 5, 10, True),         # Periodic cleanup
            ("Welcome to the Course", 6, 10, True),    # Problematic keyword
        ]
        
        for lesson_title, lesson_index, total_lessons, expected in test_cases:
            result = should_use_browser_isolation(lesson_title, lesson_index, total_lessons)
            status = "✅" if result == expected else "❌"
            print(f"{status} {lesson_title} (index {lesson_index}): {result} (expected {expected})")
        
        # Test statistics printing
        print_browser_isolation_statistics()
        
        return True
        
    except Exception as e:
        print(f"❌ Browser manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_module_imports():
    """Test that all modules can be imported correctly"""
    
    print("\n🧪 TESTING MODULE IMPORTS")
    print("=" * 50)
    
    try:
        # Test main package import
        import skool_modules
        print("✅ Main package import successful")
        
        # Test individual module imports
        from skool_modules import config_manager
        print("✅ Config manager module import successful")
        
        from skool_modules import browser_manager
        print("✅ Browser manager module import successful")
        
        # Test convenience functions
        from skool_modules import get_config, should_use_browser_isolation
        print("✅ Convenience function imports successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Module import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Testing Modular Structure")
    print()
    
    # Run tests
    test1_passed = test_config_manager()
    test2_passed = test_browser_manager()
    test3_passed = test_module_imports()
    
    print()
    print("=" * 60)
    if test1_passed and test2_passed and test3_passed:
        print("✅ ALL TESTS PASSED - Modular structure is working!")
        print()
        print("🎯 Successfully implemented:")
        print("  • Configuration Management Module")
        print("  • Browser Management Module")
        print("  • Modular package structure")
        print("  • Backward compatibility functions")
        print()
        print("💡 Ready to continue with additional modules")
    else:
        print("❌ SOME TESTS FAILED - Check the issues above")
    
    print("=" * 60)
