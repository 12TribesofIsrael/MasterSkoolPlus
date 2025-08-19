#!/usr/bin/env python3
"""
🎯 ENHANCED Skool Content Extractor
Extracts lesson content, YouTube URLs, images, and hyperlinks from Skool.com classroom collections.
Uses direct URL navigation to avoid stale element issues.
"""

import os
import time
import re
import json
import random
import urllib.request
import argparse
import sys
import subprocess
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configuration
# Optionally load environment variables from a .env file if present
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

# Read credentials from environment variables to avoid hardcoding secrets
SKOOL_EMAIL = os.getenv("SKOOL_EMAIL", "")  # Skool email from environment
SKOOL_PASSWORD = os.getenv("SKOOL_PASSWORD", "")  # Skool password from environment

# Enhanced session-level tracking to prevent duplicate video URLs across lessons in a single run
SEEN_VIDEO_IDS_SESSION = set()

# Enhanced session tracking with detailed metadata
SESSION_VIDEO_TRACKING = {}

# Session statistics for reporting
SESSION_STATS = {
    'videos_processed': 0,
    'duplicates_blocked': 0,
    'unique_videos_found': 0,
    'lessons_processed': 0,
    'extraction_methods_used': set(),
    'platforms_detected': set()
}

# Lesson-specific validation tracking
LESSON_CONTEXT = {
    'current_lesson_title': None,
    'current_lesson_url': None,
    'current_lesson_id': None,
    'lesson_video_signatures': {},  # Store video signatures per lesson
    'lesson_content_hashes': {},    # Store content hashes per lesson
    'lesson_validation_cache': {}   # Cache validation results per lesson
}

# Browser isolation tracking
BROWSER_ISOLATION = {
    'current_browser_instance': None,
    'browser_instances_created': 0,
    'browser_instances_destroyed': 0,
    'isolation_mode': 'shared',  # 'shared' or 'isolated'
    'isolation_stats': {
        'lessons_with_isolated_browsers': 0,
        'lessons_with_shared_browser': 0,
        'browser_creation_time': 0,
        'browser_destruction_time': 0
    }
}

# Enhanced debugging - track video extraction attempts across all methods
VIDEO_EXTRACTION_DEBUG_LOG = []

def reset_session_tracking():
    """Reset all session-level tracking for a new scraping session"""
    global SEEN_VIDEO_IDS_SESSION, SESSION_VIDEO_TRACKING, SESSION_STATS, VIDEO_EXTRACTION_DEBUG_LOG, LESSON_CONTEXT, BROWSER_ISOLATION
    
    SEEN_VIDEO_IDS_SESSION.clear()
    SESSION_VIDEO_TRACKING.clear()
    VIDEO_EXTRACTION_DEBUG_LOG.clear()
    
    SESSION_STATS.update({
        'videos_processed': 0,
        'duplicates_blocked': 0,
        'unique_videos_found': 0,
        'lessons_processed': 0,
        'extraction_methods_used': set(),
        'platforms_detected': set()
    })
    
    # Reset lesson context
    LESSON_CONTEXT.update({
        'current_lesson_title': None,
        'current_lesson_url': None,
        'current_lesson_id': None,
        'lesson_video_signatures': {},
        'lesson_content_hashes': {},
        'lesson_validation_cache': {}
    })
    
    # Reset browser isolation tracking
    BROWSER_ISOLATION.update({
        'current_browser_instance': None,
        'browser_instances_created': 0,
        'browser_instances_destroyed': 0,
        'isolation_mode': 'shared',
        'isolation_stats': {
            'lessons_with_isolated_browsers': 0,
            'lessons_with_shared_browser': 0,
            'browser_creation_time': 0,
            'browser_destruction_time': 0
        }
    })
    
    print("🔄 Session tracking reset for new scraping session")

def register_video_in_session(video_url, lesson_title, extraction_method, platform=None):
    """Register a video in the session tracking system with comprehensive metadata"""
    import datetime
    
    if not video_url:
        return False
    
    # Extract standardized video ID
    video_id = _extract_video_id_generic(video_url)
    if not video_id:
        print(f"⚠️ Could not extract video ID from URL: {video_url}")
        return True  # Allow video but without session tracking
    
    SESSION_STATS['videos_processed'] += 1
    SESSION_STATS['extraction_methods_used'].add(extraction_method)
    if platform:
        SESSION_STATS['platforms_detected'].add(platform)
    
    # Check if this video ID has been seen before in this session
    if video_id in SEEN_VIDEO_IDS_SESSION:
        SESSION_STATS['duplicates_blocked'] += 1
        
        # Get previous usage info
        previous_info = SESSION_VIDEO_TRACKING.get(video_id, {})
        previous_lesson = previous_info.get('lesson_title', 'Unknown')
        previous_method = previous_info.get('extraction_method', 'Unknown')
        previous_timestamp = previous_info.get('timestamp', 'Unknown')
        
        print(f"🚫 SESSION DUPLICATE DETECTED:")
        print(f"   📹 Video ID: {video_id}")
        print(f"   🔗 URL: {video_url}")
        print(f"   📚 Current Lesson: {lesson_title}")
        print(f"   🔧 Current Method: {extraction_method}")
        print(f"   📋 Previous Usage:")
        print(f"      └─ Lesson: {previous_lesson}")
        print(f"      └─ Method: {previous_method}")
        print(f"      └─ Time: {previous_timestamp}")
        
        log_video_extraction_attempt(
            f"{extraction_method}_SESSION_DUPLICATE", 
            lesson_title, 
            video_url, 
            'blocked',
            {
                'reason': 'session_duplicate',
                'video_id': video_id,
                'previous_lesson': previous_lesson,
                'previous_method': previous_method,
                'duplicate_count': SESSION_STATS['duplicates_blocked']
            }
        )
        
        return False  # Block this duplicate
    
    # Register new video in session tracking
    SEEN_VIDEO_IDS_SESSION.add(video_id)
    SESSION_VIDEO_TRACKING[video_id] = {
        'video_url': video_url,
        'lesson_title': lesson_title,
        'extraction_method': extraction_method,
        'platform': platform,
        'timestamp': datetime.datetime.now().isoformat(),
        'order': len(SESSION_VIDEO_TRACKING) + 1
    }
    
    SESSION_STATS['unique_videos_found'] += 1
    
    print(f"✅ SESSION TRACKING: Registered new video")
    print(f"   📹 Video ID: {video_id}")
    print(f"   📚 Lesson: {lesson_title}")
    print(f"   🔧 Method: {extraction_method}")
    print(f"   🏷️ Platform: {platform or 'Unknown'}")
    print(f"   📊 Unique videos this session: {SESSION_STATS['unique_videos_found']}")
    
    log_video_extraction_attempt(
        f"{extraction_method}_SESSION_REGISTERED", 
        lesson_title, 
        video_url, 
        'found',
        {
            'video_id': video_id,
            'platform': platform,
            'session_order': SESSION_VIDEO_TRACKING[video_id]['order'],
            'unique_count': SESSION_STATS['unique_videos_found']
        }
    )
    
    return True  # Allow this video

def check_session_duplicate_early(video_url, lesson_title, extraction_method):
    """Early duplicate detection before full validation - more efficient"""
    if not video_url:
        return False
    
    video_id = _extract_video_id_generic(video_url)
    if not video_id:
        return False  # Can't determine, let full validation handle it
    
    if video_id in SEEN_VIDEO_IDS_SESSION:
        previous_info = SESSION_VIDEO_TRACKING.get(video_id, {})
        print(f"🚫 EARLY SESSION DUPLICATE DETECTED in {extraction_method}")
        print(f"   📹 Video ID: {video_id} from lesson '{previous_info.get('lesson_title', 'Unknown')}'")
        return True  # This is a duplicate
    
    return False  # Not a duplicate

def print_session_statistics():
    """Print comprehensive session statistics"""
    print("\n📊 === SESSION STATISTICS ===")
    print(f"📚 Lessons Processed: {SESSION_STATS['lessons_processed']}")
    print(f"🎥 Videos Processed: {SESSION_STATS['videos_processed']}")
    print(f"✅ Unique Videos Found: {SESSION_STATS['unique_videos_found']}")
    print(f"🚫 Duplicates Blocked: {SESSION_STATS['duplicates_blocked']}")
    
    if SESSION_STATS['extraction_methods_used']:
        print(f"🔧 Extraction Methods Used: {', '.join(SESSION_STATS['extraction_methods_used'])}")
    
    if SESSION_STATS['platforms_detected']:
        print(f"🏷️ Platforms Detected: {', '.join(SESSION_STATS['platforms_detected'])}")
    
    if SESSION_VIDEO_TRACKING:
        print(f"\n📋 Video Usage Summary:")
        for i, (video_id, info) in enumerate(SESSION_VIDEO_TRACKING.items(), 1):
            platform = info.get('platform', 'Unknown')
            lesson = info.get('lesson_title', 'Unknown')
            method = info.get('extraction_method', 'Unknown')
            print(f"   {i:2d}. [{platform:7s}] {lesson} (via {method})")
    
    # Calculate efficiency metrics
    if SESSION_STATS['videos_processed'] > 0:
        efficiency = (SESSION_STATS['unique_videos_found'] / SESSION_STATS['videos_processed']) * 100
        print(f"\n📈 Session Efficiency: {efficiency:.1f}% unique videos")
    
    print("=" * 40)

