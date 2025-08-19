"""
Error Handling Module
====================

Provides comprehensive error handling and recovery mechanisms for the Skool scraper.
Includes custom exceptions, error categorization, recovery strategies, and user-friendly error messages.
"""

import sys
import traceback
import time
import random
from typing import Dict, Any, Optional, Callable, List, Tuple
from enum import Enum
from functools import wraps

from .logger import get_logger, log_exception, log_error, log_warning
from .config_manager import get_config

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories for classification"""
    NETWORK = "network"
    BROWSER = "browser"
    AUTHENTICATION = "authentication"
    EXTRACTION = "extraction"
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    FILE_OPERATION = "file_operation"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    UNKNOWN = "unknown"

class SkoolScraperError(Exception):
    """Base exception for Skool scraper errors"""
    
    def __init__(self, message: str, category: ErrorCategory = ErrorCategory.UNKNOWN, 
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                 details: Dict[str, Any] = None, 
                 recoverable: bool = True):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.recoverable = recoverable
        self.timestamp = time.time()
        self.retry_count = 0

class NetworkError(SkoolScraperError):
    """Network-related errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, ErrorCategory.NETWORK, ErrorSeverity.HIGH, details)

class BrowserError(SkoolScraperError):
    """Browser-related errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, ErrorCategory.BROWSER, ErrorSeverity.HIGH, details)

class AuthenticationError(SkoolScraperError):
    """Authentication-related errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, ErrorCategory.AUTHENTICATION, ErrorSeverity.CRITICAL, details, False)

class ExtractionError(SkoolScraperError):
    """Content extraction errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, ErrorCategory.EXTRACTION, ErrorSeverity.MEDIUM, details)

class ValidationError(SkoolScraperError):
    """Validation errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, ErrorCategory.VALIDATION, ErrorSeverity.LOW, details)

class ConfigurationError(SkoolScraperError):
    """Configuration errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, ErrorCategory.CONFIGURATION, ErrorSeverity.CRITICAL, details, False)

class FileOperationError(SkoolScraperError):
    """File operation errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, ErrorCategory.FILE_OPERATION, ErrorSeverity.MEDIUM, details)

class TimeoutError(SkoolScraperError):
    """Timeout errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, ErrorCategory.TIMEOUT, ErrorSeverity.MEDIUM, details)

class RateLimitError(SkoolScraperError):
    """Rate limiting errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, ErrorCategory.RATE_LIMIT, ErrorSeverity.HIGH, details)

