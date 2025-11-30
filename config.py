# config.py
"""
Central configuration module.

Responsibilities:
- Define default thresholds and parameters for all subsystems
- Allow environment variable overrides
- Provide validation and safe access utilities
- Support dynamic updates at runtime
"""

import os
from typing import Dict, Any, Optional


# -----------------------------
# Default configuration values
# -----------------------------
DEFAULTS: Dict[str, Any] = {
    # Confidence thresholds
    "intent_conf_threshold": 0.6,
    "emotion_conf_threshold": 0.55,
    "subtext_conf_threshold": 0.55,

    # Summarizer settings
    "summary_max_points": 10,
    "summary_max_recent": 6,

    # Model settings
    "model_provider": "mock",       # e.g. "openai", "azure", "mock"
    "model_temperature": 0.7,       # creativity vs determinism
    "max_tokens": 512,              # output length limit

    # Logging & debugging
    "log_level": "INFO",            # DEBUG, INFO, WARNING, ERROR
    "enable_tracing": False,        # toggle detailed tracing

    # State machine
    "fsm_initial_state": "idle",
    "fsm_allow_unknown": True,

    # Conversation memory
    "max_turns": 100,               # max stored turns before pruning
    "prune_strategy": "oldest",     # oldest or least_relevant

    # Subtext detector
    "subtext_max_tags": 5,

    # Emotion classifier
    "emotion_labels": ["positive", "negative", "neutral"],

    # Intent classifier
    "intent_labels": [
        "greeting", "goodbye", "help_request", "question",
        "feedback", "instruction", "request", "emotional_state",
        "exclamation", "thanks", "apology", "weather", "time"
    ],
}


# -----------------------------
# Utility functions
# -----------------------------
def get(key: str, default: Optional[Any] = None) -> Any:
    """
    Retrieve a configuration value.
    Priority: environment variable > DEFAULTS > provided default.
    """
    env_key = key.upper()
    if env_key in os.environ:
        val = os.environ[env_key]
        # Attempt type conversion based on DEFAULTS type
        if key in DEFAULTS:
            return _convert_type(val, type(DEFAULTS[key]))
        return val
    return DEFAULTS.get(key, default)


def set(key: str, value: Any) -> None:
    """
    Update a configuration value at runtime.
    """
    DEFAULTS[key] = value


def all_config() -> Dict[str, Any]:
    """
    Return a snapshot of all configuration values,
    including environment overrides.
    """
    return {k: get(k) for k in DEFAULTS.keys()}


def validate() -> Dict[str, str]:
    """
    Validate configuration values.
    Returns a dict of errors keyed by config name.
    """
    errors: Dict[str, str] = {}

    # Thresholds must be between 0 and 1
    for key in ["intent_conf_threshold", "emotion_conf_threshold", "subtext_conf_threshold"]:
        val = get(key)
        if not (0.0 <= val <= 1.0):
            errors[key] = f"Threshold {val} out of range [0,1]"

    # Temperature must be between 0 and 1
    temp = get("model_temperature")
    if not (0.0 <= temp <= 1.0):
        errors["model_temperature"] = f"Temperature {temp} out of range [0,1]"

    # Max tokens must be positive
    tokens = get("max_tokens")
    if tokens <= 0:
        errors["max_tokens"] = f"Max tokens must be > 0, got {tokens}"

    # Max turns must be positive
    turns = get("max_turns")
    if turns <= 0:
        errors["max_turns"] = f"Max turns must be > 0, got {turns}"

    return errors


def _convert_type(val: str, target_type: type) -> Any:
    """
    Convert string environment variable to target type.
    """
    try:
        if target_type is bool:
            return val.lower() in ("1", "true", "yes", "on")
        if target_type is int:
            return int(val)
        if target_type is float:
            return float(val)
        return val
    except Exception:
        return val
