# error_handler.py
"""
Error Handler

Responsibilities:
- Provide safe execution wrappers for functions
- Log exceptions with stack traces
- Offer graceful fallback messages for common error scenarios
- Categorize errors for structured handling
- Support custom error handlers and inspection utilities
"""

import traceback
from typing import Callable, Any, Optional, Dict, Type
from logger import get_logger

log = get_logger(__name__)


# -----------------------------
# Safe execution wrapper
# -----------------------------
def safe_call(fn: Callable[..., Any], *args, **kwargs) -> Optional[Any]:
    """
    Executes a function safely, logs exceptions, and returns None on failure.

    Args:
        fn: Function to execute
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Function result or None if exception occurs
    """
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        log.error(f"[safe_call] Exception in {fn.__name__}: {e}\n{traceback.format_exc()}")
        return None


# -----------------------------
# Graceful error fallbacks
# -----------------------------
class GracefulErrors:
    """
    Provides graceful fallbacks for common error scenarios.
    """

    @staticmethod
    def on_bad_input(message: str) -> str:
        """
        Fallback when user input is invalid or cannot be processed.
        """
        log.warning(f"[GracefulErrors] Bad input detected: {message}")
        return "I couldn't process that input. Could you rephrase or provide more details?"

    @staticmethod
    def on_schema_violation() -> str:
        """
        Fallback when schema validation fails.
        """
        log.error("[GracefulErrors] Schema violation occurred.")
        return "Something went wrong internally with how the data was structured. Please try again."

    @staticmethod
    def on_model_failure() -> str:
        """
        Fallback when model inference fails or model is unavailable.
        """
        log.error("[GracefulErrors] Model failure detected.")
        return "The model seems unavailable right now. Let's try a simpler approach or retry shortly."

    @staticmethod
    def on_timeout() -> str:
        """
        Fallback when operation times out.
        """
        log.error("[GracefulErrors] Operation timed out.")
        return "This is taking longer than expected. Let's try again or simplify the request."

    @staticmethod
    def on_unknown_error(e: Exception) -> str:
        """
        Fallback for unexpected errors.
        """
        log.error(f"[GracefulErrors] Unknown error: {e}\n{traceback.format_exc()}")
        return "An unexpected error occurred. Please try again later."


# -----------------------------
# Error categorization
# -----------------------------
ERROR_CATEGORIES: Dict[str, Type[Exception]] = {
    "ValueError": ValueError,
    "TypeError": TypeError,
    "KeyError": KeyError,
    "TimeoutError": TimeoutError,
    "RuntimeError": RuntimeError,
    "Exception": Exception,
}


def categorize_error(e: Exception) -> str:
    """
    Categorize an exception into a known error type string.
    """
    for name, exc_type in ERROR_CATEGORIES.items():
        if isinstance(e, exc_type):
            return name
    return "UnknownError"


# -----------------------------
# Error handling utilities
# -----------------------------
def handle_error(e: Exception) -> str:
    """
    Handle an exception gracefully and return a fallback message.
    """
    category = categorize_error(e)
    log.error(f"[handle_error] Handling {category}: {e}\n{traceback.format_exc()}")

    if category == "ValueError":
        return GracefulErrors.on_bad_input(str(e))
    elif category == "TypeError":
        return GracefulErrors.on_schema_violation()
    elif category == "TimeoutError":
        return GracefulErrors.on_timeout()
    elif category == "RuntimeError":
        return GracefulErrors.on_model_failure()
    else:
        return GracefulErrors.on_unknown_error(e)


def safe_execute(fn: Callable[..., Any], *args, **kwargs) -> str:
    """
    Execute a function safely and return either result or graceful error message.
    """
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        return handle_error(e)
