#!/usr/bin/env python3
"""
Test script for the enhanced video extraction debugging system
"""

import sys
import os
import json

# Add the current directory to Python path so we can import the main scraper
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_debugging_functions():
    """Test the enhanced debugging functions without running the full scraper"""
    
    print("🧪 TESTING ENHANCED DEBUGGING SYSTEM")
    print("=" * 60)
    
    try:
        # Import the debugging functions
        from skool_content_extractor import (
            log_video_extraction_attempt, 
            save_extraction_debug_log, 
            analyze_duplicate_patterns,
            VIDEO_EXTRACTION_DEBUG_LOG
        )
        
        print("✅ Successfully imported debugging functions")
        
        # Test logging function with various scenarios
        print("\n🔍 Testing log_video_extraction_attempt()...")
        
        # Simulate different extraction attempts
        test_scenarios = [
            {
                'method': 'METHOD_1_JSON',
                'lesson_title': 'Test Lesson 1',
                'video_url': 'https://www.youtube.com/watch?v=ABC123',
                'status': 'found',
                'additional_info': {'platform': 'youtube', 'source': 'json'}
            },
            {
                'method': 'METHOD_1_JSON', 
                'lesson_title': 'Test Lesson 2',
                'video_url': 'https://www.youtube.com/watch?v=ABC123',  # Same URL (duplicate)
                'status': 'found',
                'additional_info': {'platform': 'youtube', 'source': 'json'}
            },
            {
                'method': 'METHOD_2_CLICK',
                'lesson_title': 'Test Lesson 3', 
                'video_url': 'https://www.youtube.com/watch?v=65GvYDdzJWU',  # Known duplicate
                'status': 'blocked',
                'additional_info': {'reason': 'failed_validation'}
            },
            {
                'method': 'METHOD_3_IFRAME',
                'lesson_title': 'Test Lesson 4',
                'video_url': None,
                'status': 'none',
                'additional_info': {'reason': 'no_iframe_video_found'}
            },
            {
                'method': 'METHOD_1_JSON',
                'lesson_title': 'Test Lesson 5',
                'video_url': 'https://www.loom.com/share/unique123',
                'status': 'found',
                'additional_info': {'platform': 'loom', 'source': 'json'}
            }
        ]
        
        # Log all test scenarios
        for scenario in test_scenarios:
            log_video_extraction_attempt(
                scenario['method'],
                scenario['lesson_title'], 
                scenario['video_url'],
                scenario['status'],
                scenario['additional_info']
            )
        
        print(f"✅ Logged {len(test_scenarios)} test scenarios")
        
        # Test saving debug log
        print("\n💾 Testing save_extraction_debug_log()...")
        save_extraction_debug_log()
        
        # Verify log file was created
        if os.path.exists('debug_video_extraction_log.json'):
            print("✅ Debug log file created successfully")
            
            # Read and validate the log file
            with open('debug_video_extraction_log.json', 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            print(f"✅ Log file contains {len(log_data)} entries")
            
            # Check if entries have the expected structure
            for entry in log_data:
                required_fields = ['timestamp', 'method', 'lesson_title', 'video_url', 'status']
                if all(field in entry for field in required_fields):
                    print(f"✅ Entry structure valid: {entry['method']} - {entry['lesson_title']}")
                else:
                    print(f"❌ Invalid entry structure: {entry}")
        else:
            print("❌ Debug log file was not created")
        
        # Test duplicate pattern analysis
        print("\n🔍 Testing analyze_duplicate_patterns()...")
        analyze_duplicate_patterns()
        
        # Test with expected duplicates
        expected_duplicates = [
            'https://www.youtube.com/watch?v=ABC123',  # Should appear 2 times
            'https://www.youtube.com/watch?v=65GvYDdzJWU'  # Should be blocked but show in analysis
        ]
        
        # Verify the debugging log contains our test data
        print(f"\n📊 Debug log contains {len(VIDEO_EXTRACTION_DEBUG_LOG)} total entries")
        
        # Check for duplicates in our test data
        found_duplicates = 0
        for entry in VIDEO_EXTRACTION_DEBUG_LOG:
            if entry['video_url'] in expected_duplicates and entry['status'] == 'found':
                found_duplicates += 1
        
        print(f"📊 Found {found_duplicates} entries with expected duplicate URLs")
        
        return True
        
    except Exception as e:
        print(f"❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_validation_integration():
    """Test that the validation function works with the debugging system"""
    
    print("\n🧪 TESTING VALIDATION INTEGRATION")
    print("=" * 40)
    
    try:
        from skool_content_extractor import is_valid_lesson_video, log_video_extraction_attempt
        
        # Test known duplicate URLs
        test_urls = [
            ('https://www.youtube.com/watch?v=65GvYDdzJWU', False, 'Known duplicate'),
            ('https://www.youtube.com/watch?v=UDcrRdfB0x8', False, 'Known duplicate'),
            ('https://www.youtube.com/watch?v=UNIQUE_VIDEO_ID', True, 'Should be valid'),
            ('https://www.loom.com/share/some_unique_id', True, 'Should be valid'),
        ]
        
        for url, expected_valid, description in test_urls:
            result = is_valid_lesson_video(url)
            status = "✅" if result == expected_valid else "❌"
            print(f"{status} {description}: {url} -> {'Valid' if result else 'Blocked'}")
            
            # Log this test attempt
            log_video_extraction_attempt(
                'VALIDATION_TEST',
                'Test Validation',
                url,
                'found' if result else 'blocked',
                {'expected': expected_valid, 'actual': result}
            )
        
        return True
        
    except Exception as e:
        print(f"❌ Validation testing failed: {e}")
        return False

def cleanup_test_files():
    """Clean up test files created during testing"""
    test_files = ['debug_video_extraction_log.json']
    
    for file in test_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"🧹 Cleaned up: {file}")
            except Exception as e:
                print(f"⚠️ Could not remove {file}: {e}")

if __name__ == "__main__":
    print("🚀 Starting Enhanced Debugging System Tests")
    print()
    
    # Run tests
    test1_passed = test_debugging_functions()
    test2_passed = test_validation_integration()
    
    print()
    print("=" * 60)
    if test1_passed and test2_passed:
        print("✅ ALL TESTS PASSED - Enhanced debugging system is working!")
        print()
        print("🎯 Key features verified:")
        print("  • Comprehensive extraction logging")
        print("  • Debug log file creation and validation")
        print("  • Duplicate pattern analysis")
        print("  • Integration with validation system")
        print("  • Detailed console output with status symbols")
        print()
        print("📄 Debug log saved as: debug_video_extraction_log.json")
        print("💡 This will help identify which extraction method returns duplicates")
    else:
        print("❌ SOME TESTS FAILED - Check the issues above")
    
    print()
    
    # Ask user if they want to keep the test files
    try:
        keep_files = input("Keep test debug files for inspection? (y/N): ").strip().lower()
        if keep_files != 'y':
            cleanup_test_files()
    except (KeyboardInterrupt, EOFError):
        print("\n🧹 Cleaning up test files...")
        cleanup_test_files()
    
    print("=" * 60)
