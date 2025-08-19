#!/usr/bin/env python3
"""
Test Login Page Structure
=========================

Examines the actual structure of the Skool login page to identify correct selectors.
"""

import sys
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_login_page_structure():
    """Test and analyze the Skool login page structure"""
    
    print("🔍 ANALYZING SKOOL LOGIN PAGE STRUCTURE")
    print("=" * 50)
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        # Create driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("🌐 Navigating to Skool login page...")
        driver.get("https://www.skool.com/login")
        
        # Wait for page to load
        time.sleep(5)
        
        print(f"📄 Page Title: {driver.title}")
        print(f"🌐 Current URL: {driver.current_url}")
        print(f"📏 Page Source Length: {len(driver.page_source)}")
        
        # Look for email fields with various selectors
        email_selectors = [
            "input[name='email']",
            "input[type='email']", 
            "input[id*='email']",
            "input[placeholder*='email' i]",
            "input[placeholder*='Email' i]",
            "#email",
            "[data-testid*='email']",
            "input[autocomplete='email']"
        ]
        
        print("\n🔍 SEARCHING FOR EMAIL FIELDS:")
        print("-" * 30)
        
        for selector in email_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"✅ Found {len(elements)} element(s) with: {selector}")
                    for i, elem in enumerate(elements):
                        print(f"   Element {i+1}:")
                        print(f"     - Tag: {elem.tag_name}")
                        print(f"     - Type: {elem.get_attribute('type')}")
                        print(f"     - Name: {elem.get_attribute('name')}")
                        print(f"     - ID: {elem.get_attribute('id')}")
                        print(f"     - Placeholder: {elem.get_attribute('placeholder')}")
                        print(f"     - Visible: {elem.is_displayed()}")
                        print(f"     - Enabled: {elem.is_enabled()}")
                else:
                    print(f"❌ No elements found with: {selector}")
            except Exception as e:
                print(f"⚠️ Error with selector {selector}: {e}")
        
        # Look for password fields
        password_selectors = [
            "input[name='password']",
            "input[type='password']",
            "input[id*='password']",
            "#password",
            "[data-testid*='password']",
            "input[autocomplete='current-password']"
        ]
        
        print("\n🔒 SEARCHING FOR PASSWORD FIELDS:")
        print("-" * 30)
        
        for selector in password_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"✅ Found {len(elements)} element(s) with: {selector}")
                    for i, elem in enumerate(elements):
                        print(f"   Element {i+1}:")
                        print(f"     - Tag: {elem.tag_name}")
                        print(f"     - Type: {elem.get_attribute('type')}")
                        print(f"     - Name: {elem.get_attribute('name')}")
                        print(f"     - ID: {elem.get_attribute('id')}")
                        print(f"     - Visible: {elem.is_displayed()}")
                        print(f"     - Enabled: {elem.is_enabled()}")
                else:
                    print(f"❌ No elements found with: {selector}")
            except Exception as e:
                print(f"⚠️ Error with selector {selector}: {e}")
        
        # Look for submit buttons
        submit_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:contains('Login')",
            "button:contains('Sign In')",
            "[data-testid*='submit']",
            "[data-testid*='login']",
            "button[class*='login']",
            "button[class*='submit']"
        ]
        
        print("\n🖱️ SEARCHING FOR SUBMIT BUTTONS:")
        print("-" * 30)
        
        for selector in submit_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"✅ Found {len(elements)} element(s) with: {selector}")
                    for i, elem in enumerate(elements):
                        print(f"   Element {i+1}:")
                        print(f"     - Tag: {elem.tag_name}")
                        print(f"     - Type: {elem.get_attribute('type')}")
                        print(f"     - Text: {elem.text}")
                        print(f"     - Visible: {elem.is_displayed()}")
                        print(f"     - Enabled: {elem.is_enabled()}")
                else:
                    print(f"❌ No elements found with: {selector}")
            except Exception as e:
                print(f"⚠️ Error with selector {selector}: {e}")
        
        # Save page source for manual inspection
        with open("login_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"\n💾 Page source saved to: login_page_source.html")
        
        # Take screenshot
        driver.save_screenshot("login_page_screenshot.png")
        print(f"📸 Screenshot saved to: login_page_screenshot.png")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    test_login_page_structure()
