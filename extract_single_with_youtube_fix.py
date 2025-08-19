#!/usr/bin/env python3
"""
🎯 ENHANCED Single Lesson Extractor with Hierarchical Structure
Extract a specific lesson and save it in the new organized community structure.
"""

import os
import time
import re
import argparse
import sys
import json
import subprocess
import urllib.request
from datetime import datetime
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import traceback

# Configuration
# Optionally load environment variables from a .env file if present
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

# Read credentials from environment variables to avoid hardcoding secrets
SKOOL_EMAIL = os.getenv("SKOOL_EMAIL", "")
SKOOL_PASSWORD = os.getenv("SKOOL_PASSWORD", "")

def extract_community_info_from_url(url):
    """
    Extract community and classroom info from Skool URL
    Example: https://www.skool.com/ai-automation-society/classroom/832a1e6e?md=xxx
    Returns: ('ai-automation-society', 'classroom', '832a1e6e')
    """
    if not url:
        return None, None, None
    
    pattern = r'skool\.com/([^/]+)/([^/]+)/([^?]+)'
    match = re.search(pattern, url)
    if match:
        community = match.group(1)
        section = match.group(2)  # usually 'classroom'
        lesson_id = match.group(3)
        return community, section, lesson_id
    return None, None, None

def extract_clean_community_name(driver):
    """
    Extract a clean, readable community name from the page
    Avoids promotional text and gets the actual community name
    """
    try:
        # Wait for page to load
        time.sleep(3)
        
        # Try extracting from page title first (usually most reliable)
        try:
            title = driver.title
            if title:
                # Handle different title formats
                if '·' in title:
                    # Format: "Lesson Name · AI Money Lab"
                    community_name = title.split('·')[-1].strip()
                elif ' - ' in title:
                    # Format: "AI Money Lab - Skool"
                    parts = title.split(' - ')
                    community_name = parts[0].strip() if len(parts) > 1 else title.strip()
                else:
                    # Single title format
                    community_name = title.strip()
                
                # Clean up the community name
                if community_name and community_name.lower() not in ['skool', 'classroom', 'lessons']:
                    # Remove common suffixes and clean up
                    community_name = community_name.replace(' - Skool', '').strip()
                    community_name = re.sub(r'^(🔥\s*)', '', community_name)  # Remove fire emoji prefix
                    community_name = re.sub(r'\s*(🔥\s*)$', '', community_name)  # Remove fire emoji suffix
                    
                    # If it's still very long promotional text, try to extract the core name
                    if len(community_name) > 50:
                        # Look for patterns like "AI Money Lab" within promotional text
                        potential_names = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]*)*(?:\s+Lab|\s+Academy|\s+Society|\s+Community)?)\b', community_name)
                        if potential_names:
                            # Take the first reasonable name found
                            for name in potential_names:
                                if len(name) < 30 and name.lower() not in ['steal', 'exact', 'making', 'month']:
                                    community_name = name
                                    break
                    
                    print(f"🏷️ Extracted clean community name from title: '{community_name}'")
                    return community_name
        except Exception as e:
            print(f"⚠️ Error extracting from title: {e}")
        
        # Fallback: Try other selectors for community name
        selectors = [
            # Community branding elements
            '[class*="community"] h1',
            '[class*="brand"] h1',
            # Header navigation
            'nav [class*="logo"]',
            'header h1',
            # Meta tags
            'meta[property="og:site_name"]',
            'meta[name="application-name"]'
        ]
        
        for selector in selectors:
            try:
                if selector.startswith('meta'):
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    text = element.get_attribute('content')
                else:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    text = element.get_attribute('textContent') or element.text
                
                if text and len(text.strip()) > 0:
                    clean_text = text.strip()
                    if (clean_text.lower() not in ['skool', 'classroom', 'lessons', 'home'] and 
                        len(clean_text) < 50):
                        print(f"🏷️ Found community name with selector {selector}: '{clean_text}'")
                        return clean_text
            except Exception:
                continue
        
        print("⚠️ Could not extract clean community name")
        return None
        
    except Exception as e:
        print(f"⚠️ Error extracting clean community name: {str(e)}")
        return None

def create_organized_directories(community_display_name, community_slug):
    """Create organized directory structure: Communities/Community Name (slug)/lessons/images/videos"""
    
    # Use clean community name with URL slug
    if community_display_name:
        # Clean up the display name for folder usage
        clean_name = re.sub(r'[<>:"/\\|?*]', '_', community_display_name)
        clean_name = re.sub(r'\s+', ' ', clean_name).strip()
        
        # Create folder name as: "Community Name (slug)"
        folder_name = f"{clean_name} ({community_slug})" if community_slug else clean_name
    else:
        # Fallback to just the slug if no clean name found
        folder_name = f"Unknown Community ({community_slug})" if community_slug else "Unknown Community"
    
    # Sanitize the final folder name
    safe_folder_name = re.sub(r'[<>:"/\\|?*]', '_', folder_name)
    safe_folder_name = re.sub(r'\s+', ' ', safe_folder_name).strip()
    
    # Create the organized structure inside Communities directory
    community_path = os.path.join("Communities", safe_folder_name)
    dirs = {
        'community': community_path,
        'lessons': os.path.join(community_path, "lessons"),
        'images': os.path.join(community_path, "images"),
        'videos': os.path.join(community_path, "videos")
    }
    
    for dir_path in dirs.values():
        os.makedirs(dir_path, exist_ok=True)
    
    return dirs

def setup_driver():
    """Setup Chrome WebDriver"""
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    # Enable performance logging to sniff media requests when needed
    try:
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    except Exception:
        pass
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.maximize_window()
    return driver

def clear_browser_storage(driver):
    """Clear localStorage, sessionStorage, and cookies to avoid state contamination."""
    try:
        driver.execute_script("window.localStorage.clear();")
        driver.execute_script("window.sessionStorage.clear();")
        try:
            driver.delete_all_cookies()
            print("🧹 Cleared cookies, localStorage and sessionStorage")
        except Exception as ce:
            print(f"⚠️ Could not clear cookies: {ce}")
            print("🧹 Cleared localStorage and sessionStorage")
    except Exception as e:
        print(f"⚠️ Could not clear storage: {e}")

def login_to_skool(driver, email, password):
    """Enhanced login to Skool with anti-detection measures"""
    try:
        # Use the enhanced login function from the browser manager
        from skool_modules.browser_manager import login_to_skool as enhanced_login
        return enhanced_login(driver, email, password)
    except ImportError:
        # Fallback to original login method if modules not available
        print("🔐 Logging into Skool...")
        driver.get("https://www.skool.com/login")
        
        wait = WebDriverWait(driver, 15)
        email_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='email']")))
        email_field.clear()
        email_field.send_keys(email)
        time.sleep(1)
        
        password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(1)
        
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        time.sleep(5)
        
        success = "login" not in driver.current_url.lower()
        if success:
            print("✅ Login successful!")
        else:
            print("❌ Login failed")
        return success
        
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return False

def extract_lesson_name(driver):
    """Dynamically extracts the lesson name from the page."""
    try:
        print("🔍 Looking for lesson title...")
        
        # Try Skool.com specific selectors first
        skool_selectors = [
            "[data-testid='lesson-title']",
            "[class*='LessonTitle']",
            "[class*='lesson-title']",
            "[class*='module-title']",
            "[class*='content-title']",
            "h1[class*='title']",
            "h2[class*='title']",
            "h3[class*='title']",
            "[class*='StyledTitle']",
            "[class*='styled__Title']",
            "[class*='Title-sc-']",
            "[class*='Header'] h1",
            "[class*='Header'] h2",
            "[class*='Header'] h3",
            "[class*='header'] h1",
            "[class*='header'] h2",
            "[class*='header'] h3"
        ]
        
        # Try Skool.com specific selectors
        for selector in skool_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elements:
                    if el.is_displayed() and el.text.strip():
                        text = el.text.strip()
                        # Filter out generic titles and navigation
                        if (text and len(text) < 200 and 
                            "AI Profit Boardroom" not in text and 
                            "More videos" not in text and
                            "Login" not in text and
                            "Sign up" not in text and
                            "Menu" not in text and
                            "Search" not in text and
                            "Profile" not in text and
                            len(text) > 3):
                            print(f"✅ Found lesson title: {text}")
                            return text
            except Exception:
                continue
        
        # Fallback to more generic selectors
        generic_selectors = [
            "h1",
            "h2", 
            "h3",
            "[class*='title']",
            "[class*='header']",
            "[class*='heading']",
            "[class*='name']",
            "[class*='label']"
        ]
        
        for selector in generic_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elements:
                    if el.is_displayed() and el.text.strip():
                        text = el.text.strip()
                        # More strict filtering for generic selectors
                        if (text and len(text) < 150 and 
                            "AI Profit Boardroom" not in text and 
                            "More videos" not in text and
                            "Login" not in text and
                            "Sign up" not in text and
                            "Menu" not in text and
                            "Search" not in text and
                            "Profile" not in text and
                            "Home" not in text and
                            "Dashboard" not in text and
                            "Settings" not in text and
                            len(text) > 5 and
                            not text.isupper()):  # Avoid all-caps navigation items
                            print(f"✅ Found lesson title (generic): {text}")
                            return text
            except Exception:
                continue
        
        print("⚠️ Could not dynamically find lesson title.")
        return None
        
    except Exception as e:
        print(f"❌ Error extracting lesson name: {e}")
        return None

