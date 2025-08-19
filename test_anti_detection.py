#!/usr/bin/env python3
"""
Test Anti-Detection Measures
============================

Tests the enhanced anti-detection capabilities of the browser manager.
"""

import sys
import os
import time
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_undetected_chromedriver_availability():
    """Test if undetected-chromedriver is available"""
    
    print("🧪 TESTING UNDETECTED-CHROMEDRIVER AVAILABILITY")
    print("=" * 50)
    
    try:
        import undetected_chromedriver as uc
        print("✅ undetected-chromedriver is available")
        return True
    except ImportError:
        print("❌ undetected-chromedriver is not available")
        print("💡 Install with: pip install undetected-chromedriver")
        return False

def test_browser_manager_import():
    """Test if the enhanced browser manager can be imported"""
    
    print("\n🧪 TESTING BROWSER MANAGER IMPORT")
    print("=" * 40)
    
    try:
        from skool_modules.browser_manager import (
            setup_driver, login_to_skool, save_detection_logs,
            AntiDetectionLogger, HumanBehaviorSimulator, BrowserManager
        )
        print("✅ Enhanced browser manager imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import browser manager: {e}")
        return False

def test_anti_detection_logger():
    """Test the anti-detection logger functionality"""
    
    print("\n🧪 TESTING ANTI-DETECTION LOGGER")
    print("=" * 35)
    
    try:
        from skool_modules.browser_manager import AntiDetectionLogger
        
        logger = AntiDetectionLogger()
        
        # Test detection event logging
        logger.log_detection_event("test_event", {"test": "data"})
        print("✅ Detection event logging works")
        
        # Test login attempt logging
        logger.log_login_attempt(True, "test", 2.5, {"test": "data"})
        print("✅ Login attempt logging works")
        
        # Test browser fingerprint logging
        logger.log_browser_fingerprint({"userAgent": "test"})
        print("✅ Browser fingerprint logging works")
        
        # Test timing pattern logging
        logger.log_timing_pattern("test_action", 1.5, True)
        print("✅ Timing pattern logging works")
        
        # Test log saving
        test_filename = f"test_detection_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        logger.save_detection_log(test_filename)
        
        if os.path.exists(test_filename):
            print("✅ Detection log saving works")
            os.remove(test_filename)  # Clean up
        else:
            print("❌ Detection log saving failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Anti-detection logger test failed: {e}")
        return False

def test_human_behavior_simulator():
    """Test the human behavior simulator"""
    
    print("\n🧪 TESTING HUMAN BEHAVIOR SIMULATOR")
    print("=" * 40)
    
    try:
        from skool_modules.browser_manager import HumanBehaviorSimulator
        
        simulator = HumanBehaviorSimulator()
        
        # Test random delay
        start_time = time.time()
        delay = simulator.random_delay(0.1, 0.2)
        actual_delay = time.time() - start_time
        
        if 0.1 <= actual_delay <= 0.3:  # Allow some tolerance
            print("✅ Random delay simulation works")
        else:
            print(f"❌ Random delay simulation failed: {actual_delay}s")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Human behavior simulator test failed: {e}")
        return False

def test_browser_setup():
    """Test browser setup with anti-detection measures"""
    
    print("\n🧪 TESTING BROWSER SETUP")
    print("=" * 25)
    
    try:
        from skool_modules.browser_manager import setup_driver
        
        print("🔧 Testing standard driver setup...")
        driver = setup_driver(headless=True, use_undetected=False)
        
        if driver:
            print("✅ Standard driver setup successful")
            
            # Test browser fingerprint
            fingerprint = driver.execute_script("""
                return {
                    userAgent: navigator.userAgent,
                    webdriver: navigator.webdriver,
                    platform: navigator.platform
                };
            """)
            
            print(f"📊 Browser fingerprint: {fingerprint}")
            
            # Clean up
            driver.quit()
            print("✅ Driver cleanup successful")
        else:
            print("❌ Standard driver setup failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Browser setup test failed: {e}")
        return False

def test_undetected_driver_setup():
    """Test undetected driver setup if available"""
    
    print("\n🧪 TESTING UNDETECTED DRIVER SETUP")
    print("=" * 35)
    
    if not test_undetected_chromedriver_availability():
        print("⏭️ Skipping undetected driver test (not available)")
        return True
    
    try:
        from skool_modules.browser_manager import setup_driver
        
        print("🛡️ Testing undetected driver setup...")
        driver = setup_driver(headless=True, use_undetected=True)
        
        if driver:
            print("✅ Undetected driver setup successful")
            
            # Test browser fingerprint
            fingerprint = driver.execute_script("""
                return {
                    userAgent: navigator.userAgent,
                    webdriver: navigator.webdriver,
                    platform: navigator.platform
                };
            """)
            
            print(f"📊 Undetected browser fingerprint: {fingerprint}")
            
            # Clean up
            driver.quit()
            print("✅ Undetected driver cleanup successful")
        else:
            print("❌ Undetected driver setup failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Undetected driver setup test failed: {e}")
        return False

def main():
    """Run all anti-detection tests"""
    
    print("🛡️ ANTI-DETECTION MEASURES TEST SUITE")
    print("=" * 50)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Undetected ChromeDriver Availability", test_undetected_chromedriver_availability),
        ("Browser Manager Import", test_browser_manager_import),
        ("Anti-Detection Logger", test_anti_detection_logger),
        ("Human Behavior Simulator", test_human_behavior_simulator),
        ("Standard Browser Setup", test_browser_setup),
        ("Undetected Driver Setup", test_undetected_driver_setup),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
        
        print()
    
    print("=" * 50)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All anti-detection tests passed!")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