def save_session_tracking_report():
    """Save detailed session tracking report to file"""
    try:
        import json
        import datetime
        
        # Convert sets to lists for JSON serialization
        session_stats_copy = dict(SESSION_STATS)
        session_stats_copy['extraction_methods_used'] = list(SESSION_STATS['extraction_methods_used'])
        session_stats_copy['platforms_detected'] = list(SESSION_STATS['platforms_detected'])
        
        report = {
            'session_stats': session_stats_copy,
            'video_tracking': SESSION_VIDEO_TRACKING,
            'seen_video_ids': list(SEEN_VIDEO_IDS_SESSION),
            'lesson_context': LESSON_CONTEXT,
            'browser_isolation': BROWSER_ISOLATION,
            'report_generated': datetime.datetime.now().isoformat()
        }
        
        with open('debug_session_tracking_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Session tracking report saved: debug_session_tracking_report.json")
        
    except Exception as e:
        print(f"⚠️ Failed to save session tracking report: {e}")

def create_isolated_browser_instance():
    """Create a completely isolated browser instance for lesson processing"""
    import time
    
    print("🔄 Creating isolated browser instance...")
    start_time = time.time()
    
    try:
        # Create new driver with enhanced isolation options
        driver = setup_driver()
        
        # Additional isolation measures
        driver.execute_script("window.localStorage.clear();")
        driver.execute_script("window.sessionStorage.clear();")
        driver.delete_all_cookies()
        
        # Clear any cached data
        driver.execute_script("""
            if ('caches' in window) {
                caches.keys().then(function(names) {
                    for (let name of names) caches.delete(name);
                });
            }
        """)
        
        BROWSER_ISOLATION['browser_instances_created'] += 1
        BROWSER_ISOLATION['current_browser_instance'] = driver
        BROWSER_ISOLATION['isolation_mode'] = 'isolated'
        BROWSER_ISOLATION['isolation_stats']['browser_creation_time'] += (time.time() - start_time)
        
        print(f"✅ Isolated browser instance created (total: {BROWSER_ISOLATION['browser_instances_created']})")
        return driver
        
    except Exception as e:
        print(f"❌ Failed to create isolated browser: {e}")
        return None

def destroy_browser_instance(driver, reason="normal_cleanup"):
    """Safely destroy a browser instance with cleanup"""
    import time
    
    if not driver:
        return
    
    print(f"🗑️ Destroying browser instance ({reason})...")
    start_time = time.time()
    
    try:
        # Clear all data before closing
        try:
            driver.execute_script("window.localStorage.clear();")
            driver.execute_script("window.sessionStorage.clear();")
            driver.delete_all_cookies()
        except:
            pass  # Ignore cleanup errors
        
        # Close browser
        driver.quit()
        
        BROWSER_ISOLATION['browser_instances_destroyed'] += 1
        BROWSER_ISOLATION['current_browser_instance'] = None
        BROWSER_ISOLATION['isolation_stats']['browser_destruction_time'] += (time.time() - start_time)
        
        print(f"✅ Browser instance destroyed (total: {BROWSER_ISOLATION['browser_instances_destroyed']})")
        
    except Exception as e:
        print(f"⚠️ Error destroying browser: {e}")

def process_lesson_with_isolated_browser(lesson_title, lesson_url, lesson_id, email, password, download_videos=False, output_dirs=None, community_display_name=None, community_slug=None):
    """Process a single lesson with complete browser isolation"""
    
    print(f"🔒 PROCESSING LESSON WITH ISOLATED BROWSER: {lesson_title}")
    
    # Create isolated browser instance
    driver = create_isolated_browser_instance()
    if not driver:
        print(f"❌ Failed to create isolated browser for: {lesson_title}")
        return False
    
    try:
        # Login to Skool in isolated browser
        print(f"🔐 Logging in to Skool (isolated browser)...")
        if not login_to_skool(driver, email, password):
            print("❌ Login failed in isolated browser")
            return False
        
        print(f"✅ Login successful in isolated browser!")
        
        # Navigate to lesson
        print(f"🌐 Navigating to lesson (isolated browser)...")
        driver.get(lesson_url)
        time.sleep(3)  # Wait for page to load
        
        # Set lesson context for validation
        set_lesson_context(lesson_title, lesson_url, lesson_id)
        
        # Generate lesson content signature for validation
        generate_lesson_content_signature(driver, lesson_title)
        
        # Extract video with complete isolation
        print(f"🎥 Extracting video (isolated browser)...")
        video_data = extract_video_url(driver, lesson_title)
        
        # Extract content
        print(f"📝 Extracting content (isolated browser)...")
        content = extract_lesson_content(driver)
        
        # Download images
        images_downloaded = download_images_from_lesson(driver, lesson_title, output_dirs['images']) if output_dirs else []
        
        # Download video if requested
        video_downloaded = False
        if video_data and download_videos and output_dirs:
            video_output_dir = os.path.join(output_dirs['lessons'], sanitize_filename(lesson_title), "videos")
            video_downloaded = download_video_universal(video_data, lesson_title, video_output_dir)
        
        # Save lesson content
        if output_dirs:
            success = save_lesson_content(
                lesson_title, 
                video_data, 
                content, 
                images_downloaded,
                output_dirs,
                video_downloaded,
                community_display_name,
                community_slug
            )
            
            if success:
                SESSION_STATS['lessons_processed'] += 1
                BROWSER_ISOLATION['isolation_stats']['lessons_with_isolated_browsers'] += 1
                print(f"✅ Successfully processed lesson with isolated browser: {lesson_title}")
                return True
            else:
                print(f"❌ Failed to save lesson: {lesson_title}")
                return False
        else:
            # Just return the extracted data
            BROWSER_ISOLATION['isolation_stats']['lessons_with_isolated_browsers'] += 1
            print(f"✅ Successfully extracted lesson data with isolated browser: {lesson_title}")
            return {
                'video_data': video_data,
                'content': content,
                'images_downloaded': images_downloaded
            }
            
    except Exception as e:
        print(f"❌ Error processing lesson with isolated browser: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Always destroy the isolated browser instance
        destroy_browser_instance(driver, "lesson_complete")

def should_use_browser_isolation(lesson_title, lesson_index, total_lessons):
    """Determine if browser isolation should be used for this lesson"""
    
    # Use isolation for first few lessons (most likely to have cached state)
    if lesson_index <= 3:
        print(f"🔒 Using isolation for early lesson ({lesson_index}/{total_lessons}): {lesson_title}")
        return True
    
    # Use isolation for every 5th lesson to prevent state buildup
    if lesson_index % 5 == 0:
        print(f"🔒 Using isolation for periodic cleanup lesson ({lesson_index}/{total_lessons}): {lesson_title}")
        return True
    
    # Always use isolation for lessons that previously had duplicate issues
    problematic_lessons = [
        'introduction', 'welcome', 'overview', 'getting started',
        'basics', 'fundamentals'
    ]
    
    lesson_lower = lesson_title.lower()
    for problematic in problematic_lessons:
        # Use word boundary matching to avoid false positives
        if problematic in lesson_lower:
            # Check if it's a standalone word or at the beginning/end
            if (problematic == lesson_lower or 
                lesson_lower.startswith(problematic + ' ') or 
                lesson_lower.endswith(' ' + problematic) or
                ' ' + problematic + ' ' in lesson_lower):
                print(f"🔒 Using isolation for potentially problematic lesson: {lesson_title}")
                return True
    
    # Use isolation if we've processed many lessons with shared browser
    if BROWSER_ISOLATION['isolation_stats']['lessons_with_shared_browser'] >= 10:
        print(f"🔒 Using isolation after {BROWSER_ISOLATION['isolation_stats']['lessons_with_shared_browser']} shared lessons: {lesson_title}")
        return True
    
    return False

def print_browser_isolation_statistics():
    """Print comprehensive browser isolation statistics"""
    print("\n🔒 === BROWSER ISOLATION STATISTICS ===")
    print(f"🌐 Browser Instances Created: {BROWSER_ISOLATION['browser_instances_created']}")
    print(f"🗑️ Browser Instances Destroyed: {BROWSER_ISOLATION['browser_instances_destroyed']}")
    print(f"🔒 Lessons with Isolated Browsers: {BROWSER_ISOLATION['isolation_stats']['lessons_with_isolated_browsers']}")
    print(f"🔗 Lessons with Shared Browser: {BROWSER_ISOLATION['isolation_stats']['lessons_with_shared_browser']}")
    
    total_lessons = (BROWSER_ISOLATION['isolation_stats']['lessons_with_isolated_browsers'] + 
                    BROWSER_ISOLATION['isolation_stats']['lessons_with_shared_browser'])
    
    if total_lessons > 0:
        isolation_percentage = (BROWSER_ISOLATION['isolation_stats']['lessons_with_isolated_browsers'] / total_lessons) * 100
        print(f"📊 Isolation Usage: {isolation_percentage:.1f}% of lessons")
    
    if BROWSER_ISOLATION['isolation_stats']['browser_creation_time'] > 0:
        print(f"⏱️ Total Browser Creation Time: {BROWSER_ISOLATION['isolation_stats']['browser_creation_time']:.2f}s")
    
    if BROWSER_ISOLATION['isolation_stats']['browser_destruction_time'] > 0:
        print(f"⏱️ Total Browser Destruction Time: {BROWSER_ISOLATION['isolation_stats']['browser_destruction_time']:.2f}s")
    
    print("=" * 40)

def set_lesson_context(lesson_title, lesson_url=None, lesson_id=None):
    """Set the current lesson context for validation"""
    global LESSON_CONTEXT
    
    LESSON_CONTEXT['current_lesson_title'] = lesson_title
    LESSON_CONTEXT['current_lesson_url'] = lesson_url
    LESSON_CONTEXT['current_lesson_id'] = lesson_id
    
    print(f"📚 LESSON CONTEXT SET: {lesson_title}")
    if lesson_url:
        print(f"   🔗 URL: {lesson_url}")
    if lesson_id:
        print(f"   🆔 ID: {lesson_id}")

def generate_lesson_content_signature(driver, lesson_title):
    """Generate a unique signature for the current lesson's content"""
    try:
        import hashlib
        
        # Get page content that should be unique to this lesson
        page_title = driver.title
        current_url = driver.current_url
        
        # Try to get lesson-specific content
        lesson_content = ""
        
        # Look for lesson title in page
        try:
            lesson_elements = driver.find_elements(By.CSS_SELECTOR, 
                'h1, h2, h3, [class*="lesson"], [class*="title"], [class*="heading"]')
            for element in lesson_elements:
                text = element.text.strip()
                if text and len(text) > 5:  # Meaningful text
                    lesson_content += text + " "
        except:
            pass
        
        # Get main content area
        try:
            main_content = driver.find_elements(By.CSS_SELECTOR, 
                'main, [class*="content"], [class*="lesson"], article')
            for element in main_content:
                text = element.text.strip()
                if text and len(text) > 20:  # Substantial content
                    lesson_content += text[:200] + " "  # First 200 chars
        except:
            pass
        
        # Create signature from lesson title, URL, and content
        signature_data = f"{lesson_title}|{current_url}|{lesson_content[:500]}"
        signature = hashlib.md5(signature_data.encode('utf-8')).hexdigest()
        
        # Store in lesson context
        LESSON_CONTEXT['lesson_content_hashes'][lesson_title] = {
            'signature': signature,
            'url': current_url,
            'content_preview': lesson_content[:100] + "..." if len(lesson_content) > 100 else lesson_content,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        print(f"🔐 Generated lesson signature: {signature[:8]}... for '{lesson_title}'")
        return signature
        
    except Exception as e:
        print(f"⚠️ Failed to generate lesson signature: {e}")
        return None

def validate_video_belongs_to_lesson(video_url, lesson_title, driver=None):
    """Validate that a video actually belongs to the current lesson"""
    if not video_url or not lesson_title:
        return False
    
    # Check if we have cached validation result
    cache_key = f"{video_url}|{lesson_title}"
    if cache_key in LESSON_CONTEXT['lesson_validation_cache']:
        cached_result = LESSON_CONTEXT['lesson_validation_cache'][cache_key]
        print(f"🔍 Using cached lesson validation result: {cached_result['valid']}")
        return cached_result['valid']
    
    print(f"🔍 VALIDATING VIDEO BELONGS TO LESSON: {lesson_title}")
    print(f"   🎥 Video: {video_url}")
    
    validation_result = {
        'valid': False,
        'reason': 'unknown',
        'confidence': 0.0
    }
    
    try:
        # Method 1: Check if video URL contains lesson-specific identifiers
        lesson_identifiers = _extract_lesson_identifiers(lesson_title)
        url_lower = video_url.lower()
        
        for identifier in lesson_identifiers:
            if identifier.lower() in url_lower:
                validation_result['valid'] = True
                validation_result['reason'] = 'url_contains_lesson_identifier'
                validation_result['confidence'] = 0.8
                print(f"✅ URL contains lesson identifier: {identifier}")
                break
        
        # Method 2: Check if we're on the correct lesson page
        if driver and LESSON_CONTEXT['current_lesson_url']:
            current_url = driver.current_url
            if current_url == LESSON_CONTEXT['current_lesson_url']:
                validation_result['valid'] = True
                validation_result['reason'] = 'correct_lesson_page'
                validation_result['confidence'] = 0.9
                print(f"✅ On correct lesson page: {current_url}")
        
        # Method 3: Check page content for lesson relevance
        if driver and validation_result['confidence'] < 0.8:
            page_relevance = _check_page_content_relevance(driver, lesson_title, video_url)
            if page_relevance > 0.7:
                validation_result['valid'] = True
                validation_result['reason'] = 'page_content_relevant'
                validation_result['confidence'] = page_relevance
                print(f"✅ Page content relevant to lesson (confidence: {page_relevance:.2f})")
        
        # Method 4: Check if video was found in lesson-specific containers
        if validation_result['confidence'] < 0.6:
            container_relevance = _check_video_container_relevance(driver, lesson_title)
            if container_relevance > 0.6:
                validation_result['valid'] = True
                validation_result['reason'] = 'lesson_specific_container'
                validation_result['confidence'] = container_relevance
                print(f"✅ Video found in lesson-specific container (confidence: {container_relevance:.2f})")
        
        # Cache the result
        LESSON_CONTEXT['lesson_validation_cache'][cache_key] = validation_result
        
        if validation_result['valid']:
            print(f"✅ LESSON VALIDATION PASSED: {validation_result['reason']} (confidence: {validation_result['confidence']:.2f})")
        else:
            print(f"🚫 LESSON VALIDATION FAILED: {validation_result['reason']} (confidence: {validation_result['confidence']:.2f})")
        
        return validation_result['valid']
        
    except Exception as e:
        print(f"⚠️ Lesson validation error: {e}")
        validation_result['valid'] = False
        validation_result['reason'] = 'validation_error'
        validation_result['confidence'] = 0.0
        
        # Cache the error result
        LESSON_CONTEXT['lesson_validation_cache'][cache_key] = validation_result
        return False

def _extract_lesson_identifiers(lesson_title):
    """Extract potential identifiers from lesson title for URL matching"""
    identifiers = []
    
    # Add the full lesson title
    identifiers.append(lesson_title)
    
    # Extract key words (remove common words)
    common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
    
    words = lesson_title.lower().split()
    key_words = [word for word in words if word not in common_words and len(word) > 2]
    
    # Add key word combinations
    for i in range(len(key_words)):
        identifiers.append(key_words[i])
        if i < len(key_words) - 1:
            identifiers.append(f"{key_words[i]}-{key_words[i+1]}")
    
    # Add lesson number if present
    import re
    lesson_number_match = re.search(r'(\d+)', lesson_title)
    if lesson_number_match:
        identifiers.append(lesson_number_match.group(1))
    
    return identifiers

def _check_page_content_relevance(driver, lesson_title, video_url):
    """Check if page content is relevant to the lesson and video"""
    try:
        # Get page content
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        lesson_lower = lesson_title.lower()
        
        # Check for lesson title in page content
        title_present = lesson_lower in page_text
        if title_present:
            print(f"✅ Lesson title found in page content")
        
        # Check for video-related content near lesson title
        video_keywords = ['video', 'watch', 'play', 'lesson', 'tutorial', 'demo']
        video_context_present = any(keyword in page_text for keyword in video_keywords)
        
        # Calculate relevance score
        relevance_score = 0.0
        if title_present:
            relevance_score += 0.4
        if video_context_present:
            relevance_score += 0.3
        
        # Check if video URL appears in page content
        if video_url in page_text:
            relevance_score += 0.3
            print(f"✅ Video URL found in page content")
        
        return min(relevance_score, 1.0)
        
    except Exception as e:
        print(f"⚠️ Error checking page content relevance: {e}")
        return 0.0

def _check_video_container_relevance(driver, lesson_title):
    """Check if video was found in lesson-specific containers"""
    try:
        # Look for lesson-specific containers
        lesson_containers = driver.find_elements(By.CSS_SELECTOR, 
            '[class*="lesson"], [class*="content"], [class*="video"], [class*="player"]')
        
        if lesson_containers:
            print(f"✅ Found {len(lesson_containers)} lesson-specific containers")
            return 0.7  # Good confidence if lesson containers exist
        
        return 0.3  # Low confidence if no lesson containers found
        
    except Exception as e:
        print(f"⚠️ Error checking container relevance: {e}")
        return 0.0

def log_video_extraction_attempt(method_name, lesson_title, video_url, result_status, additional_info=None):
    """Enhanced logging for video extraction attempts with detailed tracking"""
    import datetime
    
    log_entry = {
        'timestamp': datetime.datetime.now().isoformat(),
        'method': method_name,
        'lesson_title': lesson_title or 'Unknown Lesson',
        'video_url': video_url,
        'status': result_status,  # 'found', 'blocked', 'failed', 'none'
        'additional_info': additional_info or {}
    }
    
    VIDEO_EXTRACTION_DEBUG_LOG.append(log_entry)
    
    # Enhanced console output with color coding
    status_symbol = {
        'found': '✅',
        'blocked': '🚫', 
        'failed': '❌',
        'none': '⚪'
    }.get(result_status, '❓')
    
    print(f"{status_symbol} [{method_name}] {lesson_title}: {result_status.upper()} - {video_url or 'No URL'}")
    if additional_info:
        for key, value in additional_info.items():
            print(f"    ├─ {key}: {value}")

def save_extraction_debug_log():
    """Save the complete extraction debug log to file for analysis"""
    try:
        import json
        with open('debug_video_extraction_log.json', 'w', encoding='utf-8') as f:
            json.dump(VIDEO_EXTRACTION_DEBUG_LOG, f, indent=2, ensure_ascii=False)
        print(f"📄 Saved video extraction debug log with {len(VIDEO_EXTRACTION_DEBUG_LOG)} entries")
    except Exception as e:
        print(f"⚠️ Failed to save debug log: {e}")

def analyze_duplicate_patterns():
    """Analyze the debug log for duplicate video patterns"""
    if not VIDEO_EXTRACTION_DEBUG_LOG:
        return
    
    print("\n🔍 === DUPLICATE PATTERN ANALYSIS ===")
    
    # Group by video URL
    from collections import defaultdict
    url_occurrences = defaultdict(list)
    
    for entry in VIDEO_EXTRACTION_DEBUG_LOG:
        if entry['video_url'] and entry['status'] == 'found':
            url_occurrences[entry['video_url']].append(entry)
    
    duplicates_found = False
    for url, entries in url_occurrences.items():
        if len(entries) > 1:
            duplicates_found = True
            print(f"\n🚨 DUPLICATE DETECTED: {url}")
            print(f"   📊 Found in {len(entries)} lessons:")
            for entry in entries:
                print(f"      └─ [{entry['method']}] {entry['lesson_title']} at {entry['timestamp']}")
            
            # Identify which methods found this duplicate
            methods = [entry['method'] for entry in entries]
            print(f"   🔧 Methods involved: {', '.join(set(methods))}")
    
    if not duplicates_found:
        print("✅ No duplicate videos found in this session!")
    
    print("=" * 50)

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

def create_hierarchical_lesson_directories(community_display_name, community_slug, lesson_hierarchy_path):
    """Create hierarchical directory structure for lessons based on Skool's structure"""
    
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
    
    # Create the base community path
    community_path = os.path.join("Communities", safe_folder_name)
    
    # Create hierarchical lesson path if provided
    if lesson_hierarchy_path:
        # Clean up the hierarchy path components
        path_components = lesson_hierarchy_path.split('/')
        clean_components = []
        for component in path_components:
            if component.strip():
                # Sanitize each path component
                clean_component = re.sub(r'[<>:"/\\|?*]', '_', component.strip())
                clean_component = re.sub(r'\s+', ' ', clean_component).strip()
                clean_components.append(clean_component)
        
        # Build the hierarchical lesson path
        lesson_path = os.path.join(community_path, *clean_components) if clean_components else os.path.join(community_path, "lessons")
    else:
        # Fallback to flat structure
        lesson_path = os.path.join(community_path, "lessons")
    
    dirs = {
        'community': community_path,
        'lessons': lesson_path,
        'images': os.path.join(community_path, "images"),
        'videos': os.path.join(community_path, "videos")
    }
    
    # Create all directories
    for dir_path in dirs.values():
        os.makedirs(dir_path, exist_ok=True)
    
    return dirs

def create_hierarchical_directories(community, section="classroom", base_dir="extracted_content"):
    """Create new hierarchical directory structure for any community"""
    
    # Create the hierarchical structure
    dirs = {
        'community': os.path.join(base_dir, "communities", community),
        'section': os.path.join(base_dir, "communities", community, section),
        'lessons': os.path.join(base_dir, "communities", community, section, "lessons"),
        'images': os.path.join(base_dir, "communities", community, section, "images"),
        'videos': os.path.join(base_dir, "communities", community, section, "videos"),
        'logs': os.path.join(base_dir, "communities", community, section, "logs")
    }
    
    for dir_path in dirs.values():
        os.makedirs(dir_path, exist_ok=True)
    
    return dirs

def get_already_extracted_lessons(lessons_dir):
    """Get list of already extracted lesson titles to skip duplicates"""
    extracted_lessons = set()
    if os.path.exists(lessons_dir):
        for filename in os.listdir(lessons_dir):
            if filename.endswith('.md'):
                # Convert filename back to lesson title format
                lesson_title = filename.replace('.md', '').replace('_', ' ')
                # Handle special characters that were cleaned
                extracted_lessons.add(clean_title_for_comparison(lesson_title))
    
    print(f"📋 Found {len(extracted_lessons)} already extracted lessons")
    if extracted_lessons:
        print("📄 Already extracted:")
        for lesson in list(extracted_lessons)[:5]:  # Show first 5
            print(f"  - {lesson}")
        if len(extracted_lessons) > 5:
            print(f"  ... and {len(extracted_lessons) - 5} more")
    
    return extracted_lessons

def clean_title_for_comparison(title):
    """Clean title for comparison with existing files"""
    # Remove special characters and convert to lowercase for comparison
    cleaned = re.sub(r'[^\w\s]', '', title.lower())
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def sanitize_filename(filename):
    """Enhanced sanitize filename for safe file system usage with emoji and special character support."""
    # Remove or replace emojis and special characters
    filename = re.sub(r'[^\w\s-]', '', filename)  # Remove non-alphanumeric except spaces and hyphens
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)  # Replace Windows forbidden chars
    filename = re.sub(r'\s+', ' ', filename).strip()  # Normalize spaces
    filename = filename.replace('!', '').replace('$', 'USD')  # Handle specific chars
    # Limit length to avoid path issues
    if len(filename) > 100:
        filename = filename[:100].strip()
    return filename

def setup_driver():
    """Setup Chrome WebDriver with optimal settings"""
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    # Enable performance logging to sniff media requests when needed
    try:
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    except Exception:
        pass
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.maximize_window()
    
    return driver

def clear_browser_storage_bulk(driver):
    """Clear cookies, localStorage, and sessionStorage to avoid state contamination between lessons."""
    try:
        try:
            driver.delete_all_cookies()
            print("🧹 Cleared cookies")
        except Exception as ce:
            print(f"⚠️ Could not clear cookies: {ce}")
        try:
            driver.execute_script("window.localStorage.clear();")
            driver.execute_script("window.sessionStorage.clear();")
            print("🧹 Cleared localStorage and sessionStorage")
        except Exception as se:
            print(f"⚠️ Could not clear storage: {se}")
    except Exception as e:
        print(f"⚠️ State isolation error: {e}")

def login_to_skool(driver, email, password):
    """Enhanced login function with multiple fallbacks"""
    try:
        print("🔐 Navigating to Skool login page...")
        driver.get("https://www.skool.com/login")
        
        wait = WebDriverWait(driver, 15)
        
        # Wait for and find email field with multiple selectors
        email_selectors = [
            "input[type='email']",
            "input[name='email']", 
            "#email",
            "input[placeholder*='email' i]",
            "input[placeholder*='Email' i]"
        ]
        
        email_field = None
        for selector in email_selectors:
            try:
                email_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                print(f"✅ Found email field with selector: {selector}")
                break
            except TimeoutException:
                continue
        
        if not email_field:
            print("❌ Could not find email field")
            return False
        
        # Enter email
        email_field.clear()
        email_field.send_keys(email)
        time.sleep(1)
        
        # Find password field
        password_selectors = [
            "input[type='password']",
            "input[name='password']",
            "#password"
        ]
        
        password_field = None
        for selector in password_selectors:
            try:
                password_field = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except NoSuchElementException:
                continue
        
        if not password_field:
            print("❌ Could not find password field")
            return False
        
        # Enter password
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(1)
        
        # Find and click login button
        login_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:contains('Log')",
            "button:contains('Sign')",
            ".login-button",
            "[data-testid*='login']"
        ]
        
        login_button = None
        for selector in login_selectors:
            try:
                login_button = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except NoSuchElementException:
                continue
        
        if not login_button:
            print("❌ Could not find login button")
            return False
        
        print("🔑 Clicking login button...")
        login_button.click()
        
        # Wait for successful login
        time.sleep(5)
        
        # Check if login was successful
        current_url = driver.current_url
        if "login" not in current_url.lower():
            print("✅ Login successful!")
            return True
        else:
            print(f"❌ Login failed. Current URL: {current_url}")
            return False
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return False

def extract_all_lesson_data(driver):
    """
    Extract all lesson data from page source to avoid stale element issues.
    Returns list of (lesson_name, md_value) tuples.
    """
    print("🔍 Extracting all lesson data from page source...")
    
    # Get page source
    page_source = driver.page_source
    
    lesson_data = []
    
    # Method 1: Extract lesson titles using the exact selectors we know work
    title_pattern = r'<div[^>]*title="([^"]+)"[^>]*class="[^"]*styled__MenuItemTitle-sc-1wvgzj7-8[^"]*jKdEiu[^"]*"[^>]*>'
    titles = re.findall(title_pattern, page_source)
    
    print(f"📋 Found {len(titles)} potential lesson titles in HTML")
    for title in titles[:10]:  # Show first 10
        print(f"  - {title}")
    
    # Method 2: Look for md values in URLs within the page source
    md_pattern = r'md=([a-f0-9]{32})'
    md_values = re.findall(md_pattern, page_source)
    unique_md_values = list(set(md_values))
    
    print(f"🔑 Found {len(unique_md_values)} unique md values in page source")
    
    # Method 3: Extract from JavaScript/JSON data that might contain lesson mappings
    # Look for patterns like: {"title":"Lesson Name","id":"...","md":"..."}
    js_patterns = [
        r'"title":\s*"([^"]+)"[^}]*?"[^"]*md[^"]*":\s*"([a-f0-9]{32})"',
        r'"md":\s*"([a-f0-9]{32})"[^}]*?"title":\s*"([^"]+)"',
        r'md=([a-f0-9]{32})[^>]*>([^<]+)<',
        r'href="[^"]*md=([a-f0-9]{32})[^"]*"[^>]*>([^<]+)<',
        r'data-[^=]*=["\'"][^"\']*md=([a-f0-9]{32})[^"\']*["\'"][^>]*>([^<]+)<'
    ]
    
    for i, pattern in enumerate(js_patterns):
        try:
            matches = re.findall(pattern, page_source, re.IGNORECASE)
            if matches:
                print(f"📊 Pattern {i+1} found {len(matches)} lesson data matches")
                for match in matches[:3]:  # Show first 3
                    print(f"  - {match}")
                
                # Add to lesson_data based on pattern structure
                if 'title.*md' in pattern:
                    lesson_data.extend([(title, md) for title, md in matches])
                elif 'md.*title' in pattern:
                    lesson_data.extend([(title, md) for md, title in matches])
                else:
                    lesson_data.extend([(title.strip(), md) for md, title in matches])
        except Exception as e:
            print(f"❌ Pattern {i+1} failed: {e}")
    
    # Method 4: Use Selenium to get lesson elements WITHOUT clicking (safer)
    try:
        print("🎯 Using Selenium to extract lesson data safely...")
        
        # Wait for sidebar to load
        wait = WebDriverWait(driver, 10)
        
        # First expand any collapsed months
        expand_all_months(driver)
        time.sleep(2)
        
        # Find all lesson elements
        lesson_elements = driver.find_elements(By.CSS_SELECTOR, 'div[title][class*="styled__MenuItemTitle-sc-1wvgzj7-8"][class*="jKdEiu"]')
        print(f"✅ Found {len(lesson_elements)} total lesson elements")
        
        lesson_titles = []
        for element in lesson_elements:
            try:
                title = element.get_attribute("title")
                if title and title.strip():
                    lesson_titles.append(title.strip())
            except Exception:
                continue
        
        print(f"🎯 Extracted {len(lesson_titles)} valid lesson titles")
        
        # Try to map titles to md values through strategic clicks
        print("🔄 Attempting to map titles to md values for ALL found lessons...")
        
        for title in lesson_titles:  # REMOVED LIMIT: was lesson_titles[:40]
            try:
                # Find lesson element by title
                lesson_element = driver.find_element(By.CSS_SELECTOR, f'div[title="{title}"]')
                
                # Click the lesson
                driver.execute_script("arguments[0].click();", lesson_element)
                time.sleep(1)
                
                # Get current URL and extract md value
                current_url = driver.current_url
                if 'md=' in current_url:
                    current_md = current_url.split('md=')[1].split('&')[0]
                    # Avoid adding duplicates
                    if not any(d[1] == current_md for d in lesson_data):
                        lesson_data.append((title, current_md))
                        print(f"✅ {title} -> md={current_md[:8]}...")
                    
                time.sleep(0.5)  # Small delay between clicks
                
            except Exception as e:
                print(f"⚠️ Could not get md for {title}: {str(e)}")
                continue
        
        # This strategic click section is now redundant due to the exhaustive loop above,
        # but can be kept as a final fallback if needed. Let's simplify and make it exhaustive too.
        print("🔄 Running final fallback check for any missed lessons...")
        for element in lesson_elements: # REMOVED LIMIT: was lesson_elements[:20]
            try:
                title = element.get_attribute("title")
                # Check if we already have this lesson by title or md from its URL
                has_title = any(d[0] == title for d in lesson_data)
                
                if title and not has_title:
                    # Try clicking this element
                    driver.execute_script("arguments[0].click();", element)
                    time.sleep(1)
                    
                    # Extract md value from URL
                    new_url = driver.current_url
                    if 'md=' in new_url:
                        md_value = new_url.split('md=')[1].split('&')[0]
                        if not any(d[1] == md_value for d in lesson_data):
                             lesson_data.append((title, md_value))
                             print(f"✅ Fallback success: {title} -> md={md_value[:8]}...")
                        
            except Exception:
                continue
        
        # Get base URL for constructing direct URLs
        current_url = driver.current_url
        base_url = current_url.split('?')[0] + '?md='
        
        # Try to click strategically to get more md values
        strategic_lesson_attempts = 0
        for element in lesson_elements[:20]:  # Try first 20 elements directly
            if strategic_lesson_attempts >= 10:  # Limit attempts
                break
                
            try:
                title = element.get_attribute("title")
                if title and not any(title == existing_title for existing_title, _ in lesson_data):
                    # Try clicking this element
                    driver.execute_script("arguments[0].click();", element)
                    time.sleep(1)
                    
                    # Extract md value from URL
                    new_url = driver.current_url
                    if 'md=' in new_url:
                        md_value = new_url.split('md=')[1].split('&')[0]
                        lesson_data.append((title, md_value))
                        print(f"✅ {title} -> md={md_value[:8]}...")
                        strategic_lesson_attempts += 1
                        
            except Exception:
                continue
        
        # Add fallback lesson data for known important lessons (if not already captured)
        fallback_lessons = [
            ("Claude 4", "98026e3d41fb4924be4e5f79c9f04378"),
            ("NEW Google i/O AI Updates!", "c99d5b99d3a74859aa6c9755d0dbdcf0"),
            ("N8N Appointment Setter 2.0", "0a2653968eca4638988a547892cf0864"),
            ("N8N + Slack", "1f32ebb52170470cae47d7fd9f62464e"),
            ("Qwen Web Dev + 1 Click Deployment", "c019342f35aa43fa8a55317a3893c81e"),
            ("NEW Browser Use AI Agent: Build & Automate", "92579d26c269a411c1a2e53e8b8bc5e4"),
            ("Building AI Agents in n8n With Claude", "49593d49d742489a8b96e4e42b471cfc"),
            ("New Claude MCP Update is INSANE (FREE)", "ffa201842d0a48e79ecd3d2f29b09930"),
            ("N8N: Outbound Calls Agent", "b951a93612f54446938b00c27ee5902c"),
            ("NEW N8N Scraper Agent! 🤯", "d7cd548e590f42228fbc8c4e55b6c809"),
            ("N8N + OpenAI gpt-image-1 API AI Automation 🤯", "7d84e6827dc54d438f1e5466a28c80af"),
            ("OpenAI gpt-image-1 API: Build AI Image Apps 🤯", "dfaa0691cb6342dcb3c7c9d2883b5a"),
            ("Trae AI: This FREE AI Coding Agent is INSANE 🤯", "23ceb14b52624e13a9ec3d05982c3c6d"),
            ("Suna: NEW Super AI DESTROYS Manus & Genspark? 🤯", "5770cef9877d44068aee76f5f11f80ec")
        ]
        
        print("🔧 Adding fallback lesson data...")
        existing_titles = {title for title, _ in lesson_data}
        for title, md_value in fallback_lessons:
            if title not in existing_titles:
                lesson_data.append((title, md_value))
                print(f"🔧 Added fallback: {title}")
        
    except Exception as e:
        print(f"❌ Error in Selenium extraction: {str(e)}")
    
    # Remove duplicates and return
    seen = set()
    unique_lesson_data = []
    for title, md in lesson_data:
        if (title, md) not in seen:
            seen.add((title, md))
            unique_lesson_data.append((title, md))
    
    print(f"🎉 Final lesson data: {len(unique_lesson_data)} unique lessons")
    for title, md in unique_lesson_data[:40]:  # Show first 40
        print(f"  ✅ {title} -> md={md[:8]}...")
    
    return unique_lesson_data

def expand_all_months(driver):
    """Expand all month sections to reveal all lessons by scrolling and clicking."""
    try:
        print("📂 Expanding all month sections to ensure all lessons are visible...")
        
        # Scroll the sidebar to bring all elements into view
        sidebar_xpath = "//*[contains(@class, 'styled__Sidebar') or contains(@class, 'sidebar') or contains(@class, 'Navigation')]"
        try:
            sidebar = driver.find_element(By.XPATH, sidebar_xpath)
            # Scroll down multiple times to be sure
            for _ in range(5):
                driver.execute_script("arguments[0].scrollTop += 500;", sidebar)
                time.sleep(0.5)
            print("📜 Scrolled sidebar to reveal all sections.")
        except Exception as e:
            print(f"⚠️ Could not find and scroll sidebar, proceeding without it. Error: {e}")

        # More robust selectors for expandable sections
        month_selectors = [
            'div[class*="ubFmc"]', # This seems to be a key selector for month headers
            'div[class*="month"]',
            'div[class*="section-header"]',
            'button[class*="expand"]',
            'div[class*="collapsible-header"]',
            'div[role="button"][aria-expanded="false"]' # Specifically target collapsed sections
        ]
        
        all_found_elements = []
        for selector in month_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    all_found_elements.extend(elements)
                    print(f"📅 Found {len(elements)} potential month sections with selector: '{selector}'")
            except Exception:
                continue
        
        if not all_found_elements:
            print("⚠️ No expandable month sections found. Assuming all lessons are visible.")
            return

        print(f"🖱️ Clicking on {len(all_found_elements)} potential sections to expand them...")
        for element in all_found_elements:
            try:
                # Use JavaScript click which is more reliable for overlapping elements
                driver.execute_script("arguments[0].click();", element)
                print(f"  -> Clicked on element with text: '{element.text[:30]}...'")
                time.sleep(0.2) # Small delay to allow UI to update
            except Exception as e:
                # It's okay if some clicks fail, as selectors might overlap
                print(f"  -> Note: Could not click an element, might be a stale reference. {e}")
                continue
        
        print("✅ Finished attempting to expand all sections.")
        
    except Exception as e:
        print(f"❌ A critical error occurred while expanding month sections: {str(e)}")

def extract_course_hierarchy(driver):
    """Extract the complete course hierarchy from __NEXT_DATA__ JSON"""
    try:
        print("🏗️ Extracting course hierarchy from __NEXT_DATA__...")
        script_tag = driver.find_element(By.ID, "__NEXT_DATA__")
        data = json.loads(script_tag.get_attribute("innerHTML"))
        
        # Navigate to course data
        page_props = data.get("props", {}).get("pageProps", {})
        course_data = page_props.get("course")
        
        if not course_data:
            print("⚠️ No course data found in JSON")
            return {}
        
        hierarchy = {}
        
        def process_course_item(item, parent_path=""):
            """Recursively process course items to build hierarchy"""
            course = item.get("course", {})
            unit_type = course.get("unitType")
            title = course.get("metadata", {}).get("title", "Untitled")
            course_id = course.get("id")
            
            if unit_type == "set":
                # This is a section/sub-section
                current_path = f"{parent_path}/{title}" if parent_path else title
                hierarchy[course_id] = {
                    "title": title,
                    "type": "section",
                    "path": current_path,
                    "parent_path": parent_path,
                    "children": []
                }
                
                # Process children
                children = item.get("children", [])
                for child in children:
                    process_course_item(child, current_path)
                    
            elif unit_type == "module":
                # This is an individual lesson
                hierarchy[course_id] = {
                    "title": title,
                    "type": "lesson",
                    "path": parent_path,
                    "parent_path": parent_path,
                    "metadata": course.get("metadata", {})
                }
        
        # Process the main course structure
        children = course_data.get("children", [])
        for child in children:
            process_course_item(child)
        
        print(f"✅ Extracted hierarchy for {len(hierarchy)} items")
        
        # Debug: Save hierarchy for analysis
        with open("debug_hierarchy.json", "w", encoding="utf-8") as f:
            json.dump(hierarchy, f, indent=2)
        print("💾 Saved hierarchy data to debug_hierarchy.json")
        
        return hierarchy
        
    except Exception as e:
        print(f"❌ Error extracting course hierarchy: {e}")
        return {}

def find_lesson_hierarchy_path(lesson_title, hierarchy):
    """Find the hierarchical path for a specific lesson title"""
    for item_id, item_data in hierarchy.items():
        if (item_data.get("type") == "lesson" and 
            item_data.get("title") == lesson_title):
            return item_data.get("path", "")
    return ""

def is_valid_lesson_video(video_url):
    """Centralized validation to prevent cached/duplicate videos from being returned"""
    print(f"🔍 VALIDATION CHECK: Testing URL: {video_url}")
    
    if not video_url:
        print("🚫 VALIDATION FAILED: Empty URL")
        return False
    
    # Global blacklist of known problematic cached video IDs
    CACHED_VIDEO_BLACKLIST = [
        "YTrIwmIdaJI",  # Generic header URL
        "UDcrRdfB0x8",  # Problematic cached video 1
        "7snrj0uEaDw",  # Problematic cached video 2
        "65GvYDdzJWU",  # Persistent duplicate video (re-enabled)
        # Add more as they're discovered
    ]
    
    print(f"🔍 VALIDATION: Blacklist contains: {CACHED_VIDEO_BLACKLIST}")
    
    # Extract video ID from various URL formats
    import re

    # We'll search the original URL first, but also create a stripped variant (without query/fragment)
    stripped_url = video_url.split('?')[0].split('#')[0]
    print(f"🔍 VALIDATION: Original URL: {video_url}")
    print(f"🔍 VALIDATION: Stripped URL: {stripped_url}")

    video_id_patterns = [
        # YouTube variants (standard, embed, nocookie)
        r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'youtube\-nocookie\.com/(?:embed/)?([a-zA-Z0-9_-]{11})',
        # Vimeo
        r'vimeo\.com/(\d+)',
        # Loom
        r'loom\.com/share/([a-zA-Z0-9_-]+)',
        # Wistia
        r'wistia\.com/medias/([a-zA-Z0-9_-]+)'
    ]

    for i, pattern in enumerate(video_id_patterns):
        print(f"🔍 VALIDATION: Testing pattern {i+1}: {pattern}")
        # Try matching against the full URL first; if not found, match against the stripped version
        match = re.search(pattern, video_url) or re.search(pattern, stripped_url)
        if match:
            video_id = match.group(1)
            print(f"🔍 VALIDATION: Found video ID: {video_id}")
            if video_id in CACHED_VIDEO_BLACKLIST:
                print(f"🚫 BLOCKED cached video: {video_id} from URL: {video_url}")
                return False
            else:
                print(f"✅ VALIDATION: Video ID {video_id} is NOT in blacklist - ALLOWING")
                return True
    
    print(f"⚠️ VALIDATION: No video ID extracted from URL: {video_url} - ALLOWING by default")
    return True

def _extract_video_id_generic(video_url):
    """Extract a comparable video identifier for deduplication across platforms."""
    if not video_url:
        return None
    try:
        import re
        # YouTube
        m = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})', video_url)
        if m:
            return f"yt:{m.group(1)}"
        # Vimeo
        m = re.search(r'vimeo\.com/(\d+)', video_url)
        if m:
            return f"vimeo:{m.group(1)}"
        # Loom
        m = re.search(r'loom\.com/(?:share/|embed/)?([a-zA-Z0-9]+)', video_url)
        if m:
            return f"loom:{m.group(1)}"
        # Wistia (basic)
        m = re.search(r'wistia\.com/(?:medias/)?([a-zA-Z0-9_-]+)', video_url)
        if m:
            return f"wistia:{m.group(1)}"
        # Direct files: use path
        from urllib.parse import urlparse
        parsed = urlparse(video_url)
        if parsed.path:
            return f"file:{parsed.path.lower()}"
        return video_url.lower()
    except Exception:
        return video_url.lower()

