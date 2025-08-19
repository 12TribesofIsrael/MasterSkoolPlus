#!/usr/bin/env python3
"""
Mock Objects for Selenium WebDriver Testing
==========================================

Provides comprehensive mock objects for testing Selenium WebDriver functionality
without requiring real browser instances. Includes mocks for WebDriver, WebElement,
and various Selenium operations.
"""

import sys
import os
import time
import json
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any, List, Optional, Union

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class MockWebElement:
    """Mock WebElement for Selenium testing"""
    
    def __init__(self, tag_name: str = "div", text: str = "", attributes: Dict[str, str] = None):
        self.tag_name = tag_name
        self.text = text
        self.attributes = attributes or {}
        self.is_displayed = True
        self.is_enabled = True
        self.is_selected = False
        
    def get_attribute(self, name: str) -> str:
        """Get element attribute"""
        return self.attributes.get(name, "")
    
    def get_property(self, name: str) -> str:
        """Get element property"""
        return self.attributes.get(name, "")
    
    def click(self):
        """Mock click operation"""
        pass
    
    def clear(self):
        """Mock clear operation"""
        self.text = ""
    
    def send_keys(self, keys: str):
        """Mock send keys operation"""
        self.text += keys
    
    def find_element(self, by: str, value: str) -> 'MockWebElement':
        """Find child element"""
        return MockWebElement()
    
    def find_elements(self, by: str, value: str) -> List['MockWebElement']:
        """Find child elements"""
        return [MockWebElement()]
    
    def is_displayed(self) -> bool:
        """Check if element is displayed"""
        return self.is_displayed
    
    def is_enabled(self) -> bool:
        """Check if element is enabled"""
        return self.is_enabled
    
    def is_selected(self) -> bool:
        """Check if element is selected"""
        return self.is_selected

class MockWebDriver:
    """Mock WebDriver for Selenium testing"""
    
    def __init__(self, page_source: str = "", current_url: str = ""):
        self.page_source = page_source
        self.current_url = current_url
        self.title = "Mock Page Title"
        self.window_handles = ["window_1"]
        self.current_window_handle = "window_1"
        self.elements = {}
        self.cookies = {}
        self.logs = []
        
    def get(self, url: str):
        """Mock navigate to URL"""
        self.current_url = url
        self.page_source = f"<html><body>Mock page for {url}</body></html>"
    
    def find_element(self, by: str, value: str) -> MockWebElement:
        """Find element by selector"""
        if value in self.elements:
            return self.elements[value]
        return MockWebElement()
    
    def find_elements(self, by: str, value: str) -> List[MockWebElement]:
        """Find elements by selector"""
        if value in self.elements:
            return [self.elements[value]]
        return [MockWebElement()]
    
    def execute_script(self, script: str, *args) -> Any:
        """Execute JavaScript"""
        if "return document.title" in script:
            return self.title
        elif "return window.location.href" in script:
            return self.current_url
        return None
    
    def get_log(self, log_type: str) -> List[Dict[str, Any]]:
        """Get browser logs"""
        return self.logs
    
    def switch_to(self):
        """Mock switch to context"""
        return MockSwitchTo(self)
    
    def quit(self):
        """Mock quit browser"""
        pass
    
    def close(self):
        """Mock close browser"""
        pass
    
    def add_element(self, selector: str, element: MockWebElement):
        """Add element to mock driver"""
        self.elements[selector] = element
    
    def add_log_entry(self, level: str, message: str):
        """Add log entry"""
        self.logs.append({
            "level": level,
            "message": message,
            "timestamp": time.time()
        })

class MockSwitchTo:
    """Mock switch to context"""
    
    def __init__(self, driver: MockWebDriver):
        self.driver = driver
    
    def frame(self, frame_reference):
        """Switch to frame"""
        pass
    
    def default_content(self):
        """Switch to default content"""
        pass
    
    def alert(self):
        """Switch to alert"""
        return MockAlert()

class MockAlert:
    """Mock alert dialog"""
    
    def __init__(self):
        self.text = "Mock alert text"
    
    def accept(self):
        """Accept alert"""
        pass
    
    def dismiss(self):
        """Dismiss alert"""
        pass
    
    def send_keys(self, keys: str):
        """Send keys to alert"""
        pass

