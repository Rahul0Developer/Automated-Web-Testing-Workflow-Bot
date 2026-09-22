"""
Logging utility module for the Automated Web Testing & Workflow Bot.

This module provides a robust logging system that tracks:
- Execution steps
- Timestamps
- Error traces
- Success/failure statuses
"""

import logging
import os
from datetime import datetime
from config import LOG_FILE_PATH


def setup_logger(name: str = "workflow_bot") -> logging.Logger:
    """
    Set up and return a configured logger instance.
    
    Args:
        name: Name for the logger instance
        
    Returns:
        Configured logging.Logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(LOG_FILE_PATH)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers to avoid duplicate logs
    if logger.handlers:
        logger.handlers.clear()
    
    # Create file handler for writing logs to file
    file_handler = logging.FileHandler(LOG_FILE_PATH, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Create console handler for displaying logs in terminal
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter with timestamp, level, and message
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_timestamp() -> str:
    """
    Get current timestamp in ISO format for logging purposes.
    
    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log_execution_step(logger: logging.Logger, step_name: str, 
                       details: str = "", level: str = "info") -> None:
    """
    Log an execution step with optional details.
    
    Args:
        logger: Logger instance
        step_name: Name of the step being logged
        details: Additional details about the step
        level: Log level (debug, info, warning, error, critical)
    """
    log_func = getattr(logger, level)
    message = f"[{step_name}]"
    if details:
        message += f" - {details}"
    log_func(message)


def log_error_with_traceback(logger: logging.Logger, error: Exception, 
                             context: str = "") -> None:
    """
    Log an error with full traceback information.
    
    Args:
        logger: Logger instance
        error: Exception object
        context: Additional context about where the error occurred
    """
    import traceback
    
    error_message = f"{context}: {type(error).__name__}: {str(error)}"
    logger.error(error_message)
    logger.debug(f"Traceback:\n{traceback.format_exc()}")