def detect_platform(video_url):
    """Detect video platform from URL"""
    if not video_url:
        return 'unknown'
    
    url_lower = video_url.lower()
    
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

        # Handle oEmbed wrapper: https://www.youtube.com/oembed?format=json&url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DID
        if 'youtube.com/oembed' in video_url:
            try:
                parsed = urlparse(video_url)
                q = parse_qs(parsed.query)
                wrapped = q.get('url', [None])[0]
                if wrapped:
                    wrapped = unquote(wrapped)
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
        # Normalize Wistia URL to canonical fast.wistia.net embed
        import re
        m = re.search(r'(?:wistia\.com/medias/|fast\.wistia\.net/embed/iframe/)([a-zA-Z0-9_-]+)', video_url)
        if m:
            video_id = m.group(1)
            clean_url = f"https://fast.wistia.net/embed/iframe/{video_id}"
            print(f"🧹 Cleaned Wistia URL: {video_url[:60]}... → {clean_url}")
            return clean_url
    
    # Return original URL if no cleaning rules apply
    return video_url

def sanitize_filename_for_video(filename):
    """Sanitize filename for video downloads"""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'\s+', '_', filename)
    return filename.strip()[:100]  # Limit length

def download_youtube_video(video_url, lesson_title, output_dir):
    """Download YouTube video using yt-dlp with enhanced progress and error handling"""
    try:
        print(f"📥 Downloading YouTube video: {lesson_title}")
        print(f"🔗 URL: {video_url}")
        safe_title = sanitize_filename_for_video(lesson_title)
        output_path = os.path.join(output_dir, f"{safe_title}.%(ext)s")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        print("⏳ Starting download... (this may take a few minutes)")
        
        # Enhanced yt-dlp command with progress and better quality options
        process = subprocess.run([
            "yt-dlp",
            video_url,
            "--format", "best[height<=1080][ext=mp4]/best[ext=mp4]/best",
            "--merge-output-format", "mp4",
            "-o", output_path,
            "--no-overwrites",
            "--ignore-errors",
            "--progress",
            "--no-warnings"
        ], check=False, capture_output=True, text=True, encoding='utf-8')
        
        if process.returncode == 0:
            print(f"✅ YouTube video downloaded successfully: {safe_title}")
            # Check if file actually exists
            expected_files = [f for f in os.listdir(output_dir) if safe_title in f]
            if expected_files:
                print(f"📁 Saved as: {expected_files[0]}")
                return True
            else:
                print("⚠️ Download reported success but file not found")
                return False
        else:
            print(f"❌ YouTube download failed")
            if process.stderr:
                print(f"Error details: {process.stderr[:200]}...")
            return False
            
    except FileNotFoundError:
        print("❌ yt-dlp not found. Please install: pip install yt-dlp")
        print("💡 Install with: pip install yt-dlp")
        return False
    except Exception as e:
        print(f"❌ YouTube download error: {e}")
        return False

