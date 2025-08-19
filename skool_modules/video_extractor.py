"""
Video Extraction Module
=======================

Provides comprehensive video URL extraction functionality for the Skool scraper.
Includes multiple extraction methods, validation, and testing capabilities.
"""

import re
import json
import time
import urllib.parse
from typing import Dict, Any, Optional, List, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .logger import get_logger, log_video, log_extraction_attempt
from .error_handler import (
    error_handler, ErrorCategory, ErrorSeverity, ExtractionError,
    ValidationError, TimeoutError
)
from .config_manager import get_config

class VideoExtractor:
    """Comprehensive video extraction system"""
    
    def __init__(self):
        self.logger = get_logger()
        self.extraction_stats = {
            'total_attempts': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'method_usage': {},
            'platform_usage': {}
        }
        
        # Video platform patterns
        self.platform_patterns = {
            'youtube': [
                r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
                r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
                r'(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})'
            ],
            'vimeo': [
                r'(?:https?://)?(?:www\.)?vimeo\.com/(\d+)',
                r'(?:https?://)?(?:www\.)?vimeo\.com/embed/(\d+)'
            ],
            'loom': [
                r'(?:https?://)?(?:www\.)?loom\.com/share/([a-zA-Z0-9_-]+)',
                r'(?:https?://)?(?:www\.)?loom\.com/embed/([a-zA-Z0-9_-]+)'
            ],
            'wistia': [
                r'(?:https?://)?(?:www\.)?wistia\.com/medias/([a-zA-Z0-9_-]+)',
                r'(?:https?://)?(?:www\.)?wistia\.com/embed/([a-zA-Z0-9_-]+)'
            ]
        }
        
        # Video blacklist
        self.video_blacklist = get_config('VIDEO_BLACKLIST', [])
        self.cached_video_blacklist = get_config('CACHED_VIDEO_BLACKLIST', [])
    
    @error_handler(category=ErrorCategory.EXTRACTION, severity=ErrorSeverity.MEDIUM)
    def extract_video_url(self, driver: webdriver.Chrome, lesson_title: str) -> Optional[str]:
        """Extract video URL using multiple methods"""
        
        self.extraction_stats['total_attempts'] += 1
        self.logger.video(f"Starting video extraction for: {lesson_title}")
        
        # Method 1: JSON data extraction
        video_url = self._extract_from_json_data(driver, lesson_title)
        if video_url:
            return self._validate_and_normalize_url(video_url, lesson_title, "json")
        
        # Method 2: Iframe scanning
        video_url = self._extract_from_iframes(driver, lesson_title)
        if video_url:
            return self._validate_and_normalize_url(video_url, lesson_title, "iframe")
        
        # Method 3: Direct video player clicking
        video_url = self._extract_from_video_player(driver, lesson_title)
        if video_url:
            return self._validate_and_normalize_url(video_url, lesson_title, "click")
        
        # Method 4: Network log inspection
        video_url = self._extract_from_network_logs(driver, lesson_title)
        if video_url:
            return self._validate_and_normalize_url(video_url, lesson_title, "network")
        
        # Method 5: Legacy YouTube extraction
        video_url = self._extract_legacy_youtube(driver, lesson_title)
        if video_url:
            return self._validate_and_normalize_url(video_url, lesson_title, "legacy")
        
        self.extraction_stats['failed_extractions'] += 1
        self.logger.warning(f"No video found for lesson: {lesson_title}")
        return None
    
    def _extract_from_json_data(self, driver: webdriver.Chrome, lesson_title: str) -> Optional[str]:
        """Extract video URL from __NEXT_DATA__ JSON"""
        
        try:
            # Look for __NEXT_DATA__ script
            next_data_script = driver.find_element(By.ID, "__NEXT_DATA__")
            if next_data_script:
                json_data = json.loads(next_data_script.get_attribute("innerHTML"))
                
                # Navigate through JSON structure to find video URLs
                video_url = self._find_video_in_json(json_data)
                if video_url:
                    self.logger.video(f"Found video in JSON data: {video_url}")
                    return video_url
                    
        except (NoSuchElementException, json.JSONDecodeError, KeyError) as e:
            self.logger.debug(f"JSON extraction failed: {e}")
        
        return None
    
    def _find_video_in_json(self, data: Any, path: str = "") -> Optional[str]:
        """Recursively search JSON data for video URLs"""
        
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                # Check if this key might contain video data
                if any(video_key in key.lower() for video_key in ['video', 'media', 'url', 'src']):
                    if isinstance(value, str) and self._is_video_url(value):
                        return value
                
                # Recursively search nested structures
                result = self._find_video_in_json(value, current_path)
                if result:
                    return result
                    
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                result = self._find_video_in_json(item, current_path)
                if result:
                    return result
        
        return None
    
    def _extract_from_iframes(self, driver: webdriver.Chrome, lesson_title: str) -> Optional[str]:
        """Extract video URL from iframe elements"""
        
        try:
            # Find all iframe elements
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            
            for iframe in iframes:
                try:
                    src = iframe.get_attribute("src")
                    if src and self._is_video_url(src):
                        self.logger.video(f"Found video in iframe: {src}")
                        return src
                        
                    # Check iframe content for video elements
                    driver.switch_to.frame(iframe)
                    video_elements = driver.find_elements(By.TAG_NAME, "video")
                    
                    for video in video_elements:
                        src = video.get_attribute("src")
                        if src and self._is_video_url(src):
                            driver.switch_to.default_content()
                            self.logger.video(f"Found video in iframe video element: {src}")
                            return src
                    
                    driver.switch_to.default_content()
                    
                except Exception as e:
                    driver.switch_to.default_content()
                    self.logger.debug(f"Iframe extraction error: {e}")
                    
        except Exception as e:
            self.logger.debug(f"Iframe scanning failed: {e}")
        
        return None
    
    def _extract_from_video_player(self, driver: webdriver.Chrome, lesson_title: str) -> Optional[str]:
        """Extract video URL by clicking video player elements"""
        
        try:
            # Look for video player elements
            video_selectors = [
                "video",
                "[data-video]",
                ".video-player",
                ".media-player",
                "[class*='video']",
                "[class*='player']"
            ]
            
            for selector in video_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        # Try to get video URL from various attributes
                        for attr in ['src', 'data-src', 'data-video', 'data-url']:
                            url = element.get_attribute(attr)
                            if url and self._is_video_url(url):
                                self.logger.video(f"Found video in player element: {url}")
                                return url
                        
                        # Try clicking the element to trigger video loading
                        try:
                            element.click()
                            time.sleep(2)  # Wait for video to load
                            
                            # Check if video URL appeared after clicking
                            video_elements = driver.find_elements(By.TAG_NAME, "video")
                            for video in video_elements:
                                src = video.get_attribute("src")
                                if src and self._is_video_url(src):
                                    self.logger.video(f"Found video after clicking: {src}")
                                    return src
                                    
                        except Exception as e:
                            self.logger.debug(f"Click extraction error: {e}")
                            
                except Exception as e:
                    self.logger.debug(f"Video player extraction error: {e}")
                    
        except Exception as e:
            self.logger.debug(f"Video player extraction failed: {e}")
        
        return None
    
    def _extract_from_network_logs(self, driver: webdriver.Chrome, lesson_title: str) -> Optional[str]:
        """Extract video URL from browser network logs"""
        
        try:
            # Get performance logs
            logs = driver.get_log('performance')
            
            for log in logs:
                try:
                    message = json.loads(log['message'])
                    
                    if 'message' in message and message['message']['method'] == 'Network.responseReceived':
                        response = message['message']['params']['response']
                        url = response.get('url', '')
                        
                        if self._is_video_url(url):
                            self.logger.video(f"Found video in network log: {url}")
                            return url
                            
                except (json.JSONDecodeError, KeyError):
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Network log extraction failed: {e}")
        
        return None
    
    def _extract_legacy_youtube(self, driver: webdriver.Chrome, lesson_title: str) -> Optional[str]:
        """Legacy YouTube video extraction method"""
        
        try:
            # Look for YouTube embed patterns in page source
            page_source = driver.page_source
            
            # YouTube video ID patterns
            youtube_patterns = [
                r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
                r'youtu\.be/([a-zA-Z0-9_-]{11})',
                r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
                r'youtube\.com/v/([a-zA-Z0-9_-]{11})'
            ]
            
            for pattern in youtube_patterns:
                matches = re.findall(pattern, page_source)
                if matches:
                    video_id = matches[0]
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    self.logger.video(f"Found YouTube video: {video_url}")
                    return video_url
                    
        except Exception as e:
            self.logger.debug(f"Legacy YouTube extraction failed: {e}")
        
        return None
    
    def _is_video_url(self, url: str) -> bool:
        """Check if URL is a valid video URL"""
        
        if not url or not isinstance(url, str):
            return False
        
        # Check against blacklists
        if url in self.video_blacklist or url in self.cached_video_blacklist:
            return False
        
        # Check for video platform patterns
        for platform, patterns in self.platform_patterns.items():
            for pattern in patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    return True
        
        # Check for video file extensions
        video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv']
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path.lower()
        
        return any(path.endswith(ext) for ext in video_extensions)
    
    def _validate_and_normalize_url(self, video_url: str, lesson_title: str, method: str) -> Optional[str]:
        """Validate and normalize video URL"""
        
        if not video_url:
            return None
        
        # Update statistics
        self.extraction_stats['successful_extractions'] += 1
        self.extraction_stats['method_usage'][method] = self.extraction_stats['method_usage'].get(method, 0) + 1
        
        # Determine platform
        platform = self._detect_platform(video_url)
        if platform:
            self.extraction_stats['platform_usage'][platform] = self.extraction_stats['platform_usage'].get(platform, 0) + 1
        
        # Normalize URL
        normalized_url = self._normalize_video_url(video_url)
        
        # Log extraction attempt
        log_extraction_attempt(
            method=method,
            lesson_title=lesson_title,
            video_url=normalized_url,
            result_status="success",
            additional_info={
                'platform': platform,
                'original_url': video_url,
                'normalized_url': normalized_url
            }
        )
        
        self.logger.success(f"Video extracted successfully using {method}: {normalized_url}")
        return normalized_url
    
    def _detect_platform(self, url: str) -> Optional[str]:
        """Detect video platform from URL"""
        
        for platform, patterns in self.platform_patterns.items():
            for pattern in patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    return platform
        
        return None
    
    def _normalize_video_url(self, url: str) -> str:
        """Normalize video URL to canonical format"""
        
        # YouTube normalization
        youtube_patterns = [
            (r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})', r'https://www.youtube.com/watch?v=\1'),
            (r'youtu\.be/([a-zA-Z0-9_-]{11})', r'https://www.youtube.com/watch?v=\1'),
            (r'youtube\.com/embed/([a-zA-Z0-9_-]{11})', r'https://www.youtube.com/watch?v=\1'),
            (r'youtube\.com/v/([a-zA-Z0-9_-]{11})', r'https://www.youtube.com/watch?v=\1')
        ]
        
        for pattern, replacement in youtube_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return re.sub(pattern, replacement, url, flags=re.IGNORECASE)
        
        # Vimeo normalization
        vimeo_patterns = [
            (r'vimeo\.com/(\d+)', r'https://www.vimeo.com/\1'),
            (r'vimeo\.com/embed/(\d+)', r'https://www.vimeo.com/\1')
        ]
        
        for pattern, replacement in vimeo_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return re.sub(pattern, replacement, url, flags=re.IGNORECASE)
        
        # Loom normalization
        loom_patterns = [
            (r'loom\.com/share/([a-zA-Z0-9_-]+)', r'https://www.loom.com/share/\1'),
            (r'loom\.com/embed/([a-zA-Z0-9_-]+)', r'https://www.loom.com/share/\1')
        ]
        
        for pattern, replacement in loom_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return re.sub(pattern, replacement, url, flags=re.IGNORECASE)
        
        # Wistia normalization
        wistia_patterns = [
            (r'wistia\.com/medias/([a-zA-Z0-9_-]+)', r'https://www.wistia.com/medias/\1'),
            (r'wistia\.com/embed/([a-zA-Z0-9_-]+)', r'https://www.wistia.com/medias/\1')
        ]
        
        for pattern, replacement in wistia_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return re.sub(pattern, replacement, url, flags=re.IGNORECASE)
        
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            return f"https://{url}"
        
        return url
    
    def get_extraction_statistics(self) -> Dict[str, Any]:
        """Get video extraction statistics"""
        return self.extraction_stats.copy()
    
    def print_extraction_statistics(self):
        """Print video extraction statistics"""
        
        stats = self.get_extraction_statistics()
        
        self.logger.info("=== VIDEO EXTRACTION STATISTICS ===")
        self.logger.info(f"Total Attempts: {stats['total_attempts']}")
        self.logger.info(f"Successful Extractions: {stats['successful_extractions']}")
        self.logger.info(f"Failed Extractions: {stats['failed_extractions']}")
        
        if stats['total_attempts'] > 0:
            success_rate = (stats['successful_extractions'] / stats['total_attempts']) * 100
            self.logger.info(f"Success Rate: {success_rate:.1f}%")
        
        self.logger.info("Method Usage:")
        for method, count in stats['method_usage'].items():
            self.logger.info(f"  {method}: {count}")
        
        self.logger.info("Platform Usage:")
        for platform, count in stats['platform_usage'].items():
            self.logger.info(f"  {platform}: {count}")
        
        self.logger.info("=" * 40)

# Global video extractor instance
_video_extractor = None

def get_video_extractor() -> VideoExtractor:
    """Get or create the global video extractor instance"""
    global _video_extractor
    if _video_extractor is None:
        _video_extractor = VideoExtractor()
    return _video_extractor

def extract_video_url(driver: webdriver.Chrome, lesson_title: str) -> Optional[str]:
    """Extract video URL using the global video extractor"""
    return get_video_extractor().extract_video_url(driver, lesson_title)

def get_extraction_statistics() -> Dict[str, Any]:
    """Get video extraction statistics"""
    return get_video_extractor().get_extraction_statistics()

def print_extraction_statistics():
    """Print video extraction statistics"""
    get_video_extractor().print_extraction_statistics()
