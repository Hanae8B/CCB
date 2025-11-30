# intent_classifier.py
"""
Intent Classifier

Responsibilities:
- Deterministically classify text into intents using regex/keyword matching
- Support confidence scoring and rationale
- Handle multiple overlapping intents
- Provide transparency utilities

Recognized intents:
- Standard conversation intents (greeting, goodbye, help, etc.)
- Emotional states (positive, negative, neutral)
- Exclamatory statements
- Small talk (weather, time, thanks, apologies)
- Commands/instructions
- Questions (yes/no, wh-questions, choice questions)
- Feedback and opinions
- Requests (polite or direct)
- Fallback: unknown
"""

from typing import List, Optional, Dict, Tuple, Any
import re


class IntentClassifier:
    """
    Deterministic intent classifier using keyword/regex matching.
    Fast, predictable, and dependency-free.

    Features:
    - Extensible: add new intents easily
    - Priority-based: first match wins
    - Multi-intent detection option
    - Confidence scoring
    - Rationale explanation
    """

    DEFAULT_INTENTS: Dict[str, List[str]] = {
        # Greetings & farewells
        "greeting": [r"\bhi\b", r"\bhello\b", r"\bhey\b", r"\bgood morning\b", r"\bgood evening\b"],
        "goodbye": [r"\bbye\b", r"\bfarewell\b", r"\bsee you\b", r"\btake care\b", r"\bgood night\b"],

        # Help & support
        "help_request": [r"\bhelp\b", r"\bsupport\b", r"\bassistance\b", r"\bcan you help\b"],

        # Questions
        "question": [r".*\?$"],  # ends with a question mark
        "yes_no_question": [r"^(is|are|do|does|can|will|would|should|could)\b.*\?$"],
        "wh_question": [r"^(who|what|when|where|why|how)\b.*\?$"],
        "choice_question": [r".*\bor\b.*\?"],

        # Feedback & opinions
        "feedback": [r"\blike\b", r"\blove\b", r"\bhate\b", r"\bfeedback\b", r"\bdislike\b"],
        "opinion": [r"\bI think\b", r"\bmy opinion\b", r"\bI believe\b"],

        # Instructions & requests
        "instruction": [
            r"\bplease\b", r"\bcan you\b", r"\bcalculate\b", r"\badd\b", r"\bsubtract\b",
            r"\bshow me\b", r"\bgive me\b", r"\bexplain\b"
        ],
        "request": [r"\bcan you\b", r"\bwould you\b", r"\bplease\b", r"\bI need\b", r"\bI want\b"],

        # Emotional states
        "emotional_positive": [r"\bI am happy\b", r"\bI feel good\b", r"\bI’m excited\b", r"\bI am grateful\b"],
        "emotional_negative": [
            r"\bI am sad\b", r"\bI feel bad\b", r"\bI’m angry\b", r"\bI am tired\b",
            r"\bI feel lonely\b", r"\bI am depressed\b"
        ],
        "emotional_neutral": [r"\bI am okay\b", r"\bI feel fine\b", r"\bI’m alright\b"],
        "emotional_state": [r"\bi am\b", r"\bi feel\b", r"\bI’m\b"],

        # Exclamations
        "exclamation": [r".*!{1,}$"],  # ends with one or more exclamation marks

        # Small talk
        "thanks": [r"\bthank you\b", r"\bthanks\b", r"\bmuch appreciated\b"],
        "apology": [r"\bsorry\b", r"\bmy apologies\b", r"\bforgive me\b"],
        "weather": [r"\bweather\b", r"\bris it raining\b", r"\bsunny\b", r"\bforecast\b"],
        "time": [r"\btime\b", r"\bwhat time\b", r"\bclock\b"],
    }

    PRIORITY_ORDER: List[str] = list(DEFAULT_INTENTS.keys()) + ["unknown"]

    def __init__(self, intent_patterns: Optional[Dict[str, List[str]]] = None):
        patterns = intent_patterns or self.DEFAULT_INTENTS
        self._compiled: Dict[str, List[re.Pattern]] = {
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

    def classify_with_confidence(self, text: str) -> Tuple[str, float]:
        """
        Returns (intent, confidence) based on match strength.
        Confidence is a heuristic: 1.0 for strong match, 0.5 for weak, 0.0 for none.
        """
        if not text or not text.strip():
            return "unknown", 0.0

        for intent, regexes in self._compiled.items():
            for r in regexes:
                if r.search(text):
                    # Confidence heuristic: longer regex match = stronger
                    conf = 1.0 if len(r.pattern) > 5 else 0.5
                    return intent, conf
        return "unknown", 0.0

    def classify_all(self, text: str) -> List[str]:
        """
        Returns all matching intents for the given text.
        Useful when multiple intents overlap.
        """
        if not text or not text.strip():
            return ["unknown"]

        matches = []
        for intent, regexes in self._compiled.items():
            if any(r.search(text) for r in regexes):
                matches.append(intent)
        return matches or ["unknown"]

    def explain(self, text: str) -> Dict[str, Any]:
        """
        Returns detailed explanation:
        - Primary intent
        - All matches
        - Confidence score
        - Rationale
        """
        primary, confidence = self.classify_with_confidence(text)
        all_matches = self.classify_all(text)
        rationale = f"Matched intents: {', '.join(all_matches)}" if all_matches else "No matches"
        return {
            "text": text,
            "primary": primary,
            "confidence": confidence,
            "all_matches": all_matches,
            "rationale": rationale,
        }

    def add_intent(self, name: str, patterns: List[str]) -> None:
        """
        Dynamically add a new intent with regex patterns.
        """
        self._compiled[name] = [re.compile(pat, flags=re.IGNORECASE) for pat in patterns]

    def remove_intent(self, name: str) -> None:
        """
        Remove an intent from the classifier.
        """
        if name in self._compiled:
            del self._compiled[name]

    def list_intents(self) -> List[str]:
        """
        List all available intents.
        """
        return list(self._compiled.keys())
