"""
Browser Management Module
========================

Handles browser setup, isolation, management, and cleanup for the Skool scraper.
"""

import time
import random
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from .config_manager import get_config
from .logger import get_logger
from .error_handler import (
    error_handler, ErrorCategory, ErrorSeverity, 
    BrowserError, NetworkError, AuthenticationError
)

class BrowserManager:
    """Manages browser instances and isolation"""
    
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
    
    @error_handler(category=ErrorCategory.BROWSER, severity=ErrorSeverity.HIGH)
    def setup_driver(self, headless: bool = None) -> webdriver.Chrome:
        """Setup Chrome WebDriver with optimal settings"""
        
        logger = get_logger()
        
        if headless is None:
            headless = get_config('HEADLESS_MODE', False)
        
        logger.browser("Setting up Chrome WebDriver...")
        
        # Chrome options for optimal scraping
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument("--headless")
        
        # Performance and stability options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")  # Faster loading
        chrome_options.add_argument("--disable-javascript")  # We'll enable selectively
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent to avoid detection
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Window size
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Setup service with automatic driver management
        service = Service(ChromeDriverManager().install())
        
        # Create driver
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Configure timeouts
        timeout = get_config('BROWSER_TIMEOUT', 30)
        page_load_timeout = get_config('PAGE_LOAD_TIMEOUT', 10)
        
        driver.set_page_load_timeout(page_load_timeout)
        driver.implicitly_wait(timeout)
        
        # Execute script to remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logger.success("Chrome WebDriver setup complete")
        return driver
    
    @error_handler(category=ErrorCategory.BROWSER, severity=ErrorSeverity.HIGH)
    def create_isolated_browser_instance(self) -> Optional[webdriver.Chrome]:
        """Create a completely isolated browser instance"""
        
        logger = get_logger()
        logger.isolation("Creating isolated browser instance...")
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
        
        logger.isolation(f"Destroying browser instance ({reason})...")
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
            logger.isolation(f"Using isolation for {reason}: {lesson_title}")
            logger.log_isolation_decision(lesson_title, lesson_index, total_lessons, True, reason)
            return True
        
        # Use isolation for every Nth lesson to prevent state buildup
        frequency = isolation_config.get('frequency', 5)
        if lesson_index % frequency == 0:
            reason = f"periodic cleanup lesson ({lesson_index}/{total_lessons})"
            logger.isolation(f"Using isolation for {reason}: {lesson_title}")
            logger.log_isolation_decision(lesson_title, lesson_index, total_lessons, True, reason)
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
                    logger.isolation(f"Using isolation for potentially {reason}: {lesson_title}")
                    logger.log_isolation_decision(lesson_title, lesson_index, total_lessons, True, reason)
                    return True
        
        # Use isolation if we've processed many lessons with shared browser
        max_shared = isolation_config.get('max_shared_lessons', 10)
        if self.isolation_stats['lessons_with_shared_browser'] >= max_shared:
            reason = f"after {self.isolation_stats['lessons_with_shared_browser']} shared lessons"
            logger.isolation(f"Using isolation {reason}: {lesson_title}")
            logger.log_isolation_decision(lesson_title, lesson_index, total_lessons, True, reason)
            return True
        
        logger.log_isolation_decision(lesson_title, lesson_index, total_lessons, False, "no isolation needed")
        return False
    
    @error_handler(category=ErrorCategory.AUTHENTICATION, severity=ErrorSeverity.CRITICAL)
    def login_to_skool(self, driver: webdriver.Chrome, email: str, password: str) -> bool:
        """Login to Skool.com"""
        
        logger = get_logger()
        logger.info("Logging in to Skool.com...")
        
        # Navigate to login page
        driver.get("https://app.skool.com/login")
        time.sleep(3)
        
        # Wait for login form
        wait = WebDriverWait(driver, 10)
        
        # Find and fill email field
        email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        email_field.clear()
        email_field.send_keys(email)
        
        # Find and fill password field
        password_field = driver.find_element(By.NAME, "password")
        password_field.clear()
        password_field.send_keys(password)
        
        # Submit form
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()
        
        # Wait for login to complete
        time.sleep(5)
        
        # Check if login was successful
        if "dashboard" in driver.current_url or "communities" in driver.current_url:
            logger.success("Login successful!")
            return True
        else:
            raise AuthenticationError("Login failed - check credentials")
    
    def clear_browser_storage_bulk(self, driver: webdriver.Chrome):
        """Aggressive browser storage clearing"""
        
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
            
        except Exception as e:
            logger = get_logger()
            logger.warning(f"Could not clear all browser storage: {e}")
    
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

# Global browser manager instance
browser_manager = BrowserManager()

# Convenience functions for backward compatibility
def setup_driver(headless: bool = None) -> webdriver.Chrome:
    """Setup Chrome WebDriver"""
    return browser_manager.setup_driver(headless)

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
    """Login to Skool.com"""
    return browser_manager.login_to_skool(driver, email, password)

def clear_browser_storage_bulk(driver: webdriver.Chrome):
    """Clear browser storage"""
    browser_manager.clear_browser_storage_bulk(driver)

def print_browser_isolation_statistics():
    """Print isolation statistics"""
    browser_manager.print_isolation_statistics()