def detect_platform(video_url):
    """Detect video platform from URL"""
    if not video_url:
        return 'unknown'
    
    url_lower = video_url.lower()
    
    # Filter out image URLs
    if any(img_ext in url_lower for img_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']):
        return 'unknown'
    
    # Filter out thumbnail URLs with image_crop parameters
    if 'image_crop' in url_lower or 'thumbnail' in url_lower:
        return 'unknown'
    
    if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'youtube'
    elif 'vimeo.com' in url_lower:
        return 'vimeo'
    elif 'loom.com' in url_lower:
        return 'loom'
    elif 'wistia.com' in url_lower or 'wistia.net' in url_lower or 'fast.wistia.net' in url_lower:
        return 'wistia'
    elif any(ext in url_lower for ext in ['.mp4', '.webm', '.avi', '.mov']):
        return 'direct'
    else:
        return 'unknown'

def clean_video_url(video_url, platform):
    """Clean up video URLs by removing unnecessary parameters"""
    if not video_url:
        return video_url
    
    if platform == 'youtube':
        # Extract video ID from various YouTube URL formats
        import re
        from urllib.parse import urlparse, parse_qs, unquote
        
        # Handle oEmbed URLs that wrap the real video URL in ?url=
        if 'youtube.com/oembed' in video_url:
            try:
                parsed = urlparse(video_url)
                q = parse_qs(parsed.query)
                wrapped = q.get('url', [None])[0]
                if wrapped:
                    wrapped = unquote(wrapped)
                    # Recursively clean the wrapped URL
                    return clean_video_url(wrapped, 'youtube')
            except Exception:
                pass
        
        # Handle embed URLs: https://www.youtube.com/embed/Ch-AWxvX2Jc?params...
        embed_match = re.search(r'youtube\.com/embed/([a-zA-Z0-9_-]{11})', video_url)
        if embed_match:
            video_id = embed_match.group(1)
            clean_url = f"https://www.youtube.com/watch?v={video_id}"
            print(f"🧹 Cleaned YouTube URL: {video_url[:50]}... → {clean_url}")
            return clean_url
        
        # Handle regular URLs: https://www.youtube.com/watch?v=Ch-AWxvX2Jc&params...
        watch_match = re.search(r'[?&]v=([a-zA-Z0-9_-]{11})', video_url)
        if watch_match:
            video_id = watch_match.group(1)
            clean_url = f"https://www.youtube.com/watch?v={video_id}"
            print(f"🧹 Cleaned YouTube URL: {video_url[:50]}... → {clean_url}")
            return clean_url
        
        # Handle youtu.be URLs: https://youtu.be/Ch-AWxvX2Jc?params...
        short_match = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', video_url)
        if short_match:
            video_id = short_match.group(1)
            clean_url = f"https://www.youtube.com/watch?v={video_id}"
            print(f"🧹 Cleaned YouTube URL: {video_url[:50]}... → {clean_url}")
            return clean_url
    
    elif platform == 'vimeo':
        # Clean Vimeo URLs: keep just the video ID
        import re
        vimeo_match = re.search(r'vimeo\.com/(\d+)', video_url)
        if vimeo_match:
            video_id = vimeo_match.group(1)
            clean_url = f"https://vimeo.com/{video_id}"
            print(f"🧹 Cleaned Vimeo URL: {video_url[:50]}... → {clean_url}")
            return clean_url
    
    elif platform == 'loom':
        # Clean Loom URLs: keep just the video ID
        import re
        loom_match = re.search(r'loom\.com/(?:share/|embed/)?([a-zA-Z0-9]+)', video_url)
        if loom_match:
            video_id = loom_match.group(1)
            clean_url = f"https://www.loom.com/share/{video_id}"
            print(f"🧹 Cleaned Loom URL: {video_url[:50]}... → {clean_url}")
            return clean_url
    
    elif platform == 'wistia':
        # Normalize to canonical fast.wistia.net embed URL
        import re
        # Matches medias or embed iframe forms
        m = re.search(r'(?:wistia\.com/medias/|fast\.wistia\.net/embed/iframe/)([a-zA-Z0-9_-]+)', video_url)
        if m:
            video_id = m.group(1)
            clean_url = f"https://fast.wistia.net/embed/iframe/{video_id}"
            print(f"🧹 Cleaned Wistia URL: {video_url[:60]}... → {clean_url}")
            return clean_url
    
    # Return original URL if no cleaning rules apply
    return video_url

def extract_from_next_data(driver):
    """Extract video URL from Skool's __NEXT_DATA__ JSON - Enhanced with multiple paths"""
    try:
        print("🔍 Looking for video in __NEXT_DATA__ JSON...")
        script_tag = driver.find_element(By.ID, "__NEXT_DATA__")
        data = json.loads(script_tag.get_attribute("innerHTML"))
        
        # Navigate to lesson data
        lesson = data.get("props", {}).get("pageProps", {}).get("lesson")
        if lesson:
            print("🔍 Found lesson data, checking multiple video paths...")
            
            # Method 1: Check videoLinksData (NEW - contains actual video URLs)
            video_links_data = lesson.get("videoLinksData")
            if video_links_data:
                try:
                    # Parse the JSON string in videoLinksData
                    video_links = json.loads(video_links_data)
                    if isinstance(video_links, list) and len(video_links) > 0:
                        video_info = video_links[0]  # Get first video
                        video_url = video_info.get("url")
                        if video_url:
                            platform = detect_platform(video_url)
                            clean_url = clean_video_url(video_url, platform)
                            result = {
                                'url': clean_url,
                                'platform': platform,
                                'thumbnail': video_info.get("thumbnail"),
                                'duration': video_info.get("len_ms")
                            }
                            print(f"✅ Found {platform} video in videoLinksData: {clean_url}")
                            return result
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"⚠️ Error parsing videoLinksData: {e}")
            
            # Method 2: Check lesson.video.video_url (original method)
            video_data = lesson.get("video", {})
            video_url = video_data.get("video_url")
            if video_url:
                platform = detect_platform(video_url)
                clean_url = clean_video_url(video_url, platform)
                result = {
                    'url': clean_url,
                    'platform': platform,
                    'thumbnail': video_data.get("original_thumbnail_url"),
                    'duration': video_data.get("video_length_ms")
                }
                print(f"✅ Found {platform} video in lesson.video: {clean_url}")
                return result
            
            # Method 3: Check lesson.metadata.videoLink (alternative path)
            metadata = lesson.get("metadata", {})
            video_link = metadata.get("videoLink")
            if video_link:
                platform = detect_platform(video_link)
                clean_url = clean_video_url(video_link, platform)
                result = {
                    'url': clean_url,
                    'platform': platform,
                    'thumbnail': metadata.get("thumbnail"),
                    'duration': metadata.get("duration")
                }
                print(f"✅ Found {platform} video in lesson.metadata: {clean_url}")
                return result
            
            # Method 4: Search for any URL-like patterns in lesson data
            def find_video_urls_in_object(obj, path=""):
                video_urls = []
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        current_path = f"{path}.{key}" if path else key
                        if isinstance(value, str) and any(domain in value.lower() for domain in ['youtube.com', 'youtu.be', 'vimeo.com', 'loom.com', 'wistia.com', '.mp4', '.webm']):
                            # Skip thumbnail images
                            if '.jpg' in value.lower() or '.png' in value.lower() or 'image_crop' in value.lower():
                                continue
                            video_urls.append((current_path, value))
                        elif isinstance(value, (dict, list)):
                            video_urls.extend(find_video_urls_in_object(value, current_path))
                elif isinstance(obj, list):
                    for i, value in enumerate(obj):
                        current_path = f"{path}[{i}]"
                        if isinstance(value, (dict, list)):
                            video_urls.extend(find_video_urls_in_object(value, current_path))
                return video_urls
            
            video_urls = find_video_urls_in_object(lesson)
            if video_urls:
                for path, url in video_urls:
                    platform = detect_platform(url)
                    if platform != 'unknown':
                        clean_url = clean_video_url(url, platform)
                        result = {
                            'url': clean_url,
                            'platform': platform,
                            'thumbnail': None,
                            'duration': None
                        }
                        print(f"✅ Found {platform} video in {path}: {clean_url}")
                        return result
            
            print("⚠️ No video URLs found in lesson JSON data")
        else:
            print("⚠️ No lesson data found in __NEXT_DATA__")
            
    except Exception as e:
        print(f"⚠️ JSON extraction failed: {e}")
    
    return None

def scan_video_iframes(driver):
    """Scan for video iframes and React video players from any platform"""
    try:
        print("🔍 Scanning for video iframes and React players...")
        
        # Universal iframe selectors (not just YouTube)
        iframe_selectors = [
            "iframe[src*='youtube.com']",
            "iframe[src*='youtu.be']", 
            "iframe[src*='vimeo.com']",
            "iframe[src*='loom.com']",
            "iframe[src*='wistia.com']",
            "iframe[src*='video']",
            "iframe[class*='video']",
            "iframe[class*='player']"
        ]
        
        # Check traditional iframes first with detailed logging
        for selector in iframe_selectors:
            try:
                iframes = driver.find_elements(By.CSS_SELECTOR, selector)
                if iframes:
                    print(f"🎬 Found {len(iframes)} iframe(s) with selector: {selector}")
                for iframe in iframes:
                    src = iframe.get_attribute("src")
                    print(f"   📄 iframe src: {src[:100] if src else 'None'}...")
                    if src:
                        platform = detect_platform(src)
                        if platform != 'unknown':
                            clean_url = clean_video_url(src, platform)
                            result = {
                                'url': clean_url,
                                'platform': platform,
                                'thumbnail': None,
                                'duration': None
                            }
                            print(f"✅ Found {platform} video iframe: {clean_url}")
                            return result
            except Exception as e:
                print(f"⚠️ Error with selector {selector}: {e}")
                continue
        
        # Check for React video players and other video containers
        print("🔍 Scanning for React video players and video containers...")
        video_container_selectors = [
            "[class*='ReactPlayer']",
            "[class*='VideoPlayer']", 
            "[class*='VideoWrapper']",
            "[class*='video-player']",
            "[class*='player-wrapper']",
            "video",
            "[data-video-url]",
            "[data-src*='video']"
        ]
        
        for selector in video_container_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    # Check for data attributes that might contain video URLs
                    for attr in ['data-video-url', 'data-src', 'src', 'data-url']:
                        url = element.get_attribute(attr)
                        if url:
                            platform = detect_platform(url)
                            if platform != 'unknown':
                                result = {
                                    'url': url,
                                    'platform': platform,
                                    'thumbnail': None,
                                    'duration': None
                                }
                                print(f"✅ Found {platform} video in {selector}: {url}")
                                return result
            except Exception:
                continue
    
    except Exception as e:
        print(f"⚠️ Iframe scanning failed: {e}")
    
    return None

