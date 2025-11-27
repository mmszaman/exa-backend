"""
Logger setup for structured logging across the application.
"""

import logging
import sys


def setup_logging(level=logging.INFO):
    """
    Configure structured logging with UTC timestamps and consistent formatting.
    """
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    if not root_logger.handlers:
        root_logger.addHandler(console_handler)