class MockOptions:
    """Mock Chrome options"""
    
    def __init__(self):
        self.arguments = []
        self.experimental_options = {}
    
    def add_argument(self, argument: str):
        """Add Chrome argument"""
        self.arguments.append(argument)
    
    def add_experimental_option(self, name: str, value: Any):
        """Add experimental option"""
        self.experimental_options[name] = value

class MockService:
    """Mock Chrome service"""
    
    def __init__(self, executable_path: str = ""):
        self.executable_path = executable_path

def create_mock_driver_with_video_data(video_url: str = None, lesson_title: str = "Test Lesson") -> MockWebDriver:
    """Create a mock driver with video data"""
    
    driver = MockWebDriver()
    
    # Create mock JSON data element
    json_data = {
        "props": {
            "pageProps": {
                "lesson": {
                    "title": lesson_title,
                    "videoUrl": video_url or "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    "content": f"Content for {lesson_title}"
                }
            }
        }
    }
    
    json_element = MockWebElement()
    json_element.get_attribute = lambda attr: json.dumps(json_data) if attr == "innerHTML" else ""
    driver.add_element("#__NEXT_DATA__", json_element)
    
    # Create mock iframe elements
    if video_url:
        iframe_element = MockWebElement("iframe")
        iframe_element.get_attribute = lambda attr: video_url if attr == "src" else ""
        driver.add_element("iframe", iframe_element)
    
    # Create mock video player elements
    video_player = MockWebElement("div")
    video_player.get_attribute = lambda attr: video_url if attr == "data-video" else ""
    driver.add_element(".video-player", video_player)
    
    return driver

def create_mock_driver_with_community_data(community_name: str = "Test Community", lessons: List[Dict] = None) -> MockWebDriver:
    """Create a mock driver with community data"""
    
    if lessons is None:
        lessons = [
            {"title": "Lesson 1: Introduction", "url": "lesson1"},
            {"title": "Lesson 2: Basics", "url": "lesson2"},
            {"title": "Lesson 3: Advanced", "url": "lesson3"}
        ]
    
    driver = MockWebDriver()
    
    # Create mock lesson elements
    for i, lesson in enumerate(lessons):
        lesson_element = MockWebElement("div")
        lesson_element.text = lesson["title"]
        lesson_element.get_attribute = lambda attr, url=lesson["url"]: url if attr == "href" else ""
        driver.add_element(f".lesson-{i+1}", lesson_element)
    
    # Create mock community title
    title_element = MockWebElement("h1")
    title_element.text = community_name
    driver.add_element("h1", title_element)
    
    return driver

def create_mock_driver_with_network_logs(video_urls: List[str] = None) -> MockWebDriver:
    """Create a mock driver with network logs"""
    
    if video_urls is None:
        video_urls = ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]
    
    driver = MockWebDriver()
    
    # Add network log entries
    for url in video_urls:
        driver.add_log_entry("INFO", f"Network request: {url}")
    
    return driver