def debug_page_state_after_click(driver):
    """Debug what happens after clicking video thumbnail"""
    print("🔍 DEBUGGING: Page state after video thumbnail click")
    
    # Log all iframes
    iframes = driver.find_elements(By.CSS_SELECTOR, "iframe")
    print(f"📊 Total iframes found: {len(iframes)}")
    for i, iframe in enumerate(iframes):
        src = iframe.get_attribute("src") or "No src"
        data_src = iframe.get_attribute("data-src") or "No data-src"  
        print(f"  {i+1}. src: {src[:80]}")
        print(f"      data-src: {data_src[:80]}")
    
    # Log all video-related elements
    video_elements = driver.find_elements(By.CSS_SELECTOR, "video, embed, object")
    print(f"📊 Video/embed elements found: {len(video_elements)}")
    for i, element in enumerate(video_elements):
        src = element.get_attribute("src") or "No src"
        print(f"  {i+1}. {element.tag_name}: {src[:80]}")
    
    # Log elements with video-related data attributes
    for attr in ['data-video-url', 'data-src', 'data-video', 'data-youtube-id']:
        elements = driver.find_elements(By.CSS_SELECTOR, f"[{attr}]")
        if elements:
            print(f"📊 Elements with {attr}: {len(elements)}")
            for element in elements:
                value = element.get_attribute(attr)
                print(f"    {attr}: {value[:80]}")

def click_video_thumbnail_safely(driver):
    """
    Enhanced video thumbnail clicking with comprehensive iframe detection
    """
    try:
        print("🎯 Looking for video thumbnail to click safely...")
        
        # Store current URL to detect unwanted navigation
        original_url = driver.current_url
        print(f"📍 Original URL: {original_url}")
        
        # Target the exact video thumbnail selectors from user's HTML
        thumbnail_selectors = [
            '.styled__VideoThumbnailWrapper-sc-1k73vxa-2',
            '[class*="VideoThumbnailWrapper"]',
            'div[class*="VideoThumbnail"]',
            'div[style*="justify-content: center"]',
        ]
        
        video_thumbnail_clicked = False
        for selector in thumbnail_selectors:
            try:
                thumbnails = driver.find_elements(By.CSS_SELECTOR, selector)
                if thumbnails:
                    print(f"🎬 Found {len(thumbnails)} thumbnail(s) with selector: {selector}")
                    
                    for thumbnail in thumbnails:
                        # Check if this thumbnail has duration text OR looks like a video container
                        duration_text = thumbnail.text
                        class_name = thumbnail.get_attribute('class') or ''
                        
                        print(f"🔍 Checking thumbnail - text: '{duration_text}', class: '{class_name[:50]}'")
                        
                        # More aggressive video detection - click if it looks like a video container
                        is_video_container = (
                            any(time_pattern in duration_text for time_pattern in [':', '4:12', '0:', '1:', '2:', '3:', '4:', '5:']) or
                            'VideoThumbnail' in class_name or
                            'video' in class_name.lower() or
                            'justify-content: center' in thumbnail.get_attribute('style') or ''
                        )
                        
                        if is_video_container:
                            print(f"✅ Found potential video thumbnail - attempting click")
                            
                            # RELIABILITY FIX: Validate element before clicking
                            try:
                                # Wait for element to be clickable
                                from selenium.webdriver.support.ui import WebDriverWait
                                from selenium.webdriver.support import expected_conditions as EC
                                from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
                                
                                # Check if element is still attached and clickable
                                if thumbnail.is_displayed() and thumbnail.is_enabled():
                                    print("✅ Element validated as clickable")
                                    # Click the thumbnail
                                    driver.execute_script("arguments[0].click();", thumbnail)
                                else:
                                    print("⚠️ Element not clickable, skipping...")
                                    continue
                                    
                            except StaleElementReferenceException:
                                print("⚠️ Element became stale, re-finding...")
                                # Re-find the element
                                try:
                                    refreshed_thumbnails = driver.find_elements(By.CSS_SELECTOR, selector)
                                    if refreshed_thumbnails:
                                        thumbnail = refreshed_thumbnails[0]  # Use first found
                                        if thumbnail.is_displayed() and thumbnail.is_enabled():
                                            driver.execute_script("arguments[0].click();", thumbnail)
                                        else:
                                            continue
                                    else:
                                        continue
                                except Exception as e:
                                    print(f"⚠️ Failed to re-find element: {e}")
                                    continue
                            except Exception as e:
                                print(f"⚠️ Element validation failed: {e}")
                                continue
                            print("⏳ Clicked video thumbnail, waiting for player...")
                            
                            # RELIABILITY FIX: Proper wait after click
                            time.sleep(1)  # Initial wait for click action to process
                            
                            # Check if we stayed on the same page OR redirected to lesson page
                            try:
                                # Wait for any navigation to complete
                                WebDriverWait(driver, 5).until(lambda d: d.execute_script("return document.readyState") == "complete")
                                current_url = driver.current_url
                                
                                if original_url == current_url:
                                    print("✅ Stayed on the same page after clicking thumbnail")
                                    video_thumbnail_clicked = True
                                    break
                                elif "classroom" not in current_url and len(current_url) > len(original_url):
                                    print(f"✅ Redirected to lesson-specific page: {current_url}")
                                    print("🎯 This is where the video should be located - continuing with detection...")
                                    video_thumbnail_clicked = True
                                    break
                                elif any(keyword in current_url for keyword in ["lesson", "day-", "video", "watch"]):
                                    print(f"✅ Redirected to lesson page: {current_url}")
                                    print("🎯 This might be where the video is located - continuing with detection...")
                                    video_thumbnail_clicked = True
                                    break
                                else:
                                    print(f"⚠️ Page changed unexpectedly: {current_url}")
                                    # Don't go back immediately, try to extract from current page first
                                    video_thumbnail_clicked = True
                                    break
                                    
                            except TimeoutException:
                                print("⚠️ Page load timeout after click, proceeding anyway...")
                                video_thumbnail_clicked = True
                                break
                            except Exception as e:
                                print(f"⚠️ Error checking navigation after click: {e}")
                                video_thumbnail_clicked = True
                                break
                        
                if video_thumbnail_clicked:
                    break
                    
            except Exception as e:
                print(f"⚠️ Error with thumbnail selector {selector}: {e}")
                continue
        
        if not video_thumbnail_clicked:
            print("⚠️ No video thumbnail found to click safely")
            return None
        
        # Enhanced iframe detection with progressive waiting
        print("🔍 Starting enhanced video detection after thumbnail click...")
        
        # RELIABILITY FIX: Progressive iframe detection with proper waits
        for wait_attempt, wait_time in enumerate([1, 2, 4], 1):
            print(f"🔄 Detection attempt {wait_attempt}: waiting {wait_time}s for iframe to load...")
            time.sleep(wait_time)
            
            # Wait for any iframes to be present in DOM
            try:
                WebDriverWait(driver, 5).until(lambda d: len(d.find_elements(By.TAG_NAME, "iframe")) > 0)
                print("✅ Found iframe(s) in DOM")
            except TimeoutException:
                print(f"⚠️ No iframes found after {wait_time}s wait")
                if wait_attempt < 3:  # Continue trying if not last attempt
                    continue
            
            # Debug current page state
            debug_page_state_after_click(driver)
            
            # Before scanning globally, check if a modal/dialog is open and contains the video
            modal_result = extract_video_from_modal_if_open(driver)
            if modal_result:
                return modal_result

            # Attempt to dismiss sound overlay/backdrop that blocks clicks
            try:
                overlay_selectors = [
                    '[data-handle="click-for-sound-backdrop"]',
                    '[data-handle*="click-for-sound"]',
                    '.w-ui-container',
                    '.w-css-reset[data-handle="click-for-sound-backdrop"]'
                ]
                for sel in overlay_selectors:
                    overlays = driver.find_elements(By.CSS_SELECTOR, sel)
                    for ov in overlays:
                        if ov.is_displayed():
                            driver.execute_script("arguments[0].style.pointerEvents='none'; arguments[0].style.opacity='0';", ov)
                            print(f"🧹 Dismissed overlay via {sel}")
            except Exception:
                pass

            # Enhanced video detection with comprehensive selectors
            all_video_selectors = [
                'iframe[src*="youtube"]',
                'iframe[src*="vimeo"]', 
                'iframe[src*="loom"]',
                'iframe[src*="wistia"]',
                'iframe',  # Any iframe
                'video',   # HTML5 video tags
                'embed',   # Embed tags
                'object[data*="youtube"]',
                'object[data*="vimeo"]',
                '[class*="video"]',
                '[class*="player"]',
                '[class*="VideoPlayer"]',
                '[class*="ReactPlayer"]',
                '[data-video-url]',
                '[data-src*="youtube"]',
                '[data-src*="vimeo"]',
                '[data-src*="loom"]',
                '[src*="embed"]'
            ]
            
            for selector in all_video_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"🎬 Found {len(elements)} element(s) with selector: {selector}")
                        
                    for element in elements:
                        # Check multiple attributes for video URLs
                        for attr in ['src', 'data-src', 'data-video-url', 'data-url', 'href', 'data']:
                            url = element.get_attribute(attr)
                            if url and any(domain in url.lower() for domain in ['youtube', 'vimeo', 'loom', 'wistia', 'embed']):
                                platform = detect_platform(url)
                                if platform != 'unknown':
                                    clean_url = clean_video_url(url, platform)
                                    print(f"✅ Found {platform} video after {wait_time}s wait: {clean_url}")
                                    print(f"🔧 Detection method: {selector} -> {attr}")
                                    return {
                                        'url': clean_url,
                                        'platform': platform,
                                        'source': 'safe_thumbnail_click',
                                        'thumbnail': None,
                                        'duration': None,
                                        'detection_method': f"{selector}[{attr}]",
                                        'wait_time': wait_time
                                    }
                except Exception as e:
                    print(f"⚠️ Error with selector {selector}: {e}")
                    continue

            # Additional Wistia checks: anchors with ?wvideo= and class-based embeds (global)
            try:
                from urllib.parse import urlparse, parse_qs
                import re as _re
                # Anchors anywhere on page
                anchors = driver.find_elements(By.CSS_SELECTOR, 'a[href*="wvideo="]')
                for a in anchors:
                    href = a.get_attribute('href') or ''
                    if 'wvideo=' in href:
                        q = parse_qs(urlparse(href).query)
                        wid = q.get('wvideo', [None])[0]
                        if wid and _re.fullmatch(r'[A-Za-z0-9]+', wid):
                            wistia_url = f"https://fast.wistia.net/embed/iframe/{wid}"
                            print(f"✅ Found Wistia via wvideo (global scan): {wistia_url}")
                            return {
                                'url': wistia_url,
                                'platform': 'wistia',
                                'source': 'wvideo_anchor_global'
                            }
                # Class-based embeds
                wels = driver.find_elements(By.CSS_SELECTOR, 'div[class*="wistia_embed"], div[class*="wistia_async_"]')
                for wel in wels:
                    cls = wel.get_attribute('class') or ''
                    m = _re.search(r'wistia_async_([A-Za-z0-9]+)', cls)
                    if m:
                        wid = m.group(1)
                        wistia_url = f"https://fast.wistia.net/embed/iframe/{wid}"
                        print(f"✅ Found Wistia via class (global scan): {wistia_url}")
                        return {
                            'url': wistia_url,
                            'platform': 'wistia',
                            'source': 'wistia_class_global'
                        }
            except Exception:
                pass
            
            # Check __NEXT_DATA__ JSON after click for video URLs
            try:
                print("🔍 Checking __NEXT_DATA__ JSON for video after click...")
                script_tag = driver.find_element(By.ID, "__NEXT_DATA__")
                updated_data = json.loads(script_tag.get_attribute("innerHTML"))
                
                # Look for video data that might have appeared after clicking
                lesson = updated_data.get("props", {}).get("pageProps", {}).get("lesson")
                if lesson:
                    video_data = lesson.get("video", {})
                    video_url = video_data.get("video_url")
                    if video_url:
                        platform = detect_platform(video_url)
                        clean_url = clean_video_url(video_url, platform)
                        print(f"✅ Found {platform} video in JSON after click: {clean_url}")
                        return {
                            'url': clean_url,
                            'platform': platform,
                            'source': 'json_after_click',
                            'thumbnail': video_data.get("original_thumbnail_url"),
                            'duration': video_data.get("video_length_ms"),
                            'wait_time': wait_time
                        }
            except Exception as e:
                print(f"⚠️ JSON check failed: {e}")
            
            # If we found something on earlier attempts, don't continue waiting
            if wait_attempt >= 2:  # After 2 attempts (2s + 3s), be more selective about continuing
                user_elements = driver.find_elements(By.CSS_SELECTOR, "iframe, video, embed")
                if not user_elements:
                    print("🔍 No video elements detected yet, continuing to wait...")
                else:
                    print(f"⚠️ Found {len(user_elements)} potential elements but no valid video URLs")
        
        print("⚠️ No video iframe found after comprehensive detection attempts")
        print("💡 The video might be using a different loading mechanism or platform")
        
        # Try custom video player detection for New Society community
        print("🔍 Attempting custom video player detection...")
        custom_video_result = detect_custom_video_player(driver)
        if custom_video_result:
            return custom_video_result
        
        return None
        
    except Exception as e:
        print(f"❌ Error in enhanced video thumbnail click: {str(e)}")
        return None