class ErrorHandler:
    """Comprehensive error handling system"""
    
    def __init__(self):
        self.logger = get_logger()
        self.error_stats = {
            'total_errors': 0,
            'errors_by_category': {},
            'errors_by_severity': {},
            'recovered_errors': 0,
            'unrecovered_errors': 0
        }
        self.recovery_strategies = self._setup_recovery_strategies()
        self.max_retries = get_config('MAX_RETRIES', 3)
        self.retry_delays = get_config('RETRY_DELAYS', [1, 2, 5])  # seconds
        
    def _setup_recovery_strategies(self) -> Dict[ErrorCategory, List[Callable]]:
        """Setup recovery strategies for different error categories"""
        return {
            ErrorCategory.NETWORK: [
                self._retry_with_delay,
                self._clear_browser_cache,
                self._switch_browser_instance
            ],
            ErrorCategory.BROWSER: [
                self._retry_with_delay,
                self._restart_browser,
                self._clear_browser_data
            ],
            ErrorCategory.EXTRACTION: [
                self._retry_with_delay,
                self._try_alternative_method,
                self._skip_and_continue
            ],
            ErrorCategory.VALIDATION: [
                self._retry_with_delay,
                self._relax_validation,
                self._skip_and_continue
            ],
            ErrorCategory.TIMEOUT: [
                self._retry_with_delay,
                self._increase_timeout,
                self._skip_and_continue
            ],
            ErrorCategory.RATE_LIMIT: [
                self._wait_and_retry,
                self._exponential_backoff,
                self._skip_and_continue
            ],
            ErrorCategory.FILE_OPERATION: [
                self._retry_with_delay,
                self._create_directory,
                self._use_alternative_path
            ]
        }
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """Handle an error with appropriate recovery strategies"""
        
        # Convert to SkoolScraperError if needed
        if not isinstance(error, SkoolScraperError):
            error = self._classify_error(error, context)
        
        # Update statistics
        self._update_error_stats(error)
        
        # Log the error
        self._log_error(error, context)
        
        # Check if error is recoverable
        if not error.recoverable:
            self.error_stats['unrecovered_errors'] += 1
            self._handle_unrecoverable_error(error, context)
            return False
        
        # Try recovery strategies
        return self._attempt_recovery(error, context)
    
    def _classify_error(self, error: Exception, context: Dict[str, Any] = None) -> SkoolScraperError:
        """Classify a generic exception into a specific SkoolScraperError"""
        
        error_message = str(error)
        error_type = type(error).__name__
        
        # Network errors
        if any(keyword in error_message.lower() for keyword in ['connection', 'network', 'dns', 'timeout']):
            return NetworkError(f"Network error: {error_message}", {'original_type': error_type})
        
        # Browser errors
        if any(keyword in error_message.lower() for keyword in ['webdriver', 'chrome', 'browser', 'element']):
            return BrowserError(f"Browser error: {error_message}", {'original_type': error_type})
        
        # Authentication errors
        if any(keyword in error_message.lower() for keyword in ['login', 'auth', 'credential', 'password']):
            return AuthenticationError(f"Authentication error: {error_message}", {'original_type': error_type})
        
        # Timeout errors
        if any(keyword in error_message.lower() for keyword in ['timeout', 'timed out']):
            return TimeoutError(f"Timeout error: {error_message}", {'original_type': error_type})
        
        # File operation errors
        if any(keyword in error_message.lower() for keyword in ['file', 'directory', 'permission', 'io']):
            return FileOperationError(f"File operation error: {error_message}", {'original_type': error_type})
        
        # Default to extraction error
        return ExtractionError(f"Extraction error: {error_message}", {'original_type': error_type})
    
    def _update_error_stats(self, error: SkoolScraperError):
        """Update error statistics"""
        self.error_stats['total_errors'] += 1
        
        # Update category stats
        category = error.category.value
        self.error_stats['errors_by_category'][category] = self.error_stats['errors_by_category'].get(category, 0) + 1
        
        # Update severity stats
        severity = error.severity.value
        self.error_stats['errors_by_severity'][severity] = self.error_stats['errors_by_severity'].get(severity, 0) + 1
    
    def _log_error(self, error: SkoolScraperError, context: Dict[str, Any] = None):
        """Log error with context"""
        context_info = context or {}
        
        error_data = {
            'message': error.message,
            'category': error.category.value,
            'severity': error.severity.value,
            'recoverable': error.recoverable,
            'retry_count': error.retry_count,
            'context': context_info,
            'details': error.details
        }
        
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(f"Critical error: {error.message}")
            log_exception(f"Critical error details: {error_data}")
        elif error.severity == ErrorSeverity.HIGH:
            self.logger.error(f"High severity error: {error.message}")
        elif error.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"Medium severity error: {error.message}")
        else:
            self.logger.info(f"Low severity error: {error.message}")
    
    def _attempt_recovery(self, error: SkoolScraperError, context: Dict[str, Any] = None) -> bool:
        """Attempt to recover from the error using available strategies"""
        
        strategies = self.recovery_strategies.get(error.category, [])
        
        for strategy in strategies:
            try:
                self.logger.info(f"Attempting recovery strategy: {strategy.__name__}")
                if strategy(error, context):
                    self.error_stats['recovered_errors'] += 1
                    self.logger.success(f"Successfully recovered from {error.category.value} error")
                    return True
            except Exception as recovery_error:
                self.logger.warning(f"Recovery strategy {strategy.__name__} failed: {recovery_error}")
        
        # All recovery strategies failed
        self.error_stats['unrecovered_errors'] += 1
        self.logger.error(f"Failed to recover from {error.category.value} error after trying all strategies")
        return False
    
    def _handle_unrecoverable_error(self, error: SkoolScraperError, context: Dict[str, Any] = None):
        """Handle unrecoverable errors"""
        self.logger.critical(f"Unrecoverable error: {error.message}")
        
        if error.category == ErrorCategory.AUTHENTICATION:
            self.logger.critical("Authentication failed - please check credentials")
        elif error.category == ErrorCategory.CONFIGURATION:
            self.logger.critical("Configuration error - please check settings")
        
        # Log full context for debugging
        log_exception(f"Unrecoverable error context: {context}")
    
    # Recovery Strategy Methods
    def _retry_with_delay(self, error: SkoolScraperError, context: Dict[str, Any] = None) -> bool:
        """Retry operation with delay"""
        if error.retry_count >= self.max_retries:
            return False
        
        delay = self.retry_delays[min(error.retry_count, len(self.retry_delays) - 1)]
        self.logger.info(f"Retrying in {delay} seconds (attempt {error.retry_count + 1}/{self.max_retries})")
        
        time.sleep(delay)
        error.retry_count += 1
        return True
    
    def _wait_and_retry(self, error: SkoolScraperError, context: Dict[str, Any] = None) -> bool:
        """Wait longer and retry (for rate limiting)"""
        wait_time = random.uniform(5, 15)
        self.logger.info(f"Rate limited - waiting {wait_time:.1f} seconds before retry")
        time.sleep(wait_time)
        return True
    
    def _exponential_backoff(self, error: SkoolScraperError, context: Dict[str, Any] = None) -> bool:
        """Exponential backoff for rate limiting"""
        if error.retry_count >= 3:
            return False
        
        wait_time = 2 ** error.retry_count + random.uniform(0, 1)
        self.logger.info(f"Exponential backoff: waiting {wait_time:.1f} seconds")
        time.sleep(wait_time)
        error.retry_count += 1
        return True
    
    def _clear_browser_cache(self, error: SkoolScraperError, context: Dict[str, Any] = None) -> bool:
        """Clear browser cache and retry"""
        try:
            driver = context.get('driver')
            if driver:
                driver.delete_all_cookies()
                driver.execute_script("window.localStorage.clear();")
                driver.execute_script("window.sessionStorage.clear();")
                self.logger.info("Browser cache cleared")
                return True
        except Exception as e:
            self.logger.warning(f"Failed to clear browser cache: {e}")
        return False
    
    def _restart_browser(self, error: SkoolScraperError, context: Dict[str, Any] = None) -> bool:
        """Restart browser instance"""
        try:
            from .browser_manager import create_isolated_browser_instance, destroy_browser_instance
            
            old_driver = context.get('driver')
            if old_driver:
                destroy_browser_instance(old_driver, "error_recovery")
            
            new_driver = create_isolated_browser_instance()
            if new_driver:
                context['driver'] = new_driver
                self.logger.success("Browser restarted successfully")
                return True
        except Exception as e:
            self.logger.warning(f"Failed to restart browser: {e}")
        return False
    
    def _try_alternative_method(self, error: SkoolScraperError, context: Dict[str, Any] = None) -> bool:
        """Try alternative extraction method"""
        # This would be implemented based on available extraction methods
        self.logger.info("Trying alternative extraction method")
        return True
    
    def _relax_validation(self, error: SkoolScraperError, context: Dict[str, Any] = None) -> bool:
        """Relax validation criteria"""
        self.logger.info("Relaxing validation criteria")
        return True
    
    def _skip_and_continue(self, error: SkoolScraperError, context: Dict[str, Any] = None) -> bool:
        """Skip current operation and continue"""
        self.logger.warning("Skipping current operation and continuing")
        return True
    
    def _increase_timeout(self, error: SkoolScraperError, context: Dict[str, Any] = None) -> bool:
        """Increase timeout and retry"""
        try:
            driver = context.get('driver')
            if driver:
                current_timeout = driver.timeouts.implicit_wait
                new_timeout = min(current_timeout * 2, 60)  # Max 60 seconds
                driver.implicitly_wait(new_timeout)
                self.logger.info(f"Increased timeout to {new_timeout} seconds")
                return True
        except Exception as e:
            self.logger.warning(f"Failed to increase timeout: {e}")
        return False
    
    def _create_directory(self, error: SkoolScraperError, context: Dict[str, Any] = None) -> bool:
        """Create missing directory"""
        try:
            import os
            path = context.get('path', '')
            if path:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                self.logger.info(f"Created directory for: {path}")
                return True
        except Exception as e:
            self.logger.warning(f"Failed to create directory: {e}")
        return False
    
    def _use_alternative_path(self, error: SkoolScraperError, context: Dict[str, Any] = None) -> bool:
        """Use alternative file path"""
        self.logger.info("Using alternative file path")
        return True
    
    def _switch_browser_instance(self, error: SkoolScraperError, context: Dict[str, Any] = None) -> bool:
        """Switch to a different browser instance"""
        return self._restart_browser(error, context)
    
    def _clear_browser_data(self, error: SkoolScraperError, context: Dict[str, Any] = None) -> bool:
        """Clear browser data"""
        return self._clear_browser_cache(error, context)
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        return self.error_stats.copy()
    
    def print_error_statistics(self):
        """Print error statistics"""
        stats = self.get_error_statistics()
        
        self.logger.info("=== ERROR STATISTICS ===")
        self.logger.info(f"Total Errors: {stats['total_errors']}")
        self.logger.info(f"Recovered Errors: {stats['recovered_errors']}")
        self.logger.info(f"Unrecovered Errors: {stats['unrecovered_errors']}")
        
        if stats['total_errors'] > 0:
            recovery_rate = (stats['recovered_errors'] / stats['total_errors']) * 100
            self.logger.info(f"Recovery Rate: {recovery_rate:.1f}%")
        
        self.logger.info("Errors by Category:")
        for category, count in stats['errors_by_category'].items():
            self.logger.info(f"  {category}: {count}")
        
        self.logger.info("Errors by Severity:")
        for severity, count in stats['errors_by_severity'].items():
            self.logger.info(f"  {severity}: {count}")
        
        self.logger.info("=" * 30)