def test_mock_web_element():
    """Test MockWebElement functionality"""
    
    print("🧪 TESTING MOCK WEB ELEMENT")
    print("=" * 40)
    
    try:
        # Create mock element
        element = MockWebElement("div", "Test text", {"id": "test-id", "class": "test-class"})
        
        # Test basic properties
        if element.tag_name == "div":
            print("✅ Tag name working")
        else:
            print("❌ Tag name failed")
            return False
        
        if element.text == "Test text":
            print("✅ Text property working")
        else:
            print("❌ Text property failed")
            return False
        
        # Test get_attribute
        if element.get_attribute("id") == "test-id":
            print("✅ Get attribute working")
        else:
            print("❌ Get attribute failed")
            return False
        
        # Test click
        element.click()
        print("✅ Click operation working")
        
        # Test send_keys
        element.send_keys(" additional text")
        if "additional text" in element.text:
            print("✅ Send keys working")
        else:
            print("❌ Send keys failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Mock web element test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mock_web_driver():
    """Test MockWebDriver functionality"""
    
    print("\n🧪 TESTING MOCK WEB DRIVER")
    print("=" * 40)
    
    try:
        # Create mock driver
        driver = MockWebDriver()
        
        # Test navigation
        driver.get("https://example.com")
        if driver.current_url == "https://example.com":
            print("✅ Navigation working")
        else:
            print("❌ Navigation failed")
            return False
        
        # Test find_element
        element = driver.find_element("id", "test")
        if isinstance(element, MockWebElement):
            print("✅ Find element working")
        else:
            print("❌ Find element failed")
            return False
        
        # Test add_element
        test_element = MockWebElement("button", "Click me")
        driver.add_element("button", test_element)
        
        found_element = driver.find_element("tag name", "button")
        if found_element.text == "Click me":
            print("✅ Add element working")
        else:
            print("❌ Add element failed")
            return False
        
        # Test execute_script
        result = driver.execute_script("return document.title")
        if result == "Mock Page Title":
            print("✅ Execute script working")
        else:
            print("❌ Execute script failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Mock web driver test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mock_driver_with_video_data():
    """Test mock driver with video data"""
    
    print("\n🧪 TESTING MOCK DRIVER WITH VIDEO DATA")
    print("=" * 40)
    
    try:
        # Create mock driver with video data
        video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        driver = create_mock_driver_with_video_data(video_url, "Test Lesson")
        
        # Test JSON data extraction
        json_element = driver.find_element("id", "__NEXT_DATA__")
        json_data = json.loads(json_element.get_attribute("innerHTML"))
        
        if json_data["props"]["pageProps"]["lesson"]["videoUrl"] == video_url:
            print("✅ JSON data extraction working")
        else:
            print("❌ JSON data extraction failed")
            return False
        
        # Test iframe extraction
        iframe_element = driver.find_element("tag name", "iframe")
        if iframe_element.get_attribute("src") == video_url:
            print("✅ Iframe extraction working")
        else:
            print("❌ Iframe extraction failed")
            return False
        
        # Test video player extraction
        video_player = driver.find_element("css selector", ".video-player")
        if video_player.get_attribute("data-video") == video_url:
            print("✅ Video player extraction working")
        else:
            print("❌ Video player extraction failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Mock driver with video data test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mock_driver_with_community_data():
    """Test mock driver with community data"""
    
    print("\n🧪 TESTING MOCK DRIVER WITH COMMUNITY DATA")
    print("=" * 40)
    
    try:
        # Create mock driver with community data
        lessons = [
            {"title": "Lesson 1: Introduction", "url": "lesson1"},
            {"title": "Lesson 2: Basics", "url": "lesson2"},
            {"title": "Lesson 3: Advanced", "url": "lesson3"}
        ]
        
        driver = create_mock_driver_with_community_data("Test Community", lessons)
        
        # Test lesson discovery
        for i, lesson in enumerate(lessons):
            lesson_element = driver.find_element("css selector", f".lesson-{i+1}")
            if lesson_element.text == lesson["title"]:
                print(f"✅ Lesson {i+1} discovery working")
            else:
                print(f"❌ Lesson {i+1} discovery failed")
                return False
        
        # Test community title
        title_element = driver.find_element("tag name", "h1")
        if title_element.text == "Test Community":
            print("✅ Community title working")
        else:
            print("❌ Community title failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Mock driver with community data test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mock_driver_with_network_logs():
    """Test mock driver with network logs"""
    
    print("\n🧪 TESTING MOCK DRIVER WITH NETWORK LOGS")
    print("=" * 40)
    
    try:
        # Create mock driver with network logs
        video_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.vimeo.com/123456789"
        ]
        
        driver = create_mock_driver_with_network_logs(video_urls)
        
        # Test network logs
        logs = driver.get_log("performance")
        if len(logs) == len(video_urls):
            print("✅ Network logs working")
        else:
            print("❌ Network logs failed")
            return False
        
        # Test log content
        for i, url in enumerate(video_urls):
            if f"Network request: {url}" in logs[i]["message"]:
                print(f"✅ Log entry {i+1} working")
            else:
                print(f"❌ Log entry {i+1} failed")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Mock driver with network logs test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_with_video_extractor():
    """Test integration with video extractor using mocks"""
    
    print("\n🧪 TESTING INTEGRATION WITH VIDEO EXTRACTOR")
    print("=" * 40)
    
    try:
        from skool_modules.video_extractor import extract_video_url
        
        # Create mock driver with video data
        video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        driver = create_mock_driver_with_video_data(video_url, "Test Lesson")
        
        # Test video extraction with mock driver
        extracted_url = extract_video_url(driver, "Test Lesson")
        
        if extracted_url == video_url:
            print("✅ Video extraction with mock driver working")
        else:
            print(f"❌ Video extraction with mock driver failed: {extracted_url}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Integration with video extractor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mock_alert_and_switch_to():
    """Test mock alert and switch to functionality"""
    
    print("\n🧪 TESTING MOCK ALERT AND SWITCH TO")
    print("=" * 40)
    
    try:
        # Create mock driver
        driver = MockWebDriver()
        
        # Test switch to
        switch_to = driver.switch_to()
        if isinstance(switch_to, MockSwitchTo):
            print("✅ Switch to working")
        else:
            print("❌ Switch to failed")
            return False
        
        # Test alert
        alert = switch_to.alert()
        if isinstance(alert, MockAlert):
            print("✅ Alert creation working")
        else:
            print("❌ Alert creation failed")
            return False
        
        # Test alert operations
        alert.accept()
        alert.dismiss()
        alert.send_keys("test")
        print("✅ Alert operations working")
        
        return True
        
    except Exception as e:
        print(f"❌ Mock alert and switch to test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mock_options_and_service():
    """Test mock options and service"""
    
    print("\n🧪 TESTING MOCK OPTIONS AND SERVICE")
    print("=" * 40)
    
    try:
        # Test Chrome options
        options = MockOptions()
        options.add_argument("--headless")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        if "--headless" in options.arguments:
            print("✅ Chrome options working")
        else:
            print("❌ Chrome options failed")
            return False
        
        # Test Chrome service
        service = MockService("/path/to/chromedriver")
        if service.executable_path == "/path/to/chromedriver":
            print("✅ Chrome service working")
        else:
            print("❌ Chrome service failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Mock options and service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_comprehensive_mock_scenario():
    """Test comprehensive mock scenario"""
    
    print("\n🧪 TESTING COMPREHENSIVE MOCK SCENARIO")
    print("=" * 40)
    
    try:
        # Create a comprehensive mock scenario
        driver = MockWebDriver()
        
        # Add various elements
        driver.add_element("h1", MockWebElement("h1", "Community Title"))
        driver.add_element("nav", MockWebElement("nav", "Navigation"))
        
        # Add lesson elements
        for i in range(3):
            lesson = MockWebElement("div", f"Lesson {i+1}")
            lesson.get_attribute = lambda attr, url=f"lesson{i+1}": url if attr == "href" else ""
            driver.add_element(f".lesson-{i+1}", lesson)
        
        # Add video elements
        video_element = MockWebElement("iframe")
        video_element.get_attribute = lambda attr: "https://www.youtube.com/watch?v=dQw4w9WgXcQ" if attr == "src" else ""
        driver.add_element("iframe", video_element)
        
        # Test comprehensive scenario
        title = driver.find_element("tag name", "h1")
        nav = driver.find_element("tag name", "nav")
        lessons = driver.find_elements("css selector", "[class*='lesson']")
        video = driver.find_element("tag name", "iframe")
        
        if (title.text == "Community Title" and 
            nav.text == "Navigation" and 
            len(lessons) == 3 and 
            video.get_attribute("src") == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"):
            print("✅ Comprehensive mock scenario working")
        else:
            print("❌ Comprehensive mock scenario failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Comprehensive mock scenario test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Selenium Mock Objects Test Suite")
    print()
    
    # Run all mock tests
    tests = [
        test_mock_web_element,
        test_mock_web_driver,
        test_mock_driver_with_video_data,
        test_mock_driver_with_community_data,
        test_mock_driver_with_network_logs,
        test_integration_with_video_extractor,
        test_mock_alert_and_switch_to,
        test_mock_options_and_service,
        test_comprehensive_mock_scenario
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
    print(f"📊 MOCK OBJECTS TEST RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("✅ ALL MOCK OBJECTS TESTS PASSED - Selenium mocking is working!")
        print()
        print("🎯 Successfully tested:")
        print("  • MockWebElement functionality")
        print("  • MockWebDriver functionality")
        print("  • Video data mocking")
        print("  • Community data mocking")
        print("  • Network logs mocking")
        print("  • Integration with video extractor")
        print("  • Alert and switch to mocking")
        print("  • Chrome options and service mocking")
        print("  • Comprehensive mock scenarios")
        print()
        print("💡 Selenium mock objects are ready for testing")
    else:
        print(f"❌ {total_tests - passed_tests} MOCK OBJECTS TESTS FAILED - Check the issues above")
    
    print("=" * 60)