def extract_video_from_modal_if_open(driver):
    """If a modal/dialog is open, attempt to extract video URL from within it."""
    try:
        # Helper: try to build Wistia URL from a Skool link with ?wvideo=ID
        def _extract_wistia_from_wvideo_href(href: str):
            try:
                from urllib.parse import urlparse, parse_qs
                import re as _re
                q = parse_qs(urlparse(href).query)
                wid = q.get('wvideo', [None])[0]
                if wid and _re.fullmatch(r'[A-Za-z0-9]+', wid):
                    return f"https://fast.wistia.net/embed/iframe/{wid}"
            except Exception:
                return None
            return None

        modal_selectors = [
            '[role="dialog"]',
            '[class*="modal"]', '[class*="Modal"]',
            '[class*="popup"]', '[class*="Popup"]',
            '[class*="overlay"]', '[class*="Overlay"]',
            '.ReactModal__Content',
            '[data-testid*="modal"]', '[data-testid*="popup"]',
            '[aria-modal="true"]',
            'div[style*="position: fixed"]',
        ]

        for selector in modal_selectors:
            try:
                modals = driver.find_elements(By.CSS_SELECTOR, selector)
                if not modals:
                    continue
                for modal in modals:
                    if not modal.is_displayed():
                        continue
                    # First: check anchors that may carry ?wvideo=
                    try:
                        anchors = modal.find_elements(By.CSS_SELECTOR, 'a[href]')
                        for a in anchors:
                            href = a.get_attribute('href') or ''
                            if 'wvideo=' in href:
                                wistia_url = _extract_wistia_from_wvideo_href(href)
                                if wistia_url:
                                    print(f"✅ Found Wistia via wvideo in modal: {wistia_url}")
                                    return {
                                        'url': wistia_url,
                                        'platform': 'wistia',
                                        'source': 'modal_wvideo'
                                    }
                    except Exception:
                        pass

                    # Search for iframes first
                    iframes = modal.find_elements(By.CSS_SELECTOR, 'iframe')
                    for iframe in iframes:
                        src = iframe.get_attribute('src') or ''
                        if any(domain in src.lower() for domain in ['youtube', 'vimeo', 'loom', 'wistia']):
                            platform = detect_platform(src)
                            clean_url = clean_video_url(src, platform)
                            print(f"✅ Found {platform} video in modal iframe: {clean_url}")
                            return {
                                'url': clean_url,
                                'platform': platform,
                                'source': 'modal_iframe'
                            }
                    # Search for HTML5 video elements or data attributes
                    elements = modal.find_elements(By.CSS_SELECTOR, 'video, [data-video-url], [data-src], [src]')
                    for el in elements:
                        for attr in ['data-video-url', 'data-src', 'src']:
                            url = el.get_attribute(attr)
                            if url and any(domain in url.lower() for domain in ['youtube', 'vimeo', 'loom', 'wistia', '.mp4', '.webm', '.mov']):
                                platform = detect_platform(url)
                                clean_url = clean_video_url(url, platform)
                                print(f"✅ Found {platform} video in modal element: {clean_url}")
                                return {
                                    'url': clean_url,
                                    'platform': platform,
                                    'source': 'modal_element'
                                }
                    # Check for Wistia class-based embeds
                    try:
                        wels = modal.find_elements(By.CSS_SELECTOR, 'div[class*="wistia_embed"], div[class*="wistia_async_"]')
                        import re as _re
                        for wel in wels:
                            cls = wel.get_attribute('class') or ''
                            m = _re.search(r'wistia_async_([A-Za-z0-9]+)', cls)
                            if m:
                                wid = m.group(1)
                                wistia_url = f"https://fast.wistia.net/embed/iframe/{wid}"
                                print(f"✅ Found Wistia via class in modal: {wistia_url}")
                                return {
                                    'url': wistia_url,
                                    'platform': 'wistia',
                                    'source': 'modal_wistia_class'
                                }
                    except Exception:
                        pass
            except Exception:
                continue
        return None
    except Exception as e:
        print(f"⚠️ Modal extraction failed: {e}")
        return None

def detect_custom_video_player(driver):
    """
    Enhanced detection for custom video players (like New Society community)
    """
    try:
        print("🎬 Looking for custom video player elements...")
        
        # Custom video player selectors based on the provided HTML
        custom_selectors = [
            # Target the actual play button path element first
            'svg path[d*="M62.6071 7.28471C61.8729 4.52706"]',  # Exact path from your HTML
            'svg path[fill="#202124"]',  # Dark gray/black fill color
            'svg path[fill-opacity="1"]',  # Full opacity
            # Target the SVG container
            'svg[width="64"][height="46"]',  # Exact dimensions
            'svg[viewBox*="64 46"]',  # YouTube-style play button SVG
            # Target the video thumbnail wrapper
            '[class*="VideoThumbnailWrapper"]',
            '[class*="styled__VideoThumbnailWrapper"]',
            '[class*="izIljW"]',  # Specific class from the HTML
            # Target the play button triangle
            'svg path[d*="M42.3533 22.5883L25.4121 13.1765V32"]',  # White play button triangle
            'svg path[fill="#FFFFFF"]',  # White play button triangle
            '[class*="ScrollWrapper"]',
            '[class*="fiVJWH"]',  # Scroll wrapper class
            'div[style*="justify-content: center"]',
        ]
        
        for selector in custom_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"🎬 Found {len(elements)} custom video element(s) with selector: {selector}")
                    
                    for element in elements:
                        print(f"🎬 Checking custom element - tag: {element.tag_name}, class: '{element.get_attribute('class')}'")
                        
                        # Try to click on the custom video element
                        try:
                            print(f"🎬 Attempting to click custom video element...")
                            
                            # If it's a path element (the actual play button), try clicking it directly
                            if element.tag_name == 'path':
                                print(f"🎬 Clicking SVG path element (play button)...")
                                driver.execute_script("arguments[0].click();", element)
                            else:
                                # For other elements, try clicking them
                                driver.execute_script("arguments[0].click();", element)
                            
                            time.sleep(3)  # Wait for video to load
                            
                            # Check for video URL in various sources
                            video_url = extract_video_from_custom_player(driver)
                            if video_url:
                                print(f"✅ Found video URL in custom player: {video_url}")
                                return {
                                    'url': video_url,
                                    'platform': detect_platform(video_url),
                                    'source': 'custom_player'
                                }
                            
                        except Exception as e:
                            print(f"⚠️ Error clicking custom video element: {e}")
                            continue
                            
            except Exception as e:
                print(f"⚠️ Error with custom selector {selector}: {e}")
                continue
        
        print("⚠️ No custom video player found")
        return None
        
    except Exception as e:
        print(f"❌ Error in custom video player detection: {str(e)}")
        return None

