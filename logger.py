# logger.py
"""
Logger Utility

Responsibilities:
- Provide a centralized logger factory
- Configure console and file handlers
- Support dynamic log level updates
- Ensure consistent formatting across modules
- Prevent duplicate handlers
"""

import logging
import sys
from typing import Optional


# -----------------------------
# Default configuration
# -----------------------------
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = "[%(levelname)s] %(asctime)s %(name)s: %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(
    name: Optional[str] = None,
    level: int = DEFAULT_LOG_LEVEL,
    log_to_console: bool = True,
    log_to_file: Optional[str] = None,
    propagate: bool = False,
) -> logging.Logger:
    """
    Create or retrieve a logger with standardized configuration.

    Args:
        name: Logger name (defaults to "ccb")
        level: Logging level (default INFO)
        log_to_console: Whether to log to console (default True)
        log_to_file: Optional file path for file logging
        propagate: Whether to propagate logs to parent loggers

    Returns:
        Configured logging.Logger instance
    """
    logger = logging.getLogger(name or "ccb")

    # Prevent duplicate handlers
    if not logger.handlers:
        logger.setLevel(level)
        formatter = logging.Formatter(DEFAULT_LOG_FORMAT, datefmt=DEFAULT_DATE_FORMAT)

        # Console handler
        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        # File handler
        if log_to_file:
            file_handler = logging.FileHandler(log_to_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    logger.propagate = propagate
    return logger


# -----------------------------
# Utility functions
# -----------------------------
def set_log_level(logger: logging.Logger, level: int) -> None:
    """
    Dynamically update log level for a given logger.
    """
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)


def add_file_handler(logger: logging.Logger, file_path: str, level: int = DEFAULT_LOG_LEVEL) -> None:
    """
    Add a file handler to an existing logger.
    """
    formatter = logging.Formatter(DEFAULT_LOG_FORMAT, datefmt=DEFAULT_DATE_FORMAT)
    file_handler = logging.FileHandler(file_path)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def add_console_handler(logger: logging.Logger, level: int = DEFAULT_LOG_LEVEL) -> None:
    """
    Add a console handler to an existing logger.
    """
    formatter = logging.Formatter(DEFAULT_LOG_FORMAT, datefmt=DEFAULT_DATE_FORMAT)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def remove_handlers(logger: logging.Logger) -> None:
    """
    Remove all handlers from a logger.
    """
    for handler in list(logger.handlers):
        logger.removeHandler(handler)


def get_log_levels() -> dict:
    """
    Return a dictionary of available logging levels.
    """
    return {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "NOTSET": logging.NOTSET,
    }
