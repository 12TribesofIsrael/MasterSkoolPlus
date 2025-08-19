"""
Skool Content Extractor - Modular Package
==========================================

A modular implementation of the Skool.com content extraction system.

Modules:
- browser_manager: Browser setup, isolation, and management
- video_extractor: Video URL extraction and validation
- content_extractor: Text and image content extraction
- session_tracker: Session-level tracking and statistics
- lesson_validator: Lesson-specific validation and context
- file_manager: File operations and hierarchical structure
- config_manager: Configuration and environment management
- main_extractor: Main orchestration and workflow
"""

__version__ = "6.0.0"
__author__ = "Skool Scraper Team"

# Import available modules for backward compatibility
from .browser_manager import setup_driver, create_isolated_browser_instance, should_use_browser_isolation
from .config_manager import get_config, set_config, validate_credentials, print_config
from .logger import (
    get_logger, setup_logging, log_info, log_error, log_warning, log_debug,
    log_success, log_progress, log_browser, log_video, log_lesson, log_isolation,
    log_exception, log_performance, log_extraction_attempt, log_session_event,
    log_isolation_decision, log_validation_result
)
from .error_handler import (
    get_error_handler, handle_error, error_handler, safe_execute,
    SkoolScraperError, NetworkError, BrowserError, AuthenticationError,
    ExtractionError, ValidationError, ConfigurationError, FileOperationError,
    TimeoutError, RateLimitError, ErrorCategory, ErrorSeverity,
    raise_network_error, raise_browser_error, raise_authentication_error,
    raise_extraction_error, raise_validation_error, raise_configuration_error,
    raise_file_operation_error, raise_timeout_error, raise_rate_limit_error
)
from .video_extractor import (
    get_video_extractor, extract_video_url, get_extraction_statistics,
    print_extraction_statistics
)

__all__ = [
    'setup_driver',
    'create_isolated_browser_instance',
    'should_use_browser_isolation',
    'get_config',
    'set_config', 
    'validate_credentials',
    'print_config',
    'get_logger',
    'setup_logging',
    'log_info',
    'log_error',
    'log_warning',
    'log_debug',
    'log_success',
    'log_progress',
    'log_browser',
    'log_video',
    'log_lesson',
    'log_isolation',
    'log_exception',
    'log_performance',
    'log_extraction_attempt',
    'log_session_event',
    'log_isolation_decision',
    'log_validation_result',
    'get_error_handler',
    'handle_error',
    'error_handler',
    'safe_execute',
    'SkoolScraperError',
    'NetworkError',
    'BrowserError',
    'AuthenticationError',
    'ExtractionError',
    'ValidationError',
    'ConfigurationError',
    'FileOperationError',
    'TimeoutError',
    'RateLimitError',
    'ErrorCategory',
    'ErrorSeverity',
    'raise_network_error',
    'raise_browser_error',
    'raise_authentication_error',
    'raise_extraction_error',
    'raise_validation_error',
    'raise_configuration_error',
    'raise_file_operation_error',
    'raise_timeout_error',
    'raise_rate_limit_error',
    'get_video_extractor',
    'extract_video_url',
    'get_extraction_statistics',
    'print_extraction_statistics'
]