def extract_video_from_custom_player(driver):
    """
    Extract video URL from custom video player after clicking
    """
    try:
        print("🔍 Extracting video URL from custom player...")
        
        # Wait a bit for the video to load
        time.sleep(2)
        
        # STEP 2: Look for and click the red play button in the popup/modal
        print("🎬 STEP 2: Looking for red play button in popup/modal...")
        play_button_clicked = click_red_play_button_in_popup(driver)
        
        if play_button_clicked:
            print("✅ Red play button clicked, waiting for video to start...")
            time.sleep(3)  # Wait for video to start playing
        
        # Check multiple sources for video URL
        video_sources = [
            # Check for video elements
            'video[src]',
            'video source[src]',
            # Check for iframes that might have loaded
            'iframe[src*="youtube"]',
            'iframe[src*="vimeo"]',
            'iframe[src*="loom"]',
            'iframe[src*="wistia"]',
            # Check for data attributes
            '[data-video-url]',
            '[data-src]',
            '[data-video]',
            # Check for custom video containers
            '[class*="VideoPlayer"]',
            '[class*="video-player"]',
            '[class*="custom-video"]',
        ]
        
        for selector in video_sources:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    # Check src attribute
                    src = element.get_attribute('src')
                    if src and any(platform in src.lower() for platform in ['youtube', 'vimeo', 'loom', 'wistia', 'mp4', 'webm']):
                        print(f"✅ Found video URL in src: {src}")
                        return src
                    
                    # Check data attributes
                    data_video_url = element.get_attribute('data-video-url')
                    if data_video_url:
                        print(f"✅ Found video URL in data-video-url: {data_video_url}")
                        return data_video_url
                    
                    data_src = element.get_attribute('data-src')
                    if data_src:
                        print(f"✅ Found video URL in data-src: {data_src}")
                        return data_src
                    
                    data_video = element.get_attribute('data-video')
                    if data_video:
                        print(f"✅ Found video URL in data-video: {data_video}")
                        return data_video
                        
            except Exception as e:
                print(f"⚠️ Error checking selector {selector}: {e}")
                continue
        
        # Check page source for video URLs
        page_source = driver.page_source
        video_patterns = [
            r'https://[^"\s]+\.(?:mp4|webm|mov)',
            r'https://[^"\s]+youtube\.com[^"\s]*',
            r'https://[^"\s]+vimeo\.com[^"\s]*',
            r'https://[^"\s]+loom\.com[^"\s]*',
            r'https://[^"\s]+wistia\.com[^"\s]*',
        ]
        
        for pattern in video_patterns:
            matches = re.findall(pattern, page_source)
            if matches:
                print(f"✅ Found video URL in page source: {matches[0]}")
                return matches[0]
        
        print("⚠️ No video URL found in custom player")
        return None
        
    except Exception as e:
        print(f"❌ Error extracting video from custom player: {str(e)}")
        return None

def click_red_play_button_in_popup(driver):
    """
    STEP 2: Click the red play button in the popup/modal that appears after clicking thumbnail
    """
    try:
        print("🎬 Looking for red play button in popup...")
        
        # Multiple attempts with different selectors for the red play button
        play_button_selectors = [
            # YouTube-style play button selectors
            'button[aria-label*="play"]',
            'button[title*="play"]',
            'button[aria-label*="Play"]',
            'button[title*="Play"]',
            # SVG play button selectors
            'svg path[d*="M42.3533 22.5883L25.4121 13.1765V32"]',  # White play triangle
            'svg path[fill="#FFFFFF"]',  # White fill
            'svg path[fill="white"]',  # White fill
            'svg path[fill="#FFF"]',  # White fill
            # Red play button selectors (common in video players)
            'svg path[fill="#FF0000"]',  # Red fill
            'svg path[fill="red"]',  # Red fill
            'svg path[fill="#DC2626"]',  # Red-600
            'svg path[fill="#EF4444"]',  # Red-500
            # Button elements with play-related classes
            '[class*="play"]',
            '[class*="Play"]',
            '[class*="playButton"]',
            '[class*="PlayButton"]',
            # YouTube player specific
            '.ytp-play-button',
            '.ytp-large-play-button',
            # Generic play button patterns
            'button svg',
            '[role="button"] svg',
            '.video-play-button',
            '[data-testid*="play"]',
            # Modal/popup specific selectors
            '[class*="modal"] button',
            '[class*="popup"] button',
            '[class*="overlay"] button',
            '[class*="dialog"] button',
        ]
        
        for selector in play_button_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"🎬 Found {len(elements)} potential play button(s) with selector: {selector}")
                    
                    for element in elements:
                        # Check if this looks like a play button
                        aria_label = element.get_attribute('aria-label') or ''
                        title = element.get_attribute('title') or ''
                        class_name = element.get_attribute('class') or ''
                        tag_name = element.tag_name
                        
                        print(f"🎬 Checking element - tag: {tag_name}, class: '{class_name[:50]}', aria: '{aria_label}', title: '{title}'")
                        
                        # Check if it's likely a play button
                        is_play_button = (
                            any(keyword in text.lower() for text in [aria_label, title, class_name] 
                                for keyword in ['play', 'video', 'watch', 'start']) or
                            tag_name in ['button', 'svg', 'path'] or
                            'play' in class_name.lower()
                        )
                        
                        if is_play_button:
                            print(f"✅ Found play button - attempting to click...")
                            try:
                                # Try clicking the element
                                driver.execute_script("arguments[0].click();", element)
                                print(f"✅ Clicked play button with selector: {selector}")
                                return True
                            except Exception as click_error:
                                print(f"⚠️ Error clicking play button: {click_error}")
                                continue
                                
            except Exception as e:
                print(f"⚠️ Error with play button selector {selector}: {e}")
                continue
        
        print("⚠️ No red play button found in popup")
        return False
        
    except Exception as e:
        print(f"❌ Error in click_red_play_button_in_popup: {str(e)}")
        return False

def extract_video_two_step_click(driver, target_lesson_id=None):
    """
    Handle two-step click workflow: 1) Click lesson container, 2) Click video player
    Now with intelligent container selection based on lesson ID
    """
    try:
        print("🎯 Step 1: Looking for lesson/post container to click...")
        
        # If we have a target lesson ID, try to find the specific container first
        if target_lesson_id:
            print(f"🎯 Looking for specific lesson with ID: {target_lesson_id}")
            
            # Try to find containers that might contain our target lesson
            specific_selectors = [
                f'a[href*="{target_lesson_id}"]',
                f'[data-lesson-id*="{target_lesson_id}"]',
                f'[data-module-id*="{target_lesson_id}"]',
                f'[href*="md={target_lesson_id}"]',
                # Look for containers with the lesson ID in their attributes
                f'[class*="lesson"][href*="{target_lesson_id}"]',
                f'[class*="module"][href*="{target_lesson_id}"]'
            ]
            
            for selector in specific_selectors:
                try:
                    specific_containers = driver.find_elements(By.CSS_SELECTOR, selector)
                    if specific_containers:
                        print(f"🎯 Found {len(specific_containers)} specific container(s) with selector: {selector}")
                        container = specific_containers[0]
                        print(f"🎯 Clicking specific container: {container.tag_name} with text: '{container.text[:50]}...'")
                        driver.execute_script("arguments[0].click();", container)
                        time.sleep(3)  # Wait for content to load
                        container_clicked = True
                        break
                except Exception as e:
                    print(f"⚠️ Error with specific selector {selector}: {str(e)}")
                    continue
        
        # Fallback to general container selection with better targeting
        print("🎯 No specific lesson found, using intelligent container selection...")
        
        # Try different selectors for lesson containers - Focus on main lesson post
        container_selectors = [
            # Look for the main lesson post container first
            'div[class*="styled__PostContentWrapper"]:first-of-type',
            'div[class*="PostContentWrapper"]:first-of-type',
            'div[class*="styled__PostContent"]:first-of-type', 
            'div[class*="PostContent"]:first-of-type',
            # Look for containers that might be the main lesson (not comments/posts)
            'div[class*="LessonContent"]',
            'div[class*="ModuleContent"]',
            'div[class*="CourseContent"]',
            # Fallback to more generic selectors
            'a[href*="/new-video-i-built-a-yt-strategist"]',  # Specific link from your HTML
            'a[class*="ChildrenLink"]',  # The specific class from your HTML
            '[class*="PostItem"]',
            '[class*="ModuleWrapper"]',
            '[class*="CourseContent"]',
            '[class*="LessonContainer"]',
            '.post-item',
            '.lesson-item',
            '[data-testid*="post"]',
            '[data-testid*="lesson"]'
        ]
        
        container_clicked = False
        for selector in container_selectors:
            try:
                containers = driver.find_elements(By.CSS_SELECTOR, selector)
                if containers:
                    print(f"🎯 Found {len(containers)} container(s) with selector: {selector}")
                    
                    # Instead of clicking the first container, analyze them to find the best one
                    best_container = None
                    for i, container in enumerate(containers):
                        container_text = container.text.strip()
                        container_href = container.get_attribute('href') or ''
                        
                        print(f"🎯 Container {i+1}: text='{container_text[:50]}...', href='{container_href[:50]}...'")
                        
                        # Skip containers that look like comments or unrelated posts
                        if any(skip_word in container_text.lower() for skip_word in ['comment', 'reply', 'like', 'share', 'follow']):
                            print(f"🎯 Skipping container {i+1} - appears to be a comment/post")
                            continue
                            
                        # Prefer containers that look like main lesson content
                        if any(keyword in container_text.lower() for keyword in ['lesson', 'module', 'video', 'tutorial', 'guide']):
                            print(f"🎯 Container {i+1} looks like main lesson content")
                            best_container = container
                            break
                    
                    # If no specific lesson container found, use the first one that's not clearly a comment
                    if not best_container and containers:
                        best_container = containers[0]
                    
                    if best_container:
                        print(f"🎯 Clicking best container: {best_container.tag_name} with text: '{best_container.text[:50]}...'")
                        driver.execute_script("arguments[0].click();", best_container)
                        time.sleep(3)  # Wait for content to load
                        container_clicked = True
                        break
            except Exception as e:
                print(f"⚠️ Error with selector {selector}: {str(e)}")
                continue
        
        if not container_clicked:
            print("⚠️ No lesson container found to click")
            return None
        
        print("🎯 Step 2: Looking for video play button after container click...")
        
        # Look for play buttons first (Updated with exact selectors from HTML)
        play_button_selectors = [
            '.styled__VideoThumbnailWrapper-sc-1k73vxa-2',  # Exact video container class
            '[class*="VideoThumbnailWrapper"]',  # Partial match for video container
            'div[class*="VideoThumbnail"]',  # Alternative container pattern
            'div[style*="justify-content: center"]',  # The centered div container
            'svg path[d="M42.3533 22.5883L25.4121 13.1765V32"]',  # Exact play button path
            'svg path[fill="#FFFFFF"]',  # White play button triangle
            'path[d*="M42.3533 22.5883L25.4121 13.1765V32"]',  # Partial path match
            '[class*="lbvBBI"]',  # Legacy class from previous HTML
            'svg path[fill="white"]',
            'svg path[fill="#FFF"]',
            'button[aria-label*="play"]',
            'button[title*="play"]', 
            '[class*="play"]',
            '[class*="Play"]',
            'button svg',
            '[role="button"] svg',
            '.video-play-button',
            '[data-testid*="play"]'
        ]
        
        play_button_clicked = False
        for selector in play_button_selectors:
            try:
                buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                if buttons:
                    print(f"🎯 Found {len(buttons)} play button(s) with selector: {selector}")
                    
                for button in buttons:
                    # Check if this looks like a play button
                    button_text = button.get_attribute('textContent') or ''
                    aria_label = button.get_attribute('aria-label') or ''
                    title = button.get_attribute('title') or ''
                    class_name = button.get_attribute('class') or ''
                    
                    print(f"🎯 Checking button - tag: {button.tag_name}, class: '{class_name[:50]}', text: '{button_text[:30]}', aria: '{aria_label}', title: '{title}'")
                    
                    if any(keyword in text.lower() for text in [button_text, aria_label, title] 
                           for keyword in ['play', 'video', 'watch']):
                        print(f"✅ Found play button by text/attributes with selector: {selector}")
                        driver.execute_script("arguments[0].click();", button)
                        time.sleep(3)  # Wait for video to load
                        play_button_clicked = True
                        break
                    
                    # Check for video thumbnail containers (most likely to work) - More aggressive matching
                    if ('VideoThumbnail' in selector or 'VideoThumbnail' in class_name or 
                        'lbvBBI' in selector or 'lbvBBI' in class_name or 
                        'justify-content: center' in selector or
                        'styled__VideoThumbnailWrapper' in class_name):
                        print(f"✅ Found video thumbnail container with selector: {selector}")
                        driver.execute_script("arguments[0].click();", button)
                        print("⏳ Waiting for video player to load...")
                        time.sleep(5)  # Increased wait time for video to load
                        play_button_clicked = True
                        break
                    
                    # Also check for SVG play buttons (triangle shape) - be more aggressive
                    elif button.tag_name in ['svg', 'path'] or button.find_elements(By.TAG_NAME, 'svg') or 'path' in selector:
                        print(f"✅ Found SVG/path play button with selector: {selector}")
                        # Try clicking the button itself or its parent
                        try:
                            driver.execute_script("arguments[0].click();", button)
                        except:
                            # Try clicking parent if direct click fails
                            parent = button.find_element(By.XPATH, '..')
                            driver.execute_script("arguments[0].click();", parent)
                        time.sleep(3)  # Wait for video to load
                        play_button_clicked = True
                        break
                        
                if play_button_clicked:
                    break
            except Exception as e:
                print(f"⚠️ Error with play button selector {selector}: {str(e)}")
                continue
        
        if play_button_clicked:
            print("✅ Play button clicked, now looking for video iframe...")
        
        print("🎯 Step 3: Looking for video iframes after play button click...")
        
        # Now look for video players that appeared after clicking
        video_selectors = [
            'iframe[src*="youtube"]',
            'iframe[src*="vimeo"]',
            'iframe[src*="loom"]',
            'iframe[src*="wistia"]',
            'iframe',  # Check all iframes
            '[class*="VideoPlayer"]',
            '[class*="ReactPlayer"]',
            'video',
            '[data-video-url]',
            '[data-src*="youtube"]',
            '[data-src*="vimeo"]',
            '[data-src*="loom"]'
        ]
        
        print(f"🔍 Looking for video elements after play button click...")
        for selector in video_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"🎬 Found {len(elements)} element(s) with selector: {selector}")
                for element in elements:
                    print(f"🔍 Examining {element.tag_name} element...")
                    # Try different attributes for video URL
                    for attr in ['src', 'data-src', 'data-video-url', 'data-url', 'href']:
                        url = element.get_attribute(attr)
                        if url:
                            print(f"   📄 {attr}: {url[:100]}...")
                            if any(platform in url.lower() for platform in ['youtube', 'vimeo', 'loom', 'wistia']):
                                platform = detect_platform(url)
                                clean_url = clean_video_url(url, platform)
                                print(f"✅ Found {platform} video after two-step click: {clean_url}")
                                return {
                                    'url': clean_url,
                                    'platform': platform,
                                    'source': 'two_step_click',
                                    'element_type': element.tag_name,
                                    'selector_used': selector
                                }
                        else:
                            print(f"   ⚪ {attr}: None")
            except Exception as e:
                continue
        
        print("⚠️ No video found after two-step click workflow")
        return None
        
    except Exception as e:
        print(f"❌ Error in two-step click workflow: {str(e)}")
        return None

