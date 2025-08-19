"""
Logging Framework Module
========================

Provides comprehensive logging functionality for the Skool Content Extractor.
Replaces print statements with structured logging for better debugging and monitoring.
"""

import logging
import os
import sys
import json
import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from .config_manager import get_config

class SkoolLogger:
    """Comprehensive logging system for Skool scraper"""
    
    def __init__(self, name: str = "skool_scraper"):
        self.name = name
        self.logger = None
        self.log_file = None
        self.console_handler = None
        self.file_handler = None
        self.setup_logging()
    
    def setup_logging(self):
        """Setup the logging configuration"""
        
        # Create logger
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Create formatters
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler (INFO level and above)
        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setLevel(logging.INFO)
        self.console_handler.setFormatter(console_formatter)
        self.logger.addHandler(self.console_handler)
        
        # File handler (DEBUG level and above)
        log_dir = get_config('DEBUG_LOG_DIR', 'debug_logs')
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = os.path.join(log_dir, f'skool_scraper_{timestamp}.log')
        
        self.file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        self.file_handler.setLevel(logging.DEBUG)
        self.file_handler.setFormatter(file_formatter)
        self.logger.addHandler(self.file_handler)
        
        # Log startup
        self.info("🚀 Skool Logger initialized")
        self.info(f"📁 Log file: {self.log_file}")
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(f"⚠️ {message}")
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(f"❌ {message}")
    
    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(f"🚨 {message}")
    
    def success(self, message: str):
        """Log success message"""
        self.logger.info(f"✅ {message}")
    
    def progress(self, message: str):
        """Log progress message"""
        self.logger.info(f"📊 {message}")
    
    def browser(self, message: str):
        """Log browser-related message"""
        self.logger.info(f"🌐 {message}")
    
    def video(self, message: str):
        """Log video-related message"""
        self.logger.info(f"🎥 {message}")
    
    def lesson(self, message: str):
        """Log lesson-related message"""
        self.logger.info(f"📚 {message}")
    
    def isolation(self, message: str):
        """Log browser isolation message"""
        self.logger.info(f"🔒 {message}")
    
    def config(self, message: str):
        """Log configuration message"""
        self.logger.info(f"⚙️ {message}")
    
    def session(self, message: str):
        """Log session tracking message"""
        self.logger.info(f"📈 {message}")
    
    def validation(self, message: str):
        """Log validation message"""
        self.logger.info(f"🔍 {message}")
    
    def file_operation(self, message: str):
        """Log file operation message"""
        self.logger.info(f"📁 {message}")
    
    def exception(self, message: str, exc_info: bool = True):
        """Log exception with traceback"""
        self.logger.exception(f"💥 {message}", exc_info=exc_info)
    
    def log_dict(self, data: Dict[str, Any], level: str = "info"):
        """Log dictionary data in a structured format"""
        message = json.dumps(data, indent=2, default=str)
        if level == "debug":
            self.debug(f"Data: {message}")
        elif level == "info":
            self.info(f"Data: {message}")
        elif level == "warning":
            self.warning(f"Data: {message}")
        elif level == "error":
            self.error(f"Data: {message}")
    
    def log_performance(self, operation: str, duration: float, details: Dict[str, Any] = None):
        """Log performance metrics"""
        message = f"Performance | {operation} | {duration:.2f}s"
        if details:
            message += f" | {json.dumps(details, default=str)}"
        self.info(message)
    
    def log_extraction_attempt(self, method: str, lesson_title: str, video_url: str, 
                             result_status: str, additional_info: Dict[str, Any] = None):
        """Log video extraction attempt with structured data"""
        data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'method': method,
            'lesson_title': lesson_title,
            'video_url': video_url,
            'result_status': result_status,
            'additional_info': additional_info or {}
        }
        self.log_dict(data, "debug")
    
    def log_session_event(self, event_type: str, lesson_title: str, video_url: str = None,
                         extraction_method: str = None, platform: str = None):
        """Log session tracking events"""
        data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'event_type': event_type,
            'lesson_title': lesson_title,
            'video_url': video_url,
            'extraction_method': extraction_method,
            'platform': platform
        }
        self.log_dict(data, "debug")
    
    def log_isolation_decision(self, lesson_title: str, lesson_index: int, total_lessons: int,
                             decision: bool, reason: str):
        """Log browser isolation decisions"""
        data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'lesson_title': lesson_title,
            'lesson_index': lesson_index,
            'total_lessons': total_lessons,
            'isolation_decision': decision,
            'reason': reason
        }
        self.log_dict(data, "debug")
    
    def log_validation_result(self, lesson_title: str, video_url: str, validation_type: str,
                            result: bool, details: Dict[str, Any] = None):
        """Log validation results"""
        data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'lesson_title': lesson_title,
            'video_url': video_url,
            'validation_type': validation_type,
            'result': result,
            'details': details or {}
        }
        self.log_dict(data, "debug")
    
    def get_log_file_path(self) -> str:
        """Get the current log file path"""
        return self.log_file
    
    def close(self):
        """Close logging handlers"""
        if self.console_handler:
            self.console_handler.close()
        if self.file_handler:
            self.file_handler.close()
        self.info("🔚 Logger closed")

