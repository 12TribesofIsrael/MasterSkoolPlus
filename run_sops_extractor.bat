@echo off
echo ===================================
echo 🚀 Starting SOPs Collection Extractor
echo ===================================

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
echo Usage: This script now requires a URL parameter
echo.
echo Example:
echo python skool_content_extractor.py "https://www.skool.com/ai-profit-lab-7462/classroom/cbb27978?md=672c0cfa7a984d3fa4df84b1a35569c9"
echo.
echo Please provide the URL you want to extract content from:
echo.

set /p URL="Enter the Skool.com URL: "

if "%URL%"=="" (
    echo ❌ No URL provided. Exiting.
    pause
    exit /b 1
)

:: Run the extractor
echo 🎯 Running SOPs collection extractor for: %URL%
python skool_content_extractor.py "%URL%"

echo ===================================
echo ✅ Extraction complete!
echo 📁 Check the extracted_content folder
echo ===================================
pause 