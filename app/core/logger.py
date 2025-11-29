"""
Exa Logger - Write logs to different files for different modules.
"""

import logging
import os
from datetime import datetime
from pathlib import Path


class ExaLogger:
    """
    Custom logger that writes to specific log files.
    Each module can have its own log file for easy debugging.
    """
    
    _loggers = {}  # Cache loggers to avoid duplicates
    
    @staticmethod
    def get_logger(name: str, log_file: str = None) -> logging.Logger:
        """
        Get or create a logger that writes to a specific file.
        
        Args:
            name: Logger name (usually module name like 'email_service')
            log_file: File path to write logs (default: logs/{name}.log)
            
        Returns:
            logging.Logger: Configured logger instance
        """
        # Use cached logger if already created
        if name in ExaLogger._loggers:
            return ExaLogger._loggers[name]
        
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)  # Capture all levels
        
        # Prevent duplicate handlers if logger already exists
        if logger.handlers:
            return logger
        
        # Determine log file path
        if log_file is None:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)  # Create logs folder if doesn't exist
            log_file = log_dir / f"{name}.log"
        
        # Create formatters
        file_formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = logging.Formatter(
            fmt='%(levelname)s - %(name)s - %(message)s'
        )
        
        # File handler (writes to file)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        
        # Console handler (prints to terminal)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)  # Only INFO+ to console
        console_handler.setFormatter(console_formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        # Cache logger
        ExaLogger._loggers[name] = logger
        
        return logger


# Convenience function for quick use
def get_logger(name: str, log_file: str = None) -> logging.Logger:
    """
    Quick function to get a logger.
    
    Usage:
        from app.core.logger import get_logger
        logger = get_logger('email_service')
        logger.info('Email sent successfully')
    """
    return ExaLogger.get_logger(name, log_file)