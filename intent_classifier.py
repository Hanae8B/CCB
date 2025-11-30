# intent_classifier.py
from typing import List, Optional, Dict
import re


class IntentClassifier:
    """
    Deterministic intent classifier using keyword/regex matching.
    Fast, predictable, and dependency-free.

    Recognizes:
    - standard conversation intents
    - emotional states
    - exclamatory statements
    """

    DEFAULT_INTENTS = {
        "greeting": [r"\bhi\b", r"\bhello\b", r"\bhey\b"],
        "goodbye": [r"\bbye\b", r"\bfarewell\b", r"\bsee you\b"],
        "help_request": [r"\bhelp\b", r"\bsupport\b", r"\bassistance\b"],
        # Refined question patterns: only actual questions
        "question": [r".*\?$"],  # ends with a question mark
        "feedback": [r"\blike\b", r"\blove\b", r"\bhate\b", r"\bfeedback\b"],
        "instruction": [r"\bplease\b", r"\bcan you\b", r"\bcalculate\b", r"\badd\b", r"\bsubtract\b"],
        "request": [r"\bcan you\b", r"\bwould you\b", r"\bplease\b"],
        # Emotional states
        "emotional_state": [r"\bi am\b", r"\bi feel\b", r"\bI’m\b", r"\bI am exhausted\b", r"\bI am tired\b", r"\bI feel sad\b"],
        # New intent for exclamatory statements
        "exclamation": [r".*!{1,}"],  # sentences ending with one or more exclamation marks
    }

    def __init__(self, intent_patterns: Optional[Dict[str, List[str]]] = None):
        patterns = intent_patterns or self.DEFAULT_INTENTS
        self._compiled = {
            intent: [re.compile(pat, flags=re.IGNORECASE) for pat in pats]
            for intent, pats in patterns.items()
        }

    def classify(self, text: str) -> str:
        """
        Returns the best-matching intent label or 'unknown' if no match.
        Priority is based on the order of dict keys.
        """
        if not text or not text.strip():
            return "unknown"

        for intent, regexes in self._compiled.items():
            if any(r.search(text) for r in regexes):
                return intent
        return "unknown"