def download_vimeo_video(video_url, lesson_title, output_dir):
    """Download Vimeo video using yt-dlp with enhanced progress and error handling"""
    try:
        print(f"📥 Downloading Vimeo video: {lesson_title}")
        print(f"🔗 URL: {video_url}")
        safe_title = sanitize_filename_for_video(lesson_title)
        output_path = os.path.join(output_dir, f"{safe_title}.%(ext)s")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        print("⏳ Starting Vimeo download... (this may take a few minutes)")
        
        process = subprocess.run([
            "yt-dlp",
            video_url,
            "--format", "best[height<=1080][ext=mp4]/best[ext=mp4]/best",
            "--merge-output-format", "mp4",
            "-o", output_path,
            "--no-overwrites",
            "--ignore-errors",
            "--progress",
            "--no-warnings"
        ], check=False, capture_output=True, text=True, encoding='utf-8')
        
        if process.returncode == 0:
            print(f"✅ Vimeo video downloaded successfully: {safe_title}")
            # Verify file exists
            expected_files = [f for f in os.listdir(output_dir) if safe_title in f]
            if expected_files:
                print(f"📁 Saved as: {expected_files[0]}")
                return True
            else:
                print("⚠️ Download reported success but file not found")
                return False
        else:
            print(f"❌ Vimeo download failed")
            if process.stderr:
                print(f"Error details: {process.stderr[:200]}...")
            return False
            
    except FileNotFoundError:
        print("❌ yt-dlp not found. Please install: pip install yt-dlp")
        print("💡 Install with: pip install yt-dlp")
        return False
    except Exception as e:
        print(f"❌ Vimeo download error: {e}")
        return False

def download_loom_video(video_url, lesson_title, output_dir):
    """Download Loom video using yt-dlp with enhanced progress and error handling"""
    try:
        print(f"📥 Downloading Loom video: {lesson_title}")
        print(f"🔗 URL: {video_url}")
        safe_title = sanitize_filename_for_video(lesson_title)
        output_path = os.path.join(output_dir, f"{safe_title}.%(ext)s")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        print("⏳ Starting Loom download... (this may take a few minutes)")
        
        process = subprocess.run([
            "yt-dlp",
            video_url,
            "--format", "best[height<=1080][ext=mp4]/best[ext=mp4]/best",
            "--merge-output-format", "mp4",
            "-o", output_path,
            "--no-overwrites",
            "--ignore-errors",
            "--progress",
            "--no-warnings"
        ], check=False, capture_output=True, text=True, encoding='utf-8')
        
        if process.returncode == 0:
            print(f"✅ Loom video downloaded successfully: {safe_title}")
            # Verify file exists
            expected_files = [f for f in os.listdir(output_dir) if safe_title in f]
            if expected_files:
                print(f"📁 Saved as: {expected_files[0]}")
                return True
            else:
                print("⚠️ Download reported success but file not found")
                return False
        else:
            print(f"❌ Loom download failed")
            if process.stderr:
                print(f"Error details: {process.stderr[:200]}...")
            return False
            
    except FileNotFoundError:
        print("❌ yt-dlp not found. Please install: pip install yt-dlp")
        print("💡 Install with: pip install yt-dlp")
        return False
    except Exception as e:
        print(f"❌ Loom download error: {e}")
        return False

