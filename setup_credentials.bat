@echo off
echo ========================================
echo 🔐 SKOOL CREDENTIALS SETUP
echo ========================================
echo.
echo This will help you set up your Skool login credentials.
echo Your credentials will be saved securely in a .env file.
echo.
echo Press any key to continue...
pause >nul

python setup_credentials.py

echo.
echo Press any key to exit...
pause >nul
