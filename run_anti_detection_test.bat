@echo off
echo ========================================
echo 🛡️ ANTI-DETECTION MEASURES SETUP
echo ========================================
echo.

echo 📦 Installing undetected-chromedriver...
pip install undetected-chromedriver>=3.5.0

echo.
echo 🧪 Running anti-detection tests...
python test_anti_detection.py

echo.
echo 📊 Saving detection logs...
python -c "from skool_modules.browser_manager import save_detection_logs; save_detection_logs()"

echo.
echo ✅ Anti-detection setup complete!
echo.
echo 💡 To use enhanced anti-detection:
echo    - Run your scraper normally
echo    - Detection logs will be saved automatically
echo    - Check detection_log_*.json files for analysis
echo.
pause
