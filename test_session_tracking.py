#!/usr/bin/env python3
"""
Test script for the enhanced session-level video tracking system
"""

import sys
import os
import json

# Add the current directory to Python path so we can import the main scraper
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_session_tracking_functions():
    """Test all session tracking functions without running the full scraper"""
    
    print("🧪 TESTING SESSION-LEVEL VIDEO TRACKING SYSTEM")
    print("=" * 60)
    
    try:
        # Import the session tracking functions
        from skool_content_extractor import (
            reset_session_tracking, 
            register_video_in_session,
            check_session_duplicate_early,
            print_session_statistics,
            save_session_tracking_report,
            SESSION_STATS,
            SESSION_VIDEO_TRACKING,
            SEEN_VIDEO_IDS_SESSION
        )
        
        print("✅ Successfully imported session tracking functions")
        
        # Test 1: Reset session tracking
        print("\n🔄 Testing reset_session_tracking()...")
        reset_session_tracking()
        
        # Verify reset worked
        if len(SEEN_VIDEO_IDS_SESSION) == 0 and len(SESSION_VIDEO_TRACKING) == 0:
            print("✅ Session tracking reset successfully")
        else:
            print("❌ Session tracking reset failed")
            return False
        
        # Test 2: Register new videos
        print("\n📝 Testing register_video_in_session()...")
        
        test_videos = [
            {
                'url': 'https://www.youtube.com/watch?v=ABC123unique',
                'lesson': 'Test Lesson 1',
                'method': 'METHOD_1_JSON',
                'platform': 'youtube'
            },
            {
                'url': 'https://www.loom.com/share/unique456',
                'lesson': 'Test Lesson 2', 
                'method': 'METHOD_2_CLICK',
                'platform': 'loom'
            },
            {
                'url': 'https://vimeo.com/987654321',
                'lesson': 'Test Lesson 3',
                'method': 'METHOD_3_IFRAME',
                'platform': 'vimeo'
            }
        ]
        
        # Register each video
        for video in test_videos:
            result = register_video_in_session(
                video['url'], 
                video['lesson'], 
                video['method'], 
                video['platform']
            )
            
            if result:
                print(f"✅ Successfully registered: {video['lesson']}")
            else:
                print(f"❌ Failed to register: {video['lesson']}")
                return False
        
        # Verify registration worked
        if SESSION_STATS['unique_videos_found'] == 3:
            print(f"✅ Correctly tracked {SESSION_STATS['unique_videos_found']} unique videos")
        else:
            print(f"❌ Expected 3 videos, got {SESSION_STATS['unique_videos_found']}")
            return False
        
        # Test 3: Duplicate detection
        print("\n🔍 Testing duplicate detection...")
        
        # Try to register a duplicate
        duplicate_result = register_video_in_session(
            'https://www.youtube.com/watch?v=ABC123unique',  # Same as first video
            'Test Lesson 4 (Duplicate)',
            'METHOD_2_CLICK',
            'youtube'
        )
        
        if not duplicate_result:
            print("✅ Duplicate correctly detected and blocked")
            print(f"✅ Duplicates blocked count: {SESSION_STATS['duplicates_blocked']}")
        else:
            print("❌ Duplicate was not detected!")
            return False
        
        # Test 4: Early duplicate detection
        print("\n⚡ Testing early duplicate detection...")
        
        early_duplicate = check_session_duplicate_early(
            'https://www.loom.com/share/unique456',  # Same as second video
            'Test Lesson 5 (Early Duplicate)',
            'METHOD_4_NETWORK'
        )
        
        if early_duplicate:
            print("✅ Early duplicate detection working correctly")
        else:
            print("❌ Early duplicate detection failed")
            return False
        
        # Test 5: Session statistics
        print("\n📊 Testing session statistics...")
        print_session_statistics()
        
        # Verify statistics
        expected_stats = {
            'lessons_processed': 0,  # We haven't processed actual lessons
            'videos_processed': 4,   # 3 unique + 1 duplicate
            'unique_videos_found': 3,
            'duplicates_blocked': 1
        }
        
        stats_correct = True
        for key, expected_value in expected_stats.items():
            actual_value = SESSION_STATS[key]
            if actual_value != expected_value:
                print(f"❌ Stats mismatch - {key}: expected {expected_value}, got {actual_value}")
                stats_correct = False
        
        if stats_correct:
            print("✅ Session statistics are correct")
        else:
            return False
        
        # Test 6: Session tracking report
        print("\n💾 Testing save_session_tracking_report()...")
        save_session_tracking_report()
        
        # Verify report file was created
        if os.path.exists('debug_session_tracking_report.json'):
            print("✅ Session tracking report file created")
            
            # Read and validate the report
            with open('debug_session_tracking_report.json', 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            required_sections = ['session_stats', 'video_tracking', 'seen_video_ids', 'report_generated']
            if all(section in report_data for section in required_sections):
                print("✅ Session tracking report has correct structure")
                print(f"✅ Report contains {len(report_data['video_tracking'])} video entries")
            else:
                print("❌ Session tracking report missing required sections")
                return False
        else:
            print("❌ Session tracking report file was not created")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_with_validation():
    """Test integration between session tracking and existing validation"""
    
    print("\n🧪 TESTING INTEGRATION WITH VALIDATION SYSTEM")
    print("=" * 50)
    
    try:
        from skool_content_extractor import (
            _final_video_validation,
            is_valid_lesson_video,
            reset_session_tracking,
            SESSION_STATS
        )
        
        # Reset for clean test
        reset_session_tracking()
        
        # Test valid video that should pass all checks
        valid_video_data = {
            'url': 'https://www.youtube.com/watch?v=VALID_UNIQUE_ID',
            'platform': 'youtube',
            'thumbnail': None,
            'duration': None
        }
        
        result = _final_video_validation(
            valid_video_data, 
            'Test Integration Lesson',
            'TEST_METHOD'
        )
        
        if result:
            print("✅ Valid video passed final validation with session tracking")
        else:
            print("❌ Valid video failed final validation")
            return False
        
        # Test that the same video is now blocked as duplicate
        duplicate_video_data = {
            'url': 'https://www.youtube.com/watch?v=VALID_UNIQUE_ID',  # Same URL
            'platform': 'youtube',
            'thumbnail': None,
            'duration': None
        }
        
        result2 = _final_video_validation(
            duplicate_video_data,
            'Test Integration Lesson 2 (Duplicate)',
            'TEST_METHOD_2'
        )
        
        if not result2:
            print("✅ Duplicate video correctly blocked by final validation")
            print(f"✅ Session duplicates blocked: {SESSION_STATS['duplicates_blocked']}")
        else:
            print("❌ Duplicate video was not blocked!")
            return False
        
        # Test known blacklisted video
        blacklisted_video_data = {
            'url': 'https://www.youtube.com/watch?v=65GvYDdzJWU',  # Known blacklisted
            'platform': 'youtube',
            'thumbnail': None,
            'duration': None
        }
        
        result3 = _final_video_validation(
            blacklisted_video_data,
            'Test Integration Lesson 3 (Blacklisted)',
            'TEST_METHOD_3'
        )
        
        if not result3:
            print("✅ Blacklisted video correctly blocked by validation")
        else:
            print("❌ Blacklisted video was not blocked!")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Integration testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_test_files():
    """Clean up test files created during testing"""
    test_files = [
        'debug_session_tracking_report.json',
        'debug_video_extraction_log.json'
    ]
    
    for file in test_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"🧹 Cleaned up: {file}")
            except Exception as e:
                print(f"⚠️ Could not remove {file}: {e}")