def download_direct_video(video_url, lesson_title, output_dir):
    """Download direct video file using urllib with enhanced error handling"""
    try:
        print(f"📥 Downloading direct video: {lesson_title}")
        print(f"🔗 URL: {video_url}")
        safe_title = sanitize_filename_for_video(lesson_title)
        
        # Extract file extension from URL
        parsed_url = urlparse(video_url)
        file_ext = os.path.splitext(parsed_url.path)[1] or '.mp4'
        
        output_path = os.path.join(output_dir, f"{safe_title}{file_ext}")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        print("⏳ Starting direct download...")
        
        # Download the file with progress indication
        def progress_hook(block_num, block_size, total_size):
            if total_size > 0:
                percent = min(100, (block_num * block_size * 100) // total_size)
                if percent % 10 == 0:  # Show progress every 10%
                    print(f"📊 Download progress: {percent}%")
        
        urllib.request.urlretrieve(video_url, output_path, progress_hook)
        
        # Verify file was downloaded and has content
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
            print(f"✅ Direct video downloaded successfully: {safe_title}")
            print(f"📁 Saved as: {os.path.basename(output_path)} ({file_size:.1f} MB)")
            return True
        else:
            print("❌ Download failed - file is empty or doesn't exist")
            return False
        
    except Exception as e:
        print(f"❌ Direct video download error: {e}")
        return False

def download_video_universal(video_data, lesson_title, output_dir="videos"):
    """Download video from any supported platform - Phase 3 Enhanced with retry logic"""
    if not video_data:
        print("⚠️ No video data provided for download")
        return False
    
    platform = video_data.get('platform', 'unknown')
    video_url = video_data.get('url', '')
    duration = video_data.get('duration')
    
    if not video_url:
        print("⚠️ No video URL found")
        return False
    
    # Display video information
    print(f"\n🎬 Video Download Information:")
    print(f"📱 Platform: {platform.title()}")
    print(f"🔗 URL: {video_url}")
    if duration:
        minutes = duration // 60000
        seconds = (duration % 60000) // 1000
        print(f"⏱️ Duration: {minutes}:{seconds:02d}")
    
    # Retry mechanism
    max_retries = 2
    for attempt in range(max_retries):
        if attempt > 0:
            print(f"\n🔄 Retry attempt {attempt + 1}/{max_retries}")
            time.sleep(2)  # Wait before retry
        
        try:
            if platform == 'youtube':
                result = download_youtube_video(video_url, lesson_title, output_dir)
            elif platform == 'vimeo':
                result = download_vimeo_video(video_url, lesson_title, output_dir)
            elif platform == 'loom':
                result = download_loom_video(video_url, lesson_title, output_dir)
            elif platform == 'direct':
                result = download_direct_video(video_url, lesson_title, output_dir)
            else:
                print(f"⚠️ Unsupported platform for download: {platform}")
                print(f"📝 Video URL will be saved in lesson content: {video_url}")
                return False
            
            if result:
                print(f"🎉 Video download completed successfully!")
                return True
            elif attempt < max_retries - 1:
                print(f"⚠️ Download failed, will retry...")
            
        except Exception as e:
            print(f"❌ Download attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print("🔄 Will retry...")
    
    print(f"❌ All download attempts failed for {platform} video")
    print(f"📝 Video URL will be saved in lesson content: {video_url}")
    return False

def extract_from_next_data(driver):
    """Extract video URL from Skool's __NEXT_DATA__ JSON - Enhanced with multiple paths"""
    try:
        print("🔍 Looking for video in __NEXT_DATA__ JSON...")
        script_tag = driver.find_element(By.ID, "__NEXT_DATA__")
        data = json.loads(script_tag.get_attribute("innerHTML"))
        
        # Debug: Save the JSON data to see structure
        with open("debug_lesson_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print("💾 Saved lesson JSON data to debug_lesson_data.json for analysis")
        
        # Navigate to lesson data
        page_props = data.get("props", {}).get("pageProps", {})
        lesson = page_props.get("lesson")
        if lesson:
            print("🔍 Found lesson data, checking multiple video paths...")
            
            # Method 1: Check lesson.video.video_url (original method)
            video_data = lesson.get("video", {})
            video_url = video_data.get("video_url")
            if video_url:
                platform = detect_platform(video_url)
                result = {
                    'url': video_url,
                    'platform': platform,
                    'thumbnail': video_data.get("original_thumbnail_url"),
                    'duration': video_data.get("video_length_ms")
                }
                print(f"✅ Found {platform} video in lesson.video: {video_url}")
                # VALIDATION CHECK: Must validate before returning
                if is_valid_lesson_video(video_url):
                    print(f"✅ JSON VIDEO VALIDATED: {video_url}")
                    return result
                else:
                    print(f"🚫 JSON VIDEO BLOCKED: {video_url}")
            
            # Method 2: Check lesson.metadata.videoLink (alternative path)
            metadata = lesson.get("metadata", {})
            video_link = metadata.get("videoLink")
            if video_link:
                platform = detect_platform(video_link)
                result = {
                    'url': video_link,
                    'platform': platform,
                    'thumbnail': metadata.get("thumbnail"),
                    'duration': metadata.get("duration")
                }
                print(f"✅ Found {platform} video in lesson.metadata: {video_link}")
                # VALIDATION CHECK: Must validate before returning
                if is_valid_lesson_video(video_link):
                    print(f"✅ METADATA VIDEO VALIDATED: {video_link}")
                    return result
                else:
                    print(f"🚫 METADATA VIDEO BLOCKED: {video_link}")
            
            # Method 3: Search for any URL-like patterns in lesson data (recursive)
            def find_video_urls_in_object(obj, path=""):
                video_urls = []
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        current_path = f"{path}.{key}" if path else key
                        if isinstance(value, str) and any(domain in value.lower() for domain in ['youtube.com', 'youtu.be', 'vimeo.com', 'loom.com', '.mp4', '.webm', 'wistia']):
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
                        result = {
                            'url': url,
                            'platform': platform,
                            'thumbnail': None,
                            'duration': None
                        }
                        print(f"✅ Found {platform} video in {path}: {url}")
                        # VALIDATION CHECK: Must validate before returning
                        if is_valid_lesson_video(url):
                            print(f"✅ RECURSIVE VIDEO VALIDATED: {url}")
                            return result
                        else:
                            print(f"🚫 RECURSIVE VIDEO BLOCKED: {url}")
            
            # NEW: Scan JSON strings for Skool links carrying ?wvideo= and convert to Wistia
            def _find_wvideo_in_obj(obj):
                try:
                    from urllib.parse import urlparse, parse_qs
                except Exception:
                    return None
                import re as _re
                if isinstance(obj, dict):
                    for v in obj.values():
                        r = _find_wvideo_in_obj(v)
                        if r:
                            return r
                elif isinstance(obj, list):
                    for v in obj:
                        r = _find_wvideo_in_obj(v)
                        if r:
                            return r
                elif isinstance(obj, str):
                    s = obj
                    if 'wvideo=' in s and 'skool.com' in s:
                        try:
                            q = parse_qs(urlparse(s).query)
                            wid = q.get('wvideo', [None])[0]
                            if wid and _re.fullmatch(r'[A-Za-z0-9]+', wid):
                                wistia_url = f"https://fast.wistia.net/embed/iframe/{wid}"
                                cleaned = clean_video_url(wistia_url, 'wistia')
                                return {
                                    'url': cleaned,
                                    'platform': 'wistia',
                                    'thumbnail': None,
                                    'duration': None
                                }
                        except Exception:
                            pass
                return None

            wv = _find_wvideo_in_obj(lesson)
            if wv:
                print(f"✅ Found Wistia via wvideo in JSON: {wv['url']}")
                return wv

            print("⚠️ No video URLs found in lesson JSON data")
            print(f"🔍 Lesson keys available: {list(lesson.keys())}")
        else:
            print("⚠️ No lesson data found in __NEXT_DATA__")
            # Some Skool pages expose video data under pageProps.course.children[...].course.metadata.videoLink
            try:
                selected_module_id = page_props.get("selectedModule") or page_props.get("selectedLesson")
                course_tree = page_props.get("course", {})
                children = course_tree.get("children", []) or []

                def extract_from_child_course(child_course_obj):
                    metadata = (child_course_obj or {}).get("metadata", {})
                    # Direct known fields
                    for key in ["videoLink", "video_url", "videoUrl"]:
                        val = metadata.get(key)
                        if isinstance(val, str) and val.strip():
                            return val
                    
                    # NEW: Check for videoId fields (Skool internal video IDs)
                    video_id = metadata.get("videoId")
                    if isinstance(video_id, str) and video_id.strip():
                        print(f"🔍 Found Skool videoId: {video_id}")
                        # These are internal Skool video IDs, not direct URLs
                        # We need to trigger the modal to get the actual video URL
                        return f"skool-video-id:{video_id}"
                    # Heuristic search inside metadata
                    def find_urls(obj):
                        found = []
                        if isinstance(obj, dict):
                            for _k, _v in obj.items():
                                found.extend(find_urls(_v))
                        elif isinstance(obj, list):
                            for _v in obj:
                                found.extend(find_urls(_v))
                        elif isinstance(obj, str):
                            s = obj.lower()
                            if any(d in s for d in ["youtube.com", "youtu.be", "vimeo.com", "loom.com", "wistia", ".mp4", ".webm"]):
                                found.append(obj)
                        return found
                    urls = find_urls(metadata)
                    return urls[0] if urls else None

                # 1) Prefer the currently selected module
                if selected_module_id and children:
                    for child in children:
                        child_course = (child or {}).get("course") or {}
                        if child_course.get("id") == selected_module_id:
                            candidate_url = extract_from_child_course(child_course)
                            if candidate_url:
                                platform = detect_platform(candidate_url)
                                cleaned = clean_video_url(candidate_url, platform)
                                result = {
                                    'url': cleaned or candidate_url,
                                    'platform': platform,
                                    'thumbnail': (child_course.get("metadata", {}) or {}).get("videoThumbnail"),
                                    'duration': (child_course.get("metadata", {}) or {}).get("videoLenMs") or (child_course.get("metadata", {}) or {}).get("video_length_ms")
                                }
                                print(f"✅ Found {platform} video in selected module metadata: {result['url']}")
                                # VALIDATION CHECK: Must validate before returning
                                if is_valid_lesson_video(result['url']):
                                    print(f"✅ SELECTED MODULE VIDEO VALIDATED: {result['url']}")
                                    return result
                                else:
                                    print(f"🚫 SELECTED MODULE VIDEO BLOCKED: {result['url']}")

                # 2) Fallback: scan all children for the first valid external video link
                for child in children:
                    child_course = (child or {}).get("course") or {}
                    candidate_url = extract_from_child_course(child_course)
                    if candidate_url:
                        platform = detect_platform(candidate_url)
                        cleaned = clean_video_url(candidate_url, platform)
                        result = {
                            'url': cleaned or candidate_url,
                            'platform': platform,
                            'thumbnail': (child_course.get("metadata", {}) or {}).get("videoThumbnail"),
                            'duration': (child_course.get("metadata", {}) or {}).get("videoLenMs") or (child_course.get("metadata", {}) or {}).get("video_length_ms")
                        }
                        print(f"✅ Found {platform} video in module metadata: {result['url']}")
                        # VALIDATION CHECK: Must validate before returning
                        if is_valid_lesson_video(result['url']):
                            print(f"✅ MODULE VIDEO VALIDATED: {result['url']}")
                            return result
                        else:
                            print(f"🚫 MODULE VIDEO BLOCKED: {result['url']}")
            except Exception as e2:
                print(f"⚠️ Course-based JSON extraction failed: {e2}")
            
    except Exception as e:
        print(f"⚠️ JSON extraction failed: {e}")
    
    return None

def scan_video_iframes_filtered(driver):
    """Scan for video iframes with lesson-specific filtering to avoid cached/header videos"""
    try:
        print("🔍 Scanning for lesson-specific video iframes...")
        
        # Focus on lesson content areas only, avoid navigation/header
        content_containers = [
            "[class*='lesson']",
            "[class*='content']", 
            "[class*='post']",
            "[class*='module']",
            "main",
            "article",
            "[role='main']"
        ]
        
        # Try to find video iframes within lesson content containers
        for container_selector in content_containers:
            try:
                containers = driver.find_elements(By.CSS_SELECTOR, container_selector)
                for container in containers:
                    # Look for video iframes within this container
                    iframe_selectors = [
                        "iframe[src*='youtube.com']",
                        "iframe[src*='youtu.be']", 
                        "iframe[src*='vimeo.com']",
                        "iframe[src*='loom.com']",
                        "iframe[src*='wistia.com']"
                    ]
                    
                    for iframe_selector in iframe_selectors:
                        try:
                            iframes = container.find_elements(By.CSS_SELECTOR, iframe_selector)
                            for iframe in iframes:
                                src = iframe.get_attribute("src")
                                if src:
                                    # Skip if this iframe is in navigation/header areas
                                    iframe_location = iframe.location
                                    if iframe_location['y'] < 200:  # Skip elements too high up (likely header)
                                        print(f"🚫 Skipping header iframe: {src[:50]}...")
                                        continue
                                    
                                    # Skip known problematic cached videos
                                    skip_video_ids = ["YTrIwmIdaJI", "UDcrRdfB0x8", "7snrj0uEaDw"]
                                    import re
                                    youtube_match = re.search(r'(?:youtube\.com/embed/|youtu\.be/)([a-zA-Z0-9_-]{11})', src)
                                    if youtube_match:
                                        video_id = youtube_match.group(1)
                                        if video_id in skip_video_ids:
                                            print(f"⚠️ Skipping known cached video: {video_id}")
                                            continue
                                    
                                    platform = detect_platform(src)
                                    if platform != 'unknown':
                                        clean_url = clean_video_url(src, platform)
                                        result = {
                                            'url': clean_url,
                                            'platform': platform,
                                            'thumbnail': None,
                                            'duration': None,
                                            'source': 'filtered_iframe'
                                        }
                                        print(f"✅ Found {platform} video in lesson content: {clean_url}")
                                        # VALIDATION CHECK: Must validate before returning
                                        if is_valid_lesson_video(clean_url):
                                            print(f"✅ IFRAME VIDEO VALIDATED: {clean_url}")
                                            return result
                                        else:
                                            print(f"🚫 IFRAME VIDEO BLOCKED: {clean_url}")
                        except Exception:
                            continue
            except Exception:
                continue
                
    except Exception as e:
        print(f"⚠️ Filtered iframe scanning failed: {e}")
    
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
        
        # Check traditional iframes first
        for selector in iframe_selectors:
            try:
                iframe = driver.find_element(By.CSS_SELECTOR, selector)
                src = iframe.get_attribute("src")
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
                        # VALIDATION CHECK: Must validate before returning
                        if is_valid_lesson_video(clean_url):
                            print(f"✅ IFRAME SCAN VIDEO VALIDATED: {clean_url}")
                            return result
                        else:
                            print(f"🚫 IFRAME SCAN VIDEO BLOCKED: {clean_url}")
            except Exception:
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
                    # Check various attributes that might contain video URLs
                    attributes_to_check = ['src', 'data-src', 'data-video-url', 'data-url', 'href']
                    for attr in attributes_to_check:
                        url = element.get_attribute(attr)
                        if url and any(domain in url.lower() for domain in ['youtube.com', 'youtu.be', 'vimeo.com', 'loom.com', '.mp4', '.webm']):
                            platform = detect_platform(url)
                            if platform != 'unknown':
                                result = {
                                    'url': url,
                                    'platform': platform,
                                    'thumbnail': None,
                                    'duration': None
                                }
                                print(f"✅ Found {platform} video in {selector} [{attr}]: {url}")
                                # VALIDATION CHECK: Must validate before returning
                                if is_valid_lesson_video(url):
                                    print(f"✅ ELEMENT VIDEO VALIDATED: {url}")
                                    return result
                                else:
                                    print(f"🚫 ELEMENT VIDEO BLOCKED: {url}")
            except Exception:
                continue
                
    except Exception as e:
        print(f"⚠️ Iframe scanning failed: {e}")
    
    return None

def debug_page_state_after_click_bulk(driver):
    """Debug what happens after clicking video thumbnail - bulk scraper version"""
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

def click_video_thumbnail_safely_bulk(driver):
    """
    Enhanced safe video thumbnail clicking for bulk scraper
    """
    try:
        print("🎯 Looking for video thumbnail to click safely...")
        
        # Store current URL to detect unwanted navigation
        original_url = driver.current_url
        print(f"📍 Original URL: {original_url}")
        
        # Target video thumbnail selectors
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
                        duration_text = thumbnail.text
                        class_name = thumbnail.get_attribute('class') or ''
                        
                        # Check if this looks like a video container
                        is_video_container = (
                            any(time_pattern in duration_text for time_pattern in [':', '0:', '1:', '2:', '3:', '4:', '5:']) or
                            'VideoThumbnail' in class_name or
                            'video' in class_name.lower() or
                            'justify-content: center' in thumbnail.get_attribute('style') or ''
                        )
                        
                        if is_video_container:
                            print(f"✅ Found potential video thumbnail - attempting click")
                            
                            # Click the thumbnail
                            driver.execute_script("arguments[0].click();", thumbnail)
                            print("⏳ Clicked video thumbnail, waiting for player...")
                            
                            # Check if we stayed on the same page OR redirected to lesson page
                            current_url = driver.current_url
                            if original_url in current_url or current_url in original_url:
                                print("✅ Stayed on the same page after clicking thumbnail")
                                video_thumbnail_clicked = True
                                break
                            elif any(keyword in current_url for keyword in ["lesson", "day-", "video", "watch"]) or len(current_url) > len(original_url):
                                print(f"✅ Redirected to lesson-specific page: {current_url}")
                                print("🎯 This might be where the video is located - continuing with detection...")
                                video_thumbnail_clicked = True
                                break
                            else:
                                print(f"⚠️ Page changed unexpectedly: {current_url}")
                                driver.get(original_url)
                                time.sleep(2)
                        
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
        
        # Try multiple wait times for different loading speeds
        for wait_attempt, wait_time in enumerate([2, 3, 5], 1):  # Shorter waits for bulk processing
            print(f"🔄 Detection attempt {wait_attempt}: waiting {wait_time}s for iframe to load...")
            time.sleep(wait_time)
            
            # Debug current page state (less verbose for bulk processing)
            if wait_attempt == 1:  # Only debug on first attempt to avoid spam
                debug_page_state_after_click_bulk(driver)
            
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

            # Enhanced video detection
            all_video_selectors = [
                'iframe[src*="youtube"]',
                'iframe[src*="vimeo"]', 
                'iframe[src*="loom"]',
                'iframe[src*="wistia"]',
                'iframe',  # Any iframe
                'video',   # HTML5 video tags
                'embed',   # Embed tags
                '[class*="VideoPlayer"]',
                '[class*="ReactPlayer"]',
                '[data-video-url]',
                '[data-src*="youtube"]',
                '[data-src*="vimeo"]',
                '[data-src*="loom"]'
            ]
            
            for selector in all_video_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        # Check multiple attributes for video URLs
                        for attr in ['src', 'data-src', 'data-video-url', 'data-url', 'href']:
                            url = element.get_attribute(attr)
                            if url and any(domain in url.lower() for domain in ['youtube', 'vimeo', 'loom', 'wistia', 'embed']):
                                platform = detect_platform(url)
                                if platform != 'unknown':
                                    clean_url = clean_video_url(url, platform)
                                    print(f"✅ Found {platform} video after {wait_time}s wait: {clean_url}")
                                    return {
                                        'url': clean_url,
                                        'platform': platform,
                                        'source': 'safe_thumbnail_click_bulk',
                                        'thumbnail': None,
                                        'duration': None,
                                        'wait_time': wait_time
                                    }
                except Exception as e:
                    continue
            
            # Check JSON after click
            try:
                script_tag = driver.find_element(By.ID, "__NEXT_DATA__")
                updated_data = json.loads(script_tag.get_attribute("innerHTML"))
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
                            'source': 'json_after_click_bulk',
                            'thumbnail': video_data.get("original_thumbnail_url"),
                            'duration': video_data.get("video_length_ms"),
                            'wait_time': wait_time
                        }
            except Exception:
                pass

        # After attempts, run additional Wistia checks for bulk pages
        try:
            from urllib.parse import urlparse, parse_qs
            import re as _re
            # Anchors anywhere on page containing ?wvideo=
            anchors = driver.find_elements(By.CSS_SELECTOR, 'a[href*="wvideo="]')
            for a in anchors:
                href = a.get_attribute('href') or ''
                if 'wvideo=' in href:
                    q = parse_qs(urlparse(href).query)
                    wid = q.get('wvideo', [None])[0]
                    if wid and _re.fullmatch(r'[A-Za-z0-9]+', wid):
                        wistia_url = f"https://fast.wistia.net/embed/iframe/{wid}"
                        print(f"✅ Found Wistia via wvideo (bulk): {wistia_url}")
                        return {
                            'url': wistia_url,
                            'platform': 'wistia',
                            'source': 'wvideo_anchor_global_bulk'
                        }
            # Class-based embeds
            wels = driver.find_elements(By.CSS_SELECTOR, 'div[class*="wistia_embed"], div[class*="wistia_async_"]')
            for wel in wels:
                cls = wel.get_attribute('class') or ''
                m = _re.search(r'wistia_async_([A-Za-z0-9]+)', cls)
                if m:
                    wid = m.group(1)
                    wistia_url = f"https://fast.wistia.net/embed/iframe/{wid}"
                    print(f"✅ Found Wistia via class (bulk): {wistia_url}")
                    return {
                        'url': wistia_url,
                        'platform': 'wistia',
                        'source': 'wistia_class_global_bulk'
                    }
        except Exception:
            pass
        
        print("⚠️ No video iframe found after enhanced detection attempts")
        return None
        
    except Exception as e:
        print(f"❌ Error in enhanced video thumbnail click: {str(e)}")
    return None

def extract_video_two_step_click(driver):
    """
    Enhanced two-step click workflow with better video detection
    """
    try:
        print("🎯 Step 1: Looking for lesson/post container to click...")
        
        # Try different selectors for lesson containers
        container_selectors = [
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
                    print(f"🎯 Found container with selector: {selector}")
                    # Click the first container
                    driver.execute_script("arguments[0].click();", containers[0])
                    time.sleep(2)  # Wait for content to load
                    container_clicked = True
                    break
            except Exception as e:
                continue
        
        if not container_clicked:
            print("⚠️ No lesson container found to click")
            return None
        
        print("🎯 Step 2: Looking for video play button after container click...")
        
        # Look for play buttons with enhanced selectors
        play_button_selectors = [
            '.styled__VideoThumbnailWrapper-sc-1k73vxa-2',  # Exact video container class
            '[class*="VideoThumbnailWrapper"]',
            'div[class*="VideoThumbnail"]',
            'div[style*="justify-content: center"]',
            'button[aria-label*="play"]',
            'button[title*="play"]', 
            '[class*="play"]',
            '[class*="Play"]',
            'svg path[fill="#FFFFFF"]',  # White play button triangle
            'button svg',
            '[role="button"] svg',
            '.video-play-button',
            '[data-testid*="play"]'
        ]
        
        play_button_clicked = False
        for selector in play_button_selectors:
            try:
                buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                for button in buttons:
                    # Check if this looks like a play button or video container
                    button_text = button.get_attribute('textContent') or ''
                    aria_label = button.get_attribute('aria-label') or ''
                    title = button.get_attribute('title') or ''
                    class_name = button.get_attribute('class') or ''
                    
                    is_video_element = (
                        any(keyword in text.lower() for text in [button_text, aria_label, title] 
                            for keyword in ['play', 'video', 'watch']) or
                        'VideoThumbnail' in class_name or
                        'video' in class_name.lower()
                    )
                    
                    if is_video_element:
                        print(f"🎯 Found video element with selector: {selector}")
                        driver.execute_script("arguments[0].click();", button)
                        time.sleep(3)  # Wait for video to load
                        play_button_clicked = True
                        break
                        
                if play_button_clicked:
                    break
            except Exception as e:
                continue
        
        if play_button_clicked:
            print("✅ Video element clicked, now looking for video iframe...")
        
        print("🎯 Step 3: Enhanced video detection after click...")
        
        # Enhanced video detection with progressive waiting
        for wait_time in [2, 4]:  # Two attempts for bulk processing
            time.sleep(wait_time)
            
            # Comprehensive video selectors
        video_selectors = [
            'iframe[src*="youtube"]',
            'iframe[src*="vimeo"]',
            'iframe[src*="loom"]',
            'iframe[src*="wistia"]',
                'iframe',  # Any iframe
            '[class*="VideoPlayer"]',
            '[class*="ReactPlayer"]',
            'video',
            '[data-video-url]',
            '[data-src*="youtube"]',
            '[data-src*="vimeo"]',
            '[data-src*="loom"]'
        ]
        
        for selector in video_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    # Try different attributes for video URL
                    for attr in ['src', 'data-src', 'data-video-url', 'data-url', 'href']:
                        url = element.get_attribute(attr)
                        if url and any(platform in url.lower() for platform in ['youtube', 'vimeo', 'loom', 'wistia']):
                            platform = detect_platform(url)
                            clean_url = clean_video_url(url, platform)
                            print(f"✅ Found {platform} video after enhanced two-step click: {clean_url}")
                            return {
                                'url': clean_url,
                                'platform': platform,
                                'source': 'enhanced_two_step_click',
                                'element_type': element.tag_name,
                                'selector_used': selector,
                                'wait_time': wait_time
                            }
            except Exception as e:
                continue
        
        print("⚠️ No video found after enhanced two-step click workflow")
        return None
        
    except Exception as e:
        print(f"❌ Error in enhanced two-step click workflow: {str(e)}")
        return None

def click_video_player_and_extract(driver):
    """Click video player elements to trigger video load and then extract URL"""
    try:
        import time
        
        # Look for video player elements that might need clicking
        player_selectors = [
            ".styled__PlaybackButton-sc-bpv3k2-5",  # Specific Skool play button
            "[class*='PlaybackButton']",
            "[class*='VideoPlayer']",
            "[class*='CoverImage']",
            "button[aria-label*='play']",
            "button[title*='play']",
            "[class*='play-button']",
            ".video-thumbnail",
            "[class*='video-thumbnail']"
        ]
        
        for selector in player_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    try:
                        # Check if element is visible and clickable
                        if element.is_displayed() and element.is_enabled():
                            print(f"🎯 Found video player element with selector: {selector}")
                            
                            # Click the element
                            driver.execute_script("arguments[0].click();", element)
                            print("▶️ Clicked video player element")
                            time.sleep(3)  # Wait for video to load
                            
                            # Now try to extract video URL after click
                            # Check for iframes that appeared after click
                            iframe_selectors = [
                                "iframe[src*='youtube']",
                                "iframe[src*='vimeo']",
                                "iframe[src*='loom']",
                                "iframe[src*='wistia']"
                            ]
                            
                            for iframe_selector in iframe_selectors:
                                try:
                                    iframes = driver.find_elements(By.CSS_SELECTOR, iframe_selector)
                                    for iframe in iframes:
                                        src = iframe.get_attribute("src")
                                        if src:
                                            platform = detect_platform(src)
                                            if platform != 'unknown':
                                                clean_url = clean_video_url(src, platform)
                                                result = {
                                                    'url': clean_url,
                                                    'platform': platform,
                                                    'thumbnail': None,
                                                    'duration': None,
                                                    'source': 'click_triggered'
                                                }
                                                print(f"✅ Found {platform} video after clicking: {clean_url}")
                                                # VALIDATION CHECK: Must validate before returning
                                                if is_valid_lesson_video(clean_url):
                                                    print(f"✅ CLICK VIDEO VALIDATED: {clean_url}")
                                                    return result
                                                else:
                                                    print(f"🚫 CLICK VIDEO BLOCKED: {clean_url}")
                                except Exception:
                                    continue
                            
                            # Also re-check JSON data after click
                            try:
                                script_tag = driver.find_element(By.ID, "__NEXT_DATA__")
                                updated_data = json.loads(script_tag.get_attribute("innerHTML"))
                                lesson = updated_data.get("props", {}).get("pageProps", {}).get("lesson")
                                if lesson:
                                    video_data = lesson.get("video", {})
                                    video_url = video_data.get("video_url")
                                    if video_url:
                                        platform = detect_platform(video_url)
                                        result = {
                                            'url': video_url,
                                            'platform': platform,
                                            'thumbnail': video_data.get("original_thumbnail_url"),
                                            'duration': video_data.get("video_length_ms"),
                                            'source': 'json_after_click'
                                        }
                                        print(f"✅ Found {platform} video in JSON after click: {video_url}")
                                        # VALIDATION CHECK: Must validate before returning
                                        if is_valid_lesson_video(video_url):
                                            print(f"✅ CLICK JSON VIDEO VALIDATED: {video_url}")
                                            return result
                                        else:
                                            print(f"🚫 CLICK JSON VIDEO BLOCKED: {video_url}")
                            except Exception:
                                pass
                                
                    except Exception as e:
                        print(f"⚠️ Error clicking element: {e}")
                        continue
            except Exception:
                continue
        
        print("⚠️ No clickable video player elements found")
        return None
        
    except Exception as e:
        print(f"❌ Error in click video player method: {str(e)}")
        return None

def detect_modal_video_player(driver, known_video_id=None):
    """Detect and extract video from modal/popup after clicking thumbnail"""
    try:
        print("🔍 MODAL METHOD: Detecting video in modal/popup...")
        if known_video_id:
            print(f"🎯 Looking for video with known ID: {known_video_id}")
        
        # Step 1: Look for video thumbnails with magnifying glass cursor
        thumbnail_selectors = [
            '.styled__VideoThumbnailWrapper-sc-1k73vxa-2',  # Exact class from HTML
            '[class*="VideoThumbnailWrapper"]',
            '[class*="VideoThumbnail"]',
            'div[style*="cursor: zoom-in"]',
            'div[style*="cursor: magnify"]',
            '[class*="video"][style*="cursor"]'
        ]
        
        clicked_thumbnail = False
        original_url = driver.current_url
        
        for selector in thumbnail_selectors:
            try:
                thumbnails = driver.find_elements(By.CSS_SELECTOR, selector)
                if thumbnails:
                    print(f"🎯 Found {len(thumbnails)} thumbnail(s) with selector: {selector}")
                    
                    for thumbnail in thumbnails:
                        try:
                            # Check if this has a duration indicator (confirms it's a video)
                            duration_text = thumbnail.text
                            if any(pattern in duration_text for pattern in [':', '0:', '1:', '2:', '3:', '4:', '5:', '6:', '7:', '8:', '9:']):
                                print(f"✅ Found video thumbnail with duration: {duration_text}")
                                
                                # Click the thumbnail to open modal
                                print("🖱️ Clicking video thumbnail to open modal...")
                                
                                # Store page state before click
                                pre_click_html_length = len(driver.page_source)
                                pre_click_url = driver.current_url
                                
                                # Try multiple click methods
                                click_methods = [
                                    lambda: driver.execute_script("arguments[0].click();", thumbnail),
                                    lambda: thumbnail.click(),
                                    lambda: driver.execute_script("arguments[0].dispatchEvent(new Event('click'));", thumbnail),
                                ]
                                
                                for i, click_method in enumerate(click_methods, 1):
                                    try:
                                        print(f"🖱️ Click attempt {i}/3...")
                                        click_method()
                                        time.sleep(3)  # Wait for changes
                                        
                                        # Check if anything changed
                                        post_click_html_length = len(driver.page_source)
                                        post_click_url = driver.current_url
                                        
                                        html_changed = abs(post_click_html_length - pre_click_html_length) > 1000
                                        url_changed = post_click_url != pre_click_url
                                        
                                        if html_changed or url_changed:
                                            print(f"✅ Click {i} triggered changes - HTML: {html_changed}, URL: {url_changed}")
                                            clicked_thumbnail = True
                                            break
                                        else:
                                            print(f"⚠️ Click {i} didn't trigger visible changes")
                                            
                                    except Exception as e:
                                        print(f"⚠️ Click method {i} failed: {e}")
                                        continue
                                
                                if clicked_thumbnail:
                                    break
                                else:
                                    print("❌ All click methods failed to trigger changes")
                                
                        except Exception as e:
                            print(f"⚠️ Error clicking thumbnail: {e}")
                            continue
                
                if clicked_thumbnail:
                    break
                    
            except Exception as e:
                print(f"⚠️ Error with selector {selector}: {e}")
                continue
        
        if not clicked_thumbnail:
            print("⚠️ No clickable video thumbnails found")
            return None
        
        # Step 2: Wait for and detect modal/popup
        print("🔍 Waiting for modal/popup to appear...")
        modal_selectors = [
            '[role="dialog"]',
            '[class*="modal"]', 
            '[class*="Modal"]',
            '[class*="popup"]',
            '[class*="Popup"]',
            '[class*="overlay"]',
            '[class*="Overlay"]',
            '[class*="lightbox"]',
            '[class*="Lightbox"]',
            '.ReactModal__Content',
            '[data-testid*="modal"]',
            '[data-testid*="popup"]',
            '[aria-modal="true"]',
            'div[style*="position: fixed"]',
            'div[style*="z-index"]'
        ]
        
        modal_found = False
        modal_element = None
        
        # Try multiple wait attempts for modal to appear with longer waits
        for attempt, wait_time in enumerate([3, 5, 8, 10], 1):
            print(f"🔄 Modal detection attempt {attempt}/4 (waiting {wait_time}s)...")
            time.sleep(wait_time)
            
            # Debug: Check what elements are currently visible
            try:
                page_title = driver.title
                current_url = driver.current_url
                print(f"🔍 Current page: {page_title[:50]}... at {current_url}")
                
                # Check if page changed (might indicate modal opened in new page)
                if current_url != original_url:
                    print(f"📍 Page navigation detected: {original_url} → {current_url}")
                
            except Exception:
                pass
            
            for modal_selector in modal_selectors:
                try:
                    modals = driver.find_elements(By.CSS_SELECTOR, modal_selector)
                    for modal in modals:
                        # Check if modal is visible and contains video-related content
                        if modal.is_displayed():
                            modal_html = modal.get_attribute('innerHTML').lower()
                            print(f"🔍 Checking modal content (length: {len(modal_html)} chars)")
                            if any(keyword in modal_html for keyword in ['video', 'iframe', 'youtube', 'vimeo', 'player', 'embed']):
                                print(f"✅ Found video modal with selector: {modal_selector}")
                                modal_element = modal
                                modal_found = True
                                break
                            else:
                                print(f"⚠️ Modal found but no video content detected")
                except Exception as e:
                    print(f"⚠️ Error checking modal {modal_selector}: {e}")
                    continue
                
                if modal_found:
                    break
            
            # Also check if the video loaded directly on the page (no modal)
            if not modal_found:
                print("🔍 No modal found, checking if video loaded directly on page...")
                try:
                    direct_iframes = driver.find_elements(By.CSS_SELECTOR, "iframe")
                    for iframe in direct_iframes:
                        src = iframe.get_attribute("src")
                        if src and any(domain in src.lower() for domain in ['youtube', 'vimeo', 'loom', 'wistia']):
                            print(f"✅ Found direct video iframe after click: {src}")
                            platform = detect_platform(src)
                            clean_url = clean_video_url(src, platform)
                            return {
                                'url': clean_url,
                                'platform': platform,
                                'source': 'direct_after_click',
                                'thumbnail': None,
                                'duration': None
                            }
                except Exception:
                    pass
            
            if modal_found:
                break
        
        if not modal_found:
            print("⚠️ No video modal detected after clicking")
            return None
        
        # Step 3: Extract video from modal
        print("🔍 Extracting video from modal content...")
        
        # Switch context to modal for extraction
        original_context = driver
        
        try:
            # Look for iframes within the modal
            modal_iframes = modal_element.find_elements(By.CSS_SELECTOR, "iframe")
            for iframe in modal_iframes:
                src = iframe.get_attribute("src")
                if src:
                    platform = detect_platform(src)
                    if platform != 'unknown':
                        clean_url = clean_video_url(src, platform)
                        print(f"✅ Found {platform} video in modal iframe: {clean_url}")
                        
                        # Close modal before returning
                        try:
                            close_buttons = modal_element.find_elements(By.CSS_SELECTOR, 
                                '[aria-label*="close"], [class*="close"], button[type="button"]')
                            if close_buttons:
                                close_buttons[0].click()
                                time.sleep(1)
                        except:
                            pass
                        
                        return {
                            'url': clean_url,
                            'platform': platform,
                            'source': 'modal_extraction',
                            'thumbnail': None,
                            'duration': None
                        }
            
            # Look for video elements within the modal
            modal_videos = modal_element.find_elements(By.CSS_SELECTOR, "video")
            for video in modal_videos:
                src = video.get_attribute("src")
                if src:
                    platform = detect_platform(src)
                    if platform != 'unknown':
                        clean_url = clean_video_url(src, platform)
                        print(f"✅ Found {platform} video element in modal: {clean_url}")
                        
                        # Close modal before returning
                        try:
                            close_buttons = modal_element.find_elements(By.CSS_SELECTOR, 
                                '[aria-label*="close"], [class*="close"], button[type="button"]')
                            if close_buttons:
                                close_buttons[0].click()
                                time.sleep(1)
                        except:
                            pass
                        
                        return {
                            'url': clean_url,
                            'platform': platform,
                            'source': 'modal_video_element',
                            'thumbnail': None,
                            'duration': None
                        }
            
            # Look for data attributes that might contain video URLs
            video_data_attrs = ['data-video-url', 'data-src', 'data-video-id', 'data-youtube-id']
            for attr in video_data_attrs:
                elements_with_attr = modal_element.find_elements(By.CSS_SELECTOR, f"[{attr}]")
                for element in elements_with_attr:
                    attr_value = element.get_attribute(attr)
                    if attr_value:
                        # If it's just an ID, construct the full URL
                        if attr == 'data-youtube-id':
                            video_url = f"https://www.youtube.com/watch?v={attr_value}"
                        else:
                            video_url = attr_value
                        
                        platform = detect_platform(video_url)
                        if platform != 'unknown':
                            clean_url = clean_video_url(video_url, platform)
                            print(f"✅ Found {platform} video from {attr}: {clean_url}")
                            
                            # Close modal before returning
                            try:
                                close_buttons = modal_element.find_elements(By.CSS_SELECTOR, 
                                    '[aria-label*="close"], [class*="close"], button[type="button"]')
                                if close_buttons:
                                    close_buttons[0].click()
                                    time.sleep(1)
                            except:
                                pass
                            
                            return {
                                'url': clean_url,
                                'platform': platform,
                                'source': f'modal_{attr}',
                                'thumbnail': None,
                                'duration': None
                            }
        
        except Exception as e:
            print(f"❌ Error extracting from modal: {e}")
        
        # Close modal if still open
        try:
            close_buttons = modal_element.find_elements(By.CSS_SELECTOR, 
                '[aria-label*="close"], [class*="close"], button[type="button"]')
            if close_buttons:
                close_buttons[0].click()
                time.sleep(1)
        except:
            # Try pressing Escape key as alternative
            try:
                from selenium.webdriver.common.keys import Keys
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                time.sleep(1)
            except:
                pass
        
        print("⚠️ No video found in modal")
        return None
        
    except Exception as e:
        print(f"❌ Modal video detection error: {e}")
        return None

def extract_video_url(driver, lesson_title=None):
    """Enhanced video extraction supporting multiple platforms and modal popups with comprehensive debugging"""
    
    lesson_title = lesson_title or "Unknown Lesson"
    print(f"🔍 === STARTING ENHANCED VIDEO EXTRACTION FOR: {lesson_title} ===")
    
    # Method 0: NEW - Modal video detection (for new classroom formats)
    print("🔍 METHOD 0: Modal video detection...")
    
    # First, check if we have a Skool video ID from JSON
    skool_video_id = None
    try:
        json_result = extract_from_next_data(driver)
        if json_result and json_result.get('url', '').startswith('skool-video-id:'):
            skool_video_id = json_result['url'].replace('skool-video-id:', '')
            print(f"🎯 Found Skool video ID from JSON: {skool_video_id}")
    except Exception as e:
        log_video_extraction_attempt('METHOD_0_JSON_PREP', lesson_title, None, 'failed', 
                                   {'error': str(e), 'step': 'skool_video_id_extraction'})
    
    video_data = detect_modal_video_player(driver, skool_video_id)
    if video_data:
        video_url = video_data.get('url')
        print(f"🔍 Modal method found URL: {video_url}")
        
        log_video_extraction_attempt('METHOD_0_MODAL', lesson_title, video_url, 'found', 
                                   {'platform': video_data.get('platform'), 'source': video_data.get('source')})
        
        # Early session duplicate check
        if check_session_duplicate_early(video_url, lesson_title, 'METHOD_0_MODAL'):
            log_video_extraction_attempt('METHOD_0_MODAL', lesson_title, video_url, 'blocked', 
                                       {'reason': 'early_session_duplicate'})
            print(f"🚫 METHOD 0 BLOCKED - Early session duplicate detected: {video_url}")
        elif is_valid_lesson_video(video_url):
            print(f"✅ METHOD 0 SUCCESS - Valid video from modal: {video_url}")
            # NUCLEAR VALIDATION: Final check before return
            final_result = _final_video_validation(video_data, lesson_title, 'METHOD_0_MODAL', driver)
            if final_result:
                log_video_extraction_attempt('METHOD_0_FINAL', lesson_title, video_url, 'found', 
                                           {'validation': 'passed', 'final_url': final_result.get('url')})
                return final_result
            else:
                log_video_extraction_attempt('METHOD_0_FINAL', lesson_title, video_url, 'blocked', 
                                           {'validation': 'failed_final_check'})
        else:
            log_video_extraction_attempt('METHOD_0_MODAL', lesson_title, video_url, 'blocked', 
                                       {'reason': 'failed_validation'})
            print(f"🚫 METHOD 0 BLOCKED - Rejected cached video from modal: {video_url}")
    else:
        print("⚠️ METHOD 0 - No video found in modal")
        log_video_extraction_attempt('METHOD_0_MODAL', lesson_title, None, 'none', 
                                   {'reason': 'no_modal_video_detected'})
    
    # Method 1: JSON data extraction (most reliable)
    print("🔍 METHOD 1: JSON data extraction...")
    video_data = extract_from_next_data(driver)
    if video_data:
        video_url = video_data.get('url')
        print(f"🔍 JSON method found URL: {video_url}")
        
        log_video_extraction_attempt('METHOD_1_JSON', lesson_title, video_url, 'found', 
                                   {'platform': video_data.get('platform'), 'source': 'next_data_json'})
        
        # Skip Skool video IDs - these need modal interaction
        if video_url and video_url.startswith('skool-video-id:'):
            print(f"⚠️ METHOD 1 - Found Skool video ID, need modal interaction: {video_url}")
            log_video_extraction_attempt('METHOD_1_JSON', lesson_title, video_url, 'none', 
                                       {'reason': 'skool_video_id_needs_modal'})
        # Early session duplicate check
        elif check_session_duplicate_early(video_url, lesson_title, 'METHOD_1_JSON'):
            log_video_extraction_attempt('METHOD_1_JSON', lesson_title, video_url, 'blocked', 
                                       {'reason': 'early_session_duplicate'})
            print(f"🚫 METHOD 1 BLOCKED - Early session duplicate detected: {video_url}")
        elif is_valid_lesson_video(video_url):
            print(f"✅ METHOD 1 SUCCESS - Valid video from JSON: {video_url}")
            # NUCLEAR VALIDATION: Final check before return
            final_result = _final_video_validation(video_data, lesson_title, 'METHOD_1_JSON', driver)
            if final_result:
                log_video_extraction_attempt('METHOD_1_FINAL', lesson_title, video_url, 'found', 
                                           {'validation': 'passed', 'final_url': final_result.get('url')})
                return final_result
            else:
                log_video_extraction_attempt('METHOD_1_FINAL', lesson_title, video_url, 'blocked', 
                                           {'validation': 'failed_final_check'})
        else:
            log_video_extraction_attempt('METHOD_1_JSON', lesson_title, video_url, 'blocked', 
                                       {'reason': 'failed_validation'})
            print(f"🚫 METHOD 1 BLOCKED - Rejected cached video from JSON: {video_url}")
    else:
        print("⚠️ METHOD 1 - No video found in JSON")
        log_video_extraction_attempt('METHOD_1_JSON', lesson_title, None, 'none', 
                                   {'reason': 'no_json_video_data'})
    
    # Method 2: Try clicking video player to trigger video load
    print("🔍 METHOD 2: Click video player extraction...")
    video_data = click_video_player_and_extract(driver)
    if video_data:
        video_url = video_data.get('url')
        print(f"🔍 Click method found URL: {video_url}")
        
        log_video_extraction_attempt('METHOD_2_CLICK', lesson_title, video_url, 'found', 
                                   {'platform': video_data.get('platform'), 'source': video_data.get('source')})
        
        # Early session duplicate check
        if check_session_duplicate_early(video_url, lesson_title, 'METHOD_2_CLICK'):
            log_video_extraction_attempt('METHOD_2_CLICK', lesson_title, video_url, 'blocked', 
                                       {'reason': 'early_session_duplicate'})
            print(f"🚫 METHOD 2 BLOCKED - Early session duplicate detected: {video_url}")
        elif is_valid_lesson_video(video_url):
            print(f"✅ METHOD 2 SUCCESS - Valid video from click: {video_url}")
            # NUCLEAR VALIDATION: Final check before return
            final_result = _final_video_validation(video_data, lesson_title, 'METHOD_2_CLICK', driver)
            if final_result:
                log_video_extraction_attempt('METHOD_2_FINAL', lesson_title, video_url, 'found', 
                                           {'validation': 'passed', 'final_url': final_result.get('url')})
                return final_result
            else:
                log_video_extraction_attempt('METHOD_2_FINAL', lesson_title, video_url, 'blocked', 
                                           {'validation': 'failed_final_check'})
        else:
            log_video_extraction_attempt('METHOD_2_CLICK', lesson_title, video_url, 'blocked', 
                                       {'reason': 'failed_validation'})
            print(f"🚫 METHOD 2 BLOCKED - Rejected cached video from click: {video_url}")
    else:
        print("⚠️ METHOD 2 - No video found via click")
        log_video_extraction_attempt('METHOD_2_CLICK', lesson_title, None, 'none', 
                                   {'reason': 'no_click_video_found'})
    
    # Method 3: iframe scanning (all platforms) with better filtering
    print("🔍 METHOD 3: Iframe scanning extraction...")
    video_data = scan_video_iframes_filtered(driver)
    if video_data:
        video_url = video_data.get('url')
        print(f"🔍 Iframe method found URL: {video_url}")
        
        log_video_extraction_attempt('METHOD_3_IFRAME', lesson_title, video_url, 'found', 
                                   {'platform': video_data.get('platform'), 'source': video_data.get('source')})
        
        # Early session duplicate check
        if check_session_duplicate_early(video_url, lesson_title, 'METHOD_3_IFRAME'):
            log_video_extraction_attempt('METHOD_3_IFRAME', lesson_title, video_url, 'blocked', 
                                       {'reason': 'early_session_duplicate'})
            print(f"🚫 METHOD 3 BLOCKED - Early session duplicate detected: {video_url}")
        elif is_valid_lesson_video(video_url):
            print(f"✅ METHOD 3 SUCCESS - Valid video from iframe: {video_url}")
            # NUCLEAR VALIDATION: Final check before return
            final_result = _final_video_validation(video_data, lesson_title, 'METHOD_3_IFRAME', driver)
            if final_result:
                log_video_extraction_attempt('METHOD_3_FINAL', lesson_title, video_url, 'found', 
                                           {'validation': 'passed', 'final_url': final_result.get('url')})
                return final_result
            else:
                log_video_extraction_attempt('METHOD_3_FINAL', lesson_title, video_url, 'blocked', 
                                           {'validation': 'failed_final_check'})
        else:
            log_video_extraction_attempt('METHOD_3_IFRAME', lesson_title, video_url, 'blocked', 
                                       {'reason': 'failed_validation'})
            print(f"🚫 METHOD 3 BLOCKED - Rejected cached video from iframe: {video_url}")
    else:
        print("⚠️ METHOD 3 - No video found in iframes")
        log_video_extraction_attempt('METHOD_3_IFRAME', lesson_title, None, 'none', 
                                   {'reason': 'no_iframe_video_found'})
    
    # Method 4: Network logs inspection for media URLs (HLS/MP4 or hidden player requests)
    print("🔍 METHOD 4: Inspecting network logs for media URLs...")
    net_video = _extract_video_from_network_logs(driver)
    if net_video:
        video_url = net_video.get('url')
        print(f"🔍 Network method found URL: {video_url}")
        
        log_video_extraction_attempt('METHOD_4_NETWORK', lesson_title, video_url, 'found', 
                                   {'platform': net_video.get('platform'), 'source': 'network_logs'})
        
        # Early session duplicate check
        if check_session_duplicate_early(video_url, lesson_title, 'METHOD_4_NETWORK'):
            log_video_extraction_attempt('METHOD_4_NETWORK', lesson_title, video_url, 'blocked', 
                                       {'reason': 'early_session_duplicate'})
            print(f"🚫 METHOD 4 BLOCKED - Early session duplicate detected: {video_url}")
        else:
            final_result = _final_video_validation(net_video, lesson_title, 'METHOD_4_NETWORK', driver)
            if final_result:
                log_video_extraction_attempt('METHOD_4_FINAL', lesson_title, video_url, 'found', 
                                           {'validation': 'passed', 'final_url': final_result.get('url')})
                return final_result
            else:
                log_video_extraction_attempt('METHOD_4_FINAL', lesson_title, video_url, 'blocked', 
                                           {'validation': 'failed_final_check'})
    else:
        print("⚠️ METHOD 4 - No media found in network logs")
        log_video_extraction_attempt('METHOD_4_NETWORK', lesson_title, None, 'none', 
                                   {'reason': 'no_network_media_found'})

    # Method 5: Legacy YouTube extraction as final fallback
    print("🔍 METHOD 5: Legacy YouTube extraction...")
    youtube_url = extract_youtube_url_legacy(driver)
    if youtube_url:
        print(f"🔍 Legacy method found URL: {youtube_url}")
        
        log_video_extraction_attempt('METHOD_5_LEGACY', lesson_title, youtube_url, 'found', 
                                   {'platform': 'youtube', 'source': 'legacy_extraction'})
        
        # Early session duplicate check
        if check_session_duplicate_early(youtube_url, lesson_title, 'METHOD_5_LEGACY'):
            log_video_extraction_attempt('METHOD_5_LEGACY', lesson_title, youtube_url, 'blocked', 
                                       {'reason': 'early_session_duplicate'})
            print(f"🚫 METHOD 5 BLOCKED - Early session duplicate detected: {youtube_url}")
        elif is_valid_lesson_video(youtube_url):
            print(f"✅ METHOD 5 SUCCESS - Valid video from legacy: {youtube_url}")
            video_data = {
                'url': youtube_url,
                'platform': 'youtube',
                'thumbnail': None,
                'duration': None
            }
            # NUCLEAR VALIDATION: Final check before return
            final_result = _final_video_validation(video_data, lesson_title, 'METHOD_5_LEGACY', driver)
            if final_result:
                log_video_extraction_attempt('METHOD_5_FINAL', lesson_title, youtube_url, 'found', 
                                           {'validation': 'passed', 'final_url': final_result.get('url')})
                return final_result
            else:
                log_video_extraction_attempt('METHOD_5_FINAL', lesson_title, youtube_url, 'blocked', 
                                           {'validation': 'failed_final_check'})
        else:
            log_video_extraction_attempt('METHOD_5_LEGACY', lesson_title, youtube_url, 'blocked', 
                                       {'reason': 'failed_validation'})
            print(f"🚫 METHOD 5 BLOCKED - Rejected cached video from legacy: {youtube_url}")
    else:
        print("⚠️ METHOD 5 - No video found via legacy")
        log_video_extraction_attempt('METHOD_5_LEGACY', lesson_title, None, 'none', 
                                   {'reason': 'no_legacy_video_found'})
    
    log_video_extraction_attempt('ALL_METHODS', lesson_title, None, 'failed', 
                               {'reason': 'all_extraction_methods_failed'})
    print("❌ === NO VALID VIDEO FOUND WITH ANY METHOD ===")
    return None

def _extract_video_from_network_logs(driver):
    """Inspect performance logs for media URLs and return canonicalized video data if found."""
    try:
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
            # Accept known player/embeds incl. oEmbed
            if ('youtube.com' in u or 'youtu.be' in u or 'vimeo.com' in u or 'loom.com' in u or
                'fast.wistia.net/embed/iframe/' in u or 'wistia.com/medias/' in u or 'oembed?format=json&url=' in u):
                return True
            # Exclude Wistia delivery images
            if 'wistia' in u and 'deliveries' in u:
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
        if not candidates:
            return None
        # Prefer canonicalized player URLs
        prioritized = sorted(candidates, key=lambda u: (('oembed' in u), ('m3u8' not in u and '.mp4' not in u)))
        best = prioritized[0]
        platform = detect_platform(best)
        clean_url = clean_video_url(best, platform)
        return {
            'url': clean_url,
            'platform': platform,
            'source': 'network_logs'
        }
    except Exception as e:
        print(f"⚠️ Network log inspection failed: {e}")
        return None

def _final_video_validation(video_data, lesson_title=None, extraction_method=None, driver=None):
    """NUCLEAR OPTION: Final validation checkpoint that NO duplicate can bypass"""
    if not video_data or not isinstance(video_data, dict):
        print("🚫 FINAL VALIDATION: Invalid video data structure")
        return None
    
    lesson_title = lesson_title or "Unknown Lesson"
    extraction_method = extraction_method or "Unknown Method"
    
    # Ensure canonical URL before validation and dedup
    video_url = video_data.get('url')
    platform = video_data.get('platform', 'unknown')
    if video_url:
        cleaned = clean_video_url(video_url, platform)
        if cleaned and cleaned != video_url:
            print(f"🧹 FINAL VALIDATION: Canonicalized URL {video_url} → {cleaned}")
            video_data['url'] = cleaned
            video_url = cleaned
    if not video_url:
        print("🚫 FINAL VALIDATION: No URL in video data")
        return None
    
    print(f"🛡️ FINAL VALIDATION CHECKPOINT: {video_url}")
    
    # Re-run validation one more time as absolute final check
    if is_valid_lesson_video(video_url):
        # NEW: Lesson-specific validation
        if validate_video_belongs_to_lesson(video_url, lesson_title, driver):
            # Enhanced session-level duplicate guard with comprehensive tracking
            if register_video_in_session(video_url, lesson_title, extraction_method, platform):
                print(f"✅ FINAL VALIDATION PASSED: Video is valid, lesson-relevant, and registered - {video_url}")
                return video_data
            else:
                print(f"🚫 FINAL VALIDATION FAILED: Session duplicate detected - {video_url}")
                return None
        else:
            print(f"🚫 FINAL VALIDATION FAILED: Video does not belong to lesson - {video_url}")
            return None
    else:
        print(f"🚫 FINAL VALIDATION FAILED: Video blocked at final checkpoint - {video_url}")
        return None

def extract_youtube_url_legacy(driver):
    """Enhanced YouTube URL extraction that targets lesson-specific videos with custom play button fix"""
    youtube_url = None
    
    try:
        print("🔍 Looking for lesson-specific YouTube video (custom play button)...")
        
        # Method 1: Click the custom play button and wait for iframe (NEW IMPROVED METHOD)
        try:
            # Click the custom play button
            play_button = driver.find_element(By.CSS_SELECTOR, ".styled__PlaybackButton-sc-bpv3k2-5")
            play_button.click()
            print("▶️ Clicked custom play button.")
            time.sleep(1)  # Wait for animation
            
            # Wait for the YouTube iframe to appear
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='youtube.com']"))
            )
            print("✅ YouTube iframe appeared after play.")
            
            # Extract the YouTube URL from the iframe
            iframe = driver.find_element(By.CSS_SELECTOR, "iframe[src*='youtube.com']")
            raw_youtube_url = iframe.get_attribute("src")
            print(f"✅ Raw YouTube iframe URL: {raw_youtube_url}")
            
            # Convert to canonical format
            match = re.search(r"(?:youtube\.com/embed/|youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})", raw_youtube_url)
            if match:
                video_id = match.group(1)
                youtube_url = f"https://youtu.be/{video_id}"
                print(f"✅ Canonical YouTube URL: {youtube_url}")
                return youtube_url
            else:
                print("⚠️ Could not extract video ID from iframe URL, returning raw URL.")
                return raw_youtube_url
                
        except Exception as e:
            print(f"⚠️ Custom play button method failed: {e}")
            # Continue to fallback methods
        
        # Method 2: Look for video player in the main content area (FALLBACK)
        video_selectors = [
            # Common video player selectors
            "iframe[src*='youtube.com/embed']",
            "iframe[src*='youtu.be']",
            "iframe[src*='youtube.com/watch']",
            # Video container selectors
            "[class*='video'] iframe[src*='youtube']",
            "[class*='player'] iframe[src*='youtube']",
            "[class*='embed'] iframe[src*='youtube']",
            # Lesson-specific video areas
            "[class*='lesson'] iframe[src*='youtube']",
            "[class*='content'] iframe[src*='youtube']",
            "[class*='main'] iframe[src*='youtube']"
        ]
        
        for selector in video_selectors:
            try:
                iframe = driver.find_element(By.CSS_SELECTOR, selector)
                src = iframe.get_attribute("src")
                if src and ("youtube.com" in src or "youtu.be" in src):
                    # Convert embed URL to watch URL
                    if "embed" in src:
                        video_id = src.split("/embed/")[-1].split("?")[0]
                        youtube_url = f"https://youtu.be/{video_id}"
                    else:
                        youtube_url = src
                    print(f"✅ Found lesson video using selector: {selector}")
                    print(f"🎥 YouTube URL: {youtube_url}")
                    return youtube_url
            except Exception:
                continue
        
        # Method 3: Look for YouTube links in the main content area (not header/nav)
        content_selectors = [
            ".styled__RichTextEditorWrapper-sc-1cnx5by-0",
            "[class*='RichTextEditor']",
            "[class*='EditorContent']",
            ".tiptap.ProseMirror",
            "[class*='ModuleBody']",
            "[class*='content']",
            "[class*='description']",
            "div[class*='MainContent']",
            "main",
            "[role='main']",
            "article"
        ]
        
        for content_selector in content_selectors:
            try:
                content_element = driver.find_element(By.CSS_SELECTOR, content_selector)
                youtube_links = content_element.find_elements(By.CSS_SELECTOR, "a[href*='youtube.com'], a[href*='youtu.be']")
                
                for link in youtube_links:
                    href = link.get_attribute("href")
                    if href and ("youtube.com" in href or "youtu.be" in href):
                        # Skip generic header/nav links
                        if "YTrIwmIdaJI" not in href:  # Skip the generic URL we found
                            youtube_url = href
                            print(f"✅ Found lesson video link in content: {youtube_url}")
                            return youtube_url
            except Exception:
                continue
        
        # Method 4: Search page source but exclude the generic header URL
        page_source = driver.page_source
        youtube_regex = r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})'
        matches = re.findall(youtube_regex, page_source)
        
        # List of video IDs to skip (known problematic cached videos)
        skip_video_ids = [
            "YTrIwmIdaJI",  # Generic header URL
            "UDcrRdfB0x8",  # The problematic cached video
            "7snrj0uEaDw"   # Another problematic cached video
        ]
        
        for video_id in matches:
            if video_id not in skip_video_ids:
                youtube_url = f"https://youtu.be/{video_id}"
                print(f"✅ Found lesson video in page source: {youtube_url}")
                return youtube_url
        
        # Method 5: Look for video elements with data attributes
        video_elements = driver.find_elements(By.CSS_SELECTOR, "video, [data-video], [data-youtube]")
        for video in video_elements:
            try:
                # Check various data attributes
                for attr in ['data-src', 'data-video', 'data-youtube', 'src']:
                    value = video.get_attribute(attr)
                    if value and ("youtube.com" in value or "youtu.be" in value):
                        if "YTrIwmIdaJI" not in value:  # Skip generic URL
                            youtube_url = value
                            print(f"✅ Found lesson video in video element: {youtube_url}")
                            return youtube_url
            except Exception:
                continue
        
        # If no lesson-specific video found, return None instead of generic URL
        print("⚠️ No lesson-specific YouTube video found")
        return None
        
    except Exception as e:
        print(f"❌ Error extracting YouTube URL: {str(e)}")
        return None

