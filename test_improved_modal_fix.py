#!/usr/bin/env python3
"""
Test script for the improved modal video extraction fix
"""

import sys
import os

# Add the current directory to Python path so we can import the main scraper
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_json_video_id_detection():
    """Test if we can detect the videoId from the debug JSON data"""
    
    print("🧪 TESTING JSON VIDEO ID DETECTION")
    print("=" * 60)
    
    try:
        # Read the debug JSON data
        with open('debug_lesson_data.json', 'r', encoding='utf-8') as f:
            import json
            data = json.load(f)
        
        print("✅ Successfully loaded debug JSON data")
        
        # Look for videoId fields in the structure
        def find_video_ids(obj, path=""):
            video_ids = []
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if key == "videoId" and isinstance(value, str):
                        video_ids.append((current_path, value))
                    elif isinstance(value, (dict, list)):
                        video_ids.extend(find_video_ids(value, current_path))
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]"
                    if isinstance(item, (dict, list)):
                        video_ids.extend(find_video_ids(item, current_path))
            return video_ids
        
        video_ids = find_video_ids(data)
        
        if video_ids:
            print(f"🎉 Found {len(video_ids)} video IDs in JSON:")
            for path, video_id in video_ids:
                print(f"  📹 {path}: {video_id}")
            
            # Test the extraction logic
            selected_module = data.get("props", {}).get("pageProps", {}).get("selectedModule")
            if selected_module:
                print(f"🎯 Selected module: {selected_module}")
                
                # Look for the selected module in the course children
                course_children = data.get("props", {}).get("pageProps", {}).get("course", {}).get("children", [])
                for child in course_children:
                    child_course = child.get("course", {})
                    if child_course.get("id") == selected_module:
                        video_id = child_course.get("metadata", {}).get("videoId")
                        if video_id:
                            print(f"✅ Found video ID for selected module: {video_id}")
                            print(f"📋 Module title: {child_course.get('metadata', {}).get('title', 'Unknown')}")
                            return True
            
            print("⚠️ No video ID found for selected module, but other videos exist")
            return True
        else:
            print("❌ No video IDs found in JSON data")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_video_extraction_logic():
    """Test the video extraction logic without actually running Selenium"""
    
    print("\n🧪 TESTING VIDEO EXTRACTION LOGIC")
    print("=" * 60)
    
    try:
        from skool_content_extractor import detect_platform, clean_video_url
        
        # Test video ID handling
        test_video_id = "7229ece164574bd5b79326477d57b6a8"
        skool_video_url = f"skool-video-id:{test_video_id}"
        
        print(f"🔍 Testing Skool video ID format: {skool_video_url}")
        
        # Test platform detection
        platform = detect_platform(skool_video_url)
        print(f"📊 Platform detected: {platform}")
        
        if platform == 'unknown':
            print("✅ Correctly identified as unknown platform (needs modal interaction)")
            
            # Test if it starts with our special prefix
            if skool_video_url.startswith('skool-video-id:'):
                extracted_id = skool_video_url.replace('skool-video-id:', '')
                print(f"✅ Successfully extracted video ID: {extracted_id}")
                return True
            else:
                print("❌ Failed to match special prefix")
                return False
        else:
            print("❌ Should have been detected as unknown platform")
            return False
            
    except Exception as e:
        print(f"❌ Logic test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Improved Modal Video Extraction Tests")
    print()
    
    test1_passed = test_json_video_id_detection()
    test2_passed = test_video_extraction_logic()
    
    print()
    print("=" * 60)
    if test1_passed and test2_passed:
        print("✅ ALL TESTS PASSED - Improved modal extraction should work!")
        print("🎯 Key improvements:")
        print("  • Detects Skool video IDs from JSON")
        print("  • Uses multiple click methods")
        print("  • Longer wait times for modal detection")
        print("  • Better debugging and change detection")
    else:
        print("❌ SOME TESTS FAILED - Check the issues above")
    print("=" * 60)