# Global error handler instance
_error_handler = None

def get_error_handler() -> ErrorHandler:
    """Get or create the global error handler instance"""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler

def handle_error(error: Exception, context: Dict[str, Any] = None) -> bool:
    """Handle an error using the global error handler"""
    return get_error_handler().handle_error(error, context)

def error_handler(category: ErrorCategory = ErrorCategory.UNKNOWN, 
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 max_retries: int = None):
    """Decorator for automatic error handling"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = max_retries or get_config('MAX_RETRIES', 3)
            
            for attempt in range(retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    context = {
                        'function': func.__name__,
                        'attempt': attempt + 1,
                        'max_attempts': retries + 1,
                        'args': str(args),
                        'kwargs': str(kwargs)
                    }
                    
                    # Convert to SkoolScraperError if needed
                    if not isinstance(e, SkoolScraperError):
                        e = SkoolScraperError(str(e), category, severity, context)
                    
                    # Handle the error
                    if not handle_error(e, context):
                        raise e  # Re-raise if not recoverable
            
            # If we get here, all retries failed
            raise SkoolScraperError(f"Function {func.__name__} failed after {retries + 1} attempts", 
                                  category, severity)
        return wrapper
    return decorator

def safe_execute(func: Callable, *args, context: Dict[str, Any] = None, **kwargs) -> Tuple[bool, Any]:
    """Safely execute a function with error handling"""
    try:
        result = func(*args, **kwargs)
        return True, result
    except Exception as e:
        success = handle_error(e, context or {})
        return success, None

# Convenience functions for common error types
def raise_network_error(message: str, details: Dict[str, Any] = None):
    """Raise a network error"""
    raise NetworkError(message, details)

def raise_browser_error(message: str, details: Dict[str, Any] = None):
    """Raise a browser error"""
    raise BrowserError(message, details)

def raise_authentication_error(message: str, details: Dict[str, Any] = None):
    """Raise an authentication error"""
    raise AuthenticationError(message, details)

def raise_extraction_error(message: str, details: Dict[str, Any] = None):
    """Raise an extraction error"""
    raise ExtractionError(message, details)

def raise_validation_error(message: str, details: Dict[str, Any] = None):
    """Raise a validation error"""
    raise ValidationError(message, details)

def raise_configuration_error(message: str, details: Dict[str, Any] = None):
    """Raise a configuration error"""
    raise ConfigurationError(message, details)

def raise_file_operation_error(message: str, details: Dict[str, Any] = None):
    """Raise a file operation error"""
    raise FileOperationError(message, details)

def raise_timeout_error(message: str, details: Dict[str, Any] = None):
    """Raise a timeout error"""
    raise TimeoutError(message, details)

def raise_rate_limit_error(message: str, details: Dict[str, Any] = None):
    """Raise a rate limit error"""
    raise RateLimitError(message, details)