def extract_lesson_content(driver):
    """Extract all text content and links from the current lesson."""
    content = {
        'text_content': '',
        'links': [],
        'resources': '',
        'examples': ''
    }
    
    try:
        # Look for main content area (the text under the video)
        content_selectors = [
            ".styled__RichTextEditorWrapper-sc-1cnx5by-0",
            "[class*='RichTextEditor']",
            "[class*='EditorContent']",
            ".tiptap.ProseMirror",
            "[class*='ModuleBody']",
            "[class*='content']",
            "[class*='description']",
            "div[class*='MainContent']",
            # Generic selectors
            "main",
            "[role='main']",
            "article"
        ]
        
        main_content_element = None
        for selector in content_selectors:
            try:
                main_content_element = driver.find_element(By.CSS_SELECTOR, selector)
                if main_content_element and main_content_element.text.strip():
                    print(f"✅ Extracted text content using selector: {selector}")
                    break
            except NoSuchElementException:
                continue
                
        if main_content_element:
            # Extract all text content
            text_content = main_content_element.text
            content['text_content'] = text_content
            
            # 1. Extract links from <a> tags
            links_from_tags = []
            links = main_content_element.find_elements(By.TAG_NAME, "a")
            for link in links:
                try:
                    href = link.get_attribute("href")
                    text = link.text.strip()
                    if href and text:
                        links_from_tags.append({
                            'text': text,
                            'url': href
                        })
                except Exception:
                    continue
            
            # 2. Extract plain text URLs using regex
            plain_text_urls = []
            url_pattern = r'https?://[^\s/$.?#].[^\s]*'
            found_urls = re.findall(url_pattern, text_content)
            for url in found_urls:
                plain_text_urls.append({
                    'text': url,  # Use the URL itself as text
                    'url': url
                })
                
            # Combine and de-duplicate links
            all_links = links_from_tags
            all_urls = {link['url'] for link in all_links}
            
            for link in plain_text_urls:
                if link['url'] not in all_urls:
                    all_links.append(link)
                    all_urls.add(link['url'])

            content['links'] = all_links
            
            # Look for specific sections
            if "RESOURCES:" in text_content:
                resources_text = text_content.split("RESOURCES:")[1]
                if "EXAMPLES:" in resources_text:
                    resources_text = resources_text.split("EXAMPLES:")[0]
                content['resources'] = resources_text.strip()
            
            if "EXAMPLES:" in text_content:
                examples_text = text_content.split("EXAMPLES:")[1]
                content['examples'] = examples_text.strip()
                
        else:
            # Fallback: get content from body
            print("⚠️ Main content not found, proceeding anyway...")
            body = driver.find_element(By.TAG_NAME, "body")
            content['text_content'] = body.text
            print("✅ Extracted text content from body element")
            
        print(f"✅ Extracted content: {len(content['links'])} links found")
        return content
        
    except Exception as e:
        print(f"❌ Error extracting lesson content: {str(e)}")
        return content

