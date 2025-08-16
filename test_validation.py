#!/usr/bin/env python3
"""
Quick test script to verify the validation function works correctly
"""

import sys
import os

# Add the current directory to the path so we can import from skool_content_extractor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skool_content_extractor import is_valid_lesson_video

def test_validation():
    """Test the validation function with known duplicate URLs"""
    
    print("🧪 TESTING VALIDATION FUNCTION")
    print("=" * 50)
    
    # Test cases - these should be BLOCKED
    blocked_urls = [
        "https://youtu.be/65GvYDdzJWU",
        "https://www.youtube.com/watch?v=65GvYDdzJWU",
        "https://www.youtube.com/embed/65GvYDdzJWU",
        "https://youtube-nocookie.com/embed/65GvYDdzJWU",
        "https://youtu.be/UDcrRdfB0x8",
        "https://youtu.be/7snrj0uEaDw",
        "https://youtu.be/YTrIwmIdaJI",
    ]
    
    # Test cases - these should be ALLOWED
    allowed_urls = [
        "https://www.loom.com/share/a532feff0368460986b819412fb3a11a",
        "https://www.loom.com/share/5b641b8e492c462e809712827d220ed3",
        "https://youtu.be/DIFFERENT_VIDEO_ID",
        "https://vimeo.com/123456789",
    ]
    
    print("\n🚫 TESTING BLOCKED URLs (should return False):")
    print("-" * 40)
    for url in blocked_urls:
        result = is_valid_lesson_video(url)
        status = "✅ CORRECTLY BLOCKED" if not result else "❌ INCORRECTLY ALLOWED"
        print(f"{status}: {url}")
        print()
    
    print("\n✅ TESTING ALLOWED URLs (should return True):")
    print("-" * 40)
    for url in allowed_urls:
        result = is_valid_lesson_video(url)
        status = "✅ CORRECTLY ALLOWED" if result else "❌ INCORRECTLY BLOCKED"
        print(f"{status}: {url}")
        print()

if __name__ == "__main__":
    test_validation()