def extract_video_url_universal_with_retry(driver, use_all_methods=False, target_lesson_id=None, max_retries=2):
    """Wrapper function with retry logic for video extraction"""
    
    for attempt in range(max_retries):
        try:
            print(f"🔄 VIDEO EXTRACTION ATTEMPT {attempt + 1}/{max_retries}")
            result = extract_video_url_universal(driver, use_all_methods, target_lesson_id)
            if result:
                print(f"✅ EXTRACTION SUCCESS on attempt {attempt + 1}")
                return result
            else:
                print(f"⚠️ EXTRACTION FAILED on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    print("🔄 Retrying extraction after clearing state...")
                    # Clear browser state between attempts
                    driver.execute_script("window.scrollTo(0, 0);")  # Reset scroll
                    time.sleep(1)
        except Exception as e:
            print(f"❌ EXTRACTION ERROR on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)  # Wait before retry
    
    print("❌ ALL EXTRACTION ATTEMPTS FAILED")
    return None

def extract_video_url_universal(driver, use_all_methods=False, target_lesson_id=None):
    """Enhanced video extraction supporting multiple platforms (YouTube, Vimeo, etc.)
    If use_all_methods is True, also attempt the two-step click workflow.
    
    RELIABILITY ENHANCEMENTS:
    - Proper wait conditions for navigation and elements
    - Element validation before interaction  
    - Retry logic with exponential backoff
    - Success validation before returning
    """
    
    # RELIABILITY FIX: Success validation function
    def validate_video_data(video_data):
        """Validate that video data is actually usable"""
        if not video_data:
            return False
        url = video_data.get('url', '')
        if not url or len(url) < 10:
            return False
        # Check it's not a thumbnail image
        if any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
            print(f"⚠️ Rejecting thumbnail image URL: {url}")
            return False
        # Check it's a valid video URL
        valid_platforms = ['youtube.com', 'youtu.be', 'vimeo.com', 'loom.com', 'wistia', '.mp4', '.m3u8', '.webm']
        if not any(platform in url.lower() for platform in valid_platforms):
            print(f"⚠️ Rejecting non-video URL: {url}")
            return False
        return True
    
    # Method 1: JSON data extraction (most reliable)
    print("🔍 METHOD 1: JSON data extraction...")
    video_data = extract_from_next_data(driver)
    if video_data and validate_video_data(video_data):
        print(f"✅ METHOD 1 SUCCESS: {video_data.get('url')}")
        return video_data
    elif video_data:
        print(f"⚠️ METHOD 1 INVALID: {video_data.get('url')}")
    
    # Method 2: iframe scanning (all platforms)
    print("🔍 METHOD 2: iframe scanning...")
    video_data = scan_video_iframes(driver)
    if video_data and validate_video_data(video_data):
        print(f"✅ METHOD 2 SUCCESS: {video_data.get('url')}")
        return video_data
    elif video_data:
        print(f"⚠️ METHOD 2 INVALID: {video_data.get('url')}")
    
    # Method 2.5: Safe video thumbnail click (with navigation handling)
    print("🔍 METHOD 2.5: Safe video thumbnail click...")
    original_url = driver.current_url
    video_data = click_video_thumbnail_safely(driver)
    if video_data and validate_video_data(video_data):
        print(f"✅ METHOD 2.5 SUCCESS: {video_data.get('url')}")
        return video_data
    elif video_data:
        print(f"⚠️ METHOD 2.5 INVALID: {video_data.get('url')}")
    
    # Method 2.6: Check if we navigated to a lesson page and extract video from there
    current_url = driver.current_url
    if original_url != current_url:
        print(f"🔍 Detected navigation from {original_url} to {current_url}")
        
        # Check if we navigated to a lesson page (not classroom)
        if "classroom" not in current_url and len(current_url) > len(original_url):
            print("🔍 Navigation detected to lesson page - extracting video from new page...")
            
            # RELIABILITY FIX: Proper wait for navigation and page load
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            try:
                # Wait for navigation to fully complete (URL stabilizes)
                WebDriverWait(driver, 10).until(lambda d: d.current_url == current_url)
                print("✅ Navigation completed successfully")
                
                # Wait for page to be fully loaded (DOM ready)
                WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")
                print("✅ Page DOM loaded completely")
                
                # Additional wait for dynamic content (video elements)
                time.sleep(2)
                print("✅ Waiting for dynamic video content to load...")
                
            except Exception as e:
                print(f"⚠️ Navigation wait failed: {e}, proceeding anyway...")
            
            # Try all extraction methods on the new page with retry logic
            extraction_methods = [
                ("JSON data", extract_from_next_data),
                ("iframe scan", scan_video_iframes),
                ("network logs", extract_video_from_network_logs),
                ("thumbnail click", click_video_thumbnail_safely)
            ]
            
            for method_name, method_func in extraction_methods:
                for attempt in range(2):  # Try each method twice
                    try:
                        print(f"🔍 Attempting {method_name} extraction (attempt {attempt + 1}/2)...")
                        video_data = method_func(driver)
                        if video_data and video_data.get('url'):
                            print(f"✅ Found video via {method_name} on lesson page: {video_data.get('url')}")
                            return video_data
                        elif attempt == 0:
                            # Wait before retry
                            print(f"⚠️ {method_name} failed, waiting before retry...")
                            time.sleep(1)
                    except Exception as e:
                        print(f"⚠️ {method_name} extraction error (attempt {attempt + 1}): {e}")
                        if attempt == 0:
                            time.sleep(1)  # Wait before retry
                
            print("⚠️ No video found on navigated lesson page after all methods")
        else:
            print("⚠️ Navigation detected but not to a lesson page")
    
    # Method 3: Two-step click workflow (enabled but with navigation protection)
    print("🔍 Trying two-step click workflow with navigation protection...")
    original_url = driver.current_url
    video_data = extract_video_two_step_click(driver, target_lesson_id)
    if video_data:
        # Check if we navigated away from the target lesson
        current_url = driver.current_url
        if original_url not in current_url and current_url not in original_url:
            print("⚠️ Navigation detected - returning to original lesson...")
            driver.get(original_url)
            time.sleep(3)
        return video_data
    
    # Method 3.5: Network logs inspection (capture HLS/MP4 or hidden player requests)
    print("🔍 Inspecting network logs for media URLs...")
    network_video = extract_video_from_network_logs(driver)
    if network_video:
        return network_video

    # Method 4: Fallback to original YouTube extraction for backward compatibility
    print("🔄 Falling back to original YouTube extraction...")
    youtube_url = extract_youtube_url_legacy(driver)
    if youtube_url:
        return {
            'url': youtube_url,
            'platform': 'youtube',
            'thumbnail': None,
            'duration': None
        }
    
    print("⚠️ No video found using any method")
    return None

def extract_video_from_network_logs(driver):
    """Inspect Chrome performance logs for media URLs (mp4, m3u8, known platforms)."""
    try:
        # Fetch performance logs
        logs = []
        try:
            logs = driver.get_log('performance')
        except Exception:
            pass

        def _is_probable_video_url(url: str) -> bool:
            u = (url or '').lower()
            # Exclude common image assets
            if any(u.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']):
                return False
            # Accept direct media files or HLS
            if any(ext in u for ext in ['.m3u8', '.mp4', '.webm', '.mov']):
                return True
            # Accept known player/embeds (but prefer direct video URLs over oembed)
            if ('youtube.com' in u or 'youtu.be' in u or 'vimeo.com' in u or 'loom.com' in u or
                'fast.wistia.net/embed/iframe/' in u or 'wistia.com/medias/' in u):
                return True
            # Exclude Wistia delivery images and oembed URLs
            if 'wistia' in u and ('deliveries' in u or 'oembed' in u):
                return False
            return False

        candidates = []
        for entry in logs:
            try:
                msg = json.loads(entry.get('message', '{}'))
                params = msg.get('message', {}).get('params', {})
                request = params.get('request', {})
                response = params.get('response', {})
                url = request.get('url') or response.get('url')
                if not url:
                    continue
                if _is_probable_video_url(url):
                    candidates.append(url)
            except Exception:
                continue

        # Prefer direct media first, then platform URLs
        prioritized = sorted(candidates, key=lambda u: (('m3u8' not in u and '.mp4' not in u), len(u)))
        if prioritized:
            best = prioritized[0]
            
            # If it's a Wistia oembed URL, extract the actual video URL
            if 'wistia.com' in best and 'oembed' in best:
                try:
                    import urllib.parse
                    parsed = urllib.parse.urlparse(best)
                    query_params = urllib.parse.parse_qs(parsed.query)
                    if 'url' in query_params:
                        actual_url = query_params['url'][0]
                        # Extract the video ID from the Wistia URL
                        if 'wistia.com/medias/' in actual_url:
                            video_id = actual_url.split('/medias/')[-1]
                            direct_wistia_url = f"https://ondrejdavidbusiness.wistia.com/medias/{video_id}"
                            print(f"✅ Found Wistia video via network logs: {direct_wistia_url}")
                            return {
                                'url': direct_wistia_url,
                                'platform': 'wistia',
                                'source': 'network_logs'
                            }
                except Exception as e:
                    print(f"⚠️ Error extracting Wistia URL: {e}")
            
            platform = detect_platform(best)
            clean_url = clean_video_url(best, platform)
            print(f"✅ Found media via network logs: {clean_url}")
            return {
                'url': clean_url,
                'platform': platform,
                'source': 'network_logs'
            }
    except Exception as e:
        print(f"⚠️ Network log inspection failed: {e}")
    return None

def extract_youtube_url_legacy(driver):
    """Legacy YouTube extraction as fallback"""
    try:
        print("🔍 Looking for lesson-specific YouTube video (custom play button)...")
        # 1. Click the custom play button
        try:
            play_button = driver.find_element(By.CSS_SELECTOR, ".styled__PlaybackButton-sc-bpv3k2-5")
            play_button.click()
            print("▶️ Clicked custom play button.")
            time.sleep(1)  # Wait for animation
        except NoSuchElementException:
            print("⚠️ Custom play button not found, video may already be playing or structure changed.")
        except Exception as e:
            print(f"⚠️ Could not click custom play button: {e}")
        
        # 2. Wait for the YouTube iframe to appear
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='youtube.com']"))
            )
            print("✅ YouTube iframe appeared after play.")
        except Exception as e:
            print(f"❌ YouTube iframe did not appear after play: {e}")
            return None
        
        # 3. Extract the YouTube URL from the iframe
        try:
            iframe = driver.find_element(By.CSS_SELECTOR, "iframe[src*='youtube.com']")
            youtube_url = iframe.get_attribute("src")
            print(f"✅ Raw YouTube iframe URL: {youtube_url}")
            # Convert to canonical format
            match = re.search(r"(?:youtube\.com/embed/|youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})", youtube_url)
            if match:
                video_id = match.group(1)
                canonical_url = f"https://youtu.be/{video_id}"
                print(f"✅ Canonical YouTube URL: {canonical_url}")
                return canonical_url
            else:
                print("⚠️ Could not extract video ID from iframe URL, returning raw URL.")
                return youtube_url
        except Exception as e:
            print(f"❌ Could not extract YouTube URL from iframe: {e}")
            return None
    except Exception as e:
        print(f"❌ Fatal error in YouTube extraction: {e}")
        return None

def sanitize_filename_for_video(filename):
    """Sanitize filename for video downloads"""
    filename = re.sub(r'[<>:"/\\|?*🎵🤯…]', '', filename)
    filename = re.sub(r'\\s+', '_', filename)
    return filename.strip()[:100]  # Limit length

def download_video_universal(video_data, lesson_title, output_dir):
    """Download video from any supported platform"""
    if not video_data or not video_data.get('url'):
        print("⚠️ No video data to download")
        return False
    
    try:
        video_url = video_data['url']
        platform = video_data['platform']
        
        print(f"📥 Downloading {platform} video: {lesson_title}")
        print(f"🔗 URL: {video_url}")
        safe_title = sanitize_filename_for_video(lesson_title)
        output_path = os.path.join(output_dir, f"{safe_title}.%(ext)s")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        if platform in ['youtube', 'vimeo', 'loom']:
            # Use yt-dlp for supported platforms
            process = subprocess.run([
                sys.executable, "-m", "yt_dlp",
                video_url,
                "--format", "best[ext=mp4]/best",
                "--merge-output-format", "mp4",
                "-o", output_path,
                "--no-overwrites",
                "--ignore-errors"
            ], check=False, capture_output=True, text=True, encoding='utf-8')
            
            if process.returncode == 0:
                print(f"✅ {platform.title()} video downloaded successfully: {safe_title}")
                return True
            else:
                print(f"❌ {platform.title()} download failed: {process.stderr}")
                return False
                
        elif platform == 'direct':
            # Direct download for MP4/video files
            parsed_url = urlparse(video_url)
            file_ext = os.path.splitext(parsed_url.path)[1] or '.mp4'
            direct_output_path = os.path.join(output_dir, f"{safe_title}{file_ext}")
            
            urllib.request.urlretrieve(video_url, direct_output_path)
            print(f"✅ Direct video downloaded successfully: {safe_title}")
            return True
            
        else:
            print(f"⚠️ Unsupported platform for download: {platform}")
            return False
            
    except FileNotFoundError:
        print("❌ yt-dlp module not accessible. Please install: pip install yt-dlp")
        return False
    except Exception as e:
        print(f"❌ Video download error: {e}")
        return False

def extract_content(driver):
    """Extract lesson content"""
    try:
        print("📝 Extracting lesson content...")
        time.sleep(3)
        
        content = {
            'text_content': 'No content found',
            'links': []
        }
        
        # Look for main content area - Target the specific lesson post, not comments
        content_selectors = [
            # Target the main lesson post specifically (first/primary post)
            "div[class*='styled__PostContentWrapper']:first-of-type",
            "div[class*='PostContentWrapper']:first-of-type", 
            "div[class*='styled__PostContent']:first-of-type",
            "div[class*='PostContent']:first-of-type",
            # Try to find content within the main post structure
            ".styled__RichTextEditorWrapper-sc-1cnx5by-0",
            "[class*='RichTextEditor']",
            "[class*='EditorContent']",
            ".tiptap.ProseMirror",
            "[class*='ModuleBody']", 
            # Generic post content (these might pick up comments instead of main lesson)
            "[class*='PostContent']",  # Skool post content
            "[class*='PostBody']",     # Skool post body
            "[class*='MessageContent']", # Skool message content
            "[class*='content']",
            "[class*='description']",
            "div[class*='MainContent']",
            "main",
            "[role='main']",
            "article"
        ]
        
        print("🔍 Searching for content elements on the page...")
        
        # First, let's see what posts are available on the page
        try:
            all_posts = driver.find_elements(By.CSS_SELECTOR, "[class*='PostContent'], [class*='PostContentWrapper'], [class*='styled__PostContent']")
            print(f"📋 Found {len(all_posts)} post-like elements on the page:")
            for i, post in enumerate(all_posts[:5]):  # Show first 5 posts
                post_preview = post.text.strip()[:80] if post.text.strip() else "No text"
                print(f"   {i+1}. '{post_preview}...'")
        except Exception as e:
            print(f"⚠️ Could not list posts: {e}")
        
        main_content_element = None
        for selector in content_selectors:
            try:
                main_content_element = driver.find_element(By.CSS_SELECTOR, selector)
                if main_content_element and main_content_element.text.strip():
                    content_preview = main_content_element.text.strip()[:100]
                    print(f"✅ Extracted content using selector: {selector}")
                    print(f"📝 Content preview: '{content_preview}...'")
                    
                    # Use the first substantial content found (don't filter by specific text)
                    content_text = main_content_element.text.strip()
                    if len(content_text) > 50:  # Ensure we have substantial content
                        print("🎯 Found lesson content!")
                        break
                    else:
                        print("⚠️ Content too short, trying next selector...")
                        main_content_element = None
                        continue
            except Exception:
                continue
        
        if main_content_element:
            text_content = main_content_element.text
            content['text_content'] = re.sub(r'\\n{3,}', '\\n\\n', text_content).strip()

            # 1. Extract links from <a> tags
            links_from_tags = []
            links = main_content_element.find_elements(By.TAG_NAME, "a")
            for link in links:
                try:
                    href = link.get_attribute("href")
                    text = link.text.strip()
                    if href and text:
                        links_from_tags.append({'text': text, 'url': href})
                except Exception:
                    continue
            
            # 2. Extract plain text URLs using regex
            plain_text_urls = []
            url_pattern = r'https?://[^\\s/$.?#].[^\\s]*'
            found_urls = re.findall(url_pattern, text_content)
            for url in found_urls:
                plain_text_urls.append({'text': url, 'url': url})
                
            # Combine and de-duplicate links
            all_links = links_from_tags
            all_urls = {link['url'] for link in all_links}
            
            for link in plain_text_urls:
                if link['url'] not in all_urls:
                    all_links.append(link)
                    all_urls.add(link['url'])

            content['links'] = all_links
        else:
            print("⚠️ Using fallback content extraction")
            body = driver.find_element(By.TAG_NAME, "body")
            content['text_content'] = re.sub(r'\\n{3,}', '\\n\\n', body.text).strip()

        print(f"📝 Content length: {len(content['text_content'])} characters")
        print(f"🔗 Links found: {len(content['links'])}")
        return content
        
    except Exception as e:
        print(f"❌ Error extracting content: {str(e)}")
        return {'text_content': 'Error extracting content', 'links': []}

def save_lesson_organized(lesson_name, video_data, content, lesson_url, community_display_name, community_slug, download_video=False):
    """Save lesson with organized structure: Communities/Community Name (slug)/lessons/images/videos"""
    try:
        # Create organized directories
        dirs = create_organized_directories(community_display_name, community_slug)
        
        # Create short, safe filename (no subdirectories for lessons)
        safe_title = lesson_name
        # Remove or replace emojis and special characters
        safe_title = re.sub(r'[^\w\s-]', '', safe_title)  # Remove non-alphanumeric except spaces and hyphens
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', safe_title)  # Replace Windows forbidden chars
        safe_title = re.sub(r'\s+', ' ', safe_title).strip()  # Normalize spaces
        safe_title = safe_title.replace('!', '').replace('$', 'USD')  # Handle specific chars
        # Keep it very short for Windows compatibility
        if len(safe_title) > 30:
            safe_title = safe_title[:30].strip()
        
        print(f"📝 Safe title: '{safe_title}'")
        
        # Create markdown file directly in lessons folder (no subdirectories)
        filename = f"{safe_title}.md"
        filepath = os.path.join(dirs['lessons'], filename)
        print(f"📄 Creating file: {filepath}")
        print(f"📁 Lessons directory exists: {os.path.exists(dirs['lessons'])}")
        
        # Format video info
        if video_data and video_data.get('url'):
            # Clean the video URL before saving to file
            clean_url = clean_video_url(video_data['url'], video_data['platform'])
            video_info = f"**🎥 Video ({video_data['platform'].title()}):** {clean_url}"
            if video_data.get('duration'):
                duration_sec = int(video_data['duration']) / 1000
                minutes = int(duration_sec // 60)
                seconds = int(duration_sec % 60)
                video_info += f" (Duration: {minutes}:{seconds:02d})"
        else:
            video_info = "**🎥 Video:** No video found"
        
        community_info = f"**📂 Community:** {community_display_name if community_display_name else 'Unknown Community'}"
        
        markdown_content = f"""# {lesson_name}

**Extracted on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{video_info}
{community_info}
**📂 Lesson Folder:** {safe_title}

## 📝 Content

{content['text_content']}
"""
        # Add links section if we have links
        if content['links']:
            markdown_content += """
## 🔗 Links and Resources
"""
            for link in content['links']:
                markdown_content += f"- [{link['text']}]({link['url']})\\n"
            markdown_content += "\\n"
        
        # Add metadata
        video_status = "✅ Found" if video_data and video_data.get('url') else "❌ No video"
        community_name_for_footer = community_display_name if community_display_name else "Unknown Community"
        markdown_content += f"""
---
*Extracted from Skool {community_name_for_footer} - V2 Universal Video Support*
*Video: {video_status}*
*Lesson URL: {lesson_url}*
"""
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
        except Exception as e:
            print(f"❌ File write error: {str(e)}")
            # Try with normalized path
            normalized_path = os.path.normpath(filepath)
            print(f"🔄 Trying normalized path: {normalized_path}")
            with open(normalized_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
        
        print(f"✅ Lesson saved successfully!")
        print(f"📂 Community: {community_display_name}")
        print(f"📂 Folder: {dirs['lessons']}")
        print(f"📄 File: {filepath}")
        
        # Download video if requested and available
        if video_data and video_data.get('url'):
            if download_video:
                print(f"🎥 Attempting to download {video_data['platform']} video...")
                download_success = download_video_universal(video_data, lesson_name, dirs['videos'])
                if download_success:
                    print(f"✅ Video downloaded to: {dirs['videos']}")
                else:
                    print(f"⚠️ Video download failed, but lesson content saved")
            else:
                clean_url = clean_video_url(video_data['url'], video_data['platform'])
                print(f"🎥 Video URL extracted: {clean_url}")
                print(f"💡 Use --download-video flag to download the video file")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving lesson: {str(e)}")
        return False

def main():
    """Main extraction function"""
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Extract a single lesson from Skool.com with hierarchical structure')
    parser.add_argument('url', help='The Skool.com lesson URL to extract')
    parser.add_argument('--email', default=SKOOL_EMAIL, help='Skool.com email (default: from config)')
    parser.add_argument('--password', default=SKOOL_PASSWORD, help='Skool.com password (default: from config)')
    parser.add_argument('--download-video', action='store_true', help='Download video files to local storage (requires yt-dlp). Default: extract video URLs only')
    
    args = parser.parse_args()
    
    # Validate URL
    if not args.url.startswith('https://www.skool.com/'):
        print("❌ Error: URL must be a valid Skool.com URL")
        print("Example: https://www.skool.com/ai-automation-society/classroom/832a1e6e?md=xxx")
        sys.exit(1)
    
    # Extract community info from URL
    community, section, lesson_id = extract_community_info_from_url(args.url)
    if not community:
        community = "unknown-community"
        section = "classroom"
        print("⚠️ Could not extract community from URL, using 'unknown-community'")
    
    print("=" * 60)
    print("🎯 ENHANCED SINGLE LESSON EXTRACTOR")
    print("=" * 60)
    print(f"🌐 Community: {community}")
    print(f"📚 Section: {section}")
    print(f"🎯 Target URL: {args.url}")
    
    driver = setup_driver()
    
    try:
        if not login_to_skool(driver, args.email, args.password):
            print("❌ Login failed - cannot proceed")
            return
        
        print(f"🔗 Navigating to lesson...")
        driver.get(args.url)
        time.sleep(5)
        
        # Extract clean community name
        print("\n🏷️ Extracting clean community name...")
        community_display_name = extract_clean_community_name(driver)
        if community_display_name:
            print(f"✅ Clean Community Name: {community_display_name}")
        else:
            print("⚠️ Using URL slug as fallback community name")
            community_display_name = community.replace('-', ' ').title()  # Convert slug to readable name
        
        # Extract lesson name
        lesson_name = extract_lesson_name(driver)
        if not lesson_name:
            lesson_name = "Untitled Lesson - " + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        
        # Extract video with universal detection (aggressive all-methods mode)
        # Extract lesson ID from URL for better targeting
        lesson_module_id = None
        if 'md=' in args.url:
            lesson_module_id = args.url.split('md=')[1].split('&')[0]
            print(f"🎯 Extracted lesson module ID: {lesson_module_id}")
        
        video_data = extract_video_url_universal_with_retry(driver, use_all_methods=True, target_lesson_id=lesson_module_id)
        
        # Extract content
        content = extract_content(driver)
        
        # Save lesson with organized structure  
        if save_lesson_organized(lesson_name, video_data, content, args.url, community_display_name, community, args.download_video):
            print("\\n🎉 SUCCESS! Lesson extracted and saved with organized structure.")
            folder_name = f"{community_display_name} ({community})" if community_display_name else f"Unknown Community ({community})"
            print(f"📁 Check: Communities/{folder_name}/lessons/{re.sub(r'[^\\w\\s-]', '', lesson_name)[:30]}.md")
        else:
            print("\\n❌ FAILED to save lesson.")
        
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        traceback.print_exc()
    finally:
        driver.quit()
        print("\\n🌐 Browser closed.")

def offer_cleanup():
    """Offer cleanup option before starting extraction"""
    try:
        # Allow CI/non-interactive runs to skip prompts
        if os.getenv("SKIP_CLEANUP_PROMPT", "").strip() == "1":
            return True
        from pathlib import Path
        communities_dir = Path.cwd() / "Communities"
        
        if communities_dir.exists():
            existing_communities = [d.name for d in communities_dir.iterdir() if d.is_dir()]
            if existing_communities:
                print(f"\n🧹 CLEANUP OPTION:")
                print(f"Found {len(existing_communities)} existing community folders:")
                for i, name in enumerate(existing_communities[:3], 1):
                    print(f"   {i}. {name}")
                if len(existing_communities) > 3:
                    print(f"   ... and {len(existing_communities) - 3} more")
                
                print("\nFor single lesson extraction, you may want to:")
                print("1. Continue (lesson will be added to existing community)")
                print("2. Clean specific community first")
                print("3. Exit and run cleanup manually")
                
                while True:
                    choice = input("\n👉 Select option (1-3): ").strip()
                    if choice == '1':
                        print("✅ Continuing - lesson will be added to existing structure")
                        return True
                    elif choice == '2':
                        print("🧹 Starting cleanup tool for community selection...")
                        try:
                            import subprocess
                            result = subprocess.run([sys.executable, "cleanup_scraper.py"], 
                                                  capture_output=False)
                            if result.returncode == 0:
                                print("✅ Cleanup completed! Continuing with extraction...")
                                return True
                            else:
                                print("❌ Cleanup failed or was cancelled.")
                                return False
                        except Exception as e:
                            print(f"❌ Could not run cleanup tool: {e}")
                            print("💡 Try running: python cleanup_scraper.py")
                            return False
                    elif choice == '3':
                        print("👋 Exiting. Run 'python cleanup_scraper.py' first.")
                        return False
                    else:
                        print("❌ Invalid option. Please select 1-3.")
    except Exception as e:
        print(f"⚠️  Cleanup check failed: {e}")
        return True  # Continue anyway
    
    return True

if __name__ == "__main__":
    if offer_cleanup():
        main()