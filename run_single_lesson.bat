@echo off
echo ===================================
echo 🎯 Single Lesson Extractor with YouTube Fix
echo ===================================
echo.
echo 🧹 TIP: Run 'run_cleanup.bat' first to manage existing community data

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed! Please install Python 3.8 or higher.
    pause
    exit /b 1
)

:: Check if requirements are installed
echo 📦 Checking dependencies...
pip install -r requirements.txt

:: Get URL from user
echo.
echo Usage: This script extracts a single lesson from a Skool.com URL
echo.
echo Example:
echo python extract_single_with_youtube_fix.py "https://www.skool.com/ai-profit-lab-7462/classroom/cbb27978?md=672c0cfa7a984d3fa4df84b1a35569c9"
echo.
echo Please provide the lesson URL you want to extract:
echo.

set /p URL="Enter the Skool.com lesson URL: "

if "%URL%"=="" (
    echo ❌ No URL provided. Exiting.
    pause
    exit /b 1
)

:: Obtain credentials from env or prompt
if "%SKOOL_EMAIL%"=="" (
    set /p SKOOL_EMAIL="Enter Skool email (or set SKOOL_EMAIL env var): "
)
if "%SKOOL_PASSWORD%"=="" (
    set /p SKOOL_PASSWORD="Enter Skool password (input not hidden): "
)

:: Run the single lesson extractor with explicit credentials
echo 🎯 Running single lesson extractor for: %URL%
python extract_single_with_youtube_fix.py "%URL%" --email "%SKOOL_EMAIL%" --password "%SKOOL_PASSWORD%"

echo ===================================
echo ✅ Single lesson extraction complete!
echo 📁 Check the extracted_content/lessons folder
echo ===================================
pause 