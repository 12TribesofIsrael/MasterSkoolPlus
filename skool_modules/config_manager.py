"""
Configuration Management Module
==============================

Handles all configuration, environment variables, constants, and settings
for the Skool Content Extractor.
"""

import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ConfigManager:
    """Manages all configuration settings for the Skool scraper"""
    
    def __init__(self):
        self.config = {}
        self.load_configuration()
    
    def load_configuration(self):
        """Load all configuration from environment and defaults"""
        
        # Core settings
        self.config.update({
            'SKOOL_EMAIL': os.getenv('SKOOL_EMAIL', ''),
            'SKOOL_PASSWORD': os.getenv('SKOOL_PASSWORD', ''),
            'SKOOL_BASE_URL': os.getenv('SKOOL_BASE_URL', 'https://app.skool.com'),
            'DOWNLOAD_VIDEOS': os.getenv('DOWNLOAD_VIDEOS', 'false').lower() == 'true',
            'HEADLESS_MODE': os.getenv('HEADLESS_MODE', 'false').lower() == 'true',
            'BROWSER_TIMEOUT': int(os.getenv('BROWSER_TIMEOUT', '30')),
            'PAGE_LOAD_TIMEOUT': int(os.getenv('PAGE_LOAD_TIMEOUT', '10')),
            'RETRY_ATTEMPTS': int(os.getenv('RETRY_ATTEMPTS', '3')),
            'DELAY_BETWEEN_REQUESTS': float(os.getenv('DELAY_BETWEEN_REQUESTS', '2.0')),
        })
        
        # Video extraction settings
        self.config.update({
            'VIDEO_EXTRACTION_METHODS': [
                'modal', 'json', 'click', 'iframe', 'network', 'legacy'
            ],
            'SUPPORTED_VIDEO_PLATFORMS': [
                'youtube', 'vimeo', 'loom', 'wistia', 'unknown'
            ],
            'VIDEO_BLACKLIST': self._load_video_blacklist(),
            'CACHED_VIDEO_BLACKLIST': [
                'https://youtu.be/65GvYDdzJWU'  # Known duplicate
            ]
        })
        
        # Browser isolation settings
        self.config.update({
            'BROWSER_ISOLATION_ENABLED': os.getenv('BROWSER_ISOLATION_ENABLED', 'true').lower() == 'true',
            'ISOLATION_FREQUENCY': int(os.getenv('ISOLATION_FREQUENCY', '5')),  # Every 5th lesson
            'MAX_SHARED_LESSONS': int(os.getenv('MAX_SHARED_LESSONS', '10')),
            'PROBLEMATIC_LESSON_KEYWORDS': [
                'introduction', 'welcome', 'overview', 'getting started',
                'basics', 'fundamentals'
            ]
        })
        
        # Output settings
        self.config.update({
            'OUTPUT_DIR': os.getenv('OUTPUT_DIR', 'Communities'),
            'CREATE_HIERARCHY': os.getenv('CREATE_HIERARCHY', 'true').lower() == 'true',
            'SAVE_DEBUG_LOGS': os.getenv('SAVE_DEBUG_LOGS', 'true').lower() == 'true',
            'DEBUG_LOG_DIR': os.getenv('DEBUG_LOG_DIR', 'debug_logs'),
        })
        
        # Validation settings
        self.config.update({
            'LESSON_VALIDATION_ENABLED': os.getenv('LESSON_VALIDATION_ENABLED', 'true').lower() == 'true',
            'SESSION_TRACKING_ENABLED': os.getenv('SESSION_TRACKING_ENABLED', 'true').lower() == 'true',
            'CONTENT_SIGNATURE_ENABLED': os.getenv('CONTENT_SIGNATURE_ENABLED', 'true').lower() == 'true',
        })
    
    def _load_video_blacklist(self) -> list:
        """Load video blacklist from file or return default"""
        try:
            if os.path.exists('video_blacklist.json'):
                with open('video_blacklist.json', 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return []
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a configuration value"""
        self.config[key] = value
    
    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values"""
        self.config.update(updates)
    
    def validate_credentials(self) -> bool:
        """Validate that required credentials are present"""
        email = self.get('SKOOL_EMAIL')
        password = self.get('SKOOL_PASSWORD')
        
        if not email or not password:
            print("❌ Missing credentials. Please set SKOOL_EMAIL and SKOOL_PASSWORD in .env file")
            return False
        
        return True
    
    def get_browser_options(self) -> Dict[str, Any]:
        """Get browser configuration options"""
        return {
            'headless': self.get('HEADLESS_MODE', False),
            'timeout': self.get('BROWSER_TIMEOUT', 30),
            'page_load_timeout': self.get('PAGE_LOAD_TIMEOUT', 10),
            'retry_attempts': self.get('RETRY_ATTEMPTS', 3),
            'delay_between_requests': self.get('DELAY_BETWEEN_REQUESTS', 2.0)
        }
    
    def get_video_extraction_config(self) -> Dict[str, Any]:
        """Get video extraction configuration"""
        return {
            'methods': self.get('VIDEO_EXTRACTION_METHODS', []),
            'platforms': self.get('SUPPORTED_VIDEO_PLATFORMS', []),
            'blacklist': self.get('VIDEO_BLACKLIST', []),
            'cached_blacklist': self.get('CACHED_VIDEO_BLACKLIST', [])
        }
    
    def get_isolation_config(self) -> Dict[str, Any]:
        """Get browser isolation configuration"""
        return {
            'enabled': self.get('BROWSER_ISOLATION_ENABLED', True),
            'frequency': self.get('ISOLATION_FREQUENCY', 5),
            'max_shared_lessons': self.get('MAX_SHARED_LESSONS', 10),
            'problematic_keywords': self.get('PROBLEMATIC_LESSON_KEYWORDS', [])
        }
    
    def print_configuration(self):
        """Print current configuration (without sensitive data)"""
        print("\n📋 Current Configuration:")
        print("=" * 50)
        
        safe_config = {k: v for k, v in self.config.items() 
                      if 'PASSWORD' not in k.upper() and 'EMAIL' not in k.upper()}
        
        for key, value in safe_config.items():
            if isinstance(value, list):
                print(f"  {key}: {len(value)} items")
            else:
                print(f"  {key}: {value}")
        
        print("=" * 50)

# Global configuration instance
config = ConfigManager()

# Convenience functions
def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value"""
    return config.get(key, default)

def set_config(key: str, value: Any):
    """Set configuration value"""
    config.set(key, value)

def validate_credentials() -> bool:
    """Validate credentials"""
    return config.validate_credentials()

def print_config():
    """Print configuration"""
    config.print_configuration()
