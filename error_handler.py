# error_handler.py
import traceback
from typing import Callable, Any, Optional
from logger import get_logger

log = get_logger(__name__)


def safe_call(fn: Callable[..., Any], *args, **kwargs) -> Optional[Any]:
    """
    Executes a function safely, logs exceptions, and returns None on failure.
    """
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        log.error(f"Exception: {e}\n{traceback.format_exc()}")
        return None


class GracefulErrors:
    """
    Provides graceful fallbacks for common error scenarios.
    """

    @staticmethod
    def on_bad_input(message: str) -> str:
        return "I couldn't process that input. Could you rephrase or provide more details?"

    @staticmethod
    def on_schema_violation() -> str:
        return "Something went wrong internally with how the data was structured. Please try again."

    @staticmethod
    def on_model_failure() -> str:
        return "The model seems unavailable right now. Let's try a simpler approach or retry shortly."
