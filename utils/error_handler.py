"""
Error handling utilities for Rise of Kingdoms Tool
Provides centralized error handling, retry mechanisms, and error recovery
"""

import logging
import traceback
import time
import config
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Centralized error handling with retry mechanisms"""
    
    def __init__(self, max_retries: int = None, retry_delay: float = None):
        self.max_retries = max_retries or config.MAX_ERROR_RETRIES
        self.retry_delay = retry_delay or config.ERROR_RETRY_DELAY
    
    def retry_operation(self, operation: Callable, *args, **kwargs) -> Optional[Any]:
        """
        Retry an operation with exponential backoff
        
        Args:
            operation: Function to retry
            *args: Arguments for the operation
            **kwargs: Keyword arguments for the operation
            
        Returns:
            Result of the operation if successful, None if all retries failed
        """
        
        for attempt in range(self.max_retries + 1):
            try:
                result = operation(*args, **kwargs)
                if attempt > 0:
                    logger.info(f"Operation succeeded on attempt {attempt + 1}")
                return result
                
            except Exception as e:
                if attempt < self.max_retries:
                    wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Operation failed on attempt {attempt + 1}/{self.max_retries + 1}: {e}")
                    logger.info(f"Retrying in {wait_time:.2f} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Operation failed after {self.max_retries + 1} attempts. Final error: {e}")
        
        return None
    
    def safe_execute(self, operation: Callable, *args, **kwargs) -> Optional[Any]:
        """
        Execute an operation safely with error handling
        
        Args:
            operation: Function to execute
            *args: Arguments for the operation
            **kwargs: Keyword arguments for the operation
            
        Returns:
            Result of the operation if successful, None if failed
        """
        try:
            return operation(*args, **kwargs)
        except Exception as e:
            logger.error(f"Operation failed: {e}")
            logger.error(traceback.format_exc())
            return None
    
    def handle_device_error(self, device_id: str, error: Exception, operation: str) -> bool:
        """
        Handle device-specific errors with recovery attempts
        
        Args:
            device_id: ID of the device that encountered the error
            error: The error that occurred
            operation: Description of the operation that failed
            
        Returns:
            True if error was handled/recovered, False otherwise
        """
        error_msg = f"Device {device_id} error during {operation}: {error}"
        logger.error(error_msg)
        
        # Try to recover based on error type
        if "device not found" in str(error).lower():
            logger.info(f"Attempting to reconnect to device {device_id}")
            # Could implement reconnection logic here
            return False
        elif "timeout" in str(error).lower():
            logger.info(f"Timeout error for device {device_id}, will retry")
            return True
        elif "adb server" in str(error).lower():
            logger.info(f"ADB server error for device {device_id}, attempting server restart")
            # Could implement ADB server restart here
            return False
        
        return False

def create_error_handler(max_retries: int = None, retry_delay: float = None) -> ErrorHandler:
    """Factory function to create an ErrorHandler instance"""
    return ErrorHandler(max_retries, retry_delay)

def log_error_with_context(error: Exception, context: str = "", device_id: str = "", **kwargs):
    """
    Log an error with additional context information
    
    Args:
        error: The exception that occurred
        context: Description of what was happening when the error occurred
        device_id: ID of the device involved (if applicable)
        **kwargs: Additional context variables to log
    """
    error_info = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
        "device_id": device_id,
        **kwargs
    }
    
    logger.error(f"Error occurred: {error_info}")
    logger.error(traceback.format_exc())
    
    # Log additional context if provided
    if kwargs:
        context_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        logger.error(f"Additional context: {context_str}")

def is_recoverable_error(error: Exception) -> bool:
    """
    Determine if an error is recoverable
    
    Args:
        error: The exception to check
        
    Returns:
        True if the error is recoverable, False otherwise
    """
    recoverable_errors = (
        TimeoutError,
        ConnectionError,
        OSError,  # For file/network operations
    )
    
    return isinstance(error, recoverable_errors)

def get_error_summary(error: Exception) -> dict:
    """
    Get a summary of error information
    
    Args:
        error: The exception to analyze
        
    Returns:
        Dictionary containing error summary information
    """
    return {
        "type": type(error).__name__,
        "message": str(error),
        "recoverable": is_recoverable_error(error),
        "traceback": traceback.format_exc()
    }
