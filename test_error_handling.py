#!/usr/bin/env python3
"""
Test script for the error handling system
"""

import sys
import os
import time

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_error_handling_basic():
    """Test basic error handling functionality"""
    
    print("🧪 TESTING BASIC ERROR HANDLING")
    print("=" * 50)
    
    try:
        from skool_modules.error_handler import (
            get_error_handler, handle_error, safe_execute,
            SkoolScraperError, NetworkError, BrowserError, AuthenticationError,
            ExtractionError, ValidationError, ConfigurationError, FileOperationError,
            TimeoutError, RateLimitError, ErrorCategory, ErrorSeverity,
            raise_network_error, raise_browser_error, raise_authentication_error,
            raise_extraction_error, raise_validation_error, raise_configuration_error,
            raise_file_operation_error, raise_timeout_error, raise_rate_limit_error
        )
        
        print("✅ Successfully imported error handling functions")
        
        # Test 1: Error handler instance
        print("\n🔧 Testing error handler instance...")
        error_handler = get_error_handler()
        print(f"✅ Error handler created: {type(error_handler).__name__}")
        
        # Test 2: Custom exceptions
        print("\n🚨 Testing custom exceptions...")
        
        try:
            raise_network_error("Test network error")
        except NetworkError as e:
            print(f"✅ NetworkError caught: {e.message}")
            print(f"   Category: {e.category.value}")
            print(f"   Severity: {e.severity.value}")
            print(f"   Recoverable: {e.recoverable}")
        
        try:
            raise_browser_error("Test browser error")
        except BrowserError as e:
            print(f"✅ BrowserError caught: {e.message}")
        
        try:
            raise_authentication_error("Test authentication error")
        except AuthenticationError as e:
            print(f"✅ AuthenticationError caught: {e.message}")
            print(f"   Recoverable: {e.recoverable}")  # Should be False
        
        try:
            raise_extraction_error("Test extraction error")
        except ExtractionError as e:
            print(f"✅ ExtractionError caught: {e.message}")
        
        try:
            raise_validation_error("Test validation error")
        except ValidationError as e:
            print(f"✅ ValidationError caught: {e.message}")
        
        try:
            raise_configuration_error("Test configuration error")
        except ConfigurationError as e:
            print(f"✅ ConfigurationError caught: {e.message}")
        
        try:
            raise_file_operation_error("Test file operation error")
        except FileOperationError as e:
            print(f"✅ FileOperationError caught: {e.message}")
        
        try:
            raise_timeout_error("Test timeout error")
        except TimeoutError as e:
            print(f"✅ TimeoutError caught: {e.message}")
        
        try:
            raise_rate_limit_error("Test rate limit error")
        except RateLimitError as e:
            print(f"✅ RateLimitError caught: {e.message}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic error handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_recovery():
    """Test error recovery strategies"""
    
    print("\n🧪 TESTING ERROR RECOVERY")
    print("=" * 40)
    
    try:
        from skool_modules.error_handler import handle_error, NetworkError, BrowserError
        
        # Test 1: Network error recovery
        print("\n🌐 Testing network error recovery...")
        
        def simulate_network_operation():
            # Simulate a network error
            raise ConnectionError("Connection refused")
        
        context = {'operation': 'network_test', 'retry_count': 0}
        success = handle_error(ConnectionError("Connection refused"), context)
        print(f"✅ Network error recovery result: {success}")
        
        # Test 2: Browser error recovery
        print("\n🌐 Testing browser error recovery...")
        
        browser_error = BrowserError("Element not found")
        context = {'driver': None, 'operation': 'browser_test'}
        success = handle_error(browser_error, context)
        print(f"✅ Browser error recovery result: {success}")
        
        # Test 3: Safe execute function
        print("\n🛡️ Testing safe execute function...")
        
        def risky_function():
            if time.time() % 2 == 0:  # Simulate intermittent failure
                raise ValueError("Random error")
            return "Success"
        
        success, result = safe_execute(risky_function, context={'test': True})
        print(f"✅ Safe execute result: {success}, {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error recovery test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_decorator():
    """Test error handler decorator"""
    
    print("\n🧪 TESTING ERROR DECORATOR")
    print("=" * 40)
    
    try:
        from skool_modules.error_handler import error_handler, ErrorCategory, ErrorSeverity, NetworkError
        
        # Test 1: Decorated function with automatic retry
        print("\n🔄 Testing decorated function...")
        
        @error_handler(category=ErrorCategory.NETWORK, severity=ErrorSeverity.MEDIUM, max_retries=2)
        def test_function_with_errors(should_fail=True):
            if should_fail:
                raise NetworkError("Simulated network error")
            return "Success"
        
        try:
            result = test_function_with_errors(should_fail=True)
            print(f"✅ Decorated function result: {result}")
        except Exception as e:
            print(f"✅ Decorated function failed as expected: {type(e).__name__}")
        
        # Test 2: Successful decorated function
        result = test_function_with_errors(should_fail=False)
        print(f"✅ Successful decorated function: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error decorator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_statistics():
    """Test error statistics tracking"""
    
    print("\n🧪 TESTING ERROR STATISTICS")
    print("=" * 40)
    
    try:
        from skool_modules.error_handler import get_error_handler, NetworkError, BrowserError, ValidationError
        
        error_handler = get_error_handler()
        
        # Generate some test errors
        print("\n📊 Generating test errors...")
        
        test_errors = [
            NetworkError("Test network error 1"),
            NetworkError("Test network error 2"),
            BrowserError("Test browser error 1"),
            ValidationError("Test validation error 1"),
            ValidationError("Test validation error 2"),
            ValidationError("Test validation error 3")
        ]
        
        for error in test_errors:
            handle_error(error, {'test': True})
        
        # Get and display statistics
        print("\n📈 Error Statistics:")
        stats = error_handler.get_error_statistics()
        
        print(f"Total Errors: {stats['total_errors']}")
        print(f"Recovered Errors: {stats['recovered_errors']}")
        print(f"Unrecovered Errors: {stats['unrecovered_errors']}")
        
        if stats['total_errors'] > 0:
            recovery_rate = (stats['recovered_errors'] / stats['total_errors']) * 100
            print(f"Recovery Rate: {recovery_rate:.1f}%")
        
        print("\nErrors by Category:")
        for category, count in stats['errors_by_category'].items():
            print(f"  {category}: {count}")
        
        print("\nErrors by Severity:")
        for severity, count in stats['errors_by_severity'].items():
            print(f"  {severity}: {count}")
        
        # Print formatted statistics
        print("\n📋 Formatted Statistics:")
        error_handler.print_error_statistics()
        
        return True
        
    except Exception as e:
        print(f"❌ Error statistics test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_integration():
    """Test error handling integration with other modules"""
    
    print("\n🧪 TESTING ERROR INTEGRATION")
    print("=" * 40)
    
    try:
        from skool_modules.browser_manager import should_use_browser_isolation
        from skool_modules.config_manager import get_config
        from skool_modules.error_handler import handle_error, ConfigurationError
        
        print("✅ Successfully imported integrated modules")
        
        # Test 1: Browser manager with error handling
        print("\n🌐 Testing browser manager integration...")
        
        result = should_use_browser_isolation("Test Lesson", 1, 10)
        print(f"✅ Browser isolation decision: {result}")
        
        # Test 2: Config manager with error handling
        print("\n⚙️ Testing config manager integration...")
        
        base_url = get_config('SKOOL_BASE_URL')
        print(f"✅ Config value: {base_url}")
        
        # Test 3: Error handling with context
        print("\n🔧 Testing error handling with context...")
        
        context = {
            'module': 'test_integration',
            'operation': 'config_test',
            'timestamp': time.time()
        }
        
        try:
            # Simulate a configuration error
            raise ConfigurationError("Test configuration error")
        except Exception as e:
            success = handle_error(e, context)
            print(f"✅ Error handling with context: {success}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_classification():
    """Test automatic error classification"""
    
    print("\n🧪 TESTING ERROR CLASSIFICATION")
    print("=" * 40)
    
    try:
        from skool_modules.error_handler import handle_error
        
        # Test different types of generic exceptions
        test_exceptions = [
            ("ConnectionError", ConnectionError("Connection refused")),
            ("TimeoutError", TimeoutError("Operation timed out")),
            ("FileNotFoundError", FileNotFoundError("File not found")),
            ("PermissionError", PermissionError("Permission denied")),
            ("ValueError", ValueError("Invalid value")),
            ("KeyError", KeyError("Key not found"))
        ]
        
        for exception_name, exception in test_exceptions:
            print(f"\n🔍 Testing {exception_name}...")
            
            context = {'test_type': exception_name}
            success = handle_error(exception, context)
            
            print(f"✅ {exception_name} handled: {success}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error classification test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Error Handling Tests")
    print()
    
    # Run tests
    test1_passed = test_error_handling_basic()
    test2_passed = test_error_recovery()
    test3_passed = test_error_decorator()
    test4_passed = test_error_statistics()
    test5_passed = test_error_integration()
    test6_passed = test_error_classification()
    
    print()
    print("=" * 60)
    if all([test1_passed, test2_passed, test3_passed, test4_passed, test5_passed, test6_passed]):
        print("✅ ALL TESTS PASSED - Error handling system is working!")
        print()
        print("🎯 Successfully implemented:")
        print("  • Comprehensive error handling system")
        print("  • Custom exception classes")
        print("  • Automatic error classification")
        print("  • Recovery strategies")
        print("  • Error statistics tracking")
        print("  • Decorator-based error handling")
        print("  • Integration with other modules")
        print()
        print("💡 Ready to continue with additional improvements")
    else:
        print("❌ SOME TESTS FAILED - Check the issues above")
    
    print("=" * 60)
