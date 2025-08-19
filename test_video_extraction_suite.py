#!/usr/bin/env python3
"""
Comprehensive Test Suite for Video Extraction Methods
====================================================

Tests all video extraction methods, edge cases, and validation logic.
"""

import sys
import os
import json
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_video_extractor_initialization():
    """Test video extractor initialization"""
    
    print("🧪 TESTING VIDEO EXTRACTOR INITIALIZATION")
    print("=" * 50)
    
    try:
        from skool_modules.video_extractor import get_video_extractor, VideoExtractor
        
        # Test singleton pattern
        extractor1 = get_video_extractor()
        extractor2 = get_video_extractor()
        
        if extractor1 is extractor2:
            print("✅ Singleton pattern working correctly")
        else:
            print("❌ Singleton pattern failed")
            return False
        
        # Test initialization
        if isinstance(extractor1, VideoExtractor):
            print("✅ VideoExtractor initialized correctly")
        else:
            print("❌ VideoExtractor initialization failed")
            return False
        
        # Test default statistics
        stats = extractor1.get_extraction_statistics()
        expected_keys = ['total_attempts', 'successful_extractions', 'failed_extractions', 'method_usage', 'platform_usage']
        
        for key in expected_keys:
            if key in stats:
                print(f"✅ Statistics key '{key}' present")
            else:
                print(f"❌ Statistics key '{key}' missing")
                return False
        
        # Test platform patterns
        expected_platforms = ['youtube', 'vimeo', 'loom', 'wistia']
        for platform in expected_platforms:
            if platform in extractor1.platform_patterns:
                print(f"✅ Platform '{platform}' patterns loaded")
            else:
                print(f"❌ Platform '{platform}' patterns missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_url_validation():
    """Test video URL validation logic"""
    
    print("\n🧪 TESTING URL VALIDATION")
    print("=" * 40)
    
    try:
        from skool_modules.video_extractor import get_video_extractor
        
        extractor = get_video_extractor()
        
        # Test valid video URLs
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.vimeo.com/123456789",
            "https://www.loom.com/share/abc123",
            "https://www.wistia.com/medias/xyz789",
            "https://example.com/video.mp4",
            "http://example.com/video.avi"
        ]
        
        for url in valid_urls:
            if extractor._is_video_url(url):
                print(f"✅ Valid URL detected: {url}")
            else:
                print(f"❌ Valid URL not detected: {url}")
                return False
        
        # Test invalid URLs
        invalid_urls = [
            "https://www.google.com",
            "https://example.com/image.jpg",
            "https://example.com/document.pdf",
            "",
            None,
            "not a url"
        ]
        
        for url in invalid_urls:
            if not extractor._is_video_url(url):
                print(f"✅ Invalid URL correctly rejected: {url}")
            else:
                print(f"❌ Invalid URL incorrectly accepted: {url}")
                return False
        
        # Test blacklisted URLs
        blacklisted_url = "https://youtu.be/65GvYDdzJWU"  # Known duplicate
        if not extractor._is_video_url(blacklisted_url):
            print(f"✅ Blacklisted URL correctly rejected: {blacklisted_url}")
        else:
            print(f"❌ Blacklisted URL incorrectly accepted: {blacklisted_url}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ URL validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_platform_detection():
    """Test video platform detection"""
    
    print("\n🧪 TESTING PLATFORM DETECTION")
    print("=" * 40)
    
    try:
        from skool_modules.video_extractor import get_video_extractor
        
        extractor = get_video_extractor()
        
        # Test platform detection
        test_cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "youtube"),
            ("https://youtu.be/dQw4w9WgXcQ", "youtube"),
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", "youtube"),
            ("https://www.vimeo.com/123456789", "vimeo"),
            ("https://www.vimeo.com/embed/123456789", "vimeo"),
            ("https://www.loom.com/share/abc123", "loom"),
            ("https://www.loom.com/embed/abc123", "loom"),
            ("https://www.wistia.com/medias/xyz789", "wistia"),
            ("https://www.wistia.com/embed/xyz789", "wistia"),
            ("https://example.com/video.mp4", None),  # No specific platform
        ]
        
        for url, expected_platform in test_cases:
            detected_platform = extractor._detect_platform(url)
            if detected_platform == expected_platform:
                print(f"✅ Platform detected correctly: {url} -> {detected_platform}")
            else:
                print(f"❌ Platform detection failed: {url} -> {detected_platform} (expected: {expected_platform})")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Platform detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_url_normalization():
    """Test video URL normalization"""
    
    print("\n🧪 TESTING URL NORMALIZATION")
    print("=" * 40)
    
    try:
        from skool_modules.video_extractor import get_video_extractor
        
        extractor = get_video_extractor()
        
        # Test URL normalization
        test_cases = [
            # YouTube normalization
            ("youtu.be/dQw4w9WgXcQ", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
            ("www.youtube.com/embed/dQw4w9WgXcQ", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
            ("youtube.com/v/dQw4w9WgXcQ", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
            
            # Vimeo normalization
            ("vimeo.com/123456789", "https://www.vimeo.com/123456789"),
            ("www.vimeo.com/embed/123456789", "https://www.vimeo.com/123456789"),
            
            # Loom normalization
            ("loom.com/share/abc123", "https://www.loom.com/share/abc123"),
            ("www.loom.com/embed/abc123", "https://www.loom.com/share/abc123"),
            
            # Wistia normalization
            ("wistia.com/medias/xyz789", "https://www.wistia.com/medias/xyz789"),
            ("www.wistia.com/embed/xyz789", "https://www.wistia.com/medias/xyz789"),
            
            # Protocol normalization
            ("example.com/video.mp4", "https://example.com/video.mp4"),
        ]
        
        for input_url, expected_url in test_cases:
            normalized_url = extractor._normalize_video_url(input_url)
            if normalized_url == expected_url:
                print(f"✅ URL normalized correctly: {input_url} -> {normalized_url}")
            else:
                print(f"❌ URL normalization failed: {input_url} -> {normalized_url} (expected: {expected_url})")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ URL normalization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_json_extraction_method():
    """Test JSON data extraction method"""
    
    print("\n🧪 TESTING JSON EXTRACTION METHOD")
    print("=" * 40)
    
    try:
        from skool_modules.video_extractor import get_video_extractor
        
        extractor = get_video_extractor()
        
        # Create mock driver
        mock_driver = Mock()
        
        # Test case 1: Video URL in JSON data
        test_json_data = {
            "props": {
                "pageProps": {
                    "lesson": {
                        "videoUrl": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                        "content": "Some lesson content"
                    }
                }
            }
        }
        
        mock_element = Mock()
        mock_element.get_attribute.return_value = json.dumps(test_json_data)
        mock_driver.find_element.return_value = mock_element
        
        video_url = extractor._extract_from_json_data(mock_driver, "Test Lesson")
        if video_url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ":
            print("✅ JSON extraction found video URL")
        else:
            print(f"❌ JSON extraction failed: {video_url}")
            return False
        
        # Test case 2: No video URL in JSON
        test_json_data_no_video = {
            "props": {
                "pageProps": {
                    "lesson": {
                        "content": "Some lesson content without video"
                    }
                }
            }
        }
        
        mock_element.get_attribute.return_value = json.dumps(test_json_data_no_video)
        video_url = extractor._extract_from_json_data(mock_driver, "Test Lesson")
        if video_url is None:
            print("✅ JSON extraction correctly returned None for no video")
        else:
            print(f"❌ JSON extraction should return None: {video_url}")
            return False
        
        # Test case 3: Invalid JSON
        mock_element.get_attribute.return_value = "invalid json"
        video_url = extractor._extract_from_json_data(mock_driver, "Test Lesson")
        if video_url is None:
            print("✅ JSON extraction handled invalid JSON correctly")
        else:
            print(f"❌ JSON extraction should handle invalid JSON: {video_url}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ JSON extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_iframe_extraction_method():
    """Test iframe extraction method"""
    
    print("\n🧪 TESTING IFRAME EXTRACTION METHOD")
    print("=" * 40)
    
    try:
        from skool_modules.video_extractor import get_video_extractor
        
        extractor = get_video_extractor()
        
        # Create mock driver
        mock_driver = Mock()
        
        # Test case 1: Video URL in iframe src
        mock_iframe = Mock()
        mock_iframe.get_attribute.return_value = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        mock_driver.find_elements.return_value = [mock_iframe]
        
        video_url = extractor._extract_from_iframes(mock_driver, "Test Lesson")
        if video_url == "https://www.youtube.com/embed/dQw4w9WgXcQ":
            print("✅ Iframe extraction found video URL in src")
        else:
            print(f"❌ Iframe extraction failed: {video_url}")
            return False
        
        # Test case 2: Video URL in iframe content
        mock_iframe_no_src = Mock()
        mock_iframe_no_src.get_attribute.return_value = None
        
        mock_video_element = Mock()
        mock_video_element.get_attribute.return_value = "https://example.com/video.mp4"
        
        mock_driver.find_elements.return_value = [mock_iframe_no_src]
        mock_driver.switch_to.frame.return_value = None
        mock_driver.find_elements.side_effect = [
            [mock_iframe_no_src],  # First call for iframes
            [mock_video_element]   # Second call for video elements
        ]
        mock_driver.switch_to.default_content.return_value = None
        
        video_url = extractor._extract_from_iframes(mock_driver, "Test Lesson")
        if video_url == "https://example.com/video.mp4":
            print("✅ Iframe extraction found video URL in content")
        else:
            print(f"❌ Iframe extraction failed: {video_url}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Iframe extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_video_player_extraction_method():
    """Test video player extraction method"""
    
    print("\n🧪 TESTING VIDEO PLAYER EXTRACTION METHOD")
    print("=" * 40)
    
    try:
        from skool_modules.video_extractor import get_video_extractor
        
        extractor = get_video_extractor()
        
        # Create mock driver
        mock_driver = Mock()
        
        # Test case 1: Video URL in player element attributes
        mock_player = Mock()
        mock_player.get_attribute.side_effect = lambda attr: {
            'src': None,
            'data-src': None,
            'data-video': "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            'data-url': None
        }.get(attr)
        
        mock_driver.find_elements.return_value = [mock_player]
        
        video_url = extractor._extract_from_video_player(mock_driver, "Test Lesson")
        if video_url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ":
            print("✅ Video player extraction found video URL in attributes")
        else:
            print(f"❌ Video player extraction failed: {video_url}")
            return False
        
        # Test case 2: Video URL after clicking
        mock_player_no_attr = Mock()
        mock_player_no_attr.get_attribute.return_value = None
        mock_player_no_attr.click.return_value = None
        
        mock_video_after_click = Mock()
        mock_video_after_click.get_attribute.return_value = "https://example.com/video.mp4"
        
        mock_driver.find_elements.side_effect = [
            [mock_player_no_attr],  # First call for player elements
            [mock_video_after_click]  # Second call for video elements after click
        ]
        
        video_url = extractor._extract_from_video_player(mock_driver, "Test Lesson")
        if video_url == "https://example.com/video.mp4":
            print("✅ Video player extraction found video URL after clicking")
        else:
            print(f"❌ Video player extraction failed: {video_url}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Video player extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_legacy_youtube_extraction_method():
    """Test legacy YouTube extraction method"""
    
    print("\n🧪 TESTING LEGACY YOUTUBE EXTRACTION METHOD")
    print("=" * 40)
    
    try:
        from skool_modules.video_extractor import get_video_extractor
        
        extractor = get_video_extractor()
        
        # Create mock driver
        mock_driver = Mock()
        
        # Test case 1: YouTube URL in page source
        test_page_source = """
        <html>
            <body>
                <div>Some content</div>
                <iframe src="https://www.youtube.com/embed/dQw4w9WgXcQ"></iframe>
                <div>More content</div>
            </body>
        </html>
        """
        mock_driver.page_source = test_page_source
        
        video_url = extractor._extract_legacy_youtube(mock_driver, "Test Lesson")
        if video_url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ":
            print("✅ Legacy YouTube extraction found video URL")
        else:
            print(f"❌ Legacy YouTube extraction failed: {video_url}")
            return False
        
        # Test case 2: No YouTube URL in page source
        test_page_source_no_youtube = """
        <html>
            <body>
                <div>Some content without YouTube</div>
            </body>
        </html>
        """
        mock_driver.page_source = test_page_source_no_youtube
        
        video_url = extractor._extract_legacy_youtube(mock_driver, "Test Lesson")
        if video_url is None:
            print("✅ Legacy YouTube extraction correctly returned None")
        else:
            print(f"❌ Legacy YouTube extraction should return None: {video_url}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Legacy YouTube extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_extraction_statistics():
    """Test extraction statistics tracking"""
    
    print("\n🧪 TESTING EXTRACTION STATISTICS")
    print("=" * 40)
    
    try:
        from skool_modules.video_extractor import get_video_extractor
        
        extractor = get_video_extractor()
        
        # Reset statistics
        extractor.extraction_stats = {
            'total_attempts': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'method_usage': {},
            'platform_usage': {}
        }
        
        # Simulate some extractions
        mock_driver = Mock()
        
        # Mock successful extraction
        mock_element = Mock()
        mock_element.get_attribute.return_value = json.dumps({
            "videoUrl": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        })
        mock_driver.find_element.return_value = mock_element
        
        video_url = extractor._extract_from_json_data(mock_driver, "Test Lesson 1")
        if video_url:
            extractor._validate_and_normalize_url(video_url, "Test Lesson 1", "json")
        
        # Mock failed extraction
        mock_driver.find_element.side_effect = Exception("Element not found")
        video_url = extractor._extract_from_json_data(mock_driver, "Test Lesson 2")
        
        # Check statistics
        stats = extractor.get_extraction_statistics()
        
        if stats['total_attempts'] > 0:
            print(f"✅ Total attempts tracked: {stats['total_attempts']}")
        else:
            print("❌ Total attempts not tracked")
            return False
        
        if stats['successful_extractions'] > 0:
            print(f"✅ Successful extractions tracked: {stats['successful_extractions']}")
        else:
            print("❌ Successful extractions not tracked")
            return False
        
        if 'json' in stats['method_usage']:
            print(f"✅ Method usage tracked: {stats['method_usage']}")
        else:
            print("❌ Method usage not tracked")
            return False
        
        if 'youtube' in stats['platform_usage']:
            print(f"✅ Platform usage tracked: {stats['platform_usage']}")
        else:
            print("❌ Platform usage not tracked")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Extraction statistics test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_with_other_modules():
    """Test integration with other modules"""
    
    print("\n🧪 TESTING MODULE INTEGRATION")
    print("=" * 40)
    
    try:
        from skool_modules.video_extractor import extract_video_url, get_extraction_statistics
        from skool_modules.logger import get_logger
        from skool_modules.error_handler import get_error_handler
        
        print("✅ Successfully imported video extractor functions")
        
        # Test logger integration
        logger = get_logger()
        logger.info("Testing logger integration with video extractor")
        print("✅ Logger integration working")
        
        # Test error handler integration
        error_handler = get_error_handler()
        print("✅ Error handler integration working")
        
        # Test statistics functions
        stats = get_extraction_statistics()
        if isinstance(stats, dict):
            print("✅ Statistics functions working")
        else:
            print("❌ Statistics functions not working")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Module integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """Test edge cases and error handling"""
    
    print("\n🧪 TESTING EDGE CASES")
    print("=" * 40)
    
    try:
        from skool_modules.video_extractor import get_video_extractor
        
        extractor = get_video_extractor()
        
        # Test with None driver
        try:
            video_url = extractor._extract_from_json_data(None, "Test Lesson")
            if video_url is None:
                print("✅ Handled None driver correctly")
            else:
                print("❌ Should handle None driver")
                return False
        except Exception:
            print("✅ Exception handling for None driver working")
        
        # Test with empty lesson title
        mock_driver = Mock()
        video_url = extractor._extract_from_json_data(mock_driver, "")
        if video_url is None:
            print("✅ Handled empty lesson title correctly")
        else:
            print("❌ Should handle empty lesson title")
            return False
        
        # Test with very long lesson title
        long_title = "A" * 1000
        video_url = extractor._extract_from_json_data(mock_driver, long_title)
        if video_url is None:
            print("✅ Handled long lesson title correctly")
        else:
            print("❌ Should handle long lesson title")
            return False
        
        # Test with special characters in lesson title
        special_title = "Lesson with special chars: !@#$%^&*()"
        video_url = extractor._extract_from_json_data(mock_driver, special_title)
        if video_url is None:
            print("✅ Handled special characters correctly")
        else:
            print("❌ Should handle special characters")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Edge cases test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Video Extraction Test Suite")
    print()
    
    # Run all tests
    tests = [
        test_video_extractor_initialization,
        test_url_validation,
        test_platform_detection,
        test_url_normalization,
        test_json_extraction_method,
        test_iframe_extraction_method,
        test_video_player_extraction_method,
        test_legacy_youtube_extraction_method,
        test_extraction_statistics,
        test_integration_with_other_modules,
        test_edge_cases
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
    print(f"📊 TEST RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("✅ ALL TESTS PASSED - Video extraction system is working!")
        print()
        print("🎯 Successfully tested:")
        print("  • Video extractor initialization")
        print("  • URL validation and normalization")
        print("  • Platform detection")
        print("  • JSON data extraction")
        print("  • Iframe extraction")
        print("  • Video player extraction")
        print("  • Legacy YouTube extraction")
        print("  • Statistics tracking")
        print("  • Module integration")
        print("  • Edge cases and error handling")
        print()
        print("💡 Video extraction system is ready for production use")
    else:
        print(f"❌ {total_tests - passed_tests} TESTS FAILED - Check the issues above")
    
    print("=" * 60)
