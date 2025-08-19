#!/usr/bin/env python3
"""
Detailed Login Interaction Test
Tests the login form step by step to understand why credentials aren't being entered
and why the submit button isn't becoming enabled.
"""

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc

def test_detailed_login_interaction():
    """Test login form interaction in detail"""
    
    # Test credentials
    email = "your_email@example.com"  # Replace with actual email
    password = "your_password"        # Replace with actual password
    
    print("🔍 DETAILED LOGIN INTERACTION TEST")
    print("=" * 50)
    
    # Setup undetected Chrome
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = uc.Chrome(options=options)
    
    try:
        # Navigate to login page
        print("🌐 Navigating to login page...")
        driver.get("https://www.skool.com/login")
        time.sleep(3)
        
        print(f"📍 Current URL: {driver.current_url}")
        print(f"📄 Page title: {driver.title}")
        
        # Wait for page to load
        wait = WebDriverWait(driver, 15)
        
        # Test 1: Check if login form exists
        print("\n🔍 TEST 1: Checking for login form...")
        form_selectors = [
            "form",
            "form[action*='login']",
            ".login-form",
            "#login-form"
        ]
        
        form_found = False
        for selector in form_selectors:
            try:
                form = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ Form found with selector: {selector}")
                print(f"   Form HTML: {form.get_attribute('outerHTML')[:200]}...")
                form_found = True
                break
            except NoSuchElementException:
                continue
        
        if not form_found:
            print("❌ No login form found!")
            return
        
        # Test 2: Find email field
        print("\n🔍 TEST 2: Finding email field...")
        email_selectors = [
            (By.ID, "email"),
            (By.CSS_SELECTOR, "input[type='email']"),
            (By.NAME, "email"),
            (By.CSS_SELECTOR, "input[placeholder*='email']"),
            (By.CSS_SELECTOR, "input[placeholder*='Email']")
        ]
        
        email_field = None
        for selector_type, selector in email_selectors:
            try:
                email_field = wait.until(EC.presence_of_element_located((selector_type, selector)))
                print(f"✅ Email field found: {selector_type}={selector}")
                print(f"   Field properties:")
                print(f"     - Enabled: {email_field.is_enabled()}")
                print(f"     - Displayed: {email_field.is_displayed()}")
                print(f"     - Type: {email_field.get_attribute('type')}")
                print(f"     - Placeholder: {email_field.get_attribute('placeholder')}")
                print(f"     - Value: {email_field.get_attribute('value')}")
                break
            except TimeoutException:
                print(f"❌ Email field not found: {selector_type}={selector}")
                continue
        
        if not email_field:
            print("❌ No email field found!")
            return
        
        # Test 3: Find password field
        print("\n🔍 TEST 3: Finding password field...")
        password_selectors = [
            (By.ID, "password"),
            (By.CSS_SELECTOR, "input[type='password']"),
            (By.NAME, "password"),
            (By.CSS_SELECTOR, "input[placeholder*='password']"),
            (By.CSS_SELECTOR, "input[placeholder*='Password']")
        ]
        
        password_field = None
        for selector_type, selector in password_selectors:
            try:
                password_field = driver.find_element(selector_type, selector)
                print(f"✅ Password field found: {selector_type}={selector}")
                print(f"   Field properties:")
                print(f"     - Enabled: {password_field.is_enabled()}")
                print(f"     - Displayed: {password_field.is_displayed()}")
                print(f"     - Type: {password_field.get_attribute('type')}")
                print(f"     - Placeholder: {password_field.get_attribute('placeholder')}")
                break
            except NoSuchElementException:
                print(f"❌ Password field not found: {selector_type}={selector}")
                continue
        
        if not password_field:
            print("❌ No password field found!")
            return
        
        # Test 4: Test email field interaction
        print("\n🔍 TEST 4: Testing email field interaction...")
        try:
            # Clear field first
            email_field.clear()
            print("✅ Email field cleared")
            
            # Click on field
            email_field.click()
            print("✅ Clicked on email field")
            time.sleep(1)
            
            # Type email
            email_field.send_keys(email)
            print(f"✅ Typed email: {email}")
            time.sleep(1)
            
            # Check if value was set
            actual_value = email_field.get_attribute('value')
            print(f"   Actual value in field: '{actual_value}'")
            
            if actual_value == email:
                print("✅ Email successfully entered!")
            else:
                print(f"❌ Email not properly entered! Expected: '{email}', Got: '{actual_value}'")
                
        except Exception as e:
            print(f"❌ Error interacting with email field: {e}")
        
        # Test 5: Test password field interaction
        print("\n🔍 TEST 5: Testing password field interaction...")
        try:
            # Clear field first
            password_field.clear()
            print("✅ Password field cleared")
            
            # Click on field
            password_field.click()
            print("✅ Clicked on password field")
            time.sleep(1)
            
            # Type password
            password_field.send_keys(password)
            print(f"✅ Typed password: {len(password) * '*'}")
            time.sleep(1)
            
            # Check if value was set
            actual_value = password_field.get_attribute('value')
            print(f"   Actual value in field: '{len(actual_value) * '*' if actual_value else 'empty'}'")
            
            if actual_value == password:
                print("✅ Password successfully entered!")
            else:
                print(f"❌ Password not properly entered! Expected: {len(password)} chars, Got: {len(actual_value) if actual_value else 0} chars")
                
        except Exception as e:
            print(f"❌ Error interacting with password field: {e}")
        
        # Test 6: Find submit button
        print("\n🔍 TEST 6: Finding submit button...")
        submit_selectors = [
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.XPATH, "//button[@type='submit']"),
            (By.XPATH, "//button[contains(text(), 'LOG IN')]"),
            (By.XPATH, "//button[contains(text(), 'Login')]"),
            (By.XPATH, "//button[contains(text(), 'Sign In')]"),
            (By.CSS_SELECTOR, "button:contains('LOG IN')"),
            (By.CSS_SELECTOR, "input[type='submit']")
        ]
        
        submit_button = None
        for selector_type, selector in submit_selectors:
            try:
                submit_button = driver.find_element(selector_type, selector)
                print(f"✅ Submit button found: {selector_type}={selector}")
                print(f"   Button properties:")
                print(f"     - Enabled: {submit_button.is_enabled()}")
                print(f"     - Displayed: {submit_button.is_displayed()}")
                print(f"     - Text: '{submit_button.text}'")
                print(f"     - Type: {submit_button.get_attribute('type')}")
                print(f"     - Disabled attribute: {submit_button.get_attribute('disabled')}")
                break
            except NoSuchElementException:
                print(f"❌ Submit button not found: {selector_type}={selector}")
                continue
        
        if not submit_button:
            print("❌ No submit button found!")
            return
        
        # Test 7: Check button state after filling fields
        print("\n🔍 TEST 7: Checking button state after filling fields...")
        print(f"   Button enabled: {submit_button.is_enabled()}")
        print(f"   Button disabled attribute: {submit_button.get_attribute('disabled')}")
        
        # Test 8: Try to enable button by triggering events
        print("\n🔍 TEST 8: Trying to trigger form validation...")
        try:
            # Trigger blur events
            driver.execute_script("arguments[0].blur();", email_field)
            time.sleep(0.5)
            driver.execute_script("arguments[0].blur();", password_field)
            time.sleep(0.5)
            
            # Trigger input events
            driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", email_field)
            time.sleep(0.5)
            driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", password_field)
            time.sleep(0.5)
            
            # Trigger change events
            driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", email_field)
            time.sleep(0.5)
            driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", password_field)
            time.sleep(1)
            
            print("✅ Triggered form validation events")
            
            # Check button state again
            print(f"   Button enabled after events: {submit_button.is_enabled()}")
            print(f"   Button disabled attribute after events: {submit_button.get_attribute('disabled')}")
            
        except Exception as e:
            print(f"❌ Error triggering events: {e}")
        
        # Test 9: Wait for button to become enabled
        print("\n🔍 TEST 9: Waiting for button to become enabled...")
        try:
            wait.until(lambda driver: submit_button.is_enabled())
            print("✅ Submit button became enabled!")
        except TimeoutException:
            print("❌ Submit button did not become enabled within timeout")
            print("   This suggests form validation is not passing")
        
        # Test 10: Check for any validation messages
        print("\n🔍 TEST 10: Checking for validation messages...")
        validation_selectors = [
            ".error",
            ".validation-error",
            ".invalid-feedback",
            "[data-error]",
            ".alert-danger"
        ]
        
        for selector in validation_selectors:
            try:
                errors = driver.find_elements(By.CSS_SELECTOR, selector)
                if errors:
                    print(f"⚠️  Found validation messages with selector '{selector}':")
                    for error in errors:
                        print(f"   - {error.text}")
            except:
                continue
        
        print("\n" + "=" * 50)
        print("🏁 TEST COMPLETE")
        
        # Keep browser open for manual inspection
        input("\nPress Enter to close browser...")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_detailed_login_interaction()
