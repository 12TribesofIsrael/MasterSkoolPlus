"""
Enhanced Browser Management Module with Anti-Detection
====================================================

Handles browser setup, isolation, management, and cleanup for the Skool scraper.
Includes advanced anti-detection measures and comprehensive logging.
"""

import time
import random
import json
import os
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Import undetected-chromedriver for enhanced anti-detection
try:
    import undetected_chromedriver as uc
    UNDETECTED_AVAILABLE = True
except ImportError:
    UNDETECTED_AVAILABLE = False
    print("⚠️ undetected-chromedriver not available. Using standard selenium.")

from .config_manager import get_config
from .logger import get_logger
from .error_handler import (
    error_handler, ErrorCategory, ErrorSeverity, 
    BrowserError, NetworkError, AuthenticationError
)

class AntiDetectionLogger:
    """Comprehensive logging for anti-detection patterns"""
    
    def __init__(self):
        self.logger = get_logger()
        self.detection_events = []
        self.login_attempts = []
        self.browser_fingerprints = []
        self.timing_patterns = []
        
    def log_detection_event(self, event_type: str, details: Dict[str, Any]):
        """Log detection-related events"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details
        }
        self.detection_events.append(event)
        self.logger.warning(f"🔍 DETECTION EVENT: {event_type} - {details}")
        
    def log_login_attempt(self, success: bool, method: str, duration: float, details: Dict[str, Any]):
        """Log login attempt details"""
        attempt = {
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'method': method,
            'duration': duration,
            'details': details
        }
        self.login_attempts.append(attempt)
        
        status = "✅ SUCCESS" if success else "❌ FAILED"
        self.logger.info(f"🔐 LOGIN ATTEMPT: {status} using {method} ({duration:.2f}s)")
        
    def log_browser_fingerprint(self, fingerprint: Dict[str, Any]):
        """Log browser fingerprint data"""
        self.browser_fingerprints.append({
            'timestamp': datetime.now().isoformat(),
            'fingerprint': fingerprint
        })
        self.logger.debug(f"🖥️ BROWSER FINGERPRINT: {fingerprint}")
        
    def log_timing_pattern(self, action: str, duration: float, randomized: bool):
        """Log timing patterns for analysis"""
        pattern = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'duration': duration,
            'randomized': randomized
        }
        self.timing_patterns.append(pattern)
        self.logger.debug(f"⏱️ TIMING: {action} took {duration:.2f}s (randomized: {randomized})")
        
    def save_detection_log(self, filename: str = None):
        """Save detection logs to file"""
        if not filename:
            filename = f"detection_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        log_data = {
            'detection_events': self.detection_events,
            'login_attempts': self.login_attempts,
            'browser_fingerprints': self.browser_fingerprints,
            'timing_patterns': self.timing_patterns,
            'summary': {
                'total_detection_events': len(self.detection_events),
                'total_login_attempts': len(self.login_attempts),
                'successful_logins': len([a for a in self.login_attempts if a['success']]),
                'failed_logins': len([a for a in self.login_attempts if not a['success']])
            }
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(log_data, f, indent=2)
            self.logger.info(f"📊 Detection log saved to: {filename}")
        except Exception as e:
            self.logger.error(f"Failed to save detection log: {e}")

class HumanBehaviorSimulator:
    """Simulates human-like behavior patterns"""
    
    def __init__(self):
        self.logger = get_logger()
        
    def random_delay(self, min_seconds: float = 0.5, max_seconds: float = 2.0):
        """Add random delay to simulate human thinking"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        return delay
        
    def human_type(self, element, text: str, min_delay: float = 0.05, max_delay: float = 0.2):
        """Type text with human-like delays between characters"""
        self.logger.debug(f"⌨️ Typing '{text}' with human-like delays")
        
        # Clear field first
        element.clear()
        self.random_delay(0.1, 0.3)
        
        # Type each character with random delays
        for char in text:
            element.send_keys(char)
            char_delay = random.uniform(min_delay, max_delay)
            time.sleep(char_delay)
            
        # Final pause after typing
        self.random_delay(0.2, 0.5)
        
    def human_click(self, driver, element, offset_x: int = 0, offset_y: int = 0):
        """Click with human-like mouse movement"""
        self.logger.debug(f"🖱️ Human-like click on element")
        
        # Move mouse to element with slight offset
        actions = ActionChains(driver)
        actions.move_to_element_with_offset(element, offset_x, offset_y)
        
        # Add small random movement
        actions.move_by_offset(random.randint(-5, 5), random.randint(-5, 5))
        
        # Pause before clicking
        actions.pause(random.uniform(0.1, 0.3))
        
        # Click
        actions.click()
        actions.perform()
        
        # Pause after clicking
        self.random_delay(0.2, 0.5)
        
    def scroll_naturally(self, driver, direction: str = "down", distance: int = None):
        """Scroll with natural human-like movement"""
        if distance is None:
            distance = random.randint(100, 300)
            
        self.logger.debug(f"📜 Natural scroll {direction} by {distance}px")
        
        # Scroll with JavaScript for smooth movement
        if direction == "down":
            driver.execute_script(f"window.scrollBy(0, {distance});")
        else:
            driver.execute_script(f"window.scrollBy(0, -{distance});")
            
        # Pause after scrolling
        self.random_delay(0.5, 1.5)

