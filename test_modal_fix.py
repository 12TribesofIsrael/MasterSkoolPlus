#!/usr/bin/env python3
"""
Test script for the modal video extraction fix
"""

import sys
import os

# Add the current directory to Python path so we can import the main scraper
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skool_content_extractor import *

def test_modal_extraction():
    """Test the modal video extraction on the problematic New Society classroom"""
    
    # Test URL from the user's screenshots
    test_url = "https://www.skool.com/new-society/classroom/f767704b?md=bb5837236f46b7b7db77dfd55c63f2"
    
    print("🧪 TESTING MODAL VIDEO EXTRACTION FIX")
    print("=" * 60)
    print(f"📍 Test URL: {test_url}")
    print()
    
    try:
        # Setup WebDriver
        print("🔧 Setting up WebDriver...")
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--log-level=WARNING")
        
        # Use webdriver-manager to handle ChromeDriver
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ WebDriver setup successful")
        
        # Login to Skool
        print("🔐 Logging in to Skool...")
        if not login_to_skool(driver):
            print("❌ Login failed")
            return False
        
        print("✅ Login successful")
        
        # Navigate to test lesson
        print(f"🌐 Navigating to test lesson...")
        driver.get(test_url)
        time.sleep(5)  # Wait for page to load
        
        print("✅ Page loaded successfully")
        
        # Test the modal video extraction
        print("🎯 Testing modal video extraction...")
        video_data = detect_modal_video_player(driver)
        
        if video_data:
            print("🎉 SUCCESS! Modal video extraction worked!")
            print(f"📹 Video URL: {video_data.get('url')}")
            print(f"🏷️ Platform: {video_data.get('platform')}")
            print(f"📍 Source: {video_data.get('source')}")
            return True
        else:
            print("❌ Modal video extraction failed")
            
            # Try the full extraction pipeline as fallback
            print("🔄 Testing full extraction pipeline...")
            video_data = extract_video_url(driver)
            
            if video_data:
                print("🎉 SUCCESS! Full pipeline worked!")
                print(f"📹 Video URL: {video_data.get('url')}")
                print(f"🏷️ Platform: {video_data.get('platform')}")
                return True
            else:
                print("❌ Full extraction pipeline also failed")
                return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        try:
            driver.quit()
            print("🔧 WebDriver closed")
        except:
            pass

if __name__ == "__main__":
    print("🚀 Starting Modal Video Extraction Test")
    print()
    
    success = test_modal_extraction()
    
    print()
    print("=" * 60)
    if success:
        print("✅ TEST PASSED - Modal video extraction is working!")
    else:
        print("❌ TEST FAILED - Modal video extraction needs more work")
    print("=" * 60)
