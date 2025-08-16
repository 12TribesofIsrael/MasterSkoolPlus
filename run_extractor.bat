@echo off
echo ============================================================
echo 🚀 SKOOL CONTENT EXTRACTOR
echo ============================================================
echo.
echo 🧹 CLEANUP OPTION: Run 'run_cleanup.bat' first to clean old data
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

echo.
:: Obtain credentials from env or prompt
if "%SKOOL_EMAIL%"=="" (
    set /p SKOOL_EMAIL="Enter Skool email (or set SKOOL_EMAIL env var): "
)
if "%SKOOL_PASSWORD%"=="" (
    set /p SKOOL_PASSWORD="Enter Skool password (input not hidden): "
)

echo Starting extraction process for: %URL%
echo.

python skool_content_extractor.py "%URL%" --email "%SKOOL_EMAIL%" --password "%SKOOL_PASSWORD%"

echo.
echo ============================================================
echo ✅ EXTRACTION COMPLETE
echo ============================================================
echo Check the extracted_content\lessons\ folder for results
echo.
pause 