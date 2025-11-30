# utils.py
import re
import logging

# -----------------------------
# Text helpers
# -----------------------------

def normalize_text(text: str) -> str:
    """
    Lowercase and normalize whitespace in a string.
    Example: "  Hello   WORLD!! " -> "hello world!!"
    """
    t = text.strip().lower()
    t = re.sub(r"\s+", " ", t)
    return t


def clean_string(text: str) -> str:
    """
    Remove non-alphanumeric characters except basic punctuation.
    """
    return re.sub(r"[^a-zA-Z0-9\s.,!?]", "", text)


def is_question(text: str) -> bool:
    """
    Quick check if a string looks like a question.
    """
    t = normalize_text(text)
    return "?" in t or t.startswith(("what", "why", "how", "when", "where", "who", "which"))


# -----------------------------
# Logging helpers
# -----------------------------

def get_logger(name: str = "ccb") -> logging.Logger:
    """
    Returns a configured logger.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(levelname)s] %(asctime)s %(name)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
