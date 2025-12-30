
import logging
import os
from datetime import datetime
from pathlib import Path


class ExaLogger:

    _loggers = {}  # Cache loggers to avoid duplicates
    
    @staticmethod
    def get_logger(name: str, log_file: str = None) -> logging.Logger:

        # Use cached logger if already created
        if name in ExaLogger._loggers:
            return ExaLogger._loggers[name]
        
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)  # Capture all levels
        
        # Prevent duplicate handlers if logger already exists
        if logger.handlers:
            return logger
        
        # Determine log file path (use /tmp on serverless platforms)
        if log_file is None:
            # Check if running on Vercel or similar read-only serverless env
            is_serverless = os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME")
            
            if is_serverless:
                log_dir = Path("/tmp/logs")
            else:
                log_dir = Path("logs")
            
            try:
                log_dir.mkdir(exist_ok=True, parents=True)
                log_file = log_dir / f"{name}.log"
            except (OSError, PermissionError):
                # If can't create log dir, skip file logging
                log_file = None
        
        # Create formatters
        file_formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = logging.Formatter(
            fmt='%(levelname)s - %(name)s - %(message)s'
        )
        
        # File handler (writes to file) - only if log_file is available
        if log_file:
            try:
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)
            except (OSError, PermissionError):
                # Skip file logging if not possible
                pass
        
        # Console handler (prints to terminal)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)  # Only INFO+ to console
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # Cache logger
        ExaLogger._loggers[name] = logger
        
        return logger


# Convenience function for quick use
def get_logger(name: str, log_file: str = None) -> logging.Logger:
    return ExaLogger.get_logger(name, log_file)