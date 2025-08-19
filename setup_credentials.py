#!/usr/bin/env python3
"""
Setup Skool Credentials
Creates a .env file with your Skool login credentials
"""

import os
import getpass

def setup_credentials():
    """Setup Skool credentials in a .env file"""
    
    print("🔐 SKOOL CREDENTIALS SETUP")
    print("=" * 40)
    print("This will create a .env file with your Skool login credentials.")
    print("The .env file will be ignored by git for security.")
    print()
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        overwrite = input("Do you want to overwrite it? (y/N): ").lower().strip()
        if overwrite != 'y':
            print("❌ Setup cancelled.")
            return
    
    # Get credentials from user
    print("Please enter your Skool credentials:")
    print()
    
    email = input("📧 Email: ").strip()
    if not email:
        print("❌ Email is required!")
        return
    
    password = getpass.getpass("🔒 Password: ").strip()
    if not password:
        print("❌ Password is required!")
        return
    
    # Create .env file
    env_content = f"""# Skool Credentials
# This file contains your Skool login credentials
# DO NOT commit this file to version control

SKOOL_EMAIL={email}
SKOOL_PASSWORD={password}
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print()
        print("✅ Credentials saved to .env file!")
        print("🔒 The .env file is automatically ignored by git")
        print()
        print("💡 You can now run your scraper scripts:")
        print("   python extract_single_with_youtube_fix.py <url>")
        print()
        
        # Test the credentials
        print("🧪 Testing credentials...")
        os.environ['SKOOL_EMAIL'] = email
        os.environ['SKOOL_PASSWORD'] = password
        
        from dotenv import load_dotenv
        load_dotenv()
        
        test_email = os.getenv("SKOOL_EMAIL")
        test_password = os.getenv("SKOOL_PASSWORD")
        
        if test_email == email and test_password == password:
            print("✅ Credentials loaded successfully!")
        else:
            print("❌ Error loading credentials")
            
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

if __name__ == "__main__":
    setup_credentials()