class BrowserManager:
    """Enhanced browser manager with anti-detection capabilities"""
    
    def __init__(self):
        self.browser_instances_created = 0
        self.browser_instances_destroyed = 0
        self.current_browser_instance = None
        self.isolation_stats = {
            'lessons_with_isolated_browsers': 0,
            'lessons_with_shared_browser': 0,
            'browser_creation_time': 0,
            'browser_destruction_time': 0
        }
        
        # Anti-detection components
        self.detection_logger = AntiDetectionLogger()
        self.human_simulator = HumanBehaviorSimulator()
        
        # User agent rotation
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
    
    @error_handler(category=ErrorCategory.BROWSER, severity=ErrorSeverity.HIGH)
    def setup_driver(self, headless: bool = None, use_undetected: bool = True) -> webdriver.Chrome:
        """Setup Chrome WebDriver with enhanced anti-detection"""
        
        logger = get_logger()
        start_time = time.time()
        
        if headless is None:
            headless = get_config('HEADLESS_MODE', False)
            
        if use_undetected and UNDETECTED_AVAILABLE:
            logger.info("🛡️ Setting up undetected Chrome WebDriver...")
            driver = self._setup_undetected_driver(headless)
        else:
            logger.info("🔧 Setting up standard Chrome WebDriver...")
            driver = self._setup_standard_driver(headless)
        
        # Log browser fingerprint
        self._log_browser_fingerprint(driver)
        
        creation_time = time.time() - start_time
        self.isolation_stats['browser_creation_time'] += creation_time
        self.browser_instances_created += 1
        
        logger.success(f"Chrome WebDriver setup complete ({creation_time:.2f}s)")
        return driver
    
    def _setup_undetected_driver(self, headless: bool) -> webdriver.Chrome:
        """Setup undetected Chrome WebDriver"""
        
        # Undetected Chrome options
        options = uc.ChromeOptions()
        
        if headless:
            options.add_argument("--headless")
            
        # Enhanced anti-detection options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--disable-ipc-flooding-protection")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-features=TranslateUI")
        options.add_argument("--disable-ipc-flooding-protection")
        
        # Random user agent
        user_agent = random.choice(self.user_agents)
        options.add_argument(f"--user-agent={user_agent}")
        
        # Window size
        width = random.randint(1200, 1920)
        height = random.randint(800, 1080)
        options.add_argument(f"--window-size={width},{height}")
        
        # Create undetected driver
        driver = uc.Chrome(options=options, version_main=None)
        
        # Configure timeouts
        timeout = get_config('BROWSER_TIMEOUT', 30)
        page_load_timeout = get_config('PAGE_LOAD_TIMEOUT', 10)
        
        driver.set_page_load_timeout(page_load_timeout)
        driver.implicitly_wait(timeout)
        
        return driver
    
    def _setup_standard_driver(self, headless: bool) -> webdriver.Chrome:
        """Setup standard Chrome WebDriver with anti-detection measures"""
        
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument("--headless")
        
        # Enhanced anti-detection options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-features=TranslateUI")
        
        # Advanced stealth options
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Random user agent
        user_agent = random.choice(self.user_agents)
        chrome_options.add_argument(f"--user-agent={user_agent}")
        
        # Window size
        width = random.randint(1200, 1920)
        height = random.randint(800, 1080)
        chrome_options.add_argument(f"--window-size={width},{height}")
        
        # Setup service
        service = Service(ChromeDriverManager().install())
        
        # Create driver
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Configure timeouts
        timeout = get_config('BROWSER_TIMEOUT', 30)
        page_load_timeout = get_config('PAGE_LOAD_TIMEOUT', 10)
        
        driver.set_page_load_timeout(page_load_timeout)
        driver.implicitly_wait(timeout)
        
        # Execute stealth scripts
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
        driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
        
        return driver
    
    def _log_browser_fingerprint(self, driver: webdriver.Chrome):
        """Log browser fingerprint for detection analysis"""
        
        try:
            fingerprint = driver.execute_script("""
                return {
                    userAgent: navigator.userAgent,
                    platform: navigator.platform,
                    language: navigator.language,
                    languages: navigator.languages,
                    cookieEnabled: navigator.cookieEnabled,
                    onLine: navigator.onLine,
                    hardwareConcurrency: navigator.hardwareConcurrency,
                    deviceMemory: navigator.deviceMemory,
                    maxTouchPoints: navigator.maxTouchPoints,
                    webdriver: navigator.webdriver,
                    plugins: navigator.plugins.length,
                    screenWidth: screen.width,
                    screenHeight: screen.height,
                    colorDepth: screen.colorDepth,
                    pixelDepth: screen.pixelDepth,
                    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
                };
            """)
            
            self.detection_logger.log_browser_fingerprint(fingerprint)
            
        except Exception as e:
            self.logger.warning(f"Could not log browser fingerprint: {e}")
    
    @error_handler(category=ErrorCategory.AUTHENTICATION, severity=ErrorSeverity.CRITICAL)
    def login_to_skool(self, driver: webdriver.Chrome, email: str, password: str) -> bool:
        """Enhanced login to Skool.com with anti-detection measures"""
        
        logger = get_logger()
        start_time = time.time()
        
        logger.info("🔐 Starting enhanced login to Skool.com...")
        
        try:
            # Navigate to login page with random delay
            logger.info("🌐 Navigating to login page...")
            driver.get("https://www.skool.com/login")
            
            # Random delay after navigation
            delay = self.human_simulator.random_delay(2, 4)
            self.detection_logger.log_timing_pattern("page_navigation", delay, True)
            
            # Wait for page to load completely
            wait = WebDriverWait(driver, 15)
            
            # Check if login form is present with multiple selectors
            email_field = None
            email_selectors = [
                (By.ID, "email"),
                (By.CSS_SELECTOR, "input[type='email']"),
                (By.NAME, "email")
            ]
            
            for selector_type, selector in email_selectors:
                try:
                    email_field = wait.until(EC.presence_of_element_located((selector_type, selector)))
                    logger.info(f"✅ Login form detected with selector: {selector_type}={selector}")
                    break
                except TimeoutException:
                    continue
            
            if not email_field:
                logger.error("❌ Login form not found - page may not have loaded properly")
                self.detection_logger.log_detection_event("login_form_not_found", {
                    'current_url': driver.current_url,
                    'page_source_length': len(driver.page_source)
                })
                return False
            
            # Simulate human-like behavior before typing
            self.human_simulator.random_delay(1, 3)
            
            # Fill email with human-like typing
            logger.info("⌨️ Typing email...")
            self.human_simulator.human_type(email_field, email)
            
            # Random delay between fields
            self.human_simulator.random_delay(0.5, 1.5)
            
            # Find and fill password field with multiple selectors
            password_field = None
            password_selectors = [
                (By.ID, "password"),
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.NAME, "password")
            ]
            
            for selector_type, selector in password_selectors:
                try:
                    password_field = driver.find_element(selector_type, selector)
                    logger.info(f"✅ Password field found with selector: {selector_type}={selector}")
                    break
                except:
                    continue
            
            if not password_field:
                raise Exception("Password field not found")
                
            logger.info("🔒 Typing password...")
            self.human_simulator.human_type(password_field, password)
            
            # Random delay before submitting
            self.human_simulator.random_delay(1, 2)
            
            # Find and wait for submit button to become enabled
            submit_button = None
            submit_selectors = [
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//button[contains(text(), 'LOG IN')]"),
                (By.XPATH, "//button[contains(text(), 'Login')]")
            ]
            
            for selector_type, selector in submit_selectors:
                try:
                    submit_button = driver.find_element(selector_type, selector)
                    logger.info(f"✅ Submit button found with selector: {selector_type}={selector}")
                    break
                except:
                    continue
            
            if not submit_button:
                raise Exception("Submit button not found")
            
            # Wait for button to become enabled (form validation)
            logger.info("⏳ Waiting for submit button to become enabled...")
            wait.until(lambda driver: submit_button.is_enabled())
            logger.info("✅ Submit button is now enabled")
            
            logger.info("🖱️ Clicking submit button...")
            self.human_simulator.human_click(driver, submit_button)
            
            # Wait for login to complete with longer timeout
            logger.info("⏳ Waiting for login to complete...")
            time.sleep(3)
            
            # Check for various success indicators
            success_indicators = [
                "dashboard" in driver.current_url,
                "communities" in driver.current_url,
                "www.skool.com" in driver.current_url and "login" not in driver.current_url
            ]
            
            login_duration = time.time() - start_time
            
            if any(success_indicators):
                logger.success("✅ Login successful!")
                self.detection_logger.log_login_attempt(True, "enhanced", login_duration, {
                    'final_url': driver.current_url,
                    'indicators_matched': success_indicators
                })
                return True
            else:
                logger.error("❌ Login failed - not redirected to expected page")
                self.detection_logger.log_login_attempt(False, "enhanced", login_duration, {
                    'final_url': driver.current_url,
                    'indicators_matched': success_indicators
                })
                
                # Log detection event
                self.detection_logger.log_detection_event("login_failed", {
                    'final_url': driver.current_url,
                    'page_title': driver.title,
                    'login_duration': login_duration
                })
                
                raise AuthenticationError("Login failed - check credentials or detection")
                
        except Exception as e:
            login_duration = time.time() - start_time
            self.detection_logger.log_login_attempt(False, "enhanced", login_duration, {
                'error': str(e),
                'error_type': type(e).__name__
            })
            raise
    
    def clear_browser_storage_bulk(self, driver: webdriver.Chrome):
        """Aggressive browser storage clearing with logging"""
        
        logger = get_logger()
        logger.info("🧹 Clearing browser storage...")
        
        try:
            # Clear all storage types
            driver.execute_script("""
                // Clear localStorage
                localStorage.clear();
                
                // Clear sessionStorage
                sessionStorage.clear();
                
                // Clear IndexedDB
                if ('indexedDB' in window) {
                    indexedDB.databases().then(function(databases) {
                        databases.forEach(function(database) {
                            indexedDB.deleteDatabase(database.name);
                        });
                    });
                }
                
                // Clear cache
                if ('caches' in window) {
                    caches.keys().then(function(names) {
                        names.forEach(function(name) {
                            caches.delete(name);
                        });
                    });
                }
                
                // Clear service worker registrations
                if ('serviceWorker' in navigator) {
                    navigator.serviceWorker.getRegistrations().then(function(registrations) {
                        registrations.forEach(function(registration) {
                            registration.unregister();
                        });
                    });
                }
            """)
            
            # Clear cookies
            driver.delete_all_cookies()
            
            logger.success("✅ Browser storage cleared successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not clear all browser storage: {e}")
    
    def print_isolation_statistics(self):
        """Print browser isolation statistics"""
        
        logger = get_logger()
        
        logger.info("=== BROWSER ISOLATION STATISTICS ===")
        logger.info(f"Browser Instances Created: {self.browser_instances_created}")
        logger.info(f"Browser Instances Destroyed: {self.browser_instances_destroyed}")
        logger.info(f"Lessons with Isolated Browsers: {self.isolation_stats['lessons_with_isolated_browsers']}")
        logger.info(f"Lessons with Shared Browser: {self.isolation_stats['lessons_with_shared_browser']}")
        
        total_lessons = (self.isolation_stats['lessons_with_isolated_browsers'] + 
                        self.isolation_stats['lessons_with_shared_browser'])
        
        if total_lessons > 0:
            isolation_percentage = (self.isolation_stats['lessons_with_isolated_browsers'] / total_lessons) * 100
            logger.info(f"Isolation Usage: {isolation_percentage:.1f}% of lessons")
        
        if self.isolation_stats['browser_creation_time'] > 0:
            logger.info(f"Total Browser Creation Time: {self.isolation_stats['browser_creation_time']:.2f}s")
        
        if self.isolation_stats['browser_destruction_time'] > 0:
            logger.info(f"Total Browser Destruction Time: {self.isolation_stats['browser_destruction_time']:.2f}s")
        
        logger.info("=" * 40)
    
    def save_detection_logs(self):
        """Save all detection logs to file"""
        self.detection_logger.save_detection_log()
    
    @error_handler(category=ErrorCategory.BROWSER, severity=ErrorSeverity.HIGH)
    def create_isolated_browser_instance(self) -> Optional[webdriver.Chrome]:
        """Create a completely isolated browser instance"""
        
        logger = get_logger()
        logger.info("🔄 Creating isolated browser instance...")
        start_time = time.time()
        
        # Create new driver
        driver = self.setup_driver()
        
        # Additional isolation measures
        self._clear_browser_data(driver)
        
        self.browser_instances_created += 1
        self.current_browser_instance = driver
        self.isolation_stats['browser_creation_time'] += (time.time() - start_time)
        
        logger.success(f"Isolated browser instance created (total: {self.browser_instances_created})")
        return driver
    
    def destroy_browser_instance(self, driver: webdriver.Chrome, reason: str = "normal_cleanup"):
        """Safely destroy a browser instance with cleanup"""
        
        logger = get_logger()
        
        if not driver:
            return
        
        logger.info(f"🗑️ Destroying browser instance ({reason})...")
        start_time = time.time()
        
        try:
            # Clear all data before closing
            try:
                self._clear_browser_data(driver)
            except:
                pass  # Ignore cleanup errors
            
            # Close browser
            driver.quit()
            
            self.browser_instances_destroyed += 1
            self.current_browser_instance = None
            self.isolation_stats['browser_destruction_time'] += (time.time() - start_time)
            
            logger.success(f"Browser instance destroyed (total: {self.browser_instances_destroyed})")
            
        except Exception as e:
            logger.warning(f"Error destroying browser: {e}")
    
    def _clear_browser_data(self, driver: webdriver.Chrome):
        """Clear all browser data for isolation"""
        
        try:
            # Clear storage
            driver.execute_script("window.localStorage.clear();")
            driver.execute_script("window.sessionStorage.clear();")
            
            # Clear cookies
            driver.delete_all_cookies()
            
            # Clear cache
            driver.execute_script("""
                if ('caches' in window) {
                    caches.keys().then(function(names) {
                        for (let name of names) caches.delete(name);
                    });
                }
            """)
            
        except Exception as e:
            logger = get_logger()
            logger.warning(f"Could not clear all browser data: {e}")
    
    def should_use_browser_isolation(self, lesson_title: str, lesson_index: int, total_lessons: int) -> bool:
        """Determine if browser isolation should be used for this lesson"""
        
        logger = get_logger()
        isolation_config = get_config('get_isolation_config', {})
        
        # Use isolation for first few lessons (most likely to have cached state)
        if lesson_index <= 3:
            reason = f"early lesson ({lesson_index}/{total_lessons})"
            logger.info(f"🔄 Using isolation for {reason}: {lesson_title}")
            return True
        
        # Use isolation for every Nth lesson to prevent state buildup
        frequency = isolation_config.get('frequency', 5)
        if lesson_index % frequency == 0:
            reason = f"periodic cleanup lesson ({lesson_index}/{total_lessons})"
            logger.info(f"🔄 Using isolation for {reason}: {lesson_title}")
            return True
        
        # Check for problematic lesson keywords
        problematic_keywords = isolation_config.get('problematic_keywords', [])
        lesson_lower = lesson_title.lower()
        
        for keyword in problematic_keywords:
            if keyword in lesson_lower:
                # Use word boundary matching to avoid false positives
                if (keyword == lesson_lower or 
                    lesson_lower.startswith(keyword + ' ') or 
                    lesson_lower.endswith(' ' + keyword) or
                    ' ' + keyword + ' ' in lesson_lower):
                    reason = f"problematic keyword: {keyword}"
                    logger.info(f"🔄 Using isolation for potentially {reason}: {lesson_title}")
                    return True
        
        # Use isolation if we've processed many lessons with shared browser
        max_shared = isolation_config.get('max_shared_lessons', 10)
        if self.isolation_stats['lessons_with_shared_browser'] >= max_shared:
            reason = f"after {self.isolation_stats['lessons_with_shared_browser']} shared lessons"
            logger.info(f"🔄 Using isolation {reason}: {lesson_title}")
            return True
        
        return False

