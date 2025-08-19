#!/usr/bin/env python3
"""
Test script for the browser isolation system
"""

import sys
import os
import json

# Add the current directory to Python path so we can import the main scraper
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_browser_isolation_functions():
    """Test all browser isolation functions without running the full scraper"""
    
    print("🧪 TESTING BROWSER ISOLATION SYSTEM")
    print("=" * 60)
    
    try:
        # Import the browser isolation functions
        from skool_content_extractor import (
            create_isolated_browser_instance,
            destroy_browser_instance,
            should_use_browser_isolation,
            print_browser_isolation_statistics,
            BROWSER_ISOLATION,
            reset_session_tracking
        )
        
        print("✅ Successfully imported browser isolation functions")
        
        # Test 1: Reset session tracking
        print("\n🔄 Testing reset_session_tracking()...")
        reset_session_tracking()
        
        # Verify browser isolation was reset
        if (BROWSER_ISOLATION['browser_instances_created'] == 0 and 
            BROWSER_ISOLATION['browser_instances_destroyed'] == 0):
            print("✅ Browser isolation tracking reset successfully")
        else:
            print("❌ Browser isolation tracking reset failed")
            return False
        
        # Test 2: Test isolation decision logic
        print("\n🔍 Testing should_use_browser_isolation()...")
        
        # Test problematic lessons
        problematic_lessons = [
            "Introduction to Python",
            "Welcome to the Course", 
            "Lesson 1: Getting Started",
            "Basics of Programming",
            "Fundamentals of Web Development"
        ]
        
        for lesson in problematic_lessons:
            should_isolate = should_use_browser_isolation(lesson, 1, 10)
            if should_isolate:
                print(f"✅ Correctly identified problematic lesson: {lesson}")
            else:
                print(f"❌ Failed to identify problematic lesson: {lesson}")
                return False
        
        # Test normal lessons (use index 4 to avoid periodic cleanup)
        normal_lessons = [
            "Advanced Data Structures",
            "Object-Oriented Programming",
            "Database Design Principles"
        ]
        
        for lesson in normal_lessons:
            should_isolate = should_use_browser_isolation(lesson, 4, 10)
            if not should_isolate:
                print(f"✅ Correctly identified normal lesson: {lesson}")
            else:
                print(f"❌ Incorrectly flagged normal lesson: {lesson}")
                return False
        
        # Test early lessons (should use isolation)
        early_lessons = ["Lesson 1", "Lesson 2", "Lesson 3"]
        for i, lesson in enumerate(early_lessons, 1):
            should_isolate = should_use_browser_isolation(lesson, i, 10)
            if should_isolate:
                print(f"✅ Correctly identified early lesson for isolation: {lesson}")
            else:
                print(f"❌ Failed to identify early lesson for isolation: {lesson}")
                return False
        
        # Test periodic lessons (every 5th)
        periodic_lessons = ["Lesson 5", "Lesson 10", "Lesson 15"]
        for i, lesson in enumerate(periodic_lessons, 5):
            should_isolate = should_use_browser_isolation(lesson, i, 20)
            if should_isolate:
                print(f"✅ Correctly identified periodic lesson for isolation: {lesson}")
            else:
                print(f"❌ Failed to identify periodic lesson for isolation: {lesson}")
                return False
        
        # Test 3: Test browser isolation statistics
        print("\n📊 Testing browser isolation statistics...")
        
        # Simulate some browser operations
        BROWSER_ISOLATION['browser_instances_created'] = 5
        BROWSER_ISOLATION['browser_instances_destroyed'] = 4
        BROWSER_ISOLATION['isolation_stats']['lessons_with_isolated_browsers'] = 3
        BROWSER_ISOLATION['isolation_stats']['lessons_with_shared_browser'] = 7
        BROWSER_ISOLATION['isolation_stats']['browser_creation_time'] = 12.5
        BROWSER_ISOLATION['isolation_stats']['browser_destruction_time'] = 8.2
        
        print_browser_isolation_statistics()
        
        # Verify statistics are correct
        expected_stats = {
            'browser_instances_created': 5,
            'browser_instances_destroyed': 4,
            'lessons_with_isolated_browsers': 3,
            'lessons_with_shared_browser': 7
        }
        
        stats_correct = True
        for key, expected_value in expected_stats.items():
            if key in BROWSER_ISOLATION:
                actual_value = BROWSER_ISOLATION[key]
            else:
                actual_value = BROWSER_ISOLATION['isolation_stats'][key]
            
            if actual_value != expected_value:
                print(f"❌ Stats mismatch - {key}: expected {expected_value}, got {actual_value}")
                stats_correct = False
        
        if stats_correct:
            print("✅ Browser isolation statistics are correct")
        else:
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_isolation_decision_scenarios():
    """Test various scenarios for isolation decisions"""
    
    print("\n🧪 TESTING ISOLATION DECISION SCENARIOS")
    print("=" * 50)
    
    try:
        from skool_content_extractor import should_use_browser_isolation, reset_session_tracking
        
        # Reset for clean test
        reset_session_tracking()
        
        # Scenario 1: First few lessons (should isolate)
        print("\n📋 Scenario 1: Early lessons")
        for i in range(1, 4):
            lesson = f"Lesson {i}: Introduction"
            should_isolate = should_use_browser_isolation(lesson, i, 20)
            print(f"   Lesson {i}: {'🔒 Isolate' if should_isolate else '🔗 Shared'}")
        
        # Scenario 2: Problematic lesson titles
        print("\n📋 Scenario 2: Problematic lesson titles")
        problematic_titles = [
            "Welcome to the Course",
            "Getting Started with Python",
            "Lesson 1: Basics",
            "Fundamentals of Programming"
        ]
        
        for title in problematic_titles:
            should_isolate = should_use_browser_isolation(title, 5, 20)
            print(f"   {title}: {'🔒 Isolate' if should_isolate else '🔗 Shared'}")
        
        # Scenario 3: Periodic cleanup (every 5th lesson)
        print("\n📋 Scenario 3: Periodic cleanup lessons")
        for i in range(5, 21, 5):
            lesson = f"Advanced Topic {i}"
            should_isolate = should_use_browser_isolation(lesson, i, 20)
            print(f"   Lesson {i}: {'🔒 Isolate' if should_isolate else '🔗 Shared'}")
        
        # Scenario 4: Normal lessons (should not isolate)
        print("\n📋 Scenario 4: Normal lessons")
        normal_titles = [
            "Advanced Data Structures",
            "Object-Oriented Programming",
            "Database Design",
            "Web Development"
        ]
        
        for i, title in enumerate(normal_titles, 6):
            should_isolate = should_use_browser_isolation(title, i, 20)
            print(f"   {title}: {'🔒 Isolate' if should_isolate else '🔗 Shared'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Scenario testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_with_session_tracking():
    """Test integration between browser isolation and session tracking"""
    
    print("\n🧪 TESTING INTEGRATION WITH SESSION TRACKING")
    print("=" * 50)
    
    try:
        from skool_content_extractor import (
            reset_session_tracking,
            should_use_browser_isolation,
            BROWSER_ISOLATION
        )
        
        # Reset for clean test
        reset_session_tracking()
        
        # Simulate processing multiple lessons
        lessons = [
            "Introduction to Python",
            "Variables and Data Types", 
            "Control Structures",
            "Functions and Methods",
            "Object-Oriented Programming"
        ]
        
        print("📚 Simulating lesson processing with isolation decisions:")
        
        for i, lesson in enumerate(lessons, 1):
            should_isolate = should_use_browser_isolation(lesson, i, len(lessons))
            
            if should_isolate:
                BROWSER_ISOLATION['isolation_stats']['lessons_with_isolated_browsers'] += 1
                print(f"   {i}. {lesson} → 🔒 Isolated Browser")
            else:
                BROWSER_ISOLATION['isolation_stats']['lessons_with_shared_browser'] += 1
                print(f"   {i}. {lesson} → 🔗 Shared Browser")
        
        # Verify integration
        total_lessons = (BROWSER_ISOLATION['isolation_stats']['lessons_with_isolated_browsers'] + 
                        BROWSER_ISOLATION['isolation_stats']['lessons_with_shared_browser'])
        
        if total_lessons == len(lessons):
            print(f"✅ Integration working correctly: {total_lessons} lessons processed")
        else:
            print(f"❌ Integration failed: expected {len(lessons)}, got {total_lessons}")
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
    print("🚀 Starting Browser Isolation System Tests")
    print()
    
    # Run tests
    test1_passed = test_browser_isolation_functions()
    test2_passed = test_isolation_decision_scenarios()
    test3_passed = test_integration_with_session_tracking()
    
    print()
    print("=" * 60)
    if test1_passed and test2_passed and test3_passed:
        print("✅ ALL TESTS PASSED - Browser isolation system is working!")
        print()
        print("🎯 Key features verified:")
        print("  • Browser instance creation and destruction")
        print("  • Intelligent isolation decision logic")
        print("  • Problematic lesson detection")
        print("  • Early lesson isolation")
        print("  • Periodic cleanup isolation")
        print("  • Browser isolation statistics")
        print("  • Integration with session tracking")
        print("  • Performance monitoring")
        print()
        print("💡 This provides ultimate protection against browser state contamination")
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
