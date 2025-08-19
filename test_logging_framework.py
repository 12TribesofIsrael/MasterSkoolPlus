#!/usr/bin/env python3
"""
Test script for the logging framework
"""

import sys
import os
import time

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_logging_framework():
    """Test the logging framework functionality"""
    
    print("🧪 TESTING LOGGING FRAMEWORK")
    print("=" * 60)
    
    try:
        from skool_modules.logger import (
            get_logger, setup_logging, log_info, log_error, log_warning, log_debug,
            log_success, log_progress, log_browser, log_video, log_lesson, log_isolation,
            log_exception, log_performance, log_extraction_attempt, log_session_event,
            log_isolation_decision, log_validation_result
        )
        
        print("✅ Successfully imported logging functions")
        
        # Test 1: Basic logging functionality
        print("\n📝 Testing basic logging functions...")
        
        logger = get_logger("test_logger")
        logger.info("This is an info message")
        logger.success("This is a success message")
        logger.warning("This is a warning message")
        logger.error("This is an error message")
        logger.debug("This is a debug message")
        
        # Test 2: Specialized logging functions
        print("\n🎯 Testing specialized logging functions...")
        
        log_browser("Browser setup initiated")
        log_video("Video extraction started")
        log_lesson("Processing lesson: Introduction to Python")
        log_isolation("Creating isolated browser instance")
        log_progress("Processing lesson 5 of 20")
        
        # Test 3: Structured logging
        print("\n📊 Testing structured logging...")
        
        # Test extraction attempt logging
        log_extraction_attempt(
            method="json",
            lesson_title="Introduction to Python",
            video_url="https://youtu.be/example123",
            result_status="success",
            additional_info={"platform": "youtube", "duration": "10:30"}
        )
        
        # Test session event logging
        log_session_event(
            event_type="video_found",
            lesson_title="Variables and Data Types",
            video_url="https://youtu.be/example456",
            extraction_method="click",
            platform="youtube"
        )
        
        # Test isolation decision logging
        log_isolation_decision(
            lesson_title="Lesson 1: Basics",
            lesson_index=1,
            total_lessons=10,
            decision=True,
            reason="early lesson"
        )
        
        # Test validation result logging
        log_validation_result(
            lesson_title="Advanced Data Structures",
            video_url="https://youtu.be/example789",
            validation_type="lesson_relevance",
            result=True,
            details={"content_match": 0.85, "keyword_match": True}
        )
        
        # Test 4: Performance logging
        print("\n⏱️ Testing performance logging...")
        
        start_time = time.time()
        time.sleep(0.1)  # Simulate some work
        duration = time.time() - start_time
        
        log_performance(
            operation="lesson_processing",
            duration=duration,
            details={"lesson_title": "Test Lesson", "content_size": "2.5KB"}
        )
        
        # Test 5: Exception logging
        print("\n💥 Testing exception logging...")
        
        try:
            # Simulate an error
            raise ValueError("This is a test exception")
        except Exception as e:
            log_exception("Test exception occurred", exc_info=True)
        
        # Test 6: Dictionary logging
        print("\n📋 Testing dictionary logging...")
        
        test_data = {
            "lesson_title": "Test Lesson",
            "video_count": 1,
            "processing_time": 2.5,
            "status": "completed"
        }
        
        logger.log_dict(test_data, "info")
        
        # Test 7: Logger instance methods
        print("\n🔧 Testing logger instance methods...")
        
        logger.config("Configuration loaded successfully")
        logger.session("Session tracking initialized")
        logger.validation("Validation system ready")
        logger.file_operation("File saved successfully")
        
        # Test 8: Log file verification
        print("\n📁 Verifying log file creation...")
        
        log_file_path = logger.get_log_file_path()
        if os.path.exists(log_file_path):
            print(f"✅ Log file created: {log_file_path}")
            
            # Check file size
            file_size = os.path.getsize(log_file_path)
            print(f"📊 Log file size: {file_size} bytes")
            
            if file_size > 0:
                print("✅ Log file contains data")
            else:
                print("❌ Log file is empty")
        else:
            print(f"❌ Log file not found: {log_file_path}")
            return False
        
        # Test 9: Multiple logger instances
        print("\n🔄 Testing multiple logger instances...")
        
        logger2 = setup_logging("test_logger_2")
        logger2.info("This is from logger 2")
        logger2.success("Logger 2 success message")
        
        # Test 10: Logger cleanup
        print("\n🧹 Testing logger cleanup...")
        
        logger.close()
        logger2.close()
        
        print("✅ Logger cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Logging framework test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_logging_integration():
    """Test logging integration with other modules"""
    
    print("\n🧪 TESTING LOGGING INTEGRATION")
    print("=" * 50)
    
    try:
        from skool_modules.browser_manager import should_use_browser_isolation
        from skool_modules.config_manager import get_config, print_config
        
        print("✅ Successfully imported integrated modules")
        
        # Test browser manager with logging
        print("\n🌐 Testing browser manager with logging...")
        
        result = should_use_browser_isolation("Introduction to Python", 1, 10)
        print(f"✅ Isolation decision: {result}")
        
        # Test config manager with logging
        print("\n⚙️ Testing config manager with logging...")
        
        base_url = get_config('SKOOL_BASE_URL')
        print(f"✅ Config value: {base_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_test_files():
    """Clean up test files created during testing"""
    import glob
    
    # Clean up log files
    log_files = glob.glob("debug_logs/skool_scraper_*.log")
    for log_file in log_files:
        try:
            os.remove(log_file)
            print(f"🧹 Cleaned up: {log_file}")
        except Exception as e:
            print(f"⚠️ Could not remove {log_file}: {e}")

if __name__ == "__main__":
    print("🚀 Starting Logging Framework Tests")
    print()
    
    # Run tests
    test1_passed = test_logging_framework()
    test2_passed = test_logging_integration()
    
    print()
    print("=" * 60)
    if test1_passed and test2_passed:
        print("✅ ALL TESTS PASSED - Logging framework is working!")
        print()
        print("🎯 Successfully implemented:")
        print("  • Comprehensive logging system")
        print("  • Structured logging for different operations")
        print("  • Performance monitoring")
        print("  • Exception tracking")
        print("  • File and console output")
        print("  • Integration with other modules")
        print()
        print("💡 Ready to continue with additional improvements")
    else:
        print("❌ SOME TESTS FAILED - Check the issues above")
    
    print()
    
    # Ask user if they want to keep the test files
    try:
        keep_files = input("Keep test log files for inspection? (y/N): ").strip().lower()
        if keep_files != 'y':
            cleanup_test_files()
    except (KeyboardInterrupt, EOFError):
        print("\n🧹 Cleaning up test files...")
        cleanup_test_files()
    
    print("=" * 60)
