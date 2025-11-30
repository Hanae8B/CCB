# utils.py
"""
Utility Module

Responsibilities:
- Provide text normalization, cleaning, and analysis helpers
- Provide logging configuration utilities
- Support extensibility and transparency
"""

import re
import logging
import unicodedata
from typing import List, Dict, Any


# -----------------------------
# Text helpers
# -----------------------------
def normalize_text(text: str) -> str:
    """
    Lowercase and normalize whitespace in a string.
    Example: "  Hello   WORLD!! " -> "hello world!!"
    """
    if not text:
        return ""
    t = text.strip().lower()
    t = re.sub(r"\s+", " ", t)
    return t


def clean_string(text: str) -> str:
    """
    Remove non-alphanumeric characters except basic punctuation.
    Example: "Hello@World!!!" -> "HelloWorld!!!"
    """
    if not text:
        return ""
    return re.sub(r"[^a-zA-Z0-9\s.,!?]", "", text)


def strip_accents(text: str) -> str:
    """
    Remove accents/diacritics from characters.
    Example: "café" -> "cafe"
    """
    if not text:
        return ""
    return "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )


def tokenize(text: str) -> List[str]:
    """
    Split text into tokens (words).
    Example: "Hello world!" -> ["hello", "world"]
    """
    if not text:
        return []
    t = normalize_text(text)
    return re.findall(r"\b\w+\b", t)


def is_question(text: str) -> bool:
    """
    Quick check if a string looks like a question.
    Example: "What time is it?" -> True
    """
    if not text:
        return False
    t = normalize_text(text)
    return "?" in t or t.startswith(
        ("what", "why", "how", "when", "where", "who", "which", "do", "can", "is", "are")
    )


def word_count(text: str) -> int:
    """
    Count number of words in text.
    """
    return len(tokenize(text))


def char_count(text: str) -> int:
    """
    Count number of characters in text.
    """
    return len(text) if text else 0


def contains_emphasis(text: str) -> bool:
    """
    Detect emphasis markers (exclamation marks, ALL CAPS words).
    """
    if not text:
        return False
    if "!" in text:
        return True
    if any(word.isupper() and len(word) > 2 for word in text.split()):
        return True
    return False


def extract_numbers(text: str) -> List[str]:
    """
    Extract all numeric substrings from text.
    Example: "I have 2 apples and 10 oranges." -> ["2", "10"]
    """
    if not text:
        return []
    return re.findall(r"\d+", text)


# -----------------------------
# Logging helpers
# -----------------------------
def get_logger(name: str = "ccb") -> logging.Logger:
    """
    Returns a configured logger.
    - Default level: INFO
    - Console handler with timestamp and module name
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(levelname)s] %(asctime)s %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def set_log_level(logger: logging.Logger, level: int) -> None:
    """
    Dynamically update log level for a given logger.
    """
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)


def add_file_handler(logger: logging.Logger, file_path: str, level: int = logging.INFO) -> None:
    """
    Add a file handler to an existing logger.
    """
    formatter = logging.Formatter(
        "[%(levelname)s] %(asctime)s %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler = logging.FileHandler(file_path)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def remove_handlers(logger: logging.Logger) -> None:
    """
    Remove all handlers from a logger.
    """
    for handler in list(logger.handlers):
        logger.removeHandler(handler)


def get_log_levels() -> Dict[str, int]:
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