# Global logger instance
_global_logger = None

def get_logger(name: str = "skool_scraper") -> SkoolLogger:
    """Get or create the global logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = SkoolLogger(name)
    return _global_logger

def setup_logging(name: str = "skool_scraper") -> SkoolLogger:
    """Setup and return a new logger instance"""
    return SkoolLogger(name)

# Convenience functions for backward compatibility
def log_info(message: str):
    """Log info message using global logger"""
    get_logger().info(message)

def log_error(message: str):
    """Log error message using global logger"""
    get_logger().error(message)

def log_warning(message: str):
    """Log warning message using global logger"""
    get_logger().warning(message)

def log_debug(message: str):
    """Log debug message using global logger"""
    get_logger().debug(message)

def log_success(message: str):
    """Log success message using global logger"""
    get_logger().success(message)

def log_progress(message: str):
    """Log progress message using global logger"""
    get_logger().progress(message)

def log_browser(message: str):
    """Log browser message using global logger"""
    get_logger().browser(message)

def log_video(message: str):
    """Log video message using global logger"""
    get_logger().video(message)

def log_lesson(message: str):
    """Log lesson message using global logger"""
    get_logger().lesson(message)

def log_isolation(message: str):
    """Log isolation message using global logger"""
    get_logger().isolation(message)

def log_exception(message: str, exc_info: bool = True):
    """Log exception using global logger"""
    get_logger().exception(message, exc_info)

def log_performance(operation: str, duration: float, details: Dict[str, Any] = None):
    """Log performance metrics using global logger"""
    get_logger().log_performance(operation, duration, details)

def log_extraction_attempt(method: str, lesson_title: str, video_url: str, 
                          result_status: str, additional_info: Dict[str, Any] = None):
    """Log extraction attempt using global logger"""
    get_logger().log_extraction_attempt(method, lesson_title, video_url, result_status, additional_info)

def log_session_event(event_type: str, lesson_title: str, video_url: str = None,
                     extraction_method: str = None, platform: str = None):
    """Log session event using global logger"""
    get_logger().log_session_event(event_type, lesson_title, video_url, extraction_method, platform)

def log_isolation_decision(lesson_title: str, lesson_index: int, total_lessons: int,
                          decision: bool, reason: str):
    """Log isolation decision using global logger"""
    get_logger().log_isolation_decision(lesson_title, lesson_index, total_lessons, decision, reason)

def log_validation_result(lesson_title: str, video_url: str, validation_type: str,
                         result: bool, details: Dict[str, Any] = None):
    """Log validation result using global logger"""
    get_logger().log_validation_result(lesson_title, video_url, validation_type, result, details)
