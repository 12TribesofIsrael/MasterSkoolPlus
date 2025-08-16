@echo off
REM 🧹 Skool Scraper Cleanup Tool - Windows Batch Runner
REM Safely clean up previous scraping data

echo.
echo ================================================================
echo 🧹 SKOOL SCRAPER CLEANUP TOOL
echo ================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Check if cleanup script exists
if not exist "cleanup_scraper.py" (
    echo ❌ cleanup_scraper.py not found
    echo Please ensure the cleanup script is in the current directory
    pause
    exit /b 1
)

REM Run the cleanup tool
echo 🚀 Starting cleanup tool...
echo.
python cleanup_scraper.py

echo.
echo ================================================================
echo 🧹 Cleanup tool finished
echo ================================================================
pause