# intent_classifier.py
from typing import List, Optional, Dict
import re


class IntentClassifier:
    """
    Bare-minimum, deterministic intent classifier using keyword/regex matching.
    Designed to be fast, predictable, and dependency-free.
    """

    DEFAULT_INTENTS = {
        "greeting": [r"\bhi\b", r"\bhello\b", r"\bhey\b"],
        "goodbye": [r"\bbye\b", r"\bfarewell\b", r"\bsee you\b"],
        "help_request": [r"\bhelp\b", r"\bsupport\b", r"\bassistance\b"],
        "question": [r"\bwho\b", r"\bwhat\b", r"\bwhen\b", r"\bwhere\b", r"\bwhy\b", r"\bhow\b", r"\?$"],
        "feedback": [r"\blike\b", r"\blove\b", r"\bhate\b", r"\bfeedback\b"],
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
        Simple priority is the order of dict keys.
        """
        if not text or not text.strip():
            return "unknown"

        for intent, regexes in self._compiled.items():
            if any(r.search(text) for r in regexes):
                return intent
        return "unknown"
