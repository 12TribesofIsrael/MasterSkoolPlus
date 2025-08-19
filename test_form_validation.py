#!/usr/bin/env python3
"""
Test Form Validation
===================

Tests the Skool login form validation to understand why the submit button remains disabled.
"""

import sys
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_form_validation():
    """Test and analyze the Skool login form validation"""
    
    print("🔍 TESTING SKOOL LOGIN FORM VALIDATION")
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
        
        # Find form elements
        email_field = driver.find_element(By.ID, "email")
        password_field = driver.find_element(By.ID, "password")
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        print(f"\n📋 INITIAL FORM STATE:")
        print(f"   Email field value: '{email_field.get_attribute('value')}'")
        print(f"   Password field value: '{password_field.get_attribute('value')}'")
        print(f"   Submit button enabled: {submit_button.is_enabled()}")
        print(f"   Submit button text: '{submit_button.text}'")
        
        # Test with valid email format
        test_email = "test@example.com"
        test_password = "password123"
        
        print(f"\n🧪 TESTING WITH VALID EMAIL: {test_email}")
        
        # Clear and fill email field
        email_field.clear()
        email_field.send_keys(test_email)
        time.sleep(1)
        
        print(f"   After email input:")
        print(f"     Email field value: '{email_field.get_attribute('value')}'")
        print(f"     Submit button enabled: {submit_button.is_enabled()}")
        
        # Clear and fill password field
        password_field.clear()
        password_field.send_keys(test_password)
        time.sleep(1)
        
        print(f"   After password input:")
        print(f"     Password field value: '{password_field.get_attribute('value')}'")
        print(f"     Submit button enabled: {submit_button.is_enabled()}")
        
        # Check for any validation messages
        validation_messages = driver.find_elements(By.CSS_SELECTOR, "[class*='error'], [class*='validation'], [class*='invalid']")
        if validation_messages:
            print(f"   Validation messages found:")
            for msg in validation_messages:
                print(f"     - {msg.text}")
        
        # Try triggering events
        print(f"\n🔄 TRIGGERING FORM EVENTS:")
        
        # Trigger input events
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", email_field)
        time.sleep(0.5)
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", password_field)
        time.sleep(0.5)
        
        print(f"   After input events:")
        print(f"     Submit button enabled: {submit_button.is_enabled()}")
        
        # Trigger change events
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", email_field)
        time.sleep(0.5)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", password_field)
        time.sleep(0.5)
        
        print(f"   After change events:")
        print(f"     Submit button enabled: {submit_button.is_enabled()}")
        
        # Trigger blur events
        driver.execute_script("arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));", email_field)
        time.sleep(0.5)
        driver.execute_script("arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));", password_field)
        time.sleep(0.5)
        
        print(f"   After blur events:")
        print(f"     Submit button enabled: {submit_button.is_enabled()}")
        
        # Check for any hidden fields or additional requirements
        print(f"\n🔍 CHECKING FOR ADDITIONAL FORM ELEMENTS:")
        
        # Look for hidden fields
        hidden_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='hidden']")
        if hidden_inputs:
            print(f"   Hidden inputs found: {len(hidden_inputs)}")
            for i, hidden in enumerate(hidden_inputs):
                print(f"     {i+1}. name='{hidden.get_attribute('name')}', value='{hidden.get_attribute('value')}'")
        
        # Look for checkboxes
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        if checkboxes:
            print(f"   Checkboxes found: {len(checkboxes)}")
            for i, checkbox in enumerate(checkboxes):
                print(f"     {i+1}. name='{checkbox.get_attribute('name')}', checked={checkbox.is_selected()}")
        
        # Look for any required fields
        required_fields = driver.find_elements(By.CSS_SELECTOR, "[required]")
        if required_fields:
            print(f"   Required fields found: {len(required_fields)}")
            for i, field in enumerate(required_fields):
                print(f"     {i+1}. tag='{field.tag_name}', name='{field.get_attribute('name')}', id='{field.get_attribute('id')}'")
        
        # Check form attributes
        form = driver.find_element(By.CSS_SELECTOR, "form")
        if form:
            print(f"\n📝 FORM ATTRIBUTES:")
            print(f"   Action: {form.get_attribute('action')}")
            print(f"   Method: {form.get_attribute('method')}")
            print(f"   ID: {form.get_attribute('id')}")
            print(f"   Class: {form.get_attribute('class')}")
        
        # Try clicking the button even if disabled
        print(f"\n🖱️ TESTING BUTTON CLICK (even if disabled):")
        try:
            submit_button.click()
            print(f"   ✅ Button click succeeded")
        except Exception as e:
            print(f"   ❌ Button click failed: {e}")
        
        # Wait a bit more to see if anything changes
        print(f"\n⏳ WAITING 5 SECONDS TO SEE IF BUTTON ENABLES...")
        for i in range(5):
            time.sleep(1)
            enabled = submit_button.is_enabled()
            print(f"   {i+1}s: Submit button enabled = {enabled}")
            if enabled:
                break
        
        # Final state
        print(f"\n📊 FINAL FORM STATE:")
        print(f"   Email field value: '{email_field.get_attribute('value')}'")
        print(f"   Password field value: '{password_field.get_attribute('value')}'")
        print(f"   Submit button enabled: {submit_button.is_enabled()}")
        print(f"   Submit button text: '{submit_button.text}'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    test_form_validation()