if __name__ == "__main__":
    print("🚀 Starting Enhanced Session Tracking System Tests")
    print()
    
    # Run tests
    test1_passed = test_session_tracking_functions()
    test2_passed = test_integration_with_validation()
    
    print()
    print("=" * 60)
    if test1_passed and test2_passed:
        print("✅ ALL TESTS PASSED - Enhanced session tracking is working!")
        print()
        print("🎯 Key features verified:")
        print("  • Session tracking reset and initialization")
        print("  • Video registration with comprehensive metadata")
        print("  • Early duplicate detection (before validation)")
        print("  • Session-level duplicate prevention")
        print("  • Integration with existing validation system")
        print("  • Comprehensive session statistics")
        print("  • Session tracking report generation")
        print("  • Blacklist and session duplicate blocking")
        print()
        print("📄 Session report saved as: debug_session_tracking_report.json")
        print("💡 This will prevent ANY video from being reused across lessons in a session")
    else:
        print("❌ SOME TESTS FAILED - Check the issues above")
    
    print()
    
    # Ask user if they want to keep the test files
    try:
        keep_files = input("Keep test files for inspection? (y/N): ").strip().lower()
        if keep_files != 'y':
            cleanup_test_files()
    except (KeyboardInterrupt, EOFError):
        print("\n🧹 Cleaning up test files...")
        cleanup_test_files()
    
    print("=" * 60)
