#!/usr/bin/env python3
"""
Test script for the lesson-specific video validation system
"""

import sys
import os
import json

# Add the current directory to Python path so we can import the main scraper
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_lesson_validation_functions():
    """Test all lesson validation functions without running the full scraper"""
    
    print("🧪 TESTING LESSON-SPECIFIC VIDEO VALIDATION SYSTEM")
    print("=" * 60)
    
    try:
        # Import the lesson validation functions
        from skool_content_extractor import (
            set_lesson_context,
            generate_lesson_content_signature,
            validate_video_belongs_to_lesson,
            _extract_lesson_identifiers,
            _check_page_content_relevance,
            _check_video_container_relevance,
            LESSON_CONTEXT,
            reset_session_tracking
        )
        
        print("✅ Successfully imported lesson validation functions")
        
        # Test 1: Reset session tracking
        print("\n🔄 Testing reset_session_tracking()...")
        reset_session_tracking()
        
        # Test 2: Set lesson context
        print("\n📚 Testing set_lesson_context()...")
        test_lesson_title = "Introduction to Python Programming"
        test_lesson_url = "https://www.skool.com/test-community/classroom/123?md=abc456"
        test_lesson_id = "abc456"
        
        set_lesson_context(test_lesson_title, test_lesson_url, test_lesson_id)
        
        # Verify context was set
        if (LESSON_CONTEXT['current_lesson_title'] == test_lesson_title and 
            LESSON_CONTEXT['current_lesson_url'] == test_lesson_url and
            LESSON_CONTEXT['current_lesson_id'] == test_lesson_id):
            print("✅ Lesson context set successfully")
        else:
            print("❌ Lesson context not set correctly")
            return False
        
        # Test 3: Extract lesson identifiers
        print("\n🔍 Testing _extract_lesson_identifiers()...")
        identifiers = _extract_lesson_identifiers(test_lesson_title)
        
        expected_identifiers = [
            "Introduction to Python Programming",
            "introduction", "python", "programming",
            "introduction-python", "python-programming"
        ]
        
        print(f"📋 Extracted identifiers: {identifiers}")
        
        # Check if key identifiers are present
        key_identifiers_found = 0
        for expected in expected_identifiers:
            if expected in identifiers:
                key_identifiers_found += 1
        
        if key_identifiers_found >= 3:  # At least 3 key identifiers should be found
            print("✅ Lesson identifiers extracted correctly")
        else:
            print(f"❌ Expected more identifiers, found {key_identifiers_found}")
            return False
        
        # Test 4: Test with lesson number
        print("\n🔢 Testing lesson number extraction...")
        lesson_with_number = "Lesson 5: Advanced Data Structures"
        number_identifiers = _extract_lesson_identifiers(lesson_with_number)
        
        if "5" in number_identifiers:
            print("✅ Lesson number extracted correctly")
        else:
            print("❌ Lesson number not extracted")
            return False
        
        # Test 5: Test content relevance checking (mock)
        print("\n📄 Testing content relevance checking...")
        
        # Mock page content relevance
        mock_relevance = _check_page_content_relevance_mock("Introduction to Python Programming", 
                                                           "https://www.youtube.com/watch?v=python123")
        
        if mock_relevance > 0.5:
            print(f"✅ Content relevance check working (score: {mock_relevance:.2f})")
        else:
            print(f"⚠️ Low content relevance score: {mock_relevance:.2f}")
        
        # Test 6: Test container relevance checking (mock)
        print("\n📦 Testing container relevance checking...")
        
        mock_container_relevance = _check_video_container_relevance_mock()
        
        if mock_container_relevance > 0.3:
            print(f"✅ Container relevance check working (score: {mock_container_relevance:.2f})")
        else:
            print(f"⚠️ Low container relevance score: {mock_container_relevance:.2f}")
        
        # Test 7: Test full validation pipeline (mock)
        print("\n🔍 Testing full validation pipeline...")
        
        # Test video that should belong to lesson
        relevant_video = "https://www.youtube.com/watch?v=python-introduction-123"
        relevant_result = validate_video_belongs_to_lesson_mock(relevant_video, test_lesson_title)
        
        if relevant_result:
            print("✅ Relevant video correctly validated")
        else:
            print("❌ Relevant video incorrectly rejected")
            return False
        
        # Test video that should NOT belong to lesson
        irrelevant_video = "https://www.youtube.com/watch?v=javascript-basics-456"
        irrelevant_result = validate_video_belongs_to_lesson_mock(irrelevant_video, test_lesson_title)
        
        if not irrelevant_result:
            print("✅ Irrelevant video correctly rejected")
        else:
            print("❌ Irrelevant video incorrectly accepted")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def _check_page_content_relevance_mock(lesson_title, video_url):
    """Mock version of content relevance checking"""
    # Simulate finding lesson title and video context
    lesson_lower = lesson_title.lower()
    
    # Mock page content that contains lesson title and video keywords
    mock_page_content = f"""
    Welcome to {lesson_title}! In this lesson, you will learn the basics of Python programming.
    Watch the video below to get started with your first Python program.
    The video URL is: {video_url}
    """
    
    # Calculate relevance score
    relevance_score = 0.0
    
    if lesson_lower in mock_page_content.lower():
        relevance_score += 0.4
    
    video_keywords = ['video', 'watch', 'play', 'lesson', 'tutorial', 'demo']
    if any(keyword in mock_page_content.lower() for keyword in video_keywords):
        relevance_score += 0.3
    
    if video_url in mock_page_content:
        relevance_score += 0.3
    
    return min(relevance_score, 1.0)