def download_images_from_lesson(driver, lesson_title, images_dir):
    """Download images from the current lesson."""
    images_downloaded = []
    
    try:
        # Create lesson-specific image directory
        safe_title = sanitize_filename(lesson_title)
        lesson_images_dir = os.path.join(images_dir, safe_title)
        os.makedirs(lesson_images_dir, exist_ok=True)
        
        # Find all images in the content area
        images = driver.find_elements(By.TAG_NAME, "img")
        
        image_count = 0
        for i, img in enumerate(images):
            try:
                src = img.get_attribute("src")
                if src and not src.startswith("data:") and "youtube" not in src.lower() and "avatar" not in src.lower():
                    # Get image filename
                    parsed_url = urlparse(src)
                    filename = os.path.basename(parsed_url.path)
                    if not filename or not any(ext in filename.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                        filename = f"image_{image_count + 1}.jpg"
                    
                    filepath = os.path.join(lesson_images_dir, filename)
                    
                    # Download image
                    urllib.request.urlretrieve(src, filepath)
                    images_downloaded.append(filepath)
                    image_count += 1
                    print(f"📸 Downloaded image: {filename}")
                    
            except Exception as e:
                print(f"⚠️ Failed to download image {i+1}: {str(e)}")
                continue
                
        if images_downloaded:
            print(f"✅ Downloaded {len(images_downloaded)} images to: {lesson_images_dir}")
        else:
            print("📷 No images found to download")
            
    except Exception as e:
        print(f"❌ Error downloading images: {str(e)}")
        
    return images_downloaded

def save_lesson_content(lesson_title, video_data, content, images_downloaded, output_dirs, video_downloaded=False, community_display_name=None, community_slug=None):
    """Enhanced lesson content saving with images and links - V2 Universal Video Support + Video Downloads"""
    try:
        # Create short, safe filename (no subdirectories for lessons)
        safe_title = sanitize_filename(lesson_title)
        
        filename = f"{safe_title}.md"
        filepath = os.path.join(output_dirs['lessons'], filename)
        
        # Format video information
        video_section = ""
        if video_data:
            platform = video_data.get('platform', 'unknown').title()
            video_url = video_data.get('url', '')
            duration = video_data.get('duration')
            thumbnail = video_data.get('thumbnail')
            
            # Format duration if available
            duration_str = ""
            if duration:
                minutes = duration // 60000  # Convert ms to minutes
                seconds = (duration % 60000) // 1000
                duration_str = f" ({minutes}:{seconds:02d})"
            
            video_section = f"**🎥 Video ({platform}):** {video_url}{duration_str}"
            
            if thumbnail:
                video_section += f"\n**📸 Thumbnail:** {thumbnail}"
        else:
            video_section = "**🎥 Video:** No video found"
        
        # Create enhanced markdown content
        community_info = f"**📂 Community:** {community_display_name}" if community_display_name else ""
        
        markdown_content = f"""# {lesson_title}

**Extracted on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{video_section}
{community_info}
**📂 Lesson Folder:** {safe_title}

## 📝 Content

{content['text_content']}

"""
        
        # Add links section if we have links
        if content['links']:
            markdown_content += """## 🔗 Links and Resources

### All Links:

"""
            for link in content['links']:
                markdown_content += f"- [{link['text']}]({link['url']})\n"
            markdown_content += "\n"
        
        # Add resources section
        if content['resources']:
            markdown_content += """### Resources:

"""
            markdown_content += content['resources'] + "\n\n"
            
        # Add examples section
        if content['examples']:
            markdown_content += """### Examples:

"""
            markdown_content += content['examples'] + "\n\n"
        
        # Add images section
        if images_downloaded:
            markdown_content += """## 🖼️ Images

"""
            for img_path in images_downloaded:
                img_name = os.path.basename(img_path)
                # Images are in ../images/ relative to lessons folder
                relative_path = f"../images/{img_name}"
                markdown_content += f"![{img_name}]({relative_path})\n\n"
        
        # Add metadata
        video_status = "✅ Downloaded" if video_downloaded else "📝 URL only" if video_data else "❌ No video"
        community_name_for_footer = community_display_name if community_display_name else "Unknown Community"
        markdown_content += f"""
---
*Extracted from Skool {community_name_for_footer} - V4 Simplified*
*Video: {video_status}*
*Images downloaded: {len(images_downloaded)}*
*Links captured: {len(content['links'])}*
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"💾 Saved content to: {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving lesson: {str(e)}")
        return False

def process_lessons_with_direct_urls(driver, lesson_data, output_dirs, collection_url, community_display_name=None, download_videos=False):
    """Process lessons by navigating to direct URLs instead of clicking elements"""
    processed_count = 0
    failed_lessons = []
    skipped_count = 0
    
    # Extract course hierarchy for organized folder structure
    print("\n🏗️ Extracting course hierarchy for better organization...")
    hierarchy = extract_course_hierarchy(driver)
    
    # Get already extracted lessons
    already_extracted = get_already_extracted_lessons(output_dirs['lessons'])
    
    # Extract base URL from collection URL
    parsed_url = urlparse(collection_url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?md="
    
    print(f"🎯 Processing {len(lesson_data)} lessons...")
    
    # Statistics tracking
    stats = {
        'total_lessons': len(lesson_data),
        'processed': 0,
        'skipped': 0,
        'failed': 0,
        'videos_found': 0,
        'videos_downloaded': 0,
        'platforms': {}
    }
    
    for i, (lesson_title, md_value) in enumerate(lesson_data, 1):
        print(f"\n{'='*60}")
        print(f"🎯 Processing lesson {i}/{len(lesson_data)}: {lesson_title}")
        print(f"🔗 MD value: {md_value}")
        print(f"📊 Progress: {((i-1)/len(lesson_data)*100):.1f}% complete")
        
        # Check if already extracted
        clean_title = clean_title_for_comparison(lesson_title)
        if clean_title in already_extracted:
            print(f"⏭️  Already extracted: {lesson_title}")
            stats['skipped'] += 1
            continue
        
        try:
            # Check if we should use browser isolation for this lesson
            use_isolation = should_use_browser_isolation(lesson_title, i, len(lesson_data))
            
            if use_isolation:
                # Process lesson with completely isolated browser
                lesson_url = base_url + md_value
                result = process_lesson_with_isolated_browser(
                    lesson_title, lesson_url, lesson_id, email, password, 
                    download_videos, output_dirs, community_display_name, community_slug
                )
                
                if result is True:
                    stats['processed'] += 1
                    print(f"✅ Successfully processed with isolated browser: {lesson_title}")
                elif isinstance(result, dict):
                    # Extract data was successful, now save it
                    video_data = result['video_data']
                    content = result['content']
                    images_downloaded = result['images_downloaded']
                    
                    # Save lesson content with hierarchical structure
                    if content['text_content'] or video_data or images_downloaded:
                        # Find hierarchical path for this lesson
                        lesson_hierarchy_path = find_lesson_hierarchy_path(lesson_title, hierarchy)
                        
                        # Extract community slug from the lesson data context
                        community_slug = collection_url.split('/')[-3] if '/' in collection_url else None
                        
                        # Create hierarchical directories for this specific lesson
                        if lesson_hierarchy_path:
                            hierarchical_dirs = create_hierarchical_lesson_directories(community_display_name, community_slug, lesson_hierarchy_path)
                            print(f"📁 Using hierarchical path: {lesson_hierarchy_path}")
                        else:
                            # Fallback to original structure if no hierarchy found
                            hierarchical_dirs = output_dirs
                            print(f"📁 Using flat structure (no hierarchy found for: {lesson_title})")
                        
                        if save_lesson_content(lesson_title, video_data, content, images_downloaded, hierarchical_dirs, False, community_display_name, community_slug):
                            stats['processed'] += 1
                            print(f"✅ Successfully processed with isolated browser: {lesson_title}")
                        else:
                            stats['failed'] += 1
                            failed_lessons.append(lesson_title)
                            print(f"❌ Failed to save: {lesson_title}")
                    else:
                        print(f"⚠️ No content found for: {lesson_title}")
                        stats['failed'] += 1
                        failed_lessons.append(lesson_title)
                else:
                    stats['failed'] += 1
                    failed_lessons.append(lesson_title)
                    print(f"❌ Failed to process with isolated browser: {lesson_title}")
                
                # Skip the rest of the shared browser processing
                continue
            
            # Use shared browser with enhanced isolation
            BROWSER_ISOLATION['isolation_stats']['lessons_with_shared_browser'] += 1
            
            # Aggressive state isolation before each lesson to avoid cross-lesson contamination
            clear_browser_storage_bulk(driver)
            # Navigate directly to the lesson URL
            lesson_url = base_url + md_value
            print(f"🌐 Navigating to: {lesson_url}")
            
            driver.get(lesson_url)
            time.sleep(3)  # Wait for page to load
            
            # Set lesson context for validation
            set_lesson_context(lesson_title, lesson_url, lesson_id)
            
            # Generate lesson content signature for validation
            generate_lesson_content_signature(driver, lesson_title)
            
            # Extract Video URL (Universal - YouTube, Vimeo, etc.)
            video_data = extract_video_url(driver, lesson_title)
            
            # Download video if found and requested (Phase 2 - Universal Video Download)
            video_downloaded = False
            if video_data:
                stats['videos_found'] += 1
                platform = video_data.get('platform', 'unknown')
                stats['platforms'][platform] = stats['platforms'].get(platform, 0) + 1
                
                if download_videos:
                    video_output_dir = os.path.join(output_dirs['lessons'], sanitize_filename(lesson_title), "videos")
                    video_downloaded = download_video_universal(video_data, lesson_title, video_output_dir)
                    
                    if video_downloaded:
                        stats['videos_downloaded'] += 1
                        print(f"✅ Video downloaded: {video_data['url']}")
                    else:
                        print(f"⚠️ Video download failed: {video_data['url']}")
                else:
                    print(f"🎥 Video URL extracted: {video_data['url']} ({platform})")
                    print(f"💡 Use --download-videos flag to download video files")
            
            # Extract content with enhanced functionality
            content = extract_lesson_content(driver)
            
            # Download images
            images_downloaded = download_images_from_lesson(driver, lesson_title, output_dirs['images'])
            
            # Save lesson content with hierarchical structure
            if content['text_content'] or video_data or images_downloaded:
                # Find hierarchical path for this lesson
                lesson_hierarchy_path = find_lesson_hierarchy_path(lesson_title, hierarchy)
                
                # Extract community slug from the lesson data context
                community_slug = collection_url.split('/')[-3] if '/' in collection_url else None
                
                # Create hierarchical directories for this specific lesson
                if lesson_hierarchy_path:
                    hierarchical_dirs = create_hierarchical_lesson_directories(community_display_name, community_slug, lesson_hierarchy_path)
                    print(f"📁 Using hierarchical path: {lesson_hierarchy_path}")
                else:
                    # Fallback to original structure if no hierarchy found
                    hierarchical_dirs = output_dirs
                    print(f"📁 Using flat structure (no hierarchy found for: {lesson_title})")
                
                if save_lesson_content(lesson_title, video_data, content, images_downloaded, hierarchical_dirs, video_downloaded, community_display_name, community_slug):
                    stats['processed'] += 1
                    SESSION_STATS['lessons_processed'] += 1
                    print(f"✅ Successfully processed: {lesson_title}")
                else:
                    stats['failed'] += 1
                    failed_lessons.append(lesson_title)
                    print(f"❌ Failed to save: {lesson_title}")
            else:
                print(f"⚠️ No content found for: {lesson_title}")
                stats['failed'] += 1
                failed_lessons.append(lesson_title)
            
            # Small delay between lessons
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            print(f"❌ Error processing {lesson_title}: {str(e)}")
            stats['failed'] += 1
            failed_lessons.append(lesson_title)
            continue
    
    # Print comprehensive summary
    print(f"\n{'='*80}")
    print("🎉 EXTRACTION COMPLETED - V2 UNIVERSAL VIDEO SUPPORT")
    print(f"{'='*80}")
    print(f"📊 FINAL STATISTICS:")
    print(f"   📚 Total Lessons: {stats['total_lessons']}")
    print(f"   ✅ Successfully Processed: {stats['processed']}")
    print(f"   ⏭️  Skipped (Already Extracted): {stats['skipped']}")
    print(f"   ❌ Failed: {stats['failed']}")
    print(f"   🎬 Videos Found: {stats['videos_found']}")
    print(f"   📥 Videos Downloaded: {stats['videos_downloaded']}")
    
    if stats['platforms']:
        print(f"\n📱 VIDEO PLATFORMS DETECTED:")
        for platform, count in stats['platforms'].items():
            print(f"   {platform.title()}: {count} videos")
    
    success_rate = (stats['processed'] / stats['total_lessons'] * 100) if stats['total_lessons'] > 0 else 0
    download_rate = (stats['videos_downloaded'] / stats['videos_found'] * 100) if stats['videos_found'] > 0 else 0
    
    print(f"\n📈 SUCCESS RATES:")
    print(f"   Content Extraction: {success_rate:.1f}%")
    if stats['videos_found'] > 0:
        print(f"   Video Downloads: {download_rate:.1f}%")
    
    if failed_lessons:
        print(f"\n❌ FAILED LESSONS ({len(failed_lessons)}):")
        for lesson in failed_lessons[:5]:  # Show first 5
            print(f"   - {lesson}")
        if len(failed_lessons) > 5:
            print(f"   ... and {len(failed_lessons) - 5} more")
    
    print(f"\n📁 Output Location: extracted_content/lessons/")
    print(f"{'='*80}")
    
    return stats['processed'], failed_lessons, stats['skipped']

def process_single_lesson(lesson_url, email, password, download_video=False):
    """Process a single lesson URL with proper navigation handling"""
    # Initialize session tracking for single lesson
    reset_session_tracking()
    
    print(f"🎯 SINGLE LESSON EXTRACTOR")
    print(f"🔗 Target URL: {lesson_url}")
    print(f"📥 Download Video: {'Yes' if download_video else 'No (URLs only)'}")
    
    # Extract community info from URL
    community, section, lesson_id = extract_community_info_from_url(lesson_url)
    if not community:
        community = "unknown-community"
        section = "classroom"
        print("⚠️ Could not extract community from URL, using 'unknown-community'")
    
    print(f"🌐 Community: {community}")
    print(f"📚 Section: {section}")
    
    driver = setup_driver()
    
    try:
        # Login to Skool
        print(f"\n🔐 Logging in to Skool...")
        if not login_to_skool(driver, email, password):
            print("❌ Login failed - cannot proceed")
            return False
        
        print(f"✅ Login successful!")
        
        # Navigate to lesson with enhanced navigation
        print(f"\n🔗 Navigating to lesson...")
        success = navigate_to_lesson_enhanced(driver, lesson_url)
        if not success:
            print("❌ Failed to navigate to lesson")
            return False
        
        # Extract clean community name
        print("\n🏷️ Extracting community information...")
        community_display_name = extract_clean_community_name(driver)
        if community_display_name:
            print(f"✅ Community Name: {community_display_name}")
        else:
            print("⚠️ Using URL slug as fallback community name")
            community_display_name = community.replace('-', ' ').title()
        
        # Extract lesson name
        lesson_name = extract_lesson_name_simple(driver)
        if not lesson_name:
            lesson_name = f"Untitled Lesson - {datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        
        print(f"📖 Lesson Name: {lesson_name}")
        
        # Set lesson context for validation
        set_lesson_context(lesson_name, lesson_url, lesson_id)
        
        # Generate lesson content signature for validation
        generate_lesson_content_signature(driver, lesson_name)
        
        # Extract video with enhanced modal detection
        print(f"\n🎥 Extracting video...")
        video_data = extract_video_url(driver, lesson_name)
        
        # Extract content
        print(f"\n📝 Extracting content...")
        content = extract_content_simple(driver)
        
        # Create output directories
        output_dirs = create_organized_directories(community_display_name or f"Unknown Community ({community})", community)
        
        # Save lesson
        print(f"\n💾 Saving lesson...")
        success = save_lesson_content(
            lesson_name, 
            video_data, 
            content, 
            [], # No images for single lesson
            output_dirs,
            download_video,
            community_display_name,
            community
        )
        
        if success:
            SESSION_STATS['lessons_processed'] += 1
            print(f"\n🎉 SUCCESS! Single lesson extracted and saved.")
            print(f"📁 Location: {output_dirs['lessons']}/{sanitize_filename(lesson_name)}.md")
            if video_data:
                print(f"🎥 Video: {video_data.get('url', 'N/A')} ({video_data.get('platform', 'unknown').title()})")
            else:
                print(f"⚠️ No video found")
            return True
        else:
            print(f"\n❌ Failed to save lesson")
            return False
            
    except Exception as e:
        print(f"❌ Fatal error in single lesson processing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        print("\n📊 Saving extraction debug logs and analyzing patterns...")
        try:
            save_extraction_debug_log()
            analyze_duplicate_patterns()
            print_session_statistics()
            print_browser_isolation_statistics()
            save_session_tracking_report()
        except Exception as debug_error:
            print(f"⚠️ Debug analysis failed: {debug_error}")
        
        driver.quit()
        print(f"\n🌐 Browser closed.")

def navigate_to_lesson_enhanced(driver, lesson_url):
    """Enhanced navigation with retry logic and redirect handling"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            print(f"🔄 Navigation attempt {attempt + 1}/{max_retries}")
            
            # Navigate to the URL
            driver.get(lesson_url)
            time.sleep(3)
            
            # Check if we were redirected to overview
            current_url = driver.current_url
            if 'md=overview' in current_url:
                print(f"⚠️ Redirected to overview page, attempting to navigate back...")
                
                # Try to navigate directly back to the lesson
                driver.get(lesson_url)
                time.sleep(5)  # Longer wait
                
                # Check again
                current_url = driver.current_url
                if 'md=overview' in current_url:
                    print(f"⚠️ Still on overview page, trying JavaScript navigation...")
                    
                    # Extract md parameter from original URL
                    md_value = lesson_url.split('md=')[1].split('&')[0]
                    
                    # Try JavaScript navigation
                    js_nav = f"window.location.href = window.location.pathname + '?md={md_value}';"
                    driver.execute_script(js_nav)
                    time.sleep(3)
                    
                    current_url = driver.current_url
                    if 'md=overview' in current_url:
                        if attempt < max_retries - 1:
                            print(f"❌ Navigation failed, retrying in 2 seconds...")
                            time.sleep(2)
                            continue
                        else:
                            print(f"❌ All navigation attempts failed")
                            return False
            
            # Verify we're on the correct lesson
            if lesson_url.split('md=')[1].split('&')[0] in current_url:
                print(f"✅ Successfully navigated to lesson")
                
                # Wait for content to load
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    time.sleep(2)  # Additional wait for dynamic content
                    return True
                except:
                    print(f"⚠️ Page loaded but content may still be loading...")
                    time.sleep(3)
                    return True
            else:
                print(f"⚠️ URL mismatch - expected md parameter not found")
                if attempt < max_retries - 1:
                    continue
                else:
                    return False
                    
        except Exception as e:
            print(f"❌ Navigation error on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                return False
    
    return False

def extract_lesson_name_simple(driver):
    """Simple lesson name extraction"""
    try:
        print("🔍 Looking for lesson title...")
        
        # Try common selectors
        selectors = [
            "h1", "h2", "h3",
            "[class*='title']",
            "[class*='header']",
            "[class*='heading']"
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elements:
                    if el.is_displayed() and el.text.strip():
                        text = el.text.strip()
                        if (text and len(text) < 200 and len(text) > 3 and
                            "Login" not in text and "Menu" not in text and
                            "Search" not in text and "Profile" not in text):
                            print(f"✅ Found lesson title: {text}")
                            return text
            except:
                continue
        
        print("⚠️ Could not find lesson title")
        return None
        
    except Exception as e:
        print(f"❌ Error extracting lesson name: {e}")
        return None

def extract_content_simple(driver):
    """Simple content extraction"""
    try:
        print("📝 Extracting lesson content...")
        
        # Get page text content
        body = driver.find_element(By.TAG_NAME, "body")
        text_content = body.text if body else ""
        
        # Get all links
        links = []
        try:
            link_elements = driver.find_elements(By.TAG_NAME, "a")
            for link in link_elements:
                href = link.get_attribute("href")
                text = link.text.strip()
                if href and text and len(text) > 2:
                    links.append({'text': text, 'url': href})
        except:
            pass
        
        return {
            'text_content': text_content[:5000] if text_content else "No content found",  # Limit size
            'links': links[:20],  # Limit links
            'images': [],  # No image extraction for single lessons
            'resources': '',  # Empty resources
            'examples': ''   # Empty examples
        }
        
    except Exception as e:
        print(f"❌ Error extracting content: {e}")
        return {
            'text_content': "Error extracting content",
            'links': [],
            'images': []
        }

def main():
    # Initialize session tracking for this scraping session
    reset_session_tracking()
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Extract content from Skool.com classroom collections with hierarchical structure')
    parser.add_argument('url', help='The Skool.com collection URL to extract content from')
    parser.add_argument('--email', default=SKOOL_EMAIL, help='Skool.com email (default: from config)')
    parser.add_argument('--password', default=SKOOL_PASSWORD, help='Skool.com password (default: from config)')
    parser.add_argument('--download-videos', action='store_true', help='Download video files to local storage (requires yt-dlp). Default: extract video URLs only')
    
    args = parser.parse_args()
    
    # Validate URL
    if not args.url.startswith('https://www.skool.com/'):
        print("❌ Error: URL must be a valid Skool.com URL")
        print("Example: https://www.skool.com/ai-profit-lab-7462/classroom/cbb27978?md=672c0cfa7a984d3fa4df84b1a35569c9")
        sys.exit(1)
    
    # NEW: Check if this is a single lesson URL (has md= parameter)
    if 'md=' in args.url and len(args.url.split('md=')[1].split('&')[0]) > 10:
        print("🎯 SINGLE LESSON DETECTED - Switching to single lesson mode")
        print("=" * 60)
        return process_single_lesson(args.url, args.email, args.password, args.download_videos)
    
    # Extract community info from URL
    community, section, lesson_id = extract_community_info_from_url(args.url)
    if not community:
        community = "unknown-community"
        section = "classroom"
        print("⚠️ Could not extract community from URL, using 'unknown-community'")
    
    print("=" * 60)
    print("🚀 ENHANCED SKOOL CONTENT EXTRACTION - HIERARCHICAL")
    print("=" * 60)
    print(f"🌐 Community (URL): {community}")
    print(f"📚 Section: {section}")
    print(f"🎯 Target URL: {args.url}")
    
    # Setup organized directories (will be updated with actual community name later)
    print("📁 Setting up organized directories...")
    # Initialize with URL slug, will be updated with clean name later
    temp_community_name = community.replace('-', ' ').title()
    output_dirs = create_organized_directories(temp_community_name, community)
    
    # Setup driver
    print("🌐 Initializing web driver...")
    driver = setup_driver()
    
    try:
        # Login to Skool
        print("\n🔐 Logging into Skool...")
        if not login_to_skool(driver, args.email, args.password):
            print("❌ Login failed. Exiting.")
            return
        
        # Navigate to collection
        print(f"\n🎯 Navigating to collection: {args.url}")
        driver.get(args.url)
        time.sleep(5)
        
        # Extract the clean community name
        print("\n🏷️ Extracting clean community name...")
        community_display_name = extract_clean_community_name(driver)
        if community_display_name:
            print(f"✅ Clean Community Name: {community_display_name}")
        else:
            print("⚠️ Using URL slug as fallback community name")
            community_display_name = community.replace('-', ' ').title()  # Convert slug to readable name
        
        # Extract all lesson data
        lesson_data = extract_all_lesson_data(driver)
        
        if not lesson_data:
            print("❌ No lessons found in collection. Exiting.")
            return
            
        # Process lessons using direct URLs
        processed_count, failed_lessons, skipped_count = process_lessons_with_direct_urls(driver, lesson_data, output_dirs, args.url, community_display_name, args.download_videos)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 EXTRACTION SUMMARY")
        print("=" * 60)
        print(f"✅ Successfully processed: {processed_count} lessons")
        print(f"⏭️  Skipped (already extracted): {skipped_count} lessons")
        print(f"❌ Failed to process: {len(failed_lessons)} lessons")
        print(f"🎯 Total lessons detected: {len(lesson_data)} lessons")
        
        if failed_lessons:
            print(f"\n❌ Failed lessons:")
            for lesson in failed_lessons:
                print(f"  - {lesson}")
        
        folder_name = f"{community_display_name} ({community})" if community_display_name else f"Unknown Community ({community})"
        print(f"\n📁 Output directory: Communities/{folder_name}/lessons/")
        print(f"🗂️  Community structure: Communities/{folder_name}/")
        print("🎉 Organized extraction complete!")
        
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
    finally:
        print("\n📊 Saving extraction debug logs and analyzing patterns...")
        try:
            save_extraction_debug_log()
            analyze_duplicate_patterns()
            print_session_statistics()
            print_browser_isolation_statistics()
            save_session_tracking_report()
        except Exception as debug_error:
            print(f"⚠️ Debug analysis failed: {debug_error}")
        
        print("\n🔒 Closing browser...")
        driver.quit()

def offer_cleanup():
    """Offer cleanup option before starting extraction"""
    try:
        from pathlib import Path
        communities_dir = Path.cwd() / "Communities"
        
        if communities_dir.exists():
            existing_communities = [d.name for d in communities_dir.iterdir() if d.is_dir()]
            if existing_communities:
                print(f"\n🧹 CLEANUP OPTION:")
                print(f"Found {len(existing_communities)} existing community folders:")
                for i, name in enumerate(existing_communities[:5], 1):
                    print(f"   {i}. {name}")
                if len(existing_communities) > 5:
                    print(f"   ... and {len(existing_communities) - 5} more")
                
                print("\nOptions:")
                print("1. Continue without cleanup (may cause conflicts)")
                print("2. Run cleanup tool first (recommended)")
                print("3. Exit and run cleanup manually")
                
                while True:
                    choice = input("\n👉 Select option (1-3): ").strip()
                    if choice == '1':
                        print("⚠️  Continuing without cleanup - watch for conflicts!")
                        return True
                    elif choice == '2':
                        print("🧹 Starting cleanup tool...")
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