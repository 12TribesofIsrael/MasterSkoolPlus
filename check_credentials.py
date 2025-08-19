#!/usr/bin/env python3
"""
Check what credentials are being loaded
"""

import os

# Try to load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ .env file loaded")
except Exception as e:
    print(f"❌ .env file not found or error loading: {e}")

# Check credentials
SKOOL_EMAIL = os.getenv("SKOOL_EMAIL", "")
SKOOL_PASSWORD = os.getenv("SKOOL_PASSWORD", "")

print(f"\n📧 SKOOL_EMAIL: '{SKOOL_EMAIL}'")
print(f"🔒 SKOOL_PASSWORD: '{len(SKOOL_PASSWORD) * '*' if SKOOL_PASSWORD else 'empty'}'")

if not SKOOL_EMAIL:
    print("❌ SKOOL_EMAIL is empty!")
if not SKOOL_PASSWORD:
    print("❌ SKOOL_PASSWORD is empty!")

if SKOOL_EMAIL and SKOOL_PASSWORD:
    print("✅ Both credentials are set")
else:
    print("❌ Missing credentials - please set SKOOL_EMAIL and SKOOL_PASSWORD environment variables")