# Global browser manager instance
browser_manager = BrowserManager()

# Convenience functions for backward compatibility
def setup_driver(headless: bool = None, use_undetected: bool = True) -> webdriver.Chrome:
    """Setup Chrome WebDriver with enhanced anti-detection"""
    return browser_manager.setup_driver(headless, use_undetected)

def create_isolated_browser_instance() -> Optional[webdriver.Chrome]:
    """Create isolated browser instance"""
    return browser_manager.create_isolated_browser_instance()

def destroy_browser_instance(driver: webdriver.Chrome, reason: str = "normal_cleanup"):
    """Destroy browser instance"""
    browser_manager.destroy_browser_instance(driver, reason)

def should_use_browser_isolation(lesson_title: str, lesson_index: int, total_lessons: int) -> bool:
    """Check if browser isolation should be used"""
    return browser_manager.should_use_browser_isolation(lesson_title, lesson_index, total_lessons)

def login_to_skool(driver: webdriver.Chrome, email: str, password: str) -> bool:
    """Enhanced login to Skool.com"""
    return browser_manager.login_to_skool(driver, email, password)

def clear_browser_storage_bulk(driver: webdriver.Chrome):
    """Clear browser storage"""
    browser_manager.clear_browser_storage_bulk(driver)

def print_browser_isolation_statistics():
    """Print isolation statistics"""
    browser_manager.print_isolation_statistics()

def save_detection_logs():
    """Save detection logs"""
    browser_manager.save_detection_logs()
