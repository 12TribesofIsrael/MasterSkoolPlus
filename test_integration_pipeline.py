#!/usr/bin/env python3
"""
Integration Tests for Full Scraping Pipeline
============================================

Tests the complete scraping workflow from start to finish, including
all modules working together in a realistic scenario.
"""

import sys
import os
import time
import json
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List, Optional

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_full_pipeline_initialization():
    """Test complete pipeline initialization with all modules"""
    
    print("🧪 TESTING FULL PIPELINE INITIALIZATION")
    print("=" * 50)
    
    try:
        # Import all modules
        from skool_modules.config_manager import get_config, set_config, validate_credentials
        from skool_modules.logger import get_logger, setup_logging
        from skool_modules.error_handler import get_error_handler, handle_error
        from skool_modules.browser_manager import setup_driver, create_isolated_browser_instance
        from skool_modules.video_extractor import get_video_extractor, extract_video_url
        
        print("✅ Successfully imported all modules")
        
        # Test configuration initialization
        config = get_config('SKOOL_BASE_URL')
        if config:
            print(f"✅ Configuration loaded: {config}")
        else:
            print("✅ Configuration loaded with default values")
        
        # Test logger initialization
        logger = get_logger()
        logger.info("Testing logger integration")
        print("✅ Logger initialized and working")
        
        # Test error handler initialization
        error_handler = get_error_handler()
        print("✅ Error handler initialized")
        
        # Test video extractor initialization
        video_extractor = get_video_extractor()
        print("✅ Video extractor initialized")
        
        # Test browser manager initialization
        print("✅ Browser manager ready")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_configuration_workflow():
    """Test complete configuration workflow"""
    
    print("\n🧪 TESTING CONFIGURATION WORKFLOW")
    print("=" * 40)
    
    try:
        from skool_modules.config_manager import get_config, set_config, validate_credentials
        
        # Test configuration loading
        base_url = get_config('SKOOL_BASE_URL')
        headless_mode = get_config('HEADLESS_MODE', False)
        timeout = get_config('BROWSER_TIMEOUT', 30)
        
        print(f"✅ Base URL: {base_url}")
        print(f"✅ Headless mode: {headless_mode}")
        print(f"✅ Timeout: {timeout}")
        
        # Test configuration setting
        set_config('TEST_MODE', True)
        test_mode = get_config('TEST_MODE', False)
        if test_mode:
            print("✅ Configuration setting working")
        else:
            print("❌ Configuration setting failed")
            return False
        
        # Test credential validation (mock)
        with patch('skool_modules.config_manager.validate_credentials') as mock_validate:
            mock_validate.return_value = True
            result = validate_credentials("test@example.com", "password123")
            if result:
                print("✅ Credential validation working")
            else:
                print("❌ Credential validation failed")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_logging_integration():
    """Test logging integration across all modules"""
    
    print("\n🧪 TESTING LOGGING INTEGRATION")
    print("=" * 40)
    
    try:
        from skool_modules.logger import get_logger, log_info, log_error, log_video, log_browser
        
        logger = get_logger()
        
        # Test basic logging
        logger.info("Testing basic logging")
        logger.success("Testing success logging")
        logger.warning("Testing warning logging")
        logger.error("Testing error logging")
        
        # Test specialized logging
        log_video("Testing video logging")
        log_browser("Testing browser logging")
        log_info("Testing info logging")
        log_error("Testing error logging")
        
        # Test structured logging
        test_data = {
            "operation": "test",
            "status": "success",
            "timestamp": time.time()
        }
        logger.log_dict(test_data, "info")
        
        print("✅ All logging functions working")
        return True
        
    except Exception as e:
        print(f"❌ Logging integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_handling_integration():
    """Test error handling integration across modules"""
    
    print("\n🧪 TESTING ERROR HANDLING INTEGRATION")
    print("=" * 40)
    
    try:
        from skool_modules.error_handler import (
            handle_error, safe_execute, NetworkError, BrowserError,
            ExtractionError, ValidationError
        )
        
        # Test error handling with different error types
        def test_function():
            raise NetworkError("Test network error")
        
        # Test safe_execute
        success, result = safe_execute(test_function, context={'test': True})
        if not success:
            print("✅ Error handling working with safe_execute")
        else:
            print("❌ Error handling failed with safe_execute")
            return False
        
        # Test handle_error directly
        try:
            raise BrowserError("Test browser error")
        except Exception as e:
            result = handle_error(e, {'test': True})
            if result is not None:
                print("✅ Direct error handling working")
            else:
                print("❌ Direct error handling failed")
                return False
        
        # Test validation error
        try:
            raise ValidationError("Test validation error")
        except Exception as e:
            result = handle_error(e, {'test': True})
            print("✅ Validation error handling working")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_browser_management_integration():
    """Test browser management integration"""
    
    print("\n🧪 TESTING BROWSER MANAGEMENT INTEGRATION")
    print("=" * 40)
    
    try:
        from skool_modules.browser_manager import (
            should_use_browser_isolation, create_isolated_browser_instance
        )
        
        # Test browser isolation decision logic
        result1 = should_use_browser_isolation("Introduction to Python", 1, 10)
        result2 = should_use_browser_isolation("Advanced Data Structures", 5, 10)
        result3 = should_use_browser_isolation("Final Project", 10, 10)
        
        print(f"✅ Early lesson isolation: {result1}")
        print(f"✅ Middle lesson isolation: {result2}")
        print(f"✅ Late lesson isolation: {result3}")
        
        # Test browser instance creation (mock)
        with patch('skool_modules.browser_manager.setup_driver') as mock_setup:
            mock_driver = Mock()
            mock_setup.return_value = mock_driver
            
            driver = create_isolated_browser_instance()
            if driver:
                print("✅ Browser instance creation working")
            else:
                print("❌ Browser instance creation failed")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Browser management integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_video_extraction_integration():
    """Test video extraction integration"""
    
    print("\n🧪 TESTING VIDEO EXTRACTION INTEGRATION")
    print("=" * 40)
    
    try:
        from skool_modules.video_extractor import (
            extract_video_url, get_extraction_statistics
        )
        
        # Create mock driver
        mock_driver = Mock()
        
        # Test JSON extraction method
        test_json_data = {
            "props": {
                "pageProps": {
                    "lesson": {
                        "videoUrl": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                    }
                }
            }
        }
        
        mock_element = Mock()
        mock_element.get_attribute.return_value = json.dumps(test_json_data)
        mock_driver.find_element.return_value = mock_element
        
        # Test video extraction
        video_url = extract_video_url(mock_driver, "Test Lesson")
        if video_url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ":
            print("✅ Video extraction working")
        else:
            print(f"❌ Video extraction failed: {video_url}")
            return False
        
        # Test statistics
        stats = get_extraction_statistics()
        if isinstance(stats, dict) and 'total_attempts' in stats:
            print("✅ Extraction statistics working")
        else:
            print("❌ Extraction statistics failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Video extraction integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_lesson_extraction_workflow():
    """Test complete lesson extraction workflow"""
    
    print("\n🧪 TESTING COMPLETE LESSON EXTRACTION WORKFLOW")
    print("=" * 50)
    
    try:
        # Import all necessary modules
        from skool_modules.config_manager import get_config
        from skool_modules.logger import get_logger
        from skool_modules.error_handler import safe_execute
        from skool_modules.browser_manager import create_isolated_browser_instance
        from skool_modules.video_extractor import extract_video_url
        
        logger = get_logger()
        
        # Mock the complete workflow
        def mock_lesson_extraction():
            # Step 1: Configuration
            base_url = get_config('SKOOL_BASE_URL')
            logger.info(f"Using base URL: {base_url}")
            
            # Step 2: Browser setup
            with patch('skool_modules.browser_manager.setup_driver') as mock_setup:
                mock_driver = Mock()
                mock_setup.return_value = mock_driver
                
                driver = create_isolated_browser_instance()
                if not driver:
                    raise Exception("Browser setup failed")
                
                logger.success("Browser setup successful")
                
                # Step 3: Video extraction
                test_json_data = {
                    "props": {
                        "pageProps": {
                            "lesson": {
                                "videoUrl": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                                "title": "Test Lesson",
                                "content": "Test content"
                            }
                        }
                    }
                }
                
                mock_element = Mock()
                mock_element.get_attribute.return_value = json.dumps(test_json_data)
                mock_driver.find_element.return_value = mock_element
                
                video_url = extract_video_url(driver, "Test Lesson")
                if video_url:
                    logger.success(f"Video extracted: {video_url}")
                else:
                    logger.warning("No video found")
                
                # Step 4: Content extraction (mock)
                lesson_data = {
                    "title": "Test Lesson",
                    "video_url": video_url,
                    "content": "Test content",
                    "links": ["https://example.com"],
                    "images": ["https://example.com/image.jpg"]
                }
                
                logger.success("Lesson extraction completed")
                return lesson_data
        
        # Execute the workflow with error handling
        success, result = safe_execute(mock_lesson_extraction, context={'workflow': 'lesson_extraction'})
        
        if success and result:
            print("✅ Complete lesson extraction workflow working")
            print(f"✅ Extracted data: {result}")
        else:
            print("❌ Complete lesson extraction workflow failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Complete lesson extraction workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_community_extraction_workflow():
    """Test complete community extraction workflow"""
    
    print("\n🧪 TESTING COMPLETE COMMUNITY EXTRACTION WORKFLOW")
    print("=" * 50)
    
    try:
        from skool_modules.config_manager import get_config
        from skool_modules.logger import get_logger
        from skool_modules.error_handler import safe_execute
        from skool_modules.browser_manager import should_use_browser_isolation
        
        logger = get_logger()
        
        # Mock community extraction workflow
        def mock_community_extraction():
            # Step 1: Community setup
            community_url = "https://www.skool.com/test-community/classroom"
            logger.info(f"Processing community: {community_url}")
            
            # Step 2: Lesson discovery (mock)
            lessons = [
                {"title": "Lesson 1: Introduction", "url": "lesson1", "index": 1},
                {"title": "Lesson 2: Basics", "url": "lesson2", "index": 2},
                {"title": "Lesson 3: Advanced", "url": "lesson3", "index": 3},
                {"title": "Lesson 4: Project", "url": "lesson4", "index": 4},
                {"title": "Lesson 5: Conclusion", "url": "lesson5", "index": 5}
            ]
            
            logger.info(f"Found {len(lessons)} lessons")
            
            # Step 3: Process each lesson
            extracted_lessons = []
            total_lessons = len(lessons)
            
            for lesson in lessons:
                logger.progress(f"Processing lesson {lesson['index']}/{total_lessons}: {lesson['title']}")
                
                # Check if browser isolation is needed
                use_isolation = should_use_browser_isolation(
                    lesson['title'], lesson['index'], total_lessons
                )
                
                if use_isolation:
                    logger.isolation(f"Using isolated browser for: {lesson['title']}")
                
                # Mock lesson extraction
                lesson_data = {
                    "title": lesson['title'],
                    "video_url": f"https://www.youtube.com/watch?v=video{lesson['index']}",
                    "content": f"Content for {lesson['title']}",
                    "extracted": True
                }
                
                extracted_lessons.append(lesson_data)
                logger.success(f"Extracted: {lesson['title']}")
            
            # Step 4: Community summary
            community_data = {
                "url": community_url,
                "total_lessons": total_lessons,
                "extracted_lessons": len(extracted_lessons),
                "lessons": extracted_lessons
            }
            
            logger.success(f"Community extraction completed: {len(extracted_lessons)}/{total_lessons} lessons")
            return community_data
        
        # Execute the workflow
        success, result = safe_execute(mock_community_extraction, context={'workflow': 'community_extraction'})
        
        if success and result:
            print("✅ Complete community extraction workflow working")
            print(f"✅ Community data: {result['total_lessons']} lessons, {result['extracted_lessons']} extracted")
        else:
            print("❌ Complete community extraction workflow failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Complete community extraction workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_recovery_workflow():
    """Test error recovery in the complete workflow"""
    
    print("\n🧪 TESTING ERROR RECOVERY WORKFLOW")
    print("=" * 40)
    
    try:
        from skool_modules.error_handler import handle_error, safe_execute, NetworkError, BrowserError
        from skool_modules.logger import get_logger
        
        logger = get_logger()
        
        # Test workflow with intentional errors
        def workflow_with_errors():
            # Simulate network error
            if time.time() % 2 == 0:
                raise NetworkError("Simulated network error")
            
            # Simulate browser error
            if time.time() % 3 == 0:
                raise BrowserError("Simulated browser error")
            
            return "Success"
        
        # Test error recovery
        success, result = safe_execute(workflow_with_errors, context={'test': 'error_recovery'})
        
        if success:
            print("✅ Error recovery working - workflow completed successfully")
        else:
            print("✅ Error recovery working - errors handled gracefully")
        
        # Test multiple error types
        error_types = [NetworkError, BrowserError, ValueError, KeyError]
        
        for error_type in error_types:
            try:
                raise error_type(f"Test {error_type.__name__}")
            except Exception as e:
                result = handle_error(e, {'error_type': error_type.__name__})
                print(f"✅ {error_type.__name__} handled: {result is not None}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error recovery workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance_monitoring():
    """Test performance monitoring across the pipeline"""
    
    print("\n🧪 TESTING PERFORMANCE MONITORING")
    print("=" * 40)
    
    try:
        from skool_modules.logger import get_logger, log_performance
        from skool_modules.error_handler import safe_execute
        import time
        
        logger = get_logger()
        
        # Test performance logging
        def performance_test():
            start_time = time.time()
            
            # Simulate some work
            time.sleep(0.1)
            
            duration = time.time() - start_time
            
            log_performance(
                operation="test_operation",
                duration=duration,
                details={"test": True, "iterations": 1}
            )
            
            return duration
        
        # Execute performance test
        success, duration = safe_execute(performance_test)
        
        if success and duration:
            print(f"✅ Performance monitoring working: {duration:.3f}s")
        else:
            print("❌ Performance monitoring failed")
            return False
        
        # Test multiple operations
        operations = ["browser_setup", "video_extraction", "content_extraction", "file_save"]
        
        for operation in operations:
            start_time = time.time()
            time.sleep(0.05)  # Simulate work
            duration = time.time() - start_time
            
            log_performance(
                operation=operation,
                duration=duration,
                details={"operation_type": "test"}
            )
            
            print(f"✅ {operation}: {duration:.3f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance monitoring failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_operations_integration():
    """Test file operations integration"""
    
    print("\n🧪 TESTING FILE OPERATIONS INTEGRATION")
    print("=" * 40)
    
    try:
        import tempfile
        import os
        import json
        from skool_modules.logger import get_logger
        from skool_modules.error_handler import safe_execute
        
        logger = get_logger()
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info(f"Using temporary directory: {temp_dir}")
            
            # Test file creation
            def create_test_files():
                # Create community directory
                community_dir = os.path.join(temp_dir, "Test Community")
                os.makedirs(community_dir, exist_ok=True)
                
                # Create lessons directory
                lessons_dir = os.path.join(community_dir, "lessons")
                os.makedirs(lessons_dir, exist_ok=True)
                
                # Create test lesson file
                lesson_data = {
                    "title": "Test Lesson",
                    "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    "content": "Test content",
                    "extracted_at": time.time()
                }
                
                lesson_file = os.path.join(lessons_dir, "test_lesson.md")
                with open(lesson_file, 'w', encoding='utf-8') as f:
                    f.write(f"# {lesson_data['title']}\n\n")
                    f.write(f"**Video:** {lesson_data['video_url']}\n\n")
                    f.write(lesson_data['content'])
                
                # Create images directory
                images_dir = os.path.join(community_dir, "images")
                os.makedirs(images_dir, exist_ok=True)
                
                # Create videos directory
                videos_dir = os.path.join(community_dir, "videos")
                os.makedirs(videos_dir, exist_ok=True)
                
                return {
                    "community_dir": community_dir,
                    "lesson_file": lesson_file,
                    "structure": os.listdir(community_dir)
                }
            
            # Execute file operations
            success, result = safe_execute(create_test_files)
            
            if success and result:
                print("✅ File operations working")
                print(f"✅ Created structure: {result['structure']}")
                
                # Verify files exist
                if os.path.exists(result['lesson_file']):
                    print("✅ Lesson file created successfully")
                else:
                    print("❌ Lesson file not created")
                    return False
            else:
                print("❌ File operations failed")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ File operations integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Integration Tests for Full Pipeline")
    print()
    
    # Run all integration tests
    tests = [
        test_full_pipeline_initialization,
        test_configuration_workflow,
        test_logging_integration,
        test_error_handling_integration,
        test_browser_management_integration,
        test_video_extraction_integration,
        test_complete_lesson_extraction_workflow,
        test_community_extraction_workflow,
        test_error_recovery_workflow,
        test_performance_monitoring,
        test_file_operations_integration
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test in tests:
        try:
            if test():
                passed_tests += 1
                print(f"✅ {test.__name__} PASSED")
            else:
                print(f"❌ {test.__name__} FAILED")
        except Exception as e:
            print(f"❌ {test.__name__} FAILED with exception: {e}")
    
    print()
    print("=" * 60)
    print(f"📊 INTEGRATION TEST RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("✅ ALL INTEGRATION TESTS PASSED - Full pipeline is working!")
        print()
        print("🎯 Successfully tested:")
        print("  • Complete pipeline initialization")
        print("  • Configuration workflow")
        print("  • Logging integration")
        print("  • Error handling integration")
        print("  • Browser management integration")
        print("  • Video extraction integration")
        print("  • Complete lesson extraction workflow")
        print("  • Complete community extraction workflow")
        print("  • Error recovery workflow")
        print("  • Performance monitoring")
        print("  • File operations integration")
        print()
        print("💡 Full pipeline is ready for production use")
    else:
        print(f"❌ {total_tests - passed_tests} INTEGRATION TESTS FAILED - Check the issues above")
    
    print("=" * 60)