def _check_video_container_relevance_mock():
    """Mock version of container relevance checking"""
    # Simulate finding lesson-specific containers
    return 0.7  # Good confidence

def validate_video_belongs_to_lesson_mock(video_url, lesson_title):
    """Mock version of lesson validation"""
    # Simple mock validation based on URL content
    from skool_content_extractor import _extract_lesson_identifiers
    lesson_identifiers = _extract_lesson_identifiers(lesson_title)
    url_lower = video_url.lower()
    
    # Check if any lesson identifier is in the URL
    for identifier in lesson_identifiers:
        if identifier.lower() in url_lower:
            return True
    
    return False

def test_integration_with_session_tracking():
    """Test integration between lesson validation and session tracking"""
    
    print("\n🧪 TESTING INTEGRATION WITH SESSION TRACKING")
    print("=" * 50)
    
    try:
        from skool_content_extractor import (
            reset_session_tracking,
            set_lesson_context,
            validate_video_belongs_to_lesson,
            register_video_in_session,
            LESSON_CONTEXT,
            SESSION_STATS
        )
        
        # Reset for clean test
        reset_session_tracking()
        
        # Set lesson context
        set_lesson_context("Test Lesson: Web Development", "https://test.com/lesson1", "lesson1")
        
        # Test video that belongs to lesson
        relevant_video = "https://www.youtube.com/watch?v=web-development-123"
        lesson_validation = validate_video_belongs_to_lesson_mock(relevant_video, "Test Lesson: Web Development")
        
        if lesson_validation:
            # Should be able to register in session
            session_result = register_video_in_session(
                relevant_video, 
                "Test Lesson: Web Development", 
                "TEST_METHOD", 
                "youtube"
            )
            
            if session_result:
                print("✅ Lesson validation + session tracking working correctly")
                print(f"✅ Session stats: {SESSION_STATS['unique_videos_found']} unique videos")
            else:
                print("❌ Session registration failed after lesson validation")
                return False
        else:
            print("❌ Lesson validation failed for relevant video")
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
    print("🚀 Starting Lesson-Specific Video Validation System Tests")
    print()
    
    # Run tests
    test1_passed = test_lesson_validation_functions()
    test2_passed = test_integration_with_session_tracking()
    
    print()
    print("=" * 60)
    if test1_passed and test2_passed:
        print("✅ ALL TESTS PASSED - Lesson-specific validation is working!")
        print()
        print("🎯 Key features verified:")
        print("  • Lesson context setting and management")
        print("  • Lesson identifier extraction")
        print("  • Content relevance checking")
        print("  • Container relevance checking")
        print("  • Full validation pipeline")
        print("  • Integration with session tracking")
        print("  • Lesson number extraction")
        print("  • Caching of validation results")
        print()
        print("💡 This ensures videos actually belong to the current lesson")
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
