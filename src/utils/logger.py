"""
Logger Configuration Module

Provides a centralized logging setup for the application. Configures both file 
and console logging with rotation support and fallback mechanisms.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional
from src.config.settings import LOG_FORMAT, LOG_FILE, LOG_LEVEL

class LoggerConfigurationError(Exception):
    """Custom exception for logger setup failures"""
    pass

def setup_logger(name: str) -> logging.Logger:
    """
    Configures and returns a logger instance with file and console handlers.
    
    Args:
        name: Name of the logger (usually __name__)
    
    Returns:
        Configured logger instance
        
    Raises:
        LoggerConfigurationError: If critical failure occurs during setup
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handler initialization
    if logger.hasHandlers():
        return logger
        
    try:
        # Ensure log directory exists
        log_dir = os.path.dirname(LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Set log level from configuration
        log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
        logger.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter(LOG_FORMAT)
        
        # File handler with rotation
        try:
            file_handler = RotatingFileHandler(
                LOG_FILE, 
                maxBytes=5*1024*1024,  # 5MB
                backupCount=3
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (PermissionError, OSError) as file_err:
            raise LoggerConfigurationError(
                f"File handler setup failed: {str(file_err)}"
            ) from file_err
        
        # Console handler (warnings and above only)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.WARNING)
        logger.addHandler(console_handler)
        
        return logger
        
    except LoggerConfigurationError as lce:
        # Reraise our custom exception
        raise lce
        
    except Exception as e:
        # Fallback to basic config
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
        logger = logging.getLogger(name)
        logger.error(
            "Logger setup failed, using basic configuration: %s", 
            str(e)
        )
        return logger
